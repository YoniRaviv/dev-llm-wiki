# claude-dev-wiki

A personal dev knowledge base for builders, maintained by an LLM (Claude Code, Cursor, etc.) and read by you. You drop sources into `raw/`, the LLM distills them into `wiki/`, and over time the wiki becomes a queryable second brain that informs every future task.

The contract for how the LLM operates is in [`CLAUDE.md`](./CLAUDE.md). That file is loaded automatically on every Claude Code session opened in this directory.

## What's in here

```
.
├── CLAUDE.md            ← workflow contract for the LLM (loaded automatically)
├── wiki/                ← LLM-maintained knowledge base (you read, LLM writes)
│   ├── index.md         ← content catalog — LLM reads this first on every op
│   ├── topics.md        ← controlled vocabulary for topic frontmatter
│   ├── hot.md           ← short-lived "what's live right now" cache
│   ├── log.md           ← append-only event log
│   ├── templates/       ← one template per entity type
│   ├── projects/        ← project pages + per-project features/ and decisions/
│   ├── patterns/        ← reusable cross-project patterns
│   ├── technologies/    ← libraries, frameworks, tools you use
│   ├── ideas/           ← processed idea pages
│   ├── sources/         ← one summary per ingested article/tweet/repo
│   └── journal/         ← daily notes (DD-MM-YYYY.md)
├── raw/                 ← user-curated sources (you write, LLM reads)
│   ├── articles/        ← web clippings
│   ├── tweets/          ← tweets & threads
│   ├── repos/           ← GitHub repo notes
│   ├── ideas/           ← raw idea dumps
│   └── projects/        ← project lifecycle docs (one folder per project)
│       └── _template/   ← skeleton copied by .scripts/new-project.sh
├── .scripts/            ← automation: new-project.sh, new-journal.sh, etc.
├── .claude/skills/      ← project-scoped skills the LLM can invoke
└── .manifest.json       ← ingest ledger (sources processed, hashes, timestamps)
```

## Getting started

### Option 1 — Clone as-is (fastest)

```sh
git clone <this-repo> my-wiki
cd my-wiki
# Open in Claude Code
claude
```

The wiki is empty and ready for ingestion. Drop your first source into `raw/articles/` (or any `raw/` subdir) and ask Claude to `ingest <path>`.

### Option 2 — Personalize first

After cloning, ask Claude:

> "Set up this wiki for me. Ask me about my stack, the kinds of projects I work on, and seed `wiki/topics.md` with starter topics that fit."

Claude will walk you through personalization and seed the topic vocabulary.

## Core workflow

Take a project from idea → ship:

1. **Capture** — drop an idea into `raw/ideas/<slug>.md`, or scaffold a full project with `.scripts/new-project.sh <slug>`. This creates `raw/projects/<slug>/` with lifecycle slots (`00-idea.md`, `01-research.md`, `02-prd.md`, `03-plan.md`, plus `features/`, `notes/`, `roadmaps/`).
2. **Research** — clip articles, tweets, and repos into `raw/`. Ask Claude to `ingest <path>`. Each ingest distills the source into `wiki/sources/` and weaves it through existing project/pattern/technology pages.
3. **PRD & plan** — fill `02-prd.md` and `03-plan.md`. Or, write them in conversation with Claude and ask it to file them.
4. **Plan features** — one file per feature in `raw/projects/<slug>/features/`. When you finish a feature plan, ask Claude to mirror it into `wiki/projects/<slug>/features/`.
5. **Build & ship** — work in your code repo. Use Claude there too; this wiki travels with you because Claude can `ingest` from anywhere.
6. **Reflect** — Claude's `QUERY` op pulls relevant past decisions, patterns, and gotchas into every new task. Old knowledge surfaces automatically (the `SURFACE` op).

## Operations

These are the five operations Claude knows about (full spec in `CLAUDE.md`):

| Op | Trigger | What it does |
|---|---|---|
| **INGEST** | "ingest `<file>`" | Distills a raw source into `wiki/sources/<page>.md` and updates every wiki page it touches. |
| **QUERY** | Any question, or "consult the brain" | Reads `wiki/index.md` + relevant pages, synthesizes an answer with citations, optionally writes the answer back. |
| **SURFACE** | Automatic on topic shift | Cites relevant past wiki pages mid-conversation, without being asked. |
| **LINT** | "lint the wiki" | Audits the whole wiki for contradictions, orphans, gaps, stale claims. |
| **BOOTSTRAP** | First-time setup, supervised | Reads all of `raw/`, generates initial wiki structure, discusses with you. |

## Skills

`.claude/skills/` is where project-scoped skills live. It's empty by default. Add skills as you go — research, ingest-url, wiki-capture, etc. See `.claude/skills/README.md` for the conventions.

## Adding to it

This template is the starting point, not the destination. Expect to:

- Tune `CLAUDE.md` to your taste (e.g. add a new operation, change the entity schemas, add new directories).
- Build out `wiki/topics.md` over the first few weeks — that's how SURFACE matches conversation to pages.
- Add skills to `.claude/skills/` as you find workflows you want to automate.
- Customize `.scripts/` for your environment (especially if you want daily-ingest to actually run on a schedule).

The wiki becomes more valuable the more you feed it. The first month is mostly investment; after that it pays you back on every task.
