# Claude Code Hooks

Reusable hooks that extend Claude Code sessions with automatic behaviors.

## Hooks

| Hook | Event | Purpose |
|------|-------|---------|
| `doc-check` | SessionStart | Checks for required docs (README.md, INSTALLATION.md, METHODS.md, TODO.md) and reminds Claude to create missing ones |
| `index-search` | SessionStart + PreToolUse | Indexes the codebase at session start (`index-repo.sh`), then searches the index before Grep/Glob calls to inject file locations as context |
| `session-todo` | SessionEnd | Extracts incomplete tasks and outstanding items from the session transcript and appends them to TODO.md |

## Installation

```bash
# 1. Copy global CLAUDE.md (sets the four-doc rule for all projects)
cp CLAUDE.md.template ~/.claude/CLAUDE.md

# 2. Copy hooks to ~/.claude/hooks/
cp -r doc-check ~/.claude/hooks/
cp -r index-search ~/.claude/hooks/
cp -r session-todo ~/.claude/hooks/

# 3. Damage control hooks are in the damage-control skill:
cp -r ../damage-control/hooks/damage-control-python ~/.claude/hooks/damage-control
cp ../damage-control/patterns.yaml ~/.claude/hooks/damage-control/

# 4. Merge settings-hooks.json into your ~/.claude/settings.json
# (copy the "hooks" section into your existing settings)
```

## How It All Works Together

| Layer | File | When | What |
|-------|------|------|------|
| 1. Global instruction | `~/.claude/CLAUDE.md` | Every session | States the four required docs and uv preference |
| 2. SessionStart hook | `doc-check-hook.py` | Session startup/resume | Checks for missing docs and injects reminders |
| 3. SessionEnd hook | `session-todo-hook.py` | Session exit | Appends outstanding items to TODO.md |
| 4. Development skill | Phase 9 in SKILL.md | During `/development` | Full templates and rules for all four docs |

## Dependencies

- **uv**: Python hooks use `uv run` with inline script metadata (PEP 723)
- **bash**: `index-repo.sh` requires bash
- **git**: Index script uses `git rev-parse` to find repo root
