---
name: development
description: Autonomous feature development using structured phases, parallel subagents, and backpressure-driven implementation. Combines guided feature development with the Ralph methodology for context-efficient, self-correcting development loops. Use when implementing features, fixing bugs, or making significant code changes.
license: MIT
metadata:
  author: vercel
  version: "1.0.0"
---

# Development

A comprehensive development methodology that combines structured feature development with autonomous loop-based implementation. Uses parallel subagents for exploration, atomic task execution, and backpressure through tests/builds for self-correction.

## Core Principles

### From Structured Feature Development
- **Ask clarifying questions**: Identify all ambiguities before implementation
- **Understand before acting**: Study existing code patterns deeply
- **Use specialized agents**: code-explorer, code-architect, test-generator, test-runner, code-reviewer
- **Track progress**: Use TodoWrite throughout all phases

### From Ralph Methodology
- **"Study" not "read"**: Achieve deep comprehension, not surface scanning
- **Don't assume not implemented**: Always verify before creating new code
- **One task = one commit**: Atomic, focused changes
- **Backpressure steering**: Tests, builds, and lints guide self-correction
- **Context efficiency**: Parallel subagents for reading, single agent for builds
- **Capture the why**: Document reasoning alongside implementation

---

## Phase 0: Requirements Definition

**Goal**: Establish clear Jobs to Be Done (JTBD)

**Actions**:
1. Discuss the feature/task with the user
2. Identify specific Jobs to Be Done
3. Break complex features into topics of concern
4. For each topic, establish:
   - What problem it solves
   - Success criteria
   - Constraints and boundaries
5. Document requirements (can be informal or in specs/ files for large projects)

**One Sentence Test**: Each topic should be describable in one sentence without using "and" to conjoin unrelated capabilities.

---

## Phase 1: Discovery

**Goal**: Deep understanding of what needs to be built

**Actions**:
1. Create todo list with all phases
2. **Study** (not just read) the feature request:
   - What problem is being solved?
   - Who benefits and how?
   - What are the boundaries?
3. If unclear, ask user for clarification
4. Summarize understanding and confirm with user

**Critical**: Use "study" mindset - achieve comprehension, not just awareness.

---

## Phase 2: Codebase Exploration

**Goal**: Comprehensive understanding of relevant existing code

**Actions**:
1. Launch 2-3 code-explorer agents **in parallel**. Each agent should:
   - **Study** the code comprehensively (trace through abstractions, architecture, control flow)
   - Target different aspects (similar features, architecture, user experience)
   - Return a list of 5-10 key files to read

   **Example agent prompts**:
   - "Study features similar to [feature], tracing through their complete implementation"
   - "Map the architecture and abstractions for [area], studying the code comprehensively"
   - "Analyze how [existing feature] works end-to-end, identifying patterns and conventions"

2. **Read all files identified by agents** to build deep understanding

3. **Critical Guard**: Don't assume something isn't implemented. Always verify:
   - Search for existing implementations before creating new ones
   - Look for utilities, helpers, and patterns already in the codebase
   - Check for partial implementations that can be extended

4. Present comprehensive summary of findings

---

## Phase 3: Planning Mode (Gap Analysis)

**Goal**: Create a prioritized implementation plan with atomic tasks

**Actions**:
1. Analyze the gap between requirements and current codebase
2. Generate an implementation plan with:
   - Prioritized task list
   - Each task is **atomic**: completable in one focused session
   - Each task produces **one commit**
   - Dependencies between tasks are explicit

3. Task format:
   ```
   [ ] Task description
       - Why: Reason this task matters
       - Files: Expected files to modify
       - Validation: How to verify completion
   ```

4. Order tasks by:
   - Dependencies (blockers first)
   - Risk (high-risk items early for faster feedback)
   - Value (high-value items early)

**Note**: The plan is disposable. Regenerate if it becomes stale rather than forcing adherence to outdated guidance.

---

## Phase 4: Clarifying Questions

**Goal**: Resolve all ambiguities before implementation

**CRITICAL**: Do not skip this phase.

**Actions**:
1. Review codebase findings and original request
2. Identify underspecified aspects:
   - Edge cases and error handling
   - Integration points
   - Scope boundaries
   - Design preferences
   - Backward compatibility
   - Performance requirements

3. **Present all questions in a clear, organized list**
4. **Wait for answers before proceeding**

If user says "whatever you think is best", provide your recommendation and get explicit confirmation.

---

## Phase 5: Architecture Design

**Goal**: Design implementation approaches with clear trade-offs

**Actions**:
1. Launch 2-3 code-architect agents **in parallel** with different focuses:
   - **Minimal changes**: Smallest change, maximum reuse of existing code
   - **Clean architecture**: Optimal maintainability, elegant abstractions
   - **Pragmatic balance**: Speed + quality trade-off

2. Review all approaches and form your opinion on best fit

3. Present to user:
   - Brief summary of each approach
   - Trade-offs comparison
   - **Your recommendation with reasoning**
   - Concrete implementation differences

4. **Ask user which approach they prefer**

---

## Phase 6: Building Mode

**Goal**: Implement features through atomic, self-correcting tasks

**DO NOT START WITHOUT USER APPROVAL**

**Actions**:
1. Wait for explicit user approval of architecture
2. Work through implementation plan **one task at a time**:

   For each task:
   a. Mark task as in_progress
   b. Read all relevant files
   c. Implement following chosen architecture
   d. **Self-correct against backpressure**:
      - Run tests after changes
      - Run build/type checks
      - Run lints
      - Fix any failures before proceeding
   e. **Capture the why**: Add comments for non-obvious decisions
   f. Mark task complete
   g. Commit changes (one task = one commit)

3. Follow codebase conventions strictly
4. Update todos as you progress

**Backpressure Loop**: If tests/builds fail, fix issues before moving to next task. The failing checks are steering signals, not blockers to work around.

---

## Phase 7: Testing

**Goal**: Comprehensive test coverage with all tests passing

**Actions**:
1. **Generate Tests**: Launch 2 test-generator agents **in parallel**:
   - Unit tests: Individual functions, edge cases, error handling
   - Integration tests: Component interactions, data flow, API contracts

   Each agent provides:
   - Test cases with full implementation
   - Priority ranking (critical/important/nice-to-have)
   - Required mocks and fixtures

2. **Review and prioritize** generated tests
3. **Implement** approved test cases
4. **Run tests**: Use **single test-runner agent** (not parallel - for controlled backpressure):
   - Execute full test suite
   - Analyze failures with root cause diagnosis
   - Provide specific fixes

5. **Fix and iterate** until all tests pass
6. **Do not proceed until all tests pass**

---

## Phase 8: Quality Review

**Goal**: Ensure code quality, simplicity, and correctness

**Actions**:
1. Launch 3 code-reviewer agents **in parallel**:
   - Simplicity, DRY, elegance
   - Bugs, functional correctness
   - Project conventions, proper abstractions

2. Consolidate findings by severity
3. **Present findings to user** with recommendations
4. Address issues based on user decision
5. If significant changes made, **re-run tests**

---

## Phase 9: Summary

**Goal**: Document accomplishments and next steps

**Actions**:
1. Mark all todos complete
2. Summarize:
   - What was built
   - Key decisions made and **why**
   - Files modified
   - Test coverage achieved
   - Any technical debt introduced
   - Suggested next steps

---

## Context Efficiency Guidelines

To maximize effective use of context window:

1. **Parallel subagents for reading**: Launch multiple explorers simultaneously
2. **Single subagent for builds/tests**: Controlled backpressure, clear signal
3. **Atomic tasks**: One task per focused session prevents context bloat
4. **Progressive disclosure**: Load detailed docs only when needed
5. **File lists from agents**: Have agents return key files, then read them yourself

## Self-Correction Patterns

When things go wrong:

1. **Failing tests**: Fix the implementation or test, don't skip
2. **Build errors**: Resolve before proceeding, they're steering signals
3. **Stale plan**: Regenerate rather than force adherence
4. **Circular implementation**: Step back, re-analyze the problem
5. **Missing context**: Launch another explorer agent, don't guess

## Anti-Patterns to Avoid

- Reading without studying (surface-level understanding)
- Assuming something isn't implemented
- Batching multiple changes into one commit
- Skipping clarifying questions
- Proceeding despite failing tests
- Over-engineering beyond requirements
- Creating abstractions for one-time operations
