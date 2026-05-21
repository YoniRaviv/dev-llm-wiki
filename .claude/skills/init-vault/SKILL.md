---
name: init-vault
description: One-time personalization of a freshly-cloned claude-dev-wiki template. Walks the user through identity/stack, date format, folder customization, journal & daily-ingest opt-in, starter topics, and optional CLAUDE.md refinements. Use whenever the user just cloned the template and says any of "set up my wiki", "initialize the vault", "personalize this template", "configure my dev brain", "I just cloned this — what now", or opens a fresh wiki for the first time. Also use when the user explicitly invokes init-vault. Auto-skips and warns if `.vault-meta.json` already exists.
---

# Init Vault

Personalizes a freshly-cloned claude-dev-wiki template to the user's specific situation. After it completes the vault is ready for daily use: the date format matches their preference, the folder structure reflects what they actually need, `wiki/topics.md` carries a starter vocabulary tailored to their stack, and CLAUDE.md reflects any workflow tweaks.

It is intended to run **exactly once per vault**. Re-running may overwrite the user's earlier choices, so the skill checks for prior runs and asks before continuing.

## Why this skill exists

A fresh clone of the template is intentionally generic. The schemas are right, the operations are documented, but nothing reflects who the user is or how they work. Without a personalization pass, the user has to read CLAUDE.md, manually decide what to keep, hand-edit examples, and seed `topics.md` from scratch — friction that often translates into "I'll do it later" and then never doing it.

This skill removes the friction. It asks ~10 questions in 3-4 batches, applies all the cascading edits, and leaves the user with a vault that's actually theirs.

## At a glance

1. Asks identity, stack, project kind, date format, folder changes, journal/daily-ingest opt-in, starter topics, and optional CLAUDE.md tweaks.
2. Applies the chosen date format first (it cascades into every subsequent date write).
3. Edits CLAUDE.md, README.md, templates, and scripts to match folder choices.
4. Removes opt-out features cleanly — deletes files AND removes references from docs.
5. Seeds `wiki/topics.md` with stack-appropriate starter topics from `references/topic-seeds.md`.
6. Writes `.vault-meta.json` at the repo root so the skill can detect re-runs (and future skills can look up the user's stack/preferences).
7. Shows a summary and offers to commit everything as a single commit.

## Procedure

### Step 1 — Check for prior initialization

Look for `.vault-meta.json` at the repo root.

If it exists:
- Read it.
- Tell the user when it was initialized and a one-line summary of the prior answers.
- Use `AskUserQuestion` to confirm a re-run. Warn that prior personalization will be overwritten.
- Continue only on "yes".

If it doesn't exist, continue.

### Step 2 — Identity & stack

One `AskUserQuestion` call with these four questions:

1. **Your name** — `header: "Name"`. Provide two plausible label options plus the implicit Other for free text. Used in the eventual commit message.
2. **Your role** — `header: "Role"`. Options: frontend, backend, full-stack, ML/data, founder or solo builder.
3. **Primary stack** — `header: "Stack"`. Options: TypeScript-React, Python-ML, Go, Rust, Ruby-Rails, Java-Kotlin. Other for anything else.
4. **What kind of projects** — `header: "Projects"`. Options: SaaS products, libraries/tools, internal/business apps, research/POCs, mixed.

Store the answers locally — you'll use them in Step 6 (topic seeding) and Step 7 (CLAUDE.md tweaks).

### Step 3 — Date format

Ask one question, with previews so the user can see exactly what they'd be choosing:

```
- DD-MM-YYYY (European, default) — 20-05-2026
- MM-DD-YYYY (US) — 05-20-2026
- YYYY-MM-DD (ISO 8601, sortable) — 2026-05-20
```

If the user picks anything other than DD-MM-YYYY, **apply the format change before any other file modifications**, because every subsequent step in this skill writes dates that need to match.

Apply:
1. Use `grep -rln "DD-MM-YYYY" .` (from the repo root, excluding `.git/` and `.claude/skills/init-vault/`) to find every reference in CLAUDE.md, README.md, templates, `_template/` files, and `.scripts/README.md`. Edit each file's literal `DD-MM-YYYY` strings to the chosen format.
2. Find example dates that match the default (e.g., `20-05-2026` in comments and previews) and rewrite them to the chosen format.
3. Edit `.scripts/new-project.sh`: change `date +%d-%m-%Y` to `%m-%d-%Y` or `%Y-%m-%d`.
4. Edit `.scripts/new-journal.sh`: change the validation regex AND the `date +%d-%m-%Y` invocation AND the display-format `date -j` line. For ISO the validation regex becomes `^[0-9]{4}-[0-9]{2}-[0-9]{2}$`.

Hold the chosen format in mind for the rest of the skill — any dates written into `vault-meta.json`, `topics.md` frontmatter, or commit messages must use it.

### Step 4 — Folder customization

Show the current `raw/` and `wiki/` subdirs as bullet lists so the user can see what's already there:

- **`raw/` defaults:** articles, tweets, repos, ideas, projects
- **`wiki/` defaults:** projects, patterns, technologies, ideas, sources, journal, templates (plus the root files index.md, topics.md, hot.md, log.md)

Then one `AskUserQuestion` call with four `multiSelect: true` questions. Empty selections (user picks nothing for a given question) mean no change for that bucket — that's normal.

**Q1 — Add to `raw/`?** `header: "raw/ adds"`. Options:
- papers
- videos
- podcasts
- books

Other (auto-provided) handles less-common additions: courses, talks, datasets, screenshots, anything else the user names.

**Q2 — Remove from `raw/`?** `header: "raw/ removes"`. Options:
- tweets
- repos
- ideas

`articles` and `projects` are core to the workflow — don't offer to remove them.

**Q3 — Add to `wiki/`?** `header: "wiki/ adds"`. Options:
- people
- retrospectives
- principles
- glossary

Other handles anything else.

**Q4 — Remove from `wiki/`?** `header: "wiki/ removes"`. Options:
- patterns
- technologies
- ideas

`projects`, `sources`, `journal`, `templates`, plus the root files (`index.md`, `topics.md`, `hot.md`, `log.md`) are structural — never offer to remove them.

#### Applying the choices

For each **addition**: `mkdir -p` the folder under the right parent and create a `.gitkeep` so git tracks the empty dir.

For each **removal**: verify the folder is empty (it should be on a fresh template). If it's not, ask the user to confirm before deleting. Then delete it.

After all folder changes:
- Edit CLAUDE.md's Directory Layout block to match — add new lines for additions, remove lines for removals.
- Edit README.md's file tree to match the same way.

### Step 5 — Journal & daily-ingest opt-in

Two `AskUserQuestion` questions:

1. **Daily journal workflow?** — yes/no. The journal is a daily note in `wiki/journal/DD-MM-YYYY.md` (or chosen format) with sections for What I Worked On, Key Decisions, Blockers, etc. Worth keeping if the user already keeps daily notes; safe to drop otherwise.
2. **(Only if journal=yes)** Auto-ingest of Claude Code conversations into the journal? — yes/no. Explain plainly: this requires implementing `daily-ingest.sh` for your environment; the template ships a stub. Most people pick no at first and add it later if they want.

If journal = no:
- Delete `wiki/journal/.gitkeep`, the `wiki/journal/` folder, `wiki/templates/daily-note.md`, and `.scripts/new-journal.sh`.
- In CLAUDE.md: remove the `journal/` row from Directory Layout AND the journal/ page entity schema section.
- In README.md: remove the `journal/` row from the file tree AND any references to daily notes.
- In `.scripts/README.md`: remove the `new-journal.sh` row.

If daily_ingest = no:
- Delete `.scripts/daily-ingest.sh` and `.scripts/install-launchd.sh`.
- In CLAUDE.md: remove the auto-fill behavior block under the journal/ schema section (only relevant if journal=yes; otherwise that block was already removed above).
- In `.scripts/README.md`: remove the `daily-ingest.sh` and `install-launchd.sh` rows.

### Step 6 — Seed topics

Read `references/topic-seeds.md`. Based on the user's stack and project-kind from Step 2, compose a starter list:

- 5-7 topics from their **stack** bucket
- 3-5 topics from their **project-kind** bucket
- 3-5 from the **cross-cutting** bucket (always relevant)
- Cap at 20 total. Trim if needed.

Show the proposed list as a clean markdown block. Ask: "Approve, edit, or skip?" via `AskUserQuestion` (Other for edits).

Apply the approved list by replacing the placeholder vocabulary section in `wiki/topics.md`. Set the `updated:` frontmatter to today's date in the chosen format.

### Step 7 — CLAUDE.md refinement (optional)

Ask the user if they want to tweak any workflow defaults. Present as a single multi-select with these three options:

1. **Skip INGEST step 2** (the "What should I emphasize from this?" mid-ingest dialogue question). Skipping makes ingest faster but loses the user-in-the-loop step. Default: keep.
2. **Tighten or loosen SURFACE budget**. Default is "max 2 inline citations per topic shift". If picked, ask follow-up for new value.
3. **Adjust `Current Status` stale threshold**. Default is "14 days". If picked, ask follow-up for new value.

For each item the user picks, edit the corresponding line in CLAUDE.md. Briefly show the before/after diff inline so they see what changed.

If they pick none, move on.

### Step 8 — Write vault-meta and commit

Write `.vault-meta.json` at the repo root:

```json
{
  "initialized": "<today's date in chosen format>",
  "skill_version": "1.0",
  "owner": "<name>",
  "role": "<role>",
  "stack_primary": "<stack>",
  "project_kinds": "<kind>",
  "date_format": "DD-MM-YYYY | MM-DD-YYYY | YYYY-MM-DD",
  "folders": {
    "raw": ["..."],
    "wiki": ["..."]
  },
  "features": {
    "journal": true,
    "daily_ingest": false
  },
  "claude_md_tweaks": ["..."]
}
```

Then show the user a summary:
- Date format applied.
- Folder changes (added X, removed Y, or "no changes").
- Features kept/removed.
- Topics seeded (count) — or "skipped".
- CLAUDE.md tweaks (list, or "none").

Ask: "Commit everything as a single `Personalize vault for <name>` commit?" via `AskUserQuestion`.

If yes:

```sh
git add -A
git commit -m "Personalize vault for <name>"
```

If no, leave the working tree dirty — the user can review the diff and commit themselves.

## Notes for the LLM

- **Edit ordering matters**. Apply the date format change first (Step 3) before any other file modifications. Otherwise dates you write in Steps 4-8 will be in the wrong format and you'll have to redo them.
- **Batch your file edits, but not your questions**. Each `AskUserQuestion` call should ask 1-4 related questions in one call (the user sees them grouped). But when applying answers across multiple files, do all the related edits in one batch and then move to the next step.
- **Before mass-editing, give a one-line heads-up**. Example: "About to remove all journal/ references in 4 places: CLAUDE.md schema section, CLAUDE.md directory layout, README tree, scripts README." This is so the user can stop you if you misunderstood. One sentence, not a paragraph.
- **Stop gracefully**. If the user says "stop" or "skip the rest" partway through, write what you have so far to `.vault-meta.json` and stop. A future re-run can pick up where you left off.
- **Re-running**. If `.vault-meta.json` exists and the user confirms a re-run, frame each question as "current value is X — change?" rather than starting fresh. Default the answer to the existing value.
- **Don't over-confirm**. After the user answers a question, apply the edits and move on — don't ask "are you sure?" for each individual file edit.
