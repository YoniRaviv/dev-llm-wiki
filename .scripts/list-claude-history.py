#!/usr/bin/env python3
"""
list-claude-history.py — enumerate Claude Code conversation history.

Scans both:
  ~/.claude/projects/                                          (CLI sessions)
  ~/Library/Application Support/Claude/local-agent-mode-sessions/   (desktop agent sessions)

and emits a JSON array of file metadata to stdout. Designed to be called once
by the `claude-history-ingest` skill so the LLM gets a full inventory in one
Bash invocation instead of triggering N separate Read permission prompts.

Each entry includes:
  path          absolute path
  size_bytes    file size
  mtime_iso     ISO-8601 mtime in UTC
  sha256        "sha256:<hex>" — the skip signal for the wiki manifest
  source_type   one of: claude_conversation, claude_memory, claude_audit_log,
                claude_session_metadata, claude_desktop_transcript
  claude_project_dir       (where applicable) the path-encoded dir name
  claude_project_decoded   best-effort decoded path
  session_id / session_started_at / cwd / title   (parsed from session metadata where present)

Usage:
  python3 .scripts/list-claude-history.py
  python3 .scripts/list-claude-history.py --since 01-04-2026
  python3 .scripts/list-claude-history.py --no-hash       # faster survey, no skip-detection
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

CLI_PROJECTS = Path.home() / ".claude" / "projects"
DESKTOP_SESSIONS = (
    Path.home() / "Library" / "Application Support" / "Claude" / "local-agent-mode-sessions"
)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def file_meta(path: Path, hash_files: bool) -> dict:
    st = path.stat()
    return {
        "path": str(path),
        "size_bytes": st.st_size,
        "mtime_iso": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
        "sha256": sha256_of(path) if hash_files else None,
    }


def decode_project_dir(name: str) -> str:
    # "-Users-name-Documents-projects-my-app" -> best-effort path.
    # The encoding is lossy: literal dashes in directory names collide with
    # path separators, so callers should prefer `cwd` from session metadata
    # when available.
    if name.startswith("-"):
        return "/" + name[1:].replace("-", "/")
    return name


def scan_cli(hash_files: bool) -> list:
    entries = []
    if not CLI_PROJECTS.is_dir():
        return entries

    for proj_dir in CLI_PROJECTS.iterdir():
        if not proj_dir.is_dir():
            continue
        decoded = decode_project_dir(proj_dir.name)

        # Conversation transcripts: *.jsonl at the project root
        for jsonl in proj_dir.glob("*.jsonl"):
            m = file_meta(jsonl, hash_files)
            m["source_type"] = "claude_conversation"
            m["claude_project_dir"] = proj_dir.name
            m["claude_project_decoded"] = decoded
            entries.append(m)

        # Memory files
        mem_dir = proj_dir / "memory"
        if mem_dir.is_dir():
            for md in mem_dir.glob("*.md"):
                m = file_meta(md, hash_files)
                m["source_type"] = "claude_memory"
                m["claude_project_dir"] = proj_dir.name
                m["claude_project_decoded"] = decoded
                entries.append(m)

    return entries


def scan_desktop(hash_files: bool) -> list:
    entries = []
    if not DESKTOP_SESSIONS.is_dir():
        return entries

    # Session metadata: local_*.json (not the directory variant)
    for meta_file in DESKTOP_SESSIONS.rglob("local_*.json"):
        if not meta_file.is_file():
            continue
        m = file_meta(meta_file, hash_files)
        m["source_type"] = "claude_session_metadata"
        try:
            data = json.loads(meta_file.read_text())
            m["session_id"] = data.get("sessionId")
            m["session_started_at"] = data.get("startedAt")
            m["cwd"] = data.get("cwd")
            m["title"] = data.get("title")
            m["model"] = data.get("model")
        except Exception as e:
            print(f"warn: could not parse {meta_file}: {e}", file=sys.stderr)
        entries.append(m)

    # Audit logs
    for audit in DESKTOP_SESSIONS.rglob("audit.jsonl"):
        m = file_meta(audit, hash_files)
        m["source_type"] = "claude_audit_log"
        entries.append(m)

    # Conversation transcripts under .claude/projects/ inside desktop sessions
    for jsonl in DESKTOP_SESSIONS.rglob("*.jsonl"):
        if jsonl.name == "audit.jsonl":
            continue
        if "/.claude/projects/" not in str(jsonl):
            continue
        m = file_meta(jsonl, hash_files)
        m["source_type"] = "claude_desktop_transcript"
        proj_dir = jsonl.parent
        m["claude_project_dir"] = proj_dir.name
        m["claude_project_decoded"] = decode_project_dir(proj_dir.name)
        entries.append(m)

    return entries


def parse_since(since_str: str) -> datetime:
    # Accept DD-MM-YYYY (default) or ISO-8601
    for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%m-%d-%Y"):
        try:
            return datetime.strptime(since_str, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    print(f"error: --since must be DD-MM-YYYY, YYYY-MM-DD, or MM-DD-YYYY (got: {since_str})", file=sys.stderr)
    sys.exit(2)


def main() -> int:
    p = argparse.ArgumentParser(description="Enumerate Claude history files for ingestion.")
    p.add_argument("--since", help="Only include files modified on/after this date")
    p.add_argument("--no-hash", action="store_true",
                   help="Skip SHA-256 (faster; manifest skip-detection won't work)")
    args = p.parse_args()

    hash_files = not args.no_hash

    entries = []
    try:
        entries.extend(scan_cli(hash_files))
        entries.extend(scan_desktop(hash_files))
    except PermissionError as e:
        print(f"error: permission denied while scanning ({e})", file=sys.stderr)
        return 1

    if args.since:
        since_dt = parse_since(args.since)
        entries = [
            e for e in entries
            if datetime.fromisoformat(e["mtime_iso"]) >= since_dt
        ]

    json.dump(entries, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
