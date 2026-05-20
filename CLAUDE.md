# Dev Brain Wiki — Schema & Workflow

This Obsidian vault is a personal dev knowledge base. `wiki/` is entirely LLM-maintained — you write it, the user reads it. `raw/` is mostly user-curated source material — you read it. The one exception is `raw/projects/`, where you may write into the lifecycle slots when asked (see "Working with raw/projects/" below).

This file is the operational contract. Treat it as authoritative. If anything below conflicts with a default behavior, follow this file.

## Directory Layout

```
wiki/
├── projects/      — one folder per project containing the project page + features/ + decisions/
│   └── <slug>.md
│   └── <slug>/
│       ├── features/  — one page per feature
│       └── decisions/ — architecture decision records for this project
├── patterns/      — reusable solutions discovered across work
├── technologies/  — tools and libraries
├── ideas/         — processed idea pages
├── sources/       — one summary page per ingested source (filename: DD-MM-YYYY-<slug>.md)
├── journal/       — daily notes (filename: DD-MM-YYYY.md); auto-created if daily-ingest is configured
├── templates/     — page templates; daily-note.md is the source for journal entries
├── index.md       — content catalog (READ THIS FIRST on every operation)
├── topics.md      — controlled vocabulary for the `topics:` frontmatter field
├── hot.md         — short-lived cache of active threads, recent activity, open loops
└── log.md         — append-only event log

raw/
├── articles/      — web-clipped articles
├── tweets/        — clipped tweets and threads
├── repos/         — clipped GitHub repos
├── ideas/         — raw idea dumps and rough notes
└── projects/      — one folder per project, all kebab-case slugs matching the wiki slug
    ├── _template/      — copy-paste skeleton; scaffold new projects with .scripts/new-project.sh
    └── <project-slug>/
        ├── STATUS.md         — user-curated quick-glance status; updated frequently
        ├── 00-idea.md        — initial spark / brief
        ├── 01-research.md    — research, competitive analysis, technical exploration (optional)
        ├── 02-prd.md         — what + why (or a design doc, for legacy projects)
        ├── 03-plan.md        — high-level how
        ├── kanban.md         — Obsidian Kanban for small tasks
        ├── features/         — one .md per feature, or a sub-folder for complex features
        ├── roadmaps/         — versioned roadmaps (v1.md, v2.md, ...)
        ├── notes/            — dated meeting/ad-hoc notes: DD-MM-YYYY-<topic>.md
        └── archive/          — superseded but worth keeping

.manifest.json     — ingest tracking ledger; records every source file ingested with hash, timestamp, and pages affected
.scripts/          — automation scripts; new-project.sh scaffolds a new raw/projects/<slug>/ from _template
.claude/skills/    — project-scoped skills the LLM may invoke
```

### Working with raw/projects/

`raw/` is user-curated source material. You only modify `raw/projects/` when:
- the user explicitly asks you to write a doc there (a feature plan, a status update, a research note),
- you are running `INGEST` and a source touches a project's lifecycle docs,
- the user asks to scaffold or restructure a project.

When writing into a project folder, respect the lifecycle slots: a feature plan goes to `features/<feature-slug>.md`, a dated meeting note goes to `notes/DD-MM-YYYY-<topic>.md`, a roadmap snapshot goes to `roadmaps/`. Never drop free-floating files at the project root unless they're spine docs (STATUS, 00–03, kanban) or an evergreen reference doc (rare). Legacy projects may have a design-spec doc filling the `02-prd.md` slot — that's expected.

## Operations

### INGEST

Triggered when the user says "ingest [file/path]" or drops a file in raw/.

1. Read the source file in full
2. Ask the user: "What should I emphasize from this?" — wait for 1-2 exchanges. While in this dialogue, run SURFACE: check if the new source overlaps `topics:` with existing wiki pages, and mention those overlaps so the user can flag connections.
3. Create `wiki/sources/DD-MM-YYYY-<slug>.md` (slug: lowercase kebab-case of title)
4. Read `wiki/index.md` — identify every page this source is relevant to
5. Update those pages: add/revise sections, strengthen or challenge existing claims, flag contradictions explicitly with a `> ⚠️ Contradiction: ...` blockquote
5b. For every `status: active` project this source affects: update its `Current Status` block. At minimum bump `Last touched`. If the source informs `Blocked on`, `Next up`, or `Open questions`, update those fields. If the source contradicts the current `Working on`, flag the contradiction with `> ⚠️ Contradiction: ...` and ask the user.
6. Create new pages if the source introduces a new pattern, technology, decision, or idea not yet in the wiki
6b. If the source carries a takeaway worth re-surfacing during future work (a gotcha, counterintuitive finding, benchmark, or "we should try X" idea), append one line to `wiki/hot.md` under `Recently Surfaced Lessons`: `- <one-line lesson> — see [[sources/<page>]]`. Optional and judgment-based.
7. Update `wiki/index.md` with any new pages (one line: `- [Title](subdir/page.md) — one-line description`)
8. Append to `wiki/log.md`: `## [DD-MM-YYYY] ingest | <source title>`

A single article will typically touch 5-15 pages. That is expected and correct.

### QUERY

Triggered when the user asks any question, or says "consult the brain on X."

1. Read `wiki/index.md` to map the space
2. Read all pages identified as relevant
3. Synthesize an answer with inline citations to wiki pages (e.g. "see [[decisions/async-state-management]]")
4. Offer to file the answer: "Should I write this back to the wiki?" — only if the synthesis is non-trivial (a comparison, decision analysis, discovered connection, or new synthesis)
5. If yes: write or update a wiki page with the content
6. Append to `wiki/log.md`: `## [DD-MM-YYYY] query | <short question>`

### SURFACE

Triggered automatically — no user command required. Runs when the conversation enters a new technical topic. Specifically:
- User pastes code touching a new subsystem.
- User mentions an external library, tool, or service not previously discussed in this session.
- User asks a design or architectural question.
- User starts a new feature or task.

Not on every message. Not on follow-up clarifications inside a topic.

Procedure:
1. Extract 1-3 candidate topics from the current turn.
2. Read `wiki/hot.md` (always loaded; cheap).
3. Grep `wiki/` for pages whose `topics:` frontmatter overlaps with candidates.
4. Score matches by topic overlap count + recency (pages with recent log entries score higher).
5. If at least one match has high confidence (≥2 topics overlap, page modified or referenced in last 90 days):
   - Cite up to 2 pages inline using `[[subdir/page]]` syntax.
   - One short sentence per citation framing the relevance.
   - Continue the response.
6. If matches are weak (single-topic, stale, low-confidence): silently skip.

Budgets:
- Max 2 inline citations per topic shift.
- Max 1 citation per page per conversation (don't repeat).
- Skip SURFACE when the user is mid-debug and just wants the bug fixed.
- Skip if a citation would only restate what the LLM already said.

Telemetry: when SURFACE fires, append to `wiki/log.md`:
`## [DD-MM-YYYY] surface | <topic> → [[page1]], [[page2]]`

### LINT

Triggered when the user says "lint the wiki."

Audit the entire wiki/ directory for:
- Contradictions between pages
- Stale claims superseded by newer sources (check source dates in frontmatter)
- Orphan pages: no other wiki page contains a `[[wikilink]]` pointing to them
- Concepts mentioned in 2+ pages but lacking their own dedicated page
- Decisions referenced in feature pages but not having a standalone decisions/ page
- Patterns appearing in 2+ features but not documented in patterns/
- Technologies mentioned repeatedly but not having a technologies/ page
- Gaps: topics where "we have no good source on X yet" — list them as suggestions
- Stale `Current Status`: any `status: active` project whose `Last touched` is >14 days old
- Unknown topics: any `topics:` entry not present in `wiki/topics.md`
- Near-duplicate topics: pairs in `topics.md` likely synonymous (e.g. `s3-uploads` vs `s3-storage`)
- Single-use topics: topics used on only one page (consolidation candidates)
- Non-DD-MM-YYYY date strings in any wiki page (frontmatter or content)
- Journal files not matching `DD-MM-YYYY.md` filename pattern

Output a markdown lint report. Fix what you can autonomously. Flag items needing user input with ❓.
Append to `wiki/log.md`: `## [DD-MM-YYYY] lint | <one-line summary>`

### BOOTSTRAP

One-time operation. Triggered once at initial setup.

1. Read all files in `raw/` recursively
2. Surface a one-paragraph summary per major source and ask: "What should I emphasize? Anything wrong or missing here?"
3. Generate wiki pages: projects/, features/, decisions/, patterns/, technologies/ from existing docs
4. Ingest articles in topic batches of 3-5; discuss between batches
5. Generate or update `wiki/index.md` with all created pages
6. Generate or seed `wiki/topics.md` based on the topics that surfaced during ingestion
7. Write first entries to `wiki/log.md`
8. Run a `LINT` pass and output the report

Bootstrap is supervised — stay in dialogue throughout.

## Entity Schemas

### Topics (controlled vocabulary)

Every wiki page carries a `topics:` array in frontmatter — 3-7 entries, lowercase kebab-case, noun phrases (not adjectives). Topics are drawn from the controlled vocabulary in `wiki/topics.md`. Adding a topic to any page requires appending it to `topics.md` in the same write. Topics are how SURFACE matches conversation context to wiki pages — keep the vocabulary tight.

### projects/ page

Frontmatter:
```yaml
---
name: [Project Name]
status: active | paused | archived
stack: [technology, technology]
topics: [topic-1, topic-2, topic-3]
started: DD-MM-YYYY
last_updated: DD-MM-YYYY
---
```

Required sections: Overview, Current Status, Architecture, Stack, Active Features, Key Decisions, Open Questions, Related Projects

**Current Status block (required):**

Kept short (5-15 lines). Updated whenever work touches the project (INGEST or manual update).

```markdown
## Current Status

**Phase:** <e.g., "Phase 2 — S3 storage">
**Last touched:** DD-MM-YYYY
**Working on:** <one line>
**Blocked on:** <one line + since DD-MM-YYYY> | none
**Next up:** <one line>
**Open questions:**
- <bullet>
- <bullet>
```

Field rules:
- `Last touched` is required; one of `Working on`, `Blocked on`, `Next up` must be populated.
- Other fields optional; omit empty.
- 5-15 lines total. If it grows past that, content belongs in a feature page or decision record.

### features/ page

Path: `wiki/projects/<project-slug>/features/<feature-slug>.md`

Frontmatter:
```yaml
---
project: project-slug
status: planned | in-progress | shipped | abandoned
topics: [topic-1, topic-2, topic-3]
started: DD-MM-YYYY
shipped: DD-MM-YYYY
---
```

Required sections: Summary, Context, Decisions Made, Implementation Notes, Related Patterns, Related Features

### decisions/ page

Path: `wiki/projects/<project-slug>/decisions/<decision-slug>.md`

Frontmatter:
```yaml
---
projects: [project-slug]
features: [feature-slug]
topics: [topic-1, topic-2, topic-3]
date: DD-MM-YYYY
status: active | superseded | deprecated
superseded_by:
---
```

Required sections: Context, Decision, Rationale, Alternatives Considered, Consequences, Superseded By

### patterns/ page

Frontmatter:
```yaml
---
used_in: [project-slug]
topics: [topic-1, topic-2, topic-3]
tags: [tag]
first_seen: DD-MM-YYYY
---
```

Required sections: Summary (1-2 sentences), When to Use, How It Works, Gotchas, Related Patterns, Sources

### technologies/ page

Frontmatter:
```yaml
---
type: library | framework | tool | service
used_in: [project-slug]
topics: [topic-1, topic-2, topic-3]
---
```

Required sections: What It Is, How We Use It, Gotchas, Resources

### ideas/ page

Frontmatter:
```yaml
---
status: exploring | parked | became-feature
related_projects: [project-slug]
related_patterns: [pattern-slug]
topics: [topic-1, topic-2, topic-3]
---
```

Required sections: The Idea, Why It's Interesting, Related Work, Open Questions, Next Steps

### sources/ page

Filename: `DD-MM-YYYY-<slug>.md`

Frontmatter:
```yaml
---
type: article | tweet | repo | doc
raw_path: raw/subdir/filename.md
topics: [topic-1, topic-2, topic-3]
date_ingested: DD-MM-YYYY
original_url:
---
```

Required sections: Summary, Key Takeaways, Wiki Pages Updated

### journal/ page

Filename: `DD-MM-YYYY.md`. Created manually with `.scripts/new-journal.sh`, or auto-created if daily-ingest is configured.

Frontmatter:
```yaml
---
date: DD-MM-YYYY
type: daily
---
```

Required sections: What I Worked On, Key Decisions, Claude Conversations, Research & Sources Ingested, Blockers / Open Questions, Notes

**Auto-fill behavior (only if daily-ingest is configured):** the script:
1. Creates the previous day's journal page if it doesn't exist
2. Finds all `.jsonl` conversation files modified that day in `~/.claude/projects/`
3. Extracts key work, decisions, and patterns; creates/updates wiki pages as needed
4. Fills in the `Claude Conversations` and `Research & Sources Ingested` sections with [[wikilinks]]
5. Updates `.manifest.json` and appends to `log.md`

If you implement daily-ingest, do not overwrite `What I Worked On`, `Key Decisions`, `Blockers`, or `Notes` — those are user-filled. Append only to the two auto-filled sections.

### hot.md (cache, not a wiki page)

Path: `wiki/hot.md`. Loaded by the LLM before any QUERY or SURFACE operation. Always consulted first.

Required structure:

```markdown
---
title: Hot Cache
updated: DD-MM-YYYY
---

## Active Threads
- **<project>** — one-line state. ([[projects/<slug>]])

## Recent Activity
- **DD-MM-YYYY — <event title>** — 1-3 sentence summary.

## Open Loops
- <thing waiting on something>, since DD-MM-YYYY. Owner: <user/external>. ([[projects/<slug>]] or [[features/<slug>]])

## Recently Surfaced Lessons
- <one-line lesson> — see [[sources/<page>]]
```

Maintenance rules:
- INGEST appends to `Recent Activity`; rotates oldest out when count exceeds 10.
- Any update touching a project's `Current Status` updates the corresponding `Active Threads` line. If no line exists yet (newly active project), add one.
- `Open Loops` is auto-aggregated by INGEST and LINT from `Blocked on` fields across all `status: active` project pages.
- `Recently Surfaced Lessons` is populated by INGEST step 6b. LLM-only, no hand-curated additions.
- Keep `Recently Surfaced Lessons` to ~5 entries; rotate oldest out.

## Naming Conventions

- All filenames: lowercase kebab-case
- Source files: `DD-MM-YYYY-<slug>.md`
- Journal files: `DD-MM-YYYY.md`
- Internal wiki links: Obsidian wikilinks `[[subdir/page]]` (no .md, relative to wiki/)
- Index links: standard markdown `[Title](subdir/page.md)` (relative to wiki/)

## Cross-Linking Rules

Every page must be reachable from at least one other wiki page (no orphans):
- project page → its features (Active Features) and key decisions (Key Decisions)
- feature page → its decisions (Decisions Made) and patterns (Related Patterns)
- decision page → all projects and features that use it
- pattern page → features that use it and sources that introduced it
- source page → all wiki pages it updated (Wiki Pages Updated)

When you create a new page: immediately add it to `wiki/index.md` and link to it from at least one existing page.
