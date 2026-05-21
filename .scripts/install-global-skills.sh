#!/usr/bin/env bash
# Copy skills from global-skills/ to ~/.claude/skills/, substituting {{VAULT_PATH}}
# with the absolute path of this repo so they work from any directory.
#
# Usage: .scripts/install-global-skills.sh
# Re-run safely — existing skills are overwritten with the latest version.

set -euo pipefail

VAULT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$VAULT/global-skills"
DEST="$HOME/.claude/skills"

if [[ ! -d "$SRC" ]]; then
  echo "No global-skills/ directory found. Nothing to install."
  exit 0
fi

mkdir -p "$DEST"

for skill_dir in "$SRC"/*/; do
  skill_name="$(basename "$skill_dir")"
  dest_dir="$DEST/$skill_name"
  mkdir -p "$dest_dir"

  for src_file in "$skill_dir"*; do
    [[ -f "$src_file" ]] || continue
    dest_file="$dest_dir/$(basename "$src_file")"
    sed "s|{{VAULT_PATH}}|$VAULT|g" "$src_file" > "$dest_file"
  done

  echo "Installed: $skill_name → $dest_dir"
done

echo
echo "Done. Skills are now available in every Claude Code session."
echo "Vault path baked in: $VAULT"
