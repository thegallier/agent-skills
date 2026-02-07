# Installation

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI installed
- [uv](https://docs.astral.sh/uv/) (for Python-based hooks)
- bash, git

## Quick Start

### 1. Clone the repo

```bash
git clone git@github.com:thegallier/agent-skills.git
cd agent-skills
```

### 2. Install global CLAUDE.md

This sets the four-doc rule (README, INSTALLATION, METHODS, TODO) for all projects:

```bash
cp skills/hooks/CLAUDE.md.template ~/.claude/CLAUDE.md
```

If you already have a `~/.claude/CLAUDE.md`, merge the contents manually.

### 3. Install hooks

```bash
# Documentation check (SessionStart)
cp -r skills/hooks/doc-check ~/.claude/hooks/

# Codebase indexer + search (SessionStart + PreToolUse)
cp -r skills/hooks/index-search ~/.claude/hooks/

# Session TODO writer (SessionEnd)
cp -r skills/hooks/session-todo ~/.claude/hooks/

# Damage control safety hooks (PreToolUse)
cp -r skills/damage-control/hooks/damage-control-python ~/.claude/hooks/damage-control
cp skills/damage-control/patterns.yaml ~/.claude/hooks/damage-control/
```

### 4. Configure hooks in settings

Merge the hook entries from `skills/hooks/settings-hooks.json` into your `~/.claude/settings.json`.

If you don't have a settings file yet, copy it directly:

```bash
cp skills/hooks/settings-hooks.json ~/.claude/settings.json
```

Otherwise, merge the `"hooks"` section into your existing settings.

### 5. Install skills

Copy any skills you want to `~/.claude/skills/`:

```bash
# Install all skills
cp -r skills/development ~/.claude/skills/
cp -r skills/damage-control ~/.claude/skills/
cp -r skills/health ~/.claude/skills/
cp -r skills/paper-to-code ~/.claude/skills/
cp -r skills/python-quality ~/.claude/skills/
cp -r skills/jean-zay ~/.claude/skills/
cp -r skills/vercel-deploy-claimable ~/.claude/skills/
cp -r skills/react-best-practices ~/.claude/skills/
cp -r skills/web-design-guidelines ~/.claude/skills/
cp -r skills/memory ~/.claude/skills/
cp -r skills/list-skills ~/.claude/skills/

# Or install everything at once
for skill in development damage-control health paper-to-code python-quality jean-zay vercel-deploy-claimable react-best-practices web-design-guidelines memory list-skills; do
  cp -r "skills/$skill" ~/.claude/skills/
done
```

### 6. Verify installation

Start a new Claude Code session. You should see:
- Doc-check reminder if any project docs are missing
- Codebase index being built on startup
- Damage control blocking destructive commands

```bash
# Quick verification
ls ~/.claude/hooks/damage-control/patterns.yaml
ls ~/.claude/hooks/doc-check/doc-check-hook.py
ls ~/.claude/hooks/index-search/index-repo.sh
ls ~/.claude/hooks/session-todo/session-todo-hook.py
```

## Install on a New Computer

Run this single block to set up everything from a fresh clone:

```bash
git clone git@github.com:thegallier/agent-skills.git
cd agent-skills

# Hooks
mkdir -p ~/.claude/hooks
cp -r skills/hooks/doc-check ~/.claude/hooks/
cp -r skills/hooks/index-search ~/.claude/hooks/
cp -r skills/hooks/session-todo ~/.claude/hooks/
cp -r skills/damage-control/hooks/damage-control-python ~/.claude/hooks/damage-control
cp skills/damage-control/patterns.yaml ~/.claude/hooks/damage-control/

# Global instructions
cp skills/hooks/CLAUDE.md.template ~/.claude/CLAUDE.md

# Settings (merge if you have existing settings)
cp skills/hooks/settings-hooks.json ~/.claude/settings.json

# Skills
mkdir -p ~/.claude/skills
for skill in development damage-control health paper-to-code python-quality jean-zay vercel-deploy-claimable react-best-practices web-design-guidelines memory list-skills; do
  cp -r "skills/$skill" ~/.claude/skills/
done
```

## Updating

Pull the latest and re-copy:

```bash
cd agent-skills
git pull
# Re-run the hook and skill copy commands above
```
