---
name: send-to-wiki
description: Send content from any project codebase to the dev wiki vault at {{VAULT_PATH}}. Use when working in a code repo and wanting to save a feature plan, PRD, research note, meeting note, or shipped-work record to the correct project slot in the vault. Triggers on: "send to wiki", "save to vault", "add to my wiki", "push to dev wiki", "save this feature plan", "write this to the vault", "capture this in the wiki".
---

# Send to Dev Wiki

Save content from a project codebase into the correct slot in the dev wiki. You are writing into a
gated vault: `{{VAULT_PATH}}/CLAUDE.md` is the contract, and `.scripts/vault-check.py` will reject
a write that breaks it.

```
VAULT = {{VAULT_PATH}}
```

## The invariant — read this before choosing a slot

> The vault stores tracker **identity** (a URL) — never tracker **state**.

There is **no status slot**. If what you are about to save is progress — "70% done", "blocked on
the API team", "next up: caching" — it belongs in the issue tracker, not here. Say so and stop.

## Step 1 — Identify the project slug

In order:

1. `git remote get-url origin` → repo name → kebab-case
2. current directory name → kebab-case
3. ask the user

Then confirm the project exists and read its tracker in one go:

```sh
ls {{VAULT_PATH}}/projects/<slug>/ 2>/dev/null
grep '^tracker:' {{VAULT_PATH}}/projects/<slug>.md
```

If the project page doesn't exist:

> "No vault project found for `<slug>`. Run `.scripts/new-project.sh <slug>` from the vault, or
> tell me a different slug."

## Step 2 — The plan gate decides half the slot map

`tracker:` is not metadata here — it determines which slots are **legal**:

| `tracker:` | Plan slots (`03-plan.md`, `roadmaps/`, `features/`) |
|---|---|
| `none` | legal — the vault holds the only copy of the how/when |
| anything else | **illegal** — the tracker owns how/when; pre-commit rejects them |

So if `tracker:` is not `none` and the user asks to save a feature plan or a roadmap, do not write
it. Say:

> "`<slug>` has `tracker: <value>`, so plans live there, not in the vault. Want me to write this
> up as a tracker issue description you can paste instead?"

## Step 3 — Slot map

| Content | Destination | Condition |
|---|---|---|
| initial spark / brief | `projects/<slug>/00-idea.md` | — |
| research, landscape, verdict | `projects/<slug>/01-research.md` | — |
| PRD — what + why | `projects/<slug>/02-prd.md` | must pass the PRD purity rules below |
| high-level how + when | `projects/<slug>/03-plan.md` | **`tracker: none` only** |
| feature plan / spec | `projects/<slug>/features/<name>.md` | **`tracker: none` only** |
| versioned roadmap | `projects/<slug>/roadmaps/v<N>.md` | **`tracker: none` only** |
| record of work that **shipped** | `projects/<slug>/shipped/<name>.md` | frontmatter needs `status: shipped` |
| dated ad-hoc / meeting note | `projects/<slug>/notes/DD-MM-YYYY-<topic>.md` | — |
| diagram, csv, html, pdf | `projects/<slug>/assets/<name>.<ext>` | — |
| build order + does-it-work | `projects/<slug>/spine.md` | **tracker set only** |
| a status update | — | **refuse** — it belongs in the tracker |

Nothing else may exist under `projects/<slug>/`. Never invent a path.

**PRD purity** — `02-prd.md` rejects `- [ ]` checkboxes, `## Phase` headings, and bare dates.
Strip them before writing, or move that content to the plan slot / tracker and tell the user which.

## Step 4 — Confirm before writing

State the full destination path and a one-line summary:

> "Writing the `user-auth` feature plan to `projects/my-app/features/user-auth.md`
> (`tracker: none`, so the plan slot is legal). OK?"

Wait for confirmation. If the file exists, read it first and ask overwrite-or-append.

## Step 5 — Frontmatter

Dates are `DD-MM-YYYY` unless `{{VAULT_PATH}}/.vault-meta.json` → `date_format` says otherwise.

**`features/*.md`**
```yaml
---
project: <slug>
topics: []
started: <today>
---
```

**`shipped/*.md`** — `status: shipped` is mandatory and must be exactly that. PR/commit refs go in
`shipped_in:`, never in `status:`.
```yaml
---
project: <slug>
status: shipped
topics: []
started: <today>
shipped: <today>
summary: "<one sentence: what now works that didn't before>"
shipped_in: <PR or commit ref>
---
```

**`notes/*.md`**
```yaml
---
date: <today>
type: note
---
```

**`00-idea.md` / `01-research.md` / `02-prd.md` / `03-plan.md`** — no required frontmatter;
preserve anything already there.

Populate the body faithfully from the conversation. Mark anything uncertain `> ❓ TBD: …`.
Never write `Working on`, `Next up`, `Blocked on`, `Phase:`, `Last touched`, or a percentage
complete into any of them.

## Step 6 — Verify, then report

```sh
cd {{VAULT_PATH}} && python3 .scripts/vault-check.py
```

If it flags something you introduced, fix it — do not leave the vault dirty for the user's next
commit. A brand-new page reported under `orphans` is expected until a wiki page links it; mention
it rather than fixing it silently.

Then report the path written.
