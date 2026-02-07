# Methods

Technical approaches and design decisions for the agent-skills system.

## Skill Architecture

### On-demand loading

Skills use a two-tier loading strategy to minimize context consumption:

1. **Startup**: Only the skill name and one-line description are loaded (from SKILL.md frontmatter)
2. **Activation**: The full SKILL.md is loaded into context only when the agent decides it's relevant

This means a repo with 15 skills only consumes ~30 lines of context at startup, not thousands.

### Progressive disclosure

SKILL.md files reference supporting files (cookbooks, references) that are read only when needed. This keeps the primary skill definition under 500 lines while allowing deep reference material.

## Hook System Design

### Four-layer documentation enforcement

The documentation standard is enforced through redundant layers, each catching what the previous might miss:

| Layer | Mechanism | When | Catches |
|-------|-----------|------|---------|
| 1. CLAUDE.md | Global instruction | Always loaded | Sets the rule — Claude knows docs are required |
| 2. doc-check hook | SessionStart | Every startup/resume | Injects specific missing file names into context |
| 3. session-todo hook | SessionEnd | Every exit | Captures outstanding work including missing docs |
| 4. Phase 9 | During /development | Feature completion | Full templates and validation checklist |

### Index-first search

The codebase indexing system replaces blind file exploration with targeted lookups:

1. **SessionStart**: `index-repo.sh` scans the repo and generates four index files in `.claude/repo-index/`:
   - `file-tree.txt` — all files with sizes
   - `symbols.txt` — functions, classes, types, interfaces with file:line locations
   - `dependencies.txt` — import graph between local files
   - `dir-tree.txt` — directory structure

2. **PreToolUse (Grep/Glob)**: `index-search-hook.py` intercepts search tool calls, extracts search terms, and searches the index files. Matching results are injected as `additionalContext` so Claude can go directly to the right file.

**Token efficiency**: Searching the index costs ~100 tokens vs ~2000+ tokens for reading a file. For a 20-file exploration, this saves 95% of context tokens.

### Damage control hooks

Safety hooks use a pattern-matching approach against a YAML config (`patterns.yaml`):

- **PreToolUse on Bash**: Checks commands against blocked patterns (rm -rf, force push, etc.)
- **PreToolUse on Edit/Write**: Checks file paths against protected patterns (credentials, env files, etc.)
- Hooks return `"permissionDecision": "block"` to prevent execution, with an explanation message

### Session TODO extraction

The SessionEnd hook parses the JSONL conversation transcript to find outstanding work:

1. **Task system**: Extracts TaskCreate/TaskUpdate calls and finds incomplete tasks
2. **TODO/FIXME markers**: Scans assistant messages for strong markers (TODO, FIXME, HACK) and weak markers (still need to, not yet implemented, blocked by)
3. **User requests**: Captures recent user messages for context
4. **Deduplication**: Normalizes and deduplicates mentions to avoid redundant entries

Results are appended to `TODO.md` with session timestamps, keeping manually curated priorities at the top undisturbed.

## Development Skill Methodology

The development skill (`/development`) uses a phased approach combining several techniques:

- **Ralph methodology**: Context-efficient, self-correcting development loops with backpressure
- **Parallel subagents**: Code exploration, testing, and verification run as parallel agents to maximize throughput
- **Task system coordination**: Atomic tasks with explicit dependency graphs (blockedBy/blocks)
- **Gap analysis**: Planning phase compares requirements against existing codebase before writing code
- **Backpressure**: Implementation pauses when too many tasks are in-progress, preventing context overload
