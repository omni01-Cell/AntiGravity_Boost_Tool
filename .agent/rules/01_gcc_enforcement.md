---
trigger: always_on
description: Maintains the Git-Context-Controller (GCC) as your persistent long-term working memory.
---

# Git-Context-Controller (GCC) — Continuous Sync

<context>
The Git-Context-Controller (`.GCC/`) is your **long-term working memory**. It is the only persistent state that survives between sessions. Every significant action must be recorded in `.GCC/main.md` before the next one begins.
</context>

<hooks>
  <hook id="decision_milestone">
    <trigger>Resolving critical bugs, selecting architectures, completing subtasks, or making persistent choices.</trigger>
    <action>
      1. Open `.GCC/main.md`.
      2. Record the date and the decision with its rationale.
      3. Update the "Current Status" section.
    </action>
  </hook>

  <hook id="divergence_plan_b">
    <trigger>An approach fails after multiple attempts AND a new strategy is proposed.</trigger>
    <action>
      1. Document the failure in `.GCC/branches/attempt_[name]_failed.md` (What, Why, Lessons).
      2. Reference the failure in `.GCC/main.md` under "Abandoned Branches".
    </action>
  </hook>

  <hook id="knowledge_sync">
    <trigger>Retrieving or rating knowledge chunks via LoopRAG tools.</trigger>
    <action>
      1. Add the chunk reference (ID, source, score) to `.GCC/main.md` under "Supabase Chunks Used".
    </action>
  </hook>
</hooks>

<confirmation_tag>
Include this verbatim at the end of your response when a hook is triggered:
```
<gcc_sync>
[X] .GCC/main.md updated — [one-line summary]
</gcc_sync>
```
</confirmation_tag>

<template id="gcc_main">
Maintain this structure in `.GCC/main.md`:

```markdown
# Current task context

## Objective
[What this session is building or solving]

## Decisions made
- [YYYY-MM-DD] Chose X over Y because [reason]

## Current status
- ✅ Done: [list]
- 🔄 In progress: [current item]
- ⏳ Pending: [list]

## Next action
[Single, concrete next step]

## Abandoned branches
- [YYYY-MM-DD] [approach] → see .GCC/branches/[filename].md

## Supabase chunks used
- chunk_id: [id] | source: [book/article] | score: [0.00]
```
</template>

<scope>
Apply to every message if `.GCC/` exists. If not and the task is non-trivial, create it with an empty `main.md`.
</scope>
