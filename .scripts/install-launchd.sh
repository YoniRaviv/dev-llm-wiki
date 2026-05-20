#!/usr/bin/env bash
# Install a macOS launchd job that runs .scripts/daily-ingest.sh at 9:30am daily.
# Usage: .scripts/install-launchd.sh
# Uninstall: launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.user.dev-wiki.daily-ingest.plist

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT="$ROOT/.scripts/daily-ingest.sh"
LOG="$ROOT/.scripts/daily-ingest.log"
PLIST="$HOME/Library/LaunchAgents/com.user.dev-wiki.daily-ingest.plist"
LABEL="com.user.dev-wiki.daily-ingest"

if [[ ! -x "$SCRIPT" ]]; then
  chmod +x "$SCRIPT"
fi

mkdir -p "$(dirname "$PLIST")"

cat > "$PLIST" <<PLIST_EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>$SCRIPT</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key><integer>9</integer>
    <key>Minute</key><integer>30</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>$LOG</string>
  <key>StandardErrorPath</key>
  <string>$LOG</string>
  <key>RunAtLoad</key>
  <false/>
</dict>
</plist>
PLIST_EOF

# Reload if already installed
if launchctl print "gui/$(id -u)/$LABEL" >/dev/null 2>&1; then
  launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
fi
launchctl bootstrap "gui/$(id -u)" "$PLIST"

echo "Installed launchd job: $LABEL"
echo "  plist:  $PLIST"
echo "  script: $SCRIPT"
echo "  log:    $LOG"
echo
echo "To uninstall:"
echo "  launchctl bootout gui/\$(id -u) $PLIST && rm $PLIST"
