#!/usr/bin/env bash
# Install this vault's skills globally, so they work from any directory.
#
#   global-skills/*      -> ~/.claude/skills/
#   scheduled-tasks/*    -> ~/.claude/scheduled-tasks/
#
# {{VAULT_PATH}} and {{CLAUDE_PROJECTS}} are substituted with real paths on the way in,
# which is why the skills must be installed rather than read in place.
#
# Usage: .scripts/install-global-skills.sh
# Re-run safely, and re-run after moving the vault or changing the date format —
# existing copies are overwritten.

set -euo pipefail

VAULT="$(cd "$(dirname "$0")/.." && pwd)"
CLAUDE_PROJECTS="$HOME/.claude/projects"

install_tree() {
  local src="$1" dest_root="$2" label="$3"

  [[ -d "$src" ]] || { echo "no $label/ directory — skipping."; return 0; }

  local unit
  for unit in "$src"/*/; do
    [[ -d "$unit" ]] || continue
    local name dest
    name="$(basename "$unit")"
    dest="$dest_root/$name"

    # Walk the whole subtree — a skill may carry references/, scripts, or fixtures.
    local rel target
    while IFS= read -r rel; do
      target="$dest/$rel"
      mkdir -p "$(dirname "$target")"
      sed -e "s|{{VAULT_PATH}}|$VAULT|g" \
          -e "s|{{CLAUDE_PROJECTS}}|$CLAUDE_PROJECTS|g" \
          "$unit$rel" > "$target"
    done < <(cd "$unit" && find . -type f ! -name '.DS_Store' | sed 's|^\./||')

    echo "Installed: $name -> $dest"
  done
}

install_tree "$VAULT/global-skills"   "$HOME/.claude/skills"          "global-skills"
install_tree "$VAULT/scheduled-tasks" "$HOME/.claude/scheduled-tasks" "scheduled-tasks"

echo
echo "Done. Vault path baked in: $VAULT"
echo "Skills are now available in every Claude Code session."
