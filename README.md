# Agent Skills

A collection of skills and hooks for Claude Code and claude.ai that extend agent capabilities with specialized workflows, safety guardrails, and automated project management.

## Features

- **Development workflow** (`development`) — Autonomous feature development with structured phases, parallel subagents, codebase indexing, and backpressure-driven implementation
- **Damage control** (`damage-control`) — Safety hooks that block destructive operations (rm -rf, force push, credential exposure) before they execute
- **Codebase indexing** (`hooks/index-search`) — Auto-indexes repos at session start; searches the index before Grep/Glob to save context tokens
- **Documentation enforcement** (`hooks/doc-check`) — Checks every project for required docs (README, INSTALLATION, METHODS, TODO) and reminds Claude to create missing ones
- **Session TODO tracking** (`hooks/session-todo`) — Extracts incomplete tasks from session transcripts and appends them to TODO.md on exit
- **Health analysis** (`health`) — Analyze 23andMe genetic data for health insights, drug interactions, and disease risk
- **Paper to code** (`paper-to-code`) — Transform research papers into production-ready Python implementations
- **Jean Zay** (`jean-zay`) — Run training jobs on the Jean Zay supercomputer with Ray Tune support
- **Vercel deploy** (`vercel-deploy-claimable`) — Deploy apps to Vercel with claimable URLs from conversations
- **React best practices** (`react-best-practices`) — 40+ performance optimization rules from Vercel Engineering
- **Web design guidelines** (`web-design-guidelines`) — 100+ rules for accessibility, performance, and UX
- **Python quality** (`python-quality`) — Enforces Python code quality with uv, ruff, mypy, and pytest
- **Memory** (`memory`) — Persistent memory system for Claude across sessions
- **List skills** (`list-skills`) — Lists all installed skills

## Architecture

```
agent-skills/
  skills/
    hooks/                    # Claude Code hooks (run automatically)
      doc-check/              #   SessionStart: check for missing docs
      index-search/           #   SessionStart: index repo + PreToolUse: search index
      session-todo/           #   SessionEnd: write outstanding items to TODO.md
      CLAUDE.md.template      #   Global instruction template
      settings-hooks.json     #   Hook config template for settings.json
    damage-control/           # Safety hooks (PreToolUse: Bash, Edit, Write)
    development/              # Full development workflow skill
    {skill-name}/             # Each skill is a self-contained directory
      SKILL.md                #   Skill definition (loaded on-demand)
      scripts/                #   Executable scripts
      references/             #   Supporting documentation (optional)
  CLAUDE.md                   # Agent instructions for this repo
```

Skills are loaded on-demand — only the name and description load at startup. The full SKILL.md loads into context only when the agent activates the skill.

## Usage

Once installed, skills activate automatically based on trigger phrases:

```
/development          # Start autonomous feature development
/damage-control       # Install or test safety hooks
/health               # Run genetic health analysis
/paper-to-code        # Implement a research paper
Deploy my app         # Triggers vercel-deploy
Review my React code  # Triggers react-best-practices
```

## License

MIT
