#!/usr/bin/env bash
# Installs the vault pre-commit gate. Re-runnable.
#
# Resolves the hooks directory through git rather than assuming `.git/hooks` — in a
# worktree `.git` is a file, and with core.hooksPath set the real directory is elsewhere.
# Writing to the wrong place leaves a hook that looks installed and never runs.
set -euo pipefail

VAULT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

git -C "$VAULT" rev-parse --git-dir >/dev/null 2>&1 || {
  echo "error: $VAULT is not a git repository — run 'git init' first." >&2
  exit 1
}

if HOOKS_PATH="$(git -C "$VAULT" config --get core.hooksPath 2>/dev/null)" && [[ -n "$HOOKS_PATH" ]]; then
  case "$HOOKS_PATH" in
    /*) HOOKS="$HOOKS_PATH" ;;
    *)  HOOKS="$VAULT/$HOOKS_PATH" ;;
  esac
  echo "note: core.hooksPath is set — installing to $HOOKS"
else
  HOOKS="$(cd "$VAULT" && git rev-parse --path-format=absolute --git-path hooks)"
fi

mkdir -p "$HOOKS"

cat > "$HOOKS/pre-commit" <<'HOOK'
#!/usr/bin/env bash
# Vault structural gate. Hard fail — `git commit --no-verify` is the only escape.
VAULT="$(git rev-parse --show-toplevel)"
python3 "$VAULT/.scripts/vault-check.py" --staged --quiet || {
  echo
  echo "  commit blocked by vault-check."
  echo "  fix the above, or run 'git commit --no-verify' deliberately."
  exit 1
}
exit 0
HOOK

chmod +x "$HOOKS/pre-commit"
echo "installed: $HOOKS/pre-commit"
