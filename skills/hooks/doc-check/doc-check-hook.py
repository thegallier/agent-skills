# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
"""
Project Documentation Check — SessionStart Hook
=================================================

Checks if the project has the four required documentation files
(README.md, INSTALLATION.md, METHODS.md, TODO.md) and injects
a reminder into Claude's context for any that are missing.

Fires on session startup and resume (not on compact/clear).
"""

import json
import os
import sys
from pathlib import Path


REQUIRED_DOCS = [
    ("README.md", "project description, features, architecture, usage"),
    ("INSTALLATION.md", "installation guide using uv for Python"),
    ("METHODS.md", "algorithms, methods, key design decisions"),
    ("TODO.md", "outstanding issues and planned work"),
]


def main() -> None:
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, Exception):
        sys.exit(0)

    # Get project directory
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", input_data.get("cwd", ""))
    if not project_dir:
        sys.exit(0)

    project_path = Path(project_dir)
    if not project_path.is_dir():
        sys.exit(0)

    # Skip non-project directories (home dir, tmp, etc.)
    # A project should have at least a .git, src/, or some code files
    is_project = (
        (project_path / ".git").exists()
        or (project_path / "src").exists()
        or (project_path / "package.json").exists()
        or (project_path / "pyproject.toml").exists()
        or (project_path / "setup.py").exists()
        or (project_path / "Cargo.toml").exists()
        or (project_path / "go.mod").exists()
        or (project_path / "CLAUDE.md").exists()
    )
    if not is_project:
        sys.exit(0)

    # Check which docs are missing
    missing = []
    for filename, purpose in REQUIRED_DOCS:
        if not (project_path / filename).exists():
            missing.append((filename, purpose))

    if not missing:
        sys.exit(0)  # All docs present, nothing to report

    # Build reminder message
    project_name = project_path.name
    missing_list = "\n".join(f"  - {name}: {purpose}" for name, purpose in missing)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": (
                f"[Doc Check] Project '{project_name}' is missing required documentation:\n"
                f"{missing_list}\n"
                f"Create these files when completing significant work. "
                f"Use /development skill Phase 9 for templates. "
                f"Prefer uv for Python installation instructions."
            ),
        }
    }
    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
