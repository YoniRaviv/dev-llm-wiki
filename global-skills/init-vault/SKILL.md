---
name: init-vault
description: One-time personalization of a freshly-cloned claude-dev-wiki template. Walks the user through identity/stack, which issue tracker owns execution, date format, capture surfaces, starter topics, an optional first domain hub, and the harness permission allowlist — then installs the pre-commit gate. Use whenever the user just cloned the template and says any of "set up my wiki", "initialize the vault", "personalize this template", "configure my dev brain", "I just cloned this — what now", or opens a fresh vault for the first time. Also use when the user explicitly invokes init-vault. Auto-skips and warns if `.vault-meta.json` already exists.
---

# Init Vault

Personalizes a freshly-cloned claude-dev-wiki template. When it finishes: the tracker is named, the
date format matches the user's preference, `raw/` holds only the capture surfaces they'll use,
`wiki/topics.md` carries a starter vocabulary for their stack, the harness has a scoped permission
allowlist, and **the pre-commit gate is installed** — so the vault's invariant is enforced from the
first commit rather than from the first time someone reads `CLAUDE.md`.

Runs **exactly once per vault**. It checks for prior runs and asks before continuing.

```
VAULT = {{VAULT_PATH}}
```

## The thing to get right

This vault has one invariant, and everything in it descends from that:

> The vault stores tracker **identity** (a URL) — never tracker **state**.

The most consequential question in this skill is therefore **which tracker owns execution**. If the
user has no tracker, that is a legitimate and complete answer (`tracker: none`) — it means the plan
slots stay in the vault, and the plan gate never fires. Do not push them toward adopting one.

Read `{{VAULT_PATH}}/CLAUDE.md` before you start. You are about to edit it.

## Procedure

### Step 1 — Check for prior initialization

Look for `.vault-meta.json` at the vault root.

If it exists: read it, tell the user when it was initialized and summarize the prior answers in one
line, then use `AskUserQuestion` to confirm a re-run — warning that prior personalization will be
overwritten. Continue only on yes. On a confirmed re-run, frame each question as "current value is
X — change?" and default to the existing value.

If it doesn't exist, continue.

### Step 2 — Identity & stack

One `AskUserQuestion` call, four questions:

1. **Your name** — `header: "Name"`. Two plausible options plus the implicit Other. Used in the
   commit message and `.vault-meta.json`.
2. **Your role** — `header: "Role"`. Options: frontend, backend, full-stack, ML/data, founder or
   solo builder.
3. **Stack(s) you work in** — `header: "Stack"`, **`multiSelect: true`**. Options:
   TypeScript-React, Python-ML, Go, Rust, Ruby-Rails, Java-Kotlin. Most people work across
   several — encourage picking all that apply.
4. **What kind of projects** — `header: "Projects"`. Options: SaaS products, libraries/tools,
   internal/business apps, research/POCs, mixed.

### Step 3 — The tracker

This is the load-bearing question. One `AskUserQuestion` call:

1. **Which tracker owns execution?** — `header: "Tracker"`. Options:
   - **Linear** — issues, cycles, projects; has an MCP server
   - **Jira** — issues, sprints, epics
   - **GitHub Issues** — issues, milestones, projects
   - **None** — I plan in the vault and build from it

   Other handles anything else (Shortcut, Asana, a shared board).

2. **(Only if not "None")** **Do you want a worked example of promotion in `CLAUDE.md`?** — yes/no.
   If yes, rewrite the "Promotion" checklist's step 2 with that tracker's own vocabulary (Linear:
   "a feature page becomes an issue, a roadmap becomes a milestone or a cycle ordering"; Jira:
   "…an epic with stories, a roadmap becomes a sprint ordering"; GitHub: "…an issue, a roadmap
   becomes a milestone").

Apply:
- In `CLAUDE.md`, replace the `tracker:` enum line so the user's tracker leads:
  `tracker:     <theirs> | none` — keeping `none` always, because it is a real state.
- If the answer is **None**: add one line under "The plan gate" noting that with no tracker
  configured, the plan slots are permanent and `spine.md` is never used. Do not delete the gate
  documentation — the user may adopt a tracker later, and the gate is what will tell them what to
  move.
- If a tracker **was** named: nothing else to change. The gate is already tracker-agnostic.

Never write a tracker URL into `CLAUDE.md`. URLs belong on project pages only.

### Step 4 — Date format

Ask one question with previews:

```
- DD-MM-YYYY (European, default) — 20-05-2026
- MM-DD-YYYY (US)                — 05-20-2026
- YYYY-MM-DD (ISO 8601, sortable) — 2026-05-20
```

If the answer is anything other than DD-MM-YYYY, **apply it before any other file edit** — every
later step writes dates.

Apply:
1. `grep -rln "DD-MM-YYYY" .` from the vault root, excluding `.git/`. Rewrite the literal
   `DD-MM-YYYY` strings in `CLAUDE.md`, `README.md`, `.templates/*`, `.templates/project/*`,
   `global-skills/*`, `scheduled-tasks/*` and `.scripts/README.md`.
2. Rewrite example dates matching the default (e.g. `20-05-2026`) to the chosen format.
3. `.scripts/new-project.sh` — change `date +%d-%m-%Y`.
4. `.scripts/new-journal.sh` — change the validation regex, the `date +%d-%m-%Y` call, and the
   display-format `date -j` line. For ISO the regex becomes `^[0-9]{4}-[0-9]{2}-[0-9]{2}$`.
5. **`.scripts/vault-check.py`** — the date regexes are format-specific. Update `PRD_DATE`,
   `PRD_DATE_IN_PATH`, and the `\d{2}-\d{2}-\d{4}` fragments; for ISO the shape is
   `\d{4}-\d{2}-\d{2}`. Then run `python3 .scripts/vault-check.py` to confirm it still parses and
   reports clean. **This step is easy to forget and it silently disables `prd-purity`.**
6. `global-skills/wiki-lint/SKILL.md` — Step 5's filename regexes and the "YYYY-MM-DD anywhere is
   wrong" grep, which is only correct for the DD-MM-YYYY default.

### Step 5 — Capture surfaces

Show what `raw/` currently holds: `articles`, `tweets`, `repos`, `ideas`, `books`, `education`,
`videos`.

One `AskUserQuestion` call, two `multiSelect: true` questions. Empty selection means no change.

**Q1 — Add to `raw/`?** Options: papers, podcasts, talks, datasets. Other for anything else.

**Q2 — Remove from `raw/`?** Options: tweets, repos, books, education, videos.
`articles` and `ideas` are core to the workflow — don't offer to remove them.

Do **not** offer to change `wiki/` or `projects/`. Their subdirectories are load-bearing:
`wiki/decisions|patterns|technologies|domains|ideas|sources|journal` are named in the entity
schemas, and the `projects/` slot list is enforced by `vault-check.py`. Changing either means
changing the gate, which is not a setup-questionnaire decision.

For each addition: `mkdir -p raw/<name>` plus a `.gitkeep`, add a matching
`.templates/raw-<name>.md` capture template modeled on the closest existing one, and add the row to
`CLAUDE.md`'s zone table and `README.md`'s tree.

For each removal: confirm the folder is empty, delete it and its `.templates/raw-<name>.md`, and
remove the references from `CLAUDE.md` and `README.md`.

### Step 6 — Seed topics

Read `references/topic-seeds.md`. From the Step 2 answers compose a starter list:

- 3–5 topics per selected stack, deduplicated across stacks
- 3–5 from the project-kind bucket
- 3–5 from the cross-cutting bucket (always relevant)
- cap at 20; when trimming, prefer topics that appear across several selected stacks

Show the proposed list as a markdown block. Ask approve / edit / skip via `AskUserQuestion` (Other
for edits). Apply by replacing the placeholder vocabulary in `wiki/topics.md`, keeping the
`- \`topic\` — description` shape the lint skill's parser expects. Set `updated:` to today.

### Step 7 — A first domain hub (optional)

Domain hubs (`wiki/domains/<domain>.md`) are what make SURFACE useful — they are the always-load
page for a subject the user keeps returning to. They only earn their keep once there is content, so
this is a seed, not a filled hub.

Ask: **"Seed a domain hub for one subject you work in deeply?"** — offer 2–3 candidates derived
from their stack and project kind, plus "skip".

If they pick one, write `wiki/domains/<slug>.md` with the schema from `CLAUDE.md`: frontmatter
(`domain`, `topics`, `trigger_topics`, `updated`, `summary`) and the three empty sections
(Distilled Core, Reading Index, Landscape), each with a one-line note on what belongs there. Add it
to `wiki/index.md`. Tell the user it will fill in as they ingest — the `wiki-ingest` skill updates
hubs whose `trigger_topics:` a source hits.

### Step 8 — Harness permissions

The vault's operations touch a predictable set of paths. A scoped allowlist removes most permission
prompts without opening the harness up.

Ask: **"Write a `.claude/settings.json` permission allowlist for this vault?"** — yes/no, defaulting
to yes. Explain in one line: it pre-approves reads across the vault and writes to `wiki/`, plus the
common read-only shell commands, so ingest and lint stop prompting.

If yes, write `.claude/settings.json` with absolute paths (they cannot be relative):

```json
{
  "permissions": {
    "allow": [
      "Read({{VAULT_PATH}}/**)",
      "Edit({{VAULT_PATH}}/wiki/**)",
      "Write({{VAULT_PATH}}/wiki/**)",
      "Edit({{VAULT_PATH}}/.manifest.json)",
      "Write({{VAULT_PATH}}/.manifest.json)",
      "Bash(python3 *)", "Bash(grep *)", "Bash(find *)", "Bash(ls *)",
      "Bash(date *)", "Bash(head *)", "Bash(tail *)", "Bash(wc *)", "Bash(sort *)"
    ]
  }
}
```

Deliberately **not** pre-approved: writes to `projects/`, `raw/`, `meetings/` or `CLAUDE.md`, and
`Bash(rm *)`. Those are the writes worth seeing a prompt for. Note that `.claude/settings.json` is
committed while `.claude/settings.local.json` is gitignored — put machine-specific overrides in the
latter.

### Step 9 — Install the gate

Not optional, and not a question. Run:

```sh
cd {{VAULT_PATH}}
.scripts/install-hooks.sh
.scripts/install-global-skills.sh
python3 .scripts/vault-check.py
```

- `install-hooks.sh` writes `.git/hooks/pre-commit`.
- `install-global-skills.sh` re-installs the global skills with this vault's path substituted — it
  must run **after** any path or date-format change, or the installed copies point at the wrong
  place.
- `vault-check.py` must print `vault-check: ✓ clean`. If it doesn't, fix what it reports before
  finishing — a template that ships dirty teaches the user to ignore the gate.

Then tell the user the one thing they need to know about the hook: it hard-fails, and
`git commit --no-verify` is the only escape.

Optionally offer to install the `daily-summary` end-of-day routine from `scheduled-tasks/` — see
that file's header for what it writes. Mention it; don't push it.

### Step 10 — Write vault-meta and commit

Write `.vault-meta.json` at the vault root:

```json
{
  "initialized": "<today, in the chosen format>",
  "skill_version": "2.0",
  "owner": "<name>",
  "role": "<role>",
  "stacks": ["<stack>"],
  "project_kinds": "<kind>",
  "tracker": "none | linear | jira | github | <other>",
  "date_format": "DD-MM-YYYY | MM-DD-YYYY | YYYY-MM-DD",
  "raw_surfaces": ["articles", "ideas"],
  "domain_hub_seeded": "<slug or null>",
  "harness_permissions": true,
  "hooks_installed": true
}
```

Summarize: tracker · date format · capture-surface changes · topics seeded (count) · domain hub ·
permissions · gate status.

Then ask whether to commit as a single `Personalize vault for <name>` commit. If yes,
`git add -A && git commit -m "Personalize vault for <name>"` — the hook you just installed will run,
which is a useful first demonstration of it. If no, leave the tree dirty.

## Notes for the LLM

- **Ordering matters.** Date format (Step 4) precedes every other file edit. `install-global-skills.sh`
  (Step 9) must run last, after all substitutions are final.
- **The date-format change includes `vault-check.py`.** Missing it leaves a gate that looks
  installed and silently no longer checks PRD dates. Verify by running the script.
- **Batch edits, not questions.** One `AskUserQuestion` per step, 1–4 related questions inside it.
  Then apply all of that step's edits together.
- **Give a one-line heads-up before a mass edit.** "About to change the date format in 9 files:
  CLAUDE.md, README.md, 8 templates, 2 scripts, vault-check.py." One sentence.
- **Never offer to remove a load-bearing folder or loosen a gate check.** If the user asks, explain
  what the check defends and let them decide — but do not volunteer it.
- **Stop gracefully.** On "stop" or "skip the rest", write what you have to `.vault-meta.json` and
  stop. A re-run picks up from there.
- **Don't over-confirm.** Apply and move on; don't ask "are you sure?" per file.
