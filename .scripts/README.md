# Scripts

Run from the vault root. All of them assume the vault is one level up from `.scripts/`.

| Script | What it does |
|---|---|
| `vault-check.py` | **The gate.** Checks every structural invariant in `CLAUDE.md`. Exit 0 clean, 1 on violation. `--staged` checks only staged files (pre-commit mode), `--quiet` drops the OK line. |
| `install-hooks.sh` | Installs `.git/hooks/pre-commit`, which runs `vault-check.py --staged`. Hard fail. Re-runnable. |
| `install-global-skills.sh` | Installs `global-skills/*` to `~/.claude/skills/` and `scheduled-tasks/*` to `~/.claude/scheduled-tasks/`, substituting `{{VAULT_PATH}}` and `{{CLAUDE_PROJECTS}}`. Re-run after moving the vault or changing the date format. |
| `new-project.sh <slug>` | Scaffolds a whitelist-legal `projects/<slug>.md` + `projects/<slug>/` from `.templates/project/`, with `tracker: none`. |
| `new-journal.sh [DATE]` | Creates `wiki/journal/<DATE>.md` from `.templates/daily-note.md`. Defaults to today. |

## The checks

`vault-check.py` reports per check. Every one of them encodes a rule from `CLAUDE.md` — read that
file before changing one.

| Check | Fails when |
|---|---|
| `whitelist` | a file exists under `projects/<slug>/` that isn't a legal slot |
| `plan-gate` | `03-plan.md`, `roadmaps/` or `features/` exist while the project has a tracker |
| `spine-gate` | `spine.md` exists while `tracker: none` |
| `spine-owner` | a spine stage row names neither a tracker ID nor "nothing owns this" |
| `prd-purity` | `02-prd.md` contains a checkbox, a `## Phase` heading, or a bare date |
| `tracker-state` | `Blocked on:` / `Next up:` / `Working on:` / `Phase:` appears under `projects/` outside a plan slot |
| `vault-skills` | a `.<harness>/skills/` directory exists in the vault |
| `secrets` | a file matches an AWS key, Anthropic key, private-key header, or `password:` line |
| `today-committed` | `today.md` is staged or tracked — it is a derived view |
| `shipped-status` | a file in `shipped/` lacks `status: shipped` |
| `broken-links` | a `[[wikilink]]` resolves to nothing (full scan only) |
| `orphans` | a `wiki/` page or project page has no inbound `[[wikilink]]` (full scan only) |

`broken-links` and `orphans` run only on a full scan, not in `--staged` mode — a brand-new project
page shows up there without blocking a commit.

## Notes

- **Never loosen a check to make a commit pass.** `git commit --no-verify` is the deliberate escape
  hatch; editing the script to stop noticing is not. If a check is genuinely wrong, fix the rule in
  `CLAUDE.md` first.
- To exempt a file from the credential scan, add its path to `SECRET_EXEMPT` in `vault-check.py`
  **with a comment saying why**. It ships empty on purpose.
- If you change the date format, `vault-check.py`'s `PRD_DATE` / `PRD_DATE_IN_PATH` regexes need
  updating too — otherwise `prd-purity` silently stops checking dates. `init-vault` handles this;
  a manual change must not forget it.
- `vault-check.py` needs Python 3 and nothing else. No dependencies, no venv.
- Scripts are POSIX-ish bash and handle both BSD (macOS) and GNU sed. Customize freely.
