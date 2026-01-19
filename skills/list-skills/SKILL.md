---
name: list-skills
description: List all installed Claude Code skills with their descriptions and usage. Use when the user says "list skills", "show skills", "what skills do I have", or "available skills".
license: MIT
metadata:
  author: user
  version: "1.0.0"
---

# List Skills

Lists all installed Claude Code skills with their functionality and how to use them.

## How It Works

1. Scans ~/.claude/skills/ directory for installed skills
2. Reads each skill's SKILL.md to extract name and description
3. Presents a formatted summary of all available skills

## Usage

```bash
bash ~/.claude/skills/list-skills/scripts/list-skills.sh
```

## Present Results to User

After running the script, present the skills in this format:

### Installed Skills

For each skill found, display:

**{skill-name}**
- Description: {description from SKILL.md}
- Invoke with: `/{skill-name}`

### Example Output

**development**
- Description: Autonomous feature development using structured phases, parallel subagents, and backpressure-driven implementation.
- Invoke with: `/development`

**memory**
- Description: Semantic memory management integrating SimpleMem with Claude Code's CLAUDE.md memory system. Store long-term memories, query past conversations, and sync to CLAUDE.md.
- Invoke with: `/memory`
- Setup required: `bash ~/.claude/skills/memory/scripts/setup.sh`

**paper-to-code**
- Description: Transforms research papers into production-ready Python code implementations.
- Invoke with: `/paper-to-code`

## Notes

- Skills are installed in ~/.claude/skills/
- Each skill has a SKILL.md file with its full documentation
- Use `/{skill-name}` to invoke any skill
- Read individual SKILL.md files for detailed usage instructions
