#!/usr/bin/env bash
# STUB — implement to fit your environment.
#
# Purpose: a daily cron-style job that prepares yesterday's journal entry and
# (optionally) auto-fills it with a summary of the previous day's Claude Code
# conversations and any sources you ingested.
#
# Typical responsibilities:
#   1. Create yesterday's wiki/journal/<DD-MM-YYYY>.md if missing (use new-journal.sh).
#   2. Find Claude Code .jsonl session files modified that day under ~/.claude/projects/.
#   3. Summarize what you worked on, key decisions, and patterns surfaced.
#   4. Append [[wikilinks]] to the journal page's "Claude Conversations" and
#      "Research & Sources Ingested" sections (do NOT overwrite the user-filled
#      sections).
#   5. Update .manifest.json and append an entry to wiki/log.md.
#
# Install on macOS:
#   See .scripts/install-launchd.sh for a launchd plist that runs this daily at 9:30am.
#
# Install on Linux:
#   Add a crontab entry like:
#     30 9 * * * /absolute/path/to/.scripts/daily-ingest.sh >> /absolute/path/to/.scripts/daily-ingest.log 2>&1
#
# Implementation hints:
#   - The hard part is steps 2-3. Easiest path: shell out to `claude` with a
#     headless prompt that takes yesterday's .jsonl paths and emits the journal
#     bullet list as stdout, then sed it into the journal page.
#   - Keep the script idempotent. If it runs twice in a day, it should not
#     duplicate entries — check the journal page before appending.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "[$(date +%Y-%m-%dT%H:%M:%S)] daily-ingest stub — not yet implemented for this vault."
echo "  Vault root: $ROOT"
echo "  Edit $ROOT/.scripts/daily-ingest.sh to enable."
exit 0
