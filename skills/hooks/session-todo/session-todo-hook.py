# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
"""
Session TODO Hook - SessionEnd Hook
=====================================

On session exit, parses the conversation transcript to extract
outstanding issues, incomplete tasks, and user requests that
weren't fully addressed. Writes them to TODO.md in the project
directory.

Sources of outstanding items:
1. Task system (TaskCreate/TaskUpdate) — incomplete tasks
2. User messages — recent requests for context
3. Assistant messages — mentions of TODO, remaining work, errors

Exit codes:
  0 = Always (SessionEnd hooks cannot block termination)
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def parse_transcript(transcript_path: str) -> List[Dict[str, Any]]:
    """Parse JSONL transcript into list of entries."""
    entries = []
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    return entries


def extract_tasks_from_transcript(entries: List[Dict[str, Any]]) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
    """Extract tasks from TaskCreate/TaskUpdate tool calls.

    Returns: (created_tasks, completed_task_ids)
    """
    created_tasks = {}  # task_id -> {subject, description, status}
    task_counter = 0

    for entry in entries:
        if entry.get("type") != "assistant":
            continue

        message = entry.get("message", {})
        content = message.get("content", [])
        if not isinstance(content, list):
            continue

        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") != "tool_use":
                continue

            name = block.get("name", "")
            inp = block.get("input", {})

            if name == "TaskCreate":
                task_counter += 1
                task_id = str(task_counter)
                created_tasks[task_id] = {
                    "subject": inp.get("subject", "Unknown task"),
                    "description": inp.get("description", ""),
                    "status": "pending",
                }

            elif name == "TaskUpdate":
                tid = inp.get("taskId", "")
                new_status = inp.get("status", "")
                if tid in created_tasks and new_status:
                    created_tasks[tid]["status"] = new_status
                # Also update subject/description if provided
                if tid in created_tasks:
                    if inp.get("subject"):
                        created_tasks[tid]["subject"] = inp["subject"]
                    if inp.get("description"):
                        created_tasks[tid]["description"] = inp["description"]

    # Also check the todos field on the last message that has it
    last_todos = None
    for entry in reversed(entries):
        todos = entry.get("todos")
        if todos and isinstance(todos, list) and len(todos) > 0:
            last_todos = todos
            break

    if last_todos:
        # Override with actual task system state
        created_tasks.clear()
        for todo in last_todos:
            tid = todo.get("id", str(len(created_tasks) + 1))
            created_tasks[tid] = {
                "subject": todo.get("subject", "Unknown"),
                "description": todo.get("description", ""),
                "status": todo.get("status", "pending"),
            }

    return created_tasks


def extract_user_requests(entries: List[Dict[str, Any]], max_messages: int = 10) -> List[str]:
    """Extract the last N user messages for context."""
    user_messages = []
    for entry in entries:
        if entry.get("type") != "user":
            continue
        message = entry.get("message", {})
        content = message.get("content", "")

        # Skip tool results
        if isinstance(content, list):
            texts = []
            for block in content:
                if isinstance(block, dict):
                    if block.get("type") == "text":
                        texts.append(block.get("text", ""))
                    elif block.get("type") == "tool_result":
                        continue
                elif isinstance(block, str):
                    texts.append(block)
            content = " ".join(texts)

        if not content or len(content.strip()) < 3:
            continue
        # Skip command messages and system tags
        if any(tag in content for tag in [
            "<command-message>", "<command-name>",
            "<local-command-stdout>", "<system-reminder>",
        ]):
            continue
        # Skip meta/system messages
        if entry.get("isMeta"):
            continue

        user_messages.append(content.strip())

    return user_messages[-max_messages:]


def extract_outstanding_mentions(entries: List[Dict[str, Any]]) -> List[str]:
    """Extract TODO/FIXME/remaining work mentions from assistant messages."""
    mentions = []
    seen = set()

    # Words that indicate something is DONE, not outstanding
    done_prefixes = re.compile(
        r'^\s*(done|completed|finished|fixed|resolved|implemented|created|added|updated|already)',
        re.IGNORECASE,
    )

    for entry in entries:
        if entry.get("type") != "assistant":
            continue
        message = entry.get("message", {})
        content = message.get("content", [])
        if not isinstance(content, list):
            continue

        for block in content:
            if not isinstance(block, dict) or block.get("type") != "text":
                continue
            text = block.get("text", "")
            for line in text.split("\n"):
                line_stripped = line.strip()

                # Skip lines that start with completion words
                if done_prefixes.match(line_stripped):
                    continue

                # Look for strong TODO/FIXME markers (always include)
                strong_match = re.search(
                    r'\b(TODO|FIXME|HACK|XXX)\b',
                    line_stripped,
                )
                # Look for weaker "outstanding work" patterns
                # but require they appear as actionable statements
                weak_match = re.search(
                    r'(still need to|needs to be|should still|not yet implemented|'
                    r'remains to be|outstanding issue|incomplete|unfinished|'
                    r'couldn\'t|was not able to|failed to|blocked by)',
                    line_stripped,
                    re.IGNORECASE,
                )

                if strong_match or weak_match:
                    # Skip very short or very long lines
                    if 10 < len(line_stripped) < 300:
                        normalized = line_stripped.lower()
                        if normalized not in seen:
                            seen.add(normalized)
                            mentions.append(line_stripped)

    # Only return the last 20 mentions (most recent are most relevant)
    return mentions[-20:]


def build_todo_content(
    tasks: Dict[str, Dict],
    user_requests: List[str],
    mentions: List[str],
    session_id: str,
    project_dir: str,
) -> Optional[str]:
    """Build the TODO.md content section for this session."""
    incomplete_tasks = {
        tid: t for tid, t in tasks.items()
        if t["status"] not in ("completed", "deleted")
    }

    # If nothing outstanding, don't write
    if not incomplete_tasks and not mentions:
        return None

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = []
    lines.append(f"\n## Session {now} ({session_id[:8]})")
    lines.append("")

    if incomplete_tasks:
        lines.append("### Incomplete Tasks")
        for tid, task in sorted(incomplete_tasks.items()):
            status_icon = "🔄" if task["status"] == "in_progress" else "⬜"
            line = f"- [ ] {status_icon} {task['subject']}"
            if task.get("description"):
                # Truncate long descriptions
                desc = task["description"][:200]
                if len(task["description"]) > 200:
                    desc += "..."
                line += f" — {desc}"
            lines.append(line)
        lines.append("")

    if mentions:
        lines.append("### Outstanding Items")
        for mention in mentions:
            # Clean up the mention
            clean = mention.lstrip("- *>#")
            lines.append(f"- [ ] {clean.strip()}")
        lines.append("")

    if user_requests:
        lines.append("### Last User Requests (context)")
        for req in user_requests[-5:]:
            # Truncate long requests
            short = req[:150]
            if len(req) > 150:
                short += "..."
            lines.append(f"- {short}")
        lines.append("")

    return "\n".join(lines)


def write_todo(project_dir: str, content: str) -> None:
    """Create or append to TODO.md in the project directory."""
    todo_path = Path(project_dir) / "TODO.md"

    if todo_path.exists():
        existing = todo_path.read_text(encoding="utf-8")
        # Append new section
        updated = existing.rstrip("\n") + "\n" + content
    else:
        # Create new file with header
        updated = "# TODO\n\nOutstanding issues from Claude Code sessions.\n" + content

    todo_path.write_text(updated, encoding="utf-8")


def main() -> None:
    # Read hook input from stdin
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, Exception):
        sys.exit(0)

    transcript_path = input_data.get("transcript_path", "")
    cwd = input_data.get("cwd", "")
    session_id = input_data.get("session_id", "unknown")

    # Determine project directory
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", cwd)
    if not project_dir:
        sys.exit(0)

    if not transcript_path or not Path(transcript_path).exists():
        sys.exit(0)

    # Parse transcript
    entries = parse_transcript(transcript_path)
    if not entries:
        sys.exit(0)

    # Extract data
    tasks = extract_tasks_from_transcript(entries)
    user_requests = extract_user_requests(entries)
    mentions = extract_outstanding_mentions(entries)

    # Build TODO content
    content = build_todo_content(tasks, user_requests, mentions, session_id, project_dir)
    if not content:
        sys.exit(0)

    # Write to TODO.md
    try:
        write_todo(project_dir, content)
    except Exception:
        pass  # Don't block exit on write errors

    sys.exit(0)


if __name__ == "__main__":
    main()
