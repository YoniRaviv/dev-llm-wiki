#!/usr/bin/env bash
# Scaffold a new project under raw/projects/ from the _template.
# Usage: .scripts/new-project.sh <slug>
# Example: .scripts/new-project.sh customer-portal

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <slug>" >&2
  echo "  slug must be lowercase kebab-case (e.g. customer-portal)" >&2
  exit 1
fi

SLUG="$1"

if [[ ! "$SLUG" =~ ^[a-z][a-z0-9-]*$ ]]; then
  echo "error: slug must be lowercase kebab-case (got: $SLUG)" >&2
  exit 1
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE="$ROOT/raw/projects/_template"
DEST="$ROOT/raw/projects/$SLUG"

if [[ ! -d "$TEMPLATE" ]]; then
  echo "error: template not found at $TEMPLATE" >&2
  exit 1
fi

if [[ -e "$DEST" ]]; then
  echo "error: $DEST already exists" >&2
  exit 1
fi

cp -R "$TEMPLATE" "$DEST"

TODAY=$(date +%d-%m-%Y)

# Portable in-place sed (macOS BSD sed vs GNU sed)
if sed --version >/dev/null 2>&1; then
  SED_INPLACE=(sed -i)
else
  SED_INPLACE=(sed -i '')
fi

"${SED_INPLACE[@]}" \
  -e "s|<project-slug>|$SLUG|g" \
  -e "s|updated: DD-MM-YYYY|updated: $TODAY|g" \
  -e "s|\\*\\*Last touched:\\*\\* DD-MM-YYYY|**Last touched:** $TODAY|g" \
  "$DEST/STATUS.md"

echo "Created raw/projects/$SLUG/"
echo "Next: open $DEST/STATUS.md and start filling in."
