#!/usr/bin/env bash
# Scaffold a new project under projects/ from .templates/project/.
# Usage: .scripts/new-project.sh <slug>
# Example: .scripts/new-project.sh customer-portal
#
# Creates only what the whitelist allows, with `tracker: none` — so the plan slots
# (03-plan.md, roadmaps/, features/) are legal. Create them when you have a plan.

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
TEMPLATE="$ROOT/.templates/project"
PAGE="$ROOT/projects/$SLUG.md"
DEST="$ROOT/projects/$SLUG"

if [[ ! -d "$TEMPLATE" ]]; then
  echo "error: template not found at $TEMPLATE" >&2
  exit 1
fi

if [[ -e "$PAGE" || -e "$DEST" ]]; then
  echo "error: projects/$SLUG already exists" >&2
  exit 1
fi

TODAY=$(date +%d-%m-%Y)

# Portable in-place sed (macOS BSD sed vs GNU sed)
if sed --version >/dev/null 2>&1; then
  SED_INPLACE=(sed -i)
else
  SED_INPLACE=(sed -i '')
fi

mkdir -p "$DEST/notes" "$DEST/assets"
touch "$DEST/notes/.gitkeep" "$DEST/assets/.gitkeep"

cp "$TEMPLATE/page.md"       "$PAGE"
cp "$TEMPLATE/00-idea.md"    "$DEST/00-idea.md"
cp "$TEMPLATE/02-prd.md"     "$DEST/02-prd.md"

"${SED_INPLACE[@]}" \
  -e "s|<project-slug>|$SLUG|g" \
  -e "s|started: DD-MM-YYYY|started: $TODAY|g" \
  "$PAGE"

cat <<EOF
Created:
  projects/$SLUG.md          project page — tracker: none
  projects/$SLUG/00-idea.md  yours to write
  projects/$SLUG/02-prd.md   what + why (never how/when)
  projects/$SLUG/notes/      dated notes
  projects/$SLUG/assets/     diagrams, exports

Optional, legal while tracker is none:
  03-plan.md · roadmaps/ · features/
Also available:
  01-research.md · shipped/   (see .templates/project/ for skeletons)

Next:
  1. Fill in 00-idea.md.
  2. Add projects/$SLUG.md to wiki/index.md and link it from one wiki page —
     until then vault-check reports it under 'orphans'. That is expected for a
     brand-new project, and it does not block a commit.
EOF
