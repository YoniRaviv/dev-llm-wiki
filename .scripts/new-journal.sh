#!/usr/bin/env bash
# Create today's journal page from the daily-note template if it doesn't exist.
# Usage: .scripts/new-journal.sh [DD-MM-YYYY]
# With no argument, defaults to today.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE="$ROOT/wiki/templates/daily-note.md"
JOURNAL_DIR="$ROOT/wiki/journal"

if [[ $# -ge 1 ]]; then
  DATE="$1"
  if [[ ! "$DATE" =~ ^[0-9]{2}-[0-9]{2}-[0-9]{4}$ ]]; then
    echo "error: date must be DD-MM-YYYY (got: $DATE)" >&2
    exit 1
  fi
else
  DATE=$(date +%d-%m-%Y)
fi

# Build a human-friendly display date (e.g. "Tuesday, 20 May 2026")
DAY=${DATE%%-*}
REST=${DATE#*-}
MONTH=${REST%%-*}
YEAR=${REST#*-}

if date -j -f "%d-%m-%Y" "$DATE" "+%A, %-d %B %Y" >/dev/null 2>&1; then
  DATE_DISPLAY=$(date -j -f "%d-%m-%Y" "$DATE" "+%A, %-d %B %Y")
else
  DATE_DISPLAY=$(date -d "$YEAR-$MONTH-$DAY" "+%A, %-d %B %Y" 2>/dev/null || echo "$DATE")
fi

DEST="$JOURNAL_DIR/$DATE.md"

if [[ -e "$DEST" ]]; then
  echo "$DEST already exists — nothing to do."
  exit 0
fi

if [[ ! -f "$TEMPLATE" ]]; then
  echo "error: template not found at $TEMPLATE" >&2
  exit 1
fi

mkdir -p "$JOURNAL_DIR"

sed -e "s|{{DATE}}|$DATE|g" -e "s|{{DATE_DISPLAY}}|$DATE_DISPLAY|g" "$TEMPLATE" > "$DEST"

echo "Created $DEST"
