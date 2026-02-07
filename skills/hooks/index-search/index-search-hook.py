# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
"""
Codebase Index Search Hook - PreToolUse Advisory Hook
======================================================

Automatically searches .claude/repo-index/ files (symbols.txt, dependencies.txt,
file-tree.txt) before Grep/Glob tool calls and injects matching lines as
additionalContext so Claude can go directly to the right file instead of
searching blindly.

Exit codes:
  0 = Allow (always allows the tool call)

JSON output with additionalContext provides index matches to Claude.
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def find_repo_index_dir() -> Optional[Path]:
    """Find .claude/repo-index/ directory in the project."""
    # 1. Check CLAUDE_PROJECT_DIR env var
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if project_dir:
        index_dir = Path(project_dir) / ".claude" / "repo-index"
        if index_dir.is_dir():
            return index_dir

    # 2. Check current working directory
    cwd = Path.cwd()
    index_dir = cwd / ".claude" / "repo-index"
    if index_dir.is_dir():
        return index_dir

    # 3. Walk up from cwd looking for it
    for parent in cwd.parents:
        index_dir = parent / ".claude" / "repo-index"
        if index_dir.is_dir():
            return index_dir
        # Stop at home directory
        if parent == Path.home():
            break

    return None


def extract_search_terms(tool_name: str, tool_input: dict) -> List[str]:
    """Extract meaningful search terms from tool input."""
    terms = []

    if tool_name == "Grep":
        pattern = tool_input.get("pattern", "")
        if pattern:
            # Strip regex metacharacters to get plain keywords
            clean = re.sub(r'[\\.*+?^${}()|[\]]', ' ', pattern)
            words = [w for w in clean.split() if len(w) >= 3]
            terms.extend(words)
            # Also keep the raw pattern for exact matching
            if len(pattern) >= 3:
                terms.append(pattern)

    elif tool_name == "Glob":
        pattern = tool_input.get("pattern", "")
        if pattern:
            # Extract meaningful parts from glob patterns
            parts = pattern.replace("*", " ").replace("?", " ").split("/")
            for part in parts:
                words = [w.strip(".") for w in part.split() if len(w.strip(".")) >= 3]
                terms.extend(words)

    # Also check the path for context
    path = tool_input.get("path", "")
    if path:
        path_parts = Path(path).parts
        for part in path_parts:
            if len(part) >= 3 and part not in ("src", "lib", "usr", "var", "tmp", "Users"):
                terms.append(part)

    return list(set(terms))  # deduplicate


def search_index_files(index_dir: Path, terms: List[str], max_lines: int = 30) -> str:
    """Search all repo-index files for lines matching any of the terms."""
    if not terms:
        return ""

    index_files = [
        ("symbols.txt", "Symbols"),
        ("file-tree.txt", "Files"),
        ("dependencies.txt", "Dependencies"),
    ]

    all_matches: List[str] = []

    for filename, label in index_files:
        filepath = index_dir / filename
        if not filepath.exists():
            continue

        try:
            content = filepath.read_text(encoding="utf-8")
        except Exception:
            continue

        lines = content.splitlines()
        matched = []

        for line in lines:
            # Skip comment/header lines
            if line.startswith("#") or not line.strip():
                continue
            line_lower = line.lower()
            for term in terms:
                if term.lower() in line_lower:
                    matched.append(line)
                    break  # Only match once per line

        if matched:
            all_matches.append(f"[{label}]")
            all_matches.extend(matched[:max_lines // len(index_files)])

    if not all_matches:
        return ""

    return "\n".join(all_matches)


def main() -> None:
    # Read hook input from stdin
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, Exception):
        sys.exit(0)  # Don't block on parse errors

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Only trigger on Grep and Glob
    if tool_name not in ("Grep", "Glob"):
        sys.exit(0)

    # Find the repo-index directory
    index_dir = find_repo_index_dir()
    if not index_dir:
        sys.exit(0)  # No index, silently allow

    # Extract search terms
    terms = extract_search_terms(tool_name, tool_input)
    if not terms:
        sys.exit(0)

    # Search the index files
    matches = search_index_files(index_dir, terms)
    if not matches:
        sys.exit(0)  # No matches, silently allow

    # Output advisory context
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "additionalContext": (
                f"[Index Search] .claude/repo-index/ matches for {terms}:\n"
                f"{matches}\n"
                f"Consider reading the indexed file directly instead of searching."
            )
        }
    }
    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
