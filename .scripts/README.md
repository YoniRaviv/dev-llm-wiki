# Scripts

Small bash helpers that operate on the vault. Run from the vault root.

| Script | What it does |
|---|---|
| `new-project.sh <slug>` | Copies `raw/projects/_template/` to `raw/projects/<slug>/` and stamps today's date into STATUS.md. |
| `new-journal.sh [DD-MM-YYYY]` | Creates `wiki/journal/<DATE>.md` from the daily-note template. Defaults to today. |
| `daily-ingest.sh` | Stub. Designed to be run on a cron schedule to auto-prepare the previous day's journal entry with Claude conversation summaries. Implement to suit your environment. |
| `install-launchd.sh` | macOS only. Installs a launchd job that runs `daily-ingest.sh` at 9:30am daily. |

## Notes

- All scripts are POSIX-ish bash and assume the vault root is one level up from `.scripts/`.
- `new-project.sh` handles both BSD (macOS) and GNU sed in-place editing.
- Scripts are intentionally minimal. Customize freely.
