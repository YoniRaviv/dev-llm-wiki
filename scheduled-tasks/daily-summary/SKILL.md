---
name: daily-summary
description: End-of-day knowledge ingest — mines today's Claude conversations into the vault's journal, patterns, decisions and shipped records. Writes knowledge only, never status.
---

You are running the end-of-day knowledge ingest. The user is not present. Work fully autonomously.

VAULT: {{VAULT_PATH}}
CLAUDE_PROJECTS: {{CLAUDE_PROJECTS}}
TODAY: `date "+%d-%m-%Y"` → DD-MM-YYYY
TODAY_DISPLAY: `date "+%A, %B %-d %Y"`

## The one rule that overrides everything

**Your tracker owns execution. This vault owns knowledge.** You write what was *learned* and
what was *decided*. You never write what is *in progress*.

Never write, anywhere in the vault: `Working on`, `Next up`, `Blocked on`, `Last touched`,
`Current Status`, `Phase`, a percentage complete, or any status block. If a session's most
interesting content is "X is still pending", that belongs in the tracker — mention it in the
journal as prose if it carries a lesson, otherwise drop it.

`wiki/hot.md` and `wiki/today.md` do not exist in this vault by design — never create them.
Never write `today.md` either: it is a derived view owned by the `standup` skill.

## Step 1 — Today's journal page

- Path: `VAULT/wiki/journal/<TODAY>.md`
- If missing, create from `VAULT/.templates/daily-note.md`, replacing `{{DATE}}` → TODAY
  and `{{DATE_DISPLAY}}` → TODAY_DISPLAY.
- If present, leave everything the user typed intact; write only the auto-marker blocks
  and append to the two running logs (Step 4).

## Step 2 — Find today's conversations

Use this exact two-command sequence (variable assignments and process substitution cause
permission prompts):

```
touch -t $(date "+%Y%m%d")0000 /tmp/daily_ref_file
find {{CLAUDE_PROJECTS}}/ -name "*.jsonl" -newer /tmp/daily_ref_file
```

Skip any path already present in `VAULT/.manifest.json`. If nothing new, note that under
`## Claude Conversations` and stop.

## Step 3 — Extract, then file

From each `.jsonl`, extract:

- **Work done** — what concretely changed, shipped, or got fixed. Not "discussed X".
- **Key decisions** — architectural, product or process choices, each with its one-line *why*.
- **Notes worth keeping** — gotchas, footguns, non-obvious fixes, reusable lessons
  ("X bites you because Y; fix is Z"). These are the highest-value lines. Mine deliberately.
- **Patterns** — techniques general enough to deserve their own page.

Skip trivial sessions (<5 meaningful exchanges, or pure Q&A with no code or decisions).

For substantive sessions, write **only** to these targets:

| What you found | Where it goes |
|---|---|
| a reusable technique | `wiki/patterns/<slug>.md` |
| an architectural or product decision | `wiki/decisions/<slug>.md`, frontmatter `projects: [<slug>]` |
| a tool/library insight | `wiki/technologies/<slug>.md` |
| something **shipped** | `projects/<slug>/shipped/<feature>.md`, frontmatter **must** include `status: shipped` |
| session narrative | today's journal page (Step 4) |

Rules for those writes:

- **`projects/<slug>.md` is off limits.** Do not touch project pages. They hold identity
  (`tracker`, `tracker_url`), never state, and nothing you extract belongs there.
- `projects/<slug>/shipped/` is for work that actually shipped. If it is in flight, it is a
  tracker issue — write nothing.
- Never create any other path under `projects/<slug>/`. The legal slots are `00-idea.md`,
  `01-research.md`, `02-prd.md`, `shipped/`, `notes/`, `assets/`. A pre-commit hook enforces
  this; violating it silently breaks the user's next commit.
- `status: shipped` must be exactly that — no trailing prose. Put PR/commit refs in a
  separate `shipped_in:` field.
- Follow each page type's existing frontmatter and required sections.
- `topics:` entries must already exist in `wiki/topics.md`, or add them there in the same run.
- Every new page gets `[[wikilinks]]` to at least 2 related existing pages, an entry in
  `wiki/index.md`, and an inbound link from one existing page. No orphans.
- Run `python3 VAULT/.scripts/vault-check.py` before you finish. If it reports a violation
  you introduced, fix it — do not leave the vault dirty for the user's next commit.

## Step 4 — Fill the journal

Aim for the density of the older journals — decisions with their *why*, footgun-level notes —
not a thin list of "worked on X".

**Marker blocks.** `Key Decisions` and `Notes` each carry
`<!-- auto:<name>:start -->…<!-- auto:<name>:end -->`. Write *only inside* the block,
replacing its contents (so a second run the same day regenerates rather than duplicates).
Anything outside the markers is the user's — never touch it. There is **no blockers block**;
if an older journal has one, leave it alone as a historical record but do not write to it.

- `## Claude Conversations` — append, no markers, running log. One dense bullet per project:
  `- **Project**: what changed + the key decision or gotcha ([[projects/<slug>]])`
- `## Research & Sources Ingested` — append, no markers. New/updated pages and sources, wikilinked.
- `<!-- auto:decisions:start -->` — `- **<decision>**: <what was chosen> — <one-line why>`
- `<!-- auto:notes:start -->` — `- **<gotcha>**: <the non-obvious thing + the fix>`
- `## What I Worked On` — **fully manual, never write to it.** `/standup` owns its
  `<!-- standup:done -->` block; do not touch that either.

## Step 5 — Tracker drift check (read-only)

For each project that saw real work today and whose `projects/<slug>.md` has a `tracker:` other
than `none`, read its open issues (via that tracker's MCP or CLI, **read-only**). Skip projects
with `tracker: none` — pre-execution by design, there is nothing to reconcile against.

If work happened with **no** matching issue, add one line under
`## Research & Sources Ingested`:

```
- ⚠️ Drift: <what was done> on <project> has no tracker issue. Reconcile.
```

**Never create, close, or comment on an issue.** You surface drift; the user decides.
If the tracker is unreachable, write `- ⚠️ Drift check skipped: tracker unreachable.` and
continue — never fail the run over it.

## Step 6 — Manifest

For each processed file append to `VAULT/.manifest.json`:

```json
{
  "path": "...",
  "ingested_at": "<ISO timestamp>",
  "size_bytes": 0,
  "source_type": "claude_conversation",
  "project": "<project-slug>",
  "pages_created": [],
  "pages_updated": []
}
```

## Step 7 — Housekeeping

- New pages → add to `wiki/index.md`: `- [Title](subdir/page.md) — one-line description`
- Append to `wiki/log.md`: `## [<TODAY>] ingest | <N> conversations across <X> projects`
  (entry type is `ingest` — `log.md` records only `ingest`, `query`, `lint`)
- Do **not** touch `today.md` or any `projects/<slug>.md`.

## Rules

- Dense, not exhaustive. A decision without its *why*, or a note without its fix, is not
  worth keeping.
- Never write status. If you are about to record progress, stop — it belongs in the tracker.
- Never `git commit`.
- Never ask for confirmation; complete every step autonomously.
