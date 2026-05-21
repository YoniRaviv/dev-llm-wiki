---
name: send-to-wiki
description: Send content from any project codebase to the dev wiki vault at {{VAULT_PATH}}. Use when working in a code repo and wanting to save a feature plan, decision, research note, or meeting note to the correct project slot in the vault. Triggers on: "send to wiki", "save to vault", "add to my wiki", "push to dev wiki", "save this feature plan", "write this to the vault", "capture this in the wiki".
---

# Send to Dev Wiki

Save content from any project codebase to the correct lifecycle slot in the dev wiki.

## Vault path

```
VAULT = {{VAULT_PATH}}
```

## Lifecycle slot map

| Content type | Destination |
|---|---|
| Feature plan / spec | `raw/projects/<slug>/features/<name>.md` |
| High-level plan (how) | `raw/projects/<slug>/03-plan.md` |
| PRD / what + why | `raw/projects/<slug>/02-prd.md` |
| Research / landscape | `raw/projects/<slug>/01-research.md` |
| Initial idea / brief | `raw/projects/<slug>/00-idea.md` |
| Meeting / ad-hoc note | `raw/projects/<slug>/notes/DD-MM-YYYY-<topic>.md` |
| Status update | `raw/projects/<slug>/STATUS.md` |

## Workflow

### 1. Identify the project slug

Try to infer from context in this order:
1. Current git repo name — run `git remote get-url origin`, parse the repo name, convert to kebab-case
2. Current working directory name, converted to kebab-case
3. Ask the user: "Which vault project should this go to? (e.g. `my-app`)"

Then verify the project exists:
```sh
ls {{VAULT_PATH}}/raw/projects/<slug>/
```

If the folder doesn't exist, tell the user:
> "No vault project found for `<slug>`. Run `.scripts/new-project.sh <slug>` from the wiki directory first, or tell me a different slug."

### 2. Identify content type and destination

Infer from context (what was just built, planned, or said). When ambiguous, show the slot map above and ask which row fits.

- **Feature plans**: ask for the feature name if not obvious, convert to kebab-case for the filename.
- **Meeting notes**: use today's date in the vault's configured date format (check `{{VAULT_PATH}}/.vault-meta.json` → `date_format`; default `DD-MM-YYYY`). Ask for a short topic label.
- **Spine docs** (00–03, STATUS): warn if the file already exists and ask whether to overwrite or append.

### 3. Confirm before writing

State the full destination path and a one-line summary:

> "Writing feature plan for `user-auth` to `raw/projects/my-app/features/user-auth.md` in the vault. OK?"

Wait for confirmation.

### 4. Format the content

Apply the correct frontmatter for the slot:

**features/\*.md**
```yaml
---
project: <slug>
status: planned
topics: []
started: <today>
---
```

**notes/\*.md**
```yaml
---
date: <today>
type: note
---
```

**00-idea.md / 01-research.md / 02-prd.md / 03-plan.md** — no required frontmatter; preserve any the user already has.

**STATUS.md** — plain markdown, no frontmatter.

Populate the body faithfully from the conversation. Mark anything uncertain with `> ❓ TBD: ...`.

### 5. Write the file

Create any missing directories (`features/`, `notes/`) before writing.

If the file already exists: read it first, then ask "Overwrite or append?"

### 6. Confirm

Report the full path written:
> "Saved to `raw/projects/my-app/features/user-auth.md`. When the feature ships, ask Claude to `promote-feature user-auth` from the wiki directory to lift it into the schema-compliant wiki page."
