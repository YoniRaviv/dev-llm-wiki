---
name: claude-history-ingest
description: Ingest Claude Code conversation history and turn it into wiki knowledge + automatic project tracking. Two outputs every run — (1) journal entries with conversation summaries appended to `wiki/journal/<DD-MM-YYYY>.md`, and (2) project-progress updates that bump `Last touched`, advance feature statuses (`planned → in-progress`, `in-progress → shipped` on strong completion signals), and flag blockers across every project the conversations touched. Use whenever the user says "ingest my Claude history", "process my conversations", "what have I been working on", "update projects from my sessions", "/claude-history-ingest", "import ~/.claude", "sync my work to the wiki", or refers to mining past sessions for knowledge. Reads `.manifest.json` to skip already-processed conversations unless content changed. Scans both `~/.claude/projects/` (CLI sessions) and `~/Library/Application Support/Claude/local-agent-mode-sessions/` (desktop agent sessions, with audit logs).
---

# Claude History Ingest — Conversation Mining + Project Tracking

Two jobs, every run:

1. **Distill conversations into wiki pages** — patterns, technologies, decisions, ideas surfaced across sessions.
2. **Keep the wiki on track with reality** — update project pages and features based on what was actually worked on. Bump `Last touched`. Advance feature statuses. Surface blockers. This is the part that keeps the wiki from drifting away from what the user is actively doing.

The second job is the load-bearing one for daily use. Without it, the wiki becomes a historical record. With it, the wiki reflects the present.

This skill can be invoked directly or via the `wiki-history-ingest` router (`/wiki-history-ingest claude`).

## Before You Start

1. Read `.manifest.json` at repo root — check what's already been ingested (content hashes are the skip signal).
2. Read `wiki/index.md` and `wiki/hot.md`.
3. Read `.vault-meta.json` — confirm date format and any progress-update preferences.
4. Glob `wiki/projects/*.md` — build a project-slug → project-page map. Read each project's `Current Status` block and `features/` directory.

If those files are missing, the vault isn't initialized — stop and point at `init-vault`.

## Ingest Modes

### Append Mode (default)

Only process conversations new or content-changed since last ingest:

- Path not in `.manifest.json` → new, process it
- Path in manifest with `content_hash` matching current SHA-256 → skip
- Hash differs → re-process

### Full Mode

Process everything regardless of manifest. Use after a rebuild or when the user asks explicitly.

## Data Locations — Scan Both

**Source 1: `~/.claude/` (CLI sessions)**

```
~/.claude/
├── projects/
│   ├── -Users-name-Documents-projects-my-app/   ← path-encoded
│   │   ├── <session-uuid>.jsonl                 ← conversation transcript
│   │   └── memory/
│   │       ├── MEMORY.md                         ← memory index (read first)
│   │       ├── user_*.md
│   │       ├── feedback_*.md
│   │       └── project_*.md
├── sessions/<pid>.json                          ← {sessionId, cwd, startedAt, ...}
└── history.jsonl                                 ← global session log
```

**Source 2: `~/Library/Application Support/Claude/local-agent-mode-sessions/` (desktop agent sessions)**

```
.../local-agent-mode-sessions/<outer-uuid>/<inner-uuid>/
    ├── local_<session-uuid>.json                ← session metadata
    └── local_<session-uuid>/
        ├── audit.jsonl                          ← tool calls, file reads, commands
        └── .claude/projects/<path-encoded-name>/<uuid>.jsonl  ← transcript
```

The `.scripts/list-claude-history.py` helper (see Step 1 below) enumerates both source locations in a single call. **Don't run `find` against these paths directly from the skill body** — that's what causes the permission-prompt storm. The script does the scanning in one process; subsequent `Read`s in this skill only happen on the small subset of files you decide to distill.

Source value ranking (combined):
1. **Memory files** — pre-distilled, gold.
2. **Conversation transcripts** — rich but noisy.
3. **Audit logs** (desktop) — tool-call record of what was actually done; grounds the conversation.
4. **Session metadata** — `cwd`, timestamps; tells you which project + when.

## Step 1 — Survey and Delta (one Bash call)

Enumerate every conversation, memory, and audit-log file in **a single Bash call** using the helper script — this is the difference between one permission prompt and dozens:

```sh
python3 .scripts/list-claude-history.py [--since DD-MM-YYYY] > /tmp/claude-history.json
```

The script scans both `~/.claude/projects/` (CLI sessions) and `~/Library/Application Support/Claude/local-agent-mode-sessions/` (desktop agent sessions), computes SHA-256 for each file, and emits a JSON array of entries with `path`, `size_bytes`, `mtime_iso`, `sha256`, `source_type`, `claude_project_dir`, `claude_project_decoded`, and (for session-metadata files) `session_id`, `cwd`, `title`.

Read the JSON and classify each entry against `.manifest.json`:

- **New** — `path` not in manifest → needs ingesting.
- **Modified** — `path` in manifest, but `content_hash` ≠ entry's `sha256` → re-ingest.
- **Unchanged** — `path` in manifest, hashes match → skip in append mode.
- **Older entry** (manifest entry has no `content_hash`) — fall back to mtime comparison.

In **append mode**, drop unchanged entries from the working set. In **full mode**, keep all entries regardless of manifest state.

Report to the user: "Found N projects, M conversations, K memory files, A audit logs. Delta: X new, Y modified."

**Do not run `find` or `glob` against the Claude history paths from the skill body.** That's what causes the permission-prompt storm — every individual file access is a separate prompt. The helper script does the enumeration server-side in one process; subsequent `Read`s only happen on the small subset of files you actually decide to distill.

## Step 2 — Ingest Memory Files First

Memory files are pre-distilled. Read `MEMORY.md` in each project's `memory/` folder first to triage, then read individual memory files based on type:

- `user` — user's role, preferences, expertise → may inform a `wiki/technologies/` page about tools they use, but mostly stays in memory; skip ingest unless something stands out.
- `feedback` — workflow corrections → these are valuable; consider a `wiki/patterns/` page if a feedback memory describes a reusable approach.
- `project` — active work, deadlines, blockers → **directly informs project-progress updates** (Step 4).
- `reference` — pointers to external resources → may inform `wiki/sources/` or technology page references.

## Step 3 — Parse Conversation Transcripts

Each JSONL file is one session. Filter to `type: "user"` and `type: "assistant"` entries.

For assistant entries, `content` is an array of blocks — extract only `text` blocks. Skip `thinking` (reasoning) and `tool_use` (mechanical actions). The audit log is the better source for "what was actually done".

The `cwd` field tells you which project this conversation belongs to. Decode the path-encoded project directory name to recover the project path:

```
-Users-name-Documents-projects-my-app  →  /Users/name/Documents/projects/my-app
```

(The leading `-` becomes `/`; remaining `-`s map back to slashes, but be cautious — directory names can also contain literal dashes. The `cwd` field gives you the canonical path; prefer it over decoding.)

**Skip from JSONL:**
- `type: "progress"`, `type: "file-history-snapshot"` — internal plumbing
- Subagent conversations unless the user asks for them

## Step 4 — Detect Project Progress Signals

**This is the load-bearing step for the project-tracking job.** Be conservative — false positives cost more than false negatives.

For each conversation, group user+assistant turns by topic and scan for these signal classes:

### Active work signals (auto-apply)

The user is currently working on something. Patterns:
- User says: "I'm working on", "let me build", "started on", "implementing", "let's add"
- Multiple file edits or Read/Write tool calls in the audit log within one session targeting the same feature/area
- Repeated returns to the same files across sessions

→ For the affected feature page, set `status: in-progress` if it was `planned`.

### Completion signals (auto-apply on strong, surface on medium)

**Strong** (auto-apply `in-progress → shipped` + set `shipped: <today>`):
- "merged the PR for X", "X is deployed", "X is live in production", "shipped X", "released X"

**Medium** (surface for confirmation):
- "finished X", "done with X", "X is done", "wrapping up X", "X is mostly there"

**Weak** (do not auto-update; mention in summary only):
- "moving on from X" — could mean done, paused, or abandoned
- "X is mostly done" — too ambiguous

### Blocker signals (auto-apply)

- "blocked on", "waiting for", "stuck on", "PR review pending", "external dependency"

→ Update `Blocked on:` in the Current Status block with `<one line> + since <date>`.

### Decision signals (always surface)

- "we decided to", "going with X over Y", "rejected Z because", "the call is to use X"

→ Propose creating `wiki/projects/<slug>/decisions/<decision-slug>.md` from `wiki/templates/decision.md`. Ask before creating.

### Confidence rules

- Single mention of a signal phrase → **weak signal**.
- 2+ mentions across a session, or strong-keyword + audit-log corroboration → **strong signal**.
- Conversation references the feature page by name → **strong signal**.

## Step 5 — Build the Proposed-Updates Plan

Group your findings by project. For each project the conversations touched, build a plan:

```
Project: my-app
├── Current Status updates:
│   - Last touched: → <today>                          [AUTO]
│   - Working on: → "implementing payment-flow"        [AUTO]
│   - Blocked on: → "Stripe webhook config" since <date>  [AUTO]
├── Feature updates:
│   - features/payment-flow.md: planned → in-progress   [AUTO]
│   - features/notification-system.md: in-progress → shipped (12-05-2026)  [STRONG → AUTO]
│   - features/refund-handling.md: in-progress → shipped?   [MEDIUM → ASK]
├── Decision candidates:
│   - "Use Stripe over Adyen" — create decisions/use-stripe.md?  [ALWAYS ASK]
└── Patterns/technologies surfaced:
    - patterns/idempotency-keys.md — create?           [ASK]
    - technologies/stripe.md — update or create?       [ASK if new]
```

**Show this plan to the user before applying anything past the AUTO-marked items.** Offer:

- "Apply all" → applies AUTO + ASK items
- "Apply auto only" → applies just AUTO items, skips ASK
- "Walk through" → goes through each ASK item one by one
- "Skip project updates" → only do the wiki-knowledge ingest, no project tracking this run

## Step 6 — Apply Updates

For each approved change:

### Project page (`wiki/projects/<slug>.md`)

Edit the Current Status block:
```markdown
## Current Status

**Phase:** <existing or updated>
**Last touched:** <today>                ← always bumped
**Working on:** <updated if signal>      ← only if active-work signal
**Blocked on:** <one line + since <date>>  ← only if blocker signal
**Next up:** <existing — don't touch unless user asks>
```

Also append to the project page's `Recent Updates` section (if it has one) — one line referencing the conversation date.

Bump `last_updated:` in frontmatter.

### Feature page (`wiki/projects/<slug>/features/<feature-slug>.md`)

Update frontmatter:
- `status: planned → in-progress` (on active-work signal)
- `status: in-progress → shipped` + `shipped: <today>` (on strong-completion signal, or ASK-approved medium signal)

Append to the **Implementation Notes** section a brief line referencing the session(s) where the work happened — e.g., "Implemented in Claude Code session on `<date>` — see [[journal/<date>]] for context."

### Decision page (if approved)

Create `wiki/projects/<slug>/decisions/<decision-slug>.md` from `wiki/templates/decision.md`. Fill in:
- Context: brief description of what was being decided.
- Decision: the chosen option (extracted from the conversation).
- Rationale: why this option (extracted).
- Alternatives Considered: rejected options if mentioned.
- Consequences: leave for user to fill or extract if clear.

Add `[[decisions/<slug>]]` link to the project page's `Key Decisions` section.

### Pattern / Technology pages

If the conversations introduced a new reusable pattern or a new tool the user is now using, create or update `wiki/patterns/<slug>.md` or `wiki/technologies/<slug>.md` from the matching template. Cross-link from the affected feature/project pages.

## Step 7 — Update Journal Entries

For each date that had Claude conversations, ensure `wiki/journal/<DD-MM-YYYY>.md` exists. If missing, create from `wiki/templates/daily-note.md`.

**Per CLAUDE.md's contract: only touch `Claude Conversations` and `Research & Sources Ingested`.** Append to those sections; do NOT modify `What I Worked On`, `Key Decisions`, `Blockers`, or `Notes` — those are for the user.

Format for `Claude Conversations`:

```markdown
## Claude Conversations

- **<project-slug>** — <1-line summary of what was discussed/done>. Touched: [[projects/<slug>]], [[projects/<slug>/features/<feature>]]
- **<project-slug>** — <another summary>. Touched: [[projects/<slug>]]
```

Format for `Research & Sources Ingested`:

```markdown
## Research & Sources Ingested

- [[sources/DD-MM-YYYY-<slug>]] — <if any sources were ingested during the conversation>
```

If a session is short or low-signal (e.g., "what's the syntax for X?"), still include it but keep the summary one short clause.

## Step 8 — Update Tracking Files

### `.manifest.json`

For each conversation file ingested, append an entry:

```json
{
  "raw_path": "~/.claude/projects/-Users-…/<uuid>.jsonl",
  "ingested_at": "<today>",
  "content_hash": "sha256:…",
  "size_bytes": NNN,
  "source_type": "claude_conversation",
  "claude_project": "<decoded-project-name>",
  "wiki_project": "<wiki-slug-if-matched>",
  "pages_updated": ["projects/my-app", "projects/my-app/features/payment-flow"],
  "pages_created": [],
  "progress_updates": {
    "current_status_bumped": true,
    "features_advanced": ["payment-flow:planned→in-progress"],
    "features_shipped": ["notification-system"],
    "blockers_added": ["Stripe webhook config"],
    "decisions_created": []
  }
}
```

For memory files: `source_type: "claude_memory"`. For audit logs: `source_type: "claude_audit_log"`.

### `wiki/index.md`

Add any newly-created pages (decisions, patterns, technologies).

### `wiki/log.md`

Append:

```
## [DD-MM-YYYY] claude_history_ingest | N conversations, M projects touched, K features advanced, J shipped, S decisions created
```

### `wiki/hot.md`

Update **Recent Activity**:

```
- **DD-MM-YYYY — Claude history ingest** — Touched N projects; advanced features X and Y; shipped Z.
```

If any project's `Active Threads` line doesn't reflect the new `Working on`, update it.

## Privacy & Safety

- **Distill, never copy verbatim.** Conversations are private; their *content* belongs in your head, but only their *takeaways* belong in the wiki.
- **Skip secrets.** API keys, tokens, passwords, credentials in conversation text or audit-log command arguments — never write them to wiki pages, never include them in summaries.
- **Audit logs may contain sensitive shell output.** Summarize the action class ("ran tests, 3 failed in auth module"), not the verbatim stack trace.
- **Conversations may reference other people.** Be thoughtful about what goes in the wiki — names, opinions, gossip don't belong in your shared knowledge base.

## Notes for the LLM

- **Be conservative with auto-apply.** A false `shipped` mark erodes trust in the wiki faster than a missed update. Lean toward surfacing for confirmation when the signal isn't unambiguous.
- **The plan summary is the user's UX.** Make it scannable. Use the AUTO / ASK markers so the user can see what's about to happen at a glance.
- **Project matching is fuzzy.** If the conversation's `cwd` doesn't match a known `wiki/projects/<slug>.md` exactly, try slug-normalization (lowercase kebab-case, strip leading paths). If no match, ask the user — don't auto-create a project page from a conversation.
- **Audit log + transcript together > either alone.** When both are available for a session, use the audit log to verify or refute claims made in the transcript. "User said 'finished the migration'" + audit log shows the migration file was actually run + git command was executed → strong completion signal.
- **Dates from `.vault-meta.json`.** Read the configured date format. Don't write ISO timestamps into wiki pages even if the JSONL uses them.
- **Idempotency.** If the user re-runs after a partial ingest, the content_hash check should make this safe. The progress-update plan should be re-derivable from already-ingested sessions — but don't re-apply updates that have already been applied (check the most recent log entry).
