# Claude Code Data Format — Reference

Detailed structure of the files this skill reads. Loaded only when needed for parsing edge cases.

## Projects Directory

`~/.claude/projects/` — one directory per project the user has opened with Claude Code. Directory names encode the absolute path:

```
/Users/name/Documents/projects/my-app  →  -Users-name-Documents-projects-my-app
```

Path recovery: replace leading `-` with `/`, then map remaining `-` to `/` cautiously (literal dashes in directory names complicate this). The `cwd` field in session/conversation data gives you the canonical path — prefer that over decoding.

## Conversation JSONL

Located at `~/.claude/projects/<project-dir>/<session-uuid>.jsonl` and at `<desktop-session-path>/.claude/projects/<project-dir>/<uuid>.jsonl`. Same format for both.

Each line is one event. Relevant event types:

| `type`                  | What it is                  | Worth reading? |
| ----------------------- | --------------------------- | -------------- |
| `user`                  | User message                | Yes — what the user asked/said |
| `assistant`             | Assistant response          | Yes — extract `text` blocks from content |
| `progress`              | Tool execution progress     | No — internal plumbing |
| `file-history-snapshot` | File state at session start | No — file listings only |

### User message structure

```json
{
  "type": "user",
  "message": { "role": "user", "content": "the user's message" },
  "timestamp": "2026-03-15T10:30:00.000Z",
  "sessionId": "uuid",
  "cwd": "/Users/name/Documents/projects/my-app"
}
```

### Assistant message structure

```json
{
  "type": "assistant",
  "message": {
    "role": "assistant",
    "content": [
      { "type": "thinking", "text": "internal reasoning (skip)" },
      { "type": "text", "text": "The visible response" },
      { "type": "tool_use", "id": "...", "name": "Read", "input": { "file_path": "..." } }
    ]
  },
  "timestamp": "2026-03-15T10:30:05.000Z"
}
```

**Extraction strategy**: pull only `text` blocks from assistant content arrays. `thinking` blocks are internal reasoning; `tool_use` blocks are mechanical — neither carries wiki-worthy knowledge directly (the audit log captures tool calls better).

## Memory Files

Located at `~/.claude/projects/<project-dir>/memory/`. Each has YAML frontmatter:

```markdown
---
name: descriptive-name
description: one-line summary used for relevance matching
type: user | feedback | project | reference
---

The memory content.
```

| Type        | Contains                                 | Wiki value for this skill |
| ----------- | ---------------------------------------- | ------------------------- |
| `user`      | User's role, preferences, expertise      | Low — stays in memory |
| `feedback`  | Workflow corrections and confirmations   | Medium — may become `patterns/` pages |
| `project`   | Active work, goals, decisions, deadlines | **High — directly informs project progress updates** |
| `reference` | Pointers to external resources           | Low-medium — may inform `sources/` or `technologies/` |

`MEMORY.md` in each memory directory is an index. Read it first to triage which individual files are worth reading.

## Session Metadata

`~/.claude/sessions/<pid>.json`:

```json
{
  "pid": 12345,
  "sessionId": "uuid",
  "cwd": "/Users/name/Documents/projects/my-app",
  "startedAt": "2026-03-15T10:30:00.000Z",
  "kind": "interactive",
  "entrypoint": "cli"
}
```

Useful for building a timeline of when the user worked on what.

## Global History

`~/.claude/history.jsonl` — append-only log of all sessions across projects. Use only for timeline reconstruction if you need to span sessions.

## Desktop App: Local Agent Mode Sessions

Path: `~/Library/Application Support/Claude/local-agent-mode-sessions/<outer-uuid>/<inner-uuid>/`

Three files per session:

### `local_<session-uuid>.json` — session metadata

JSON with `sessionId`, `cwd`, `startedAt`, `model`, `title`. Read first to contextualize.

### `audit.jsonl` — tool-call record

Each line:

```json
{
  "type": "tool_call",
  "toolName": "Bash",
  "input": { "command": "npm test" },
  "output": "…",
  "timestamp": "2026-04-10T14:22:00Z",
  "sessionId": "…"
}
```

What to extract:
- **File access patterns** — files repeatedly Read/Edited reveal the project's high-value files.
- **Shell command patterns** — recurring Bash commands reveal build/test/deploy workflows.
- **Tool call sequences** — recurring patterns (e.g., Read → Edit → Bash) reveal workflow templates.
- **Error patterns** — failed tool calls reveal pain points and rough edges.
- **MCP tool calls** — reveal which external services the project integrates with.

What to skip:
- Routine one-off file reads (config files).
- Verbose tool outputs (stack traces, logs) — summarize the error class, never copy verbatim.
- Anything that looks like secrets, tokens, credentials.

### `.claude/projects/<encoded-name>/<uuid>.jsonl` — conversation transcript

Same format as CLI JSONL above.

## Processing Order (recommended)

1. **`MEMORY.md` indexes** — fast triage.
2. **`project` memory files** — directly informs Step 4 (project progress detection).
3. **Other memory files** (`feedback`, `reference`) — distill into patterns/sources if warranted.
4. **Conversation JSONL** — rich but verbose; process selectively, prioritize by recency and project relevance.
5. **Audit logs** — pair with transcripts where available; alone, useful only for project-internal command patterns.
6. **Session metadata** — only if you need timeline context for confidence scoring on progress signals.
