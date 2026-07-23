# claude-dev-wiki

> **Seed idea:** [Andrej Karpathy's "vibe-coding" gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — the original prompt for keeping an LLM-maintained wiki alongside your code.

A personal dev knowledge base for builders, maintained by an LLM (Claude Code, Cursor, etc.) and read by you. You drop sources into `raw/`, the LLM distills them into `wiki/`, and over time the wiki becomes a queryable second brain that informs every future task.

The contract for how the LLM operates lives in [`CLAUDE.md`](./CLAUDE.md) — loaded automatically on every Claude Code session opened in this directory.

## Philosophy

Two surfaces, one knowledge graph:

- **`raw/`** is **user-curated source material** — articles you clipped, projects you're working on, ideas you're exploring. You write here. The LLM reads.
- **`wiki/`** is **LLM-maintained distillation** — patterns, decisions, technologies, sources, projects, ideas. The LLM writes here. You read.

The flow is one-way: stuff comes in through `raw/`, gets distilled into `wiki/`, and stays there as connected, citation-backed knowledge. Future questions get answered by reading the wiki — not by re-googling.

## The workflow — CRAFTED

Go deeper: https://yonathan-raviv.dev/thoughts/how-i-work-with-claude/

Every project moves through seven phases from spark to ship. Some happen in this vault (planning + records), others happen in your actual code repo (the work). The vault stores the **plan** and the **distilled result**; the project repo is where the code lives.

```mermaid
flowchart LR
    C["💡 Conceive"]:::vault
    R["🔍 Research"]:::vault
    A["📋 Architect"]:::vault
    F["🗺️ Frame"]:::repo
    T["🔨 Try"]:::repo
    E["✅ Evaluate"]:::repo
    D["🚀 Deliver"]:::done

    C --> R --> A --> F --> T --> E --> D

    classDef vault fill:#dbeafe,stroke:#93c5fd,color:#1e3a8a
    classDef repo  fill:#fef3c7,stroke:#fcd34d,color:#78350f
    classDef done  fill:#d1fae5,stroke:#6ee7b7,color:#064e3b
```

> 🔵 **Blue** = Vault (plan it) · 🟡 **Yellow** = Project repo (do it) · 🟢 **Green** = Vault (record it)

### Phase mapping

| | Phase | Where | Artifact | What helps |
|---|---|---|---|---|
| **C** | **Conceive** | Vault | `raw/projects/<slug>/00-idea.md` | Manual capture — `.scripts/new-project.sh <slug>` scaffolds the folder. |
| **R** | **Research** | Vault | `wiki/ideas/<slug>.md` (or `raw/projects/<slug>/01-research.md`) | [`idea-deep-research`](https://github.com/YoniRaviv/claude-skills) *(marketplace)* — multi-round web search, landscape + honest verdict. |
| **A** | **Architect** | Vault | `raw/projects/<slug>/02-prd.md` | Manual — what + why. The [`to-prd`](https://github.com/mattpocock/skills) skill from [Matt Pocock's skills](https://github.com/mattpocock/skills) can draft a PRD from your current conversation context. Stress-test it with [`grill-me`](https://github.com/mattpocock/skills) before committing. |
| **F** | **Frame** | **Project repo** | `raw/projects/<slug>/features/*.md` (saved back to vault) + `03-plan.md` for the high-level | **Claude Code Plan Mode** (built-in, Shift+Tab) and **[`brainstorming`](https://github.com/obra/superpowers)** + **[`writing-plans`](https://github.com/obra/superpowers)** from the [superpowers](https://github.com/obra/superpowers) plugin. Stress-test the resulting plan with **[`grill-me`](https://github.com/mattpocock/skills)** from [Matt Pocock's skills](https://github.com/mattpocock/skills). Detailed feature/section plans get written in the project repo; the resulting feature files are saved into the vault so other skills (`wiki-promote-feature`, `claude-history-ingest`) can find them. |
| **T** | **Try** | **Project repo** | code, commits, PRs | [`claude-history-ingest`](https://github.com/YoniRaviv/claude-skills) *(marketplace)* passively tracks what you worked on, advances feature statuses, flags blockers. |
| **E** | **Evaluate** | **Project repo** | tests, debugging notes | Same — captured via the same Claude Code sessions. |
| **D** | **Deliver** | Vault | `wiki/projects/<slug>/features/<name>.md` + auto-created decision pages | [`wiki-promote-feature`](.claude/skills/wiki-promote-feature/) — lifts the working feature doc into the schema-compliant wiki page. |

The key split: **detailed work (Frame, Try, Evaluate) happens in your actual code repo**, not in the vault. The vault stores the early thinking (Conceive, Research, Architect), receives the feature plans during Frame, gets passive updates during Try and Evaluate (via `claude-history-ingest`), and captures the distilled result on Deliver.

After Deliver, the wiki becomes the lasting reference — citation-backed knowledge that future projects can consult via [`wiki-query`](.claude/skills/wiki-query/).

**Cross-cutting (any phase):** [`standup`](https://github.com/YoniRaviv/claude-skills) *(marketplace)* reassembles where you left off across every project into `wiki/today.md` each morning; [`meeting-prep`](https://github.com/YoniRaviv/claude-skills) *(marketplace)* carries a meeting through prep → live notes → summary as a single note in `raw/meetings/`. Both are day-to-day surfaces that sit alongside the CRAFTED pipeline rather than inside one phase.

## Companion tools (outside the template)

The vault bundles **8 project-scoped skills** (listed below) plus a handful of **marketplace skills** it references. The Frame phase and general planning are best done with external tools that aren't bundled here — the easiest way to get all of them, and the marketplace-referenced skills above, is my one-stop skills repo: **[`YoniRaviv/claude-skills`](https://github.com/YoniRaviv/claude-skills)**.

```sh
# In any Claude Code session:
/plugin marketplace add YoniRaviv/claude-skills
/plugin install yoni-skills@yoni-marketplace     # my own skills (idea-deep-research, claude-history-ingest, …)
/plugin install superpowers@yoni-marketplace     # brainstorming, writing-plans, TDD, systematic-debugging
/plugin install ui-ux-pro-max@yoni-marketplace   # UI/UX design intelligence
```

The planning-side tools this vault leans on:

- **[Claude Code Plan Mode](https://docs.claude.com/en/docs/claude-code/overview)** — built into Claude Code. Press **Shift+Tab** in a session to switch into plan mode; Claude proposes a step-by-step plan you approve before any code is written. Best for "I know roughly what to do, let me lock in the steps before I touch files."
- **[`brainstorming`](https://github.com/obra/superpowers/tree/main/skills/brainstorming)** *(superpowers)* — explores requirements and design before implementation. Use when the shape of the solution isn't clear yet.
- **[`writing-plans`](https://github.com/obra/superpowers/tree/main/skills/writing-plans)** *(superpowers)* — turns a spec into a multi-step implementation plan. Use after brainstorming when you have requirements but no concrete plan.
- **[`to-spec`](https://github.com/mattpocock/skills)** / **[`grill-me`](https://github.com/mattpocock/skills)** *(Matt Pocock, install via `npx skills add` — see the [marketplace README](https://github.com/YoniRaviv/claude-skills) section 3)* — draft a spec/PRD from a conversation, then get grilled on it until every branch is resolved. Useful in the **Architect** and **Frame** phases.

None of these are required to use this vault — they're the planning-side tools that pair naturally with the vault's record-side skills.

## What's in here

```
.
├── CLAUDE.md            ← workflow contract for the LLM (loaded automatically)
├── wiki/                ← LLM-maintained knowledge base (you read, LLM writes)
│   ├── index.md         ← content catalog — LLM reads this first on every op
│   ├── topics.md        ← controlled vocabulary for topic frontmatter
│   ├── hot.md           ← short-lived "what's live right now" cache
│   ├── today.md         ← daily "where I left off" surface (machine-written by the standup skill)
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
│   ├── meetings/        ← meeting notes (prep + summary), one per meeting — via meeting-prep skill
│   └── projects/        ← project lifecycle docs (one folder per project)
│       ├── _template/   ← skeleton copied by .scripts/new-project.sh
│       └── <slug>/
│           ├── STATUS.md          ← quick-glance status; updated frequently
│           ├── 00-idea.md         ← Conceive: initial spark
│           ├── 01-research.md     ← Research: landscape + verdict
│           ├── 02-prd.md          ← Architect: what + why
│           ├── 03-plan.md         ← Frame: high-level how
│           ├── kanban.md          ← task board
│           ├── features/          ← one .md per feature
│           ├── roadmaps/          ← versioned roadmaps (v1.md, v2.md, …)
│           ├── notes/             ← dated meeting/ad-hoc notes
│           └── archive/           ← superseded docs worth keeping
├── global-skills/       ← skills to install globally (~/.claude/skills/) via install-global-skills.sh
│   └── send-to-wiki/    ← send feature plans & notes to the vault from any codebase
├── .scripts/            ← automation: new-project.sh, list-claude-history.py, etc.
├── .claude/skills/      ← 8 project-scoped skills bundled with the vault (+ more via the marketplace)
├── .manifest.json       ← ingest ledger (sources processed, hashes, timestamps)
└── .vault-meta.json     ← personalization config written by init-vault (one-time)
```

## Skills — when to use each

Skills come from two places:

- **Bundled** — 8 project-scoped skills under `.claude/skills/`, auto-discovered by Claude Code when you run it from this directory. They ship with the clone; no install step.
- **Marketplace** — a few workflows live in the [`YoniRaviv/claude-skills`](https://github.com/YoniRaviv/claude-skills) marketplace so they stay auto-updatable and shared with my other setups. Install once with `/plugin marketplace add YoniRaviv/claude-skills` → `/plugin install yoni-skills@yoni-marketplace`.

Trigger any skill by saying anything close to its listed phrases — you rarely have to call them by name.

### Bundled skills

**Lifecycle (per CRAFTED phase)**

| Skill | Trigger phrases | What it does |
|---|---|---|
| [`init-vault`](.claude/skills/init-vault/) | "set up my wiki", "initialize", "personalize" | **One-time** after cloning. Asks ~10 questions (date format, folder picks, topic seed, optional CLAUDE.md tweaks). Writes `.vault-meta.json`. Run once. |
| [`wiki-promote-feature`](.claude/skills/wiki-promote-feature/) | "promote feature X", "file the auth feature", "X is shipped — add to wiki" | **Deliver phase.** Lifts a finished feature plan from `raw/projects/<slug>/features/<name>.md` into the schema-compliant `wiki/projects/<slug>/features/<name>.md`. Surfaces decision and pattern candidates. |

**Knowledge (anytime)**

| Skill | Trigger phrases | What it does |
|---|---|---|
| [`wiki-ingest`](.claude/skills/wiki-ingest/) | "ingest `<path>`", "process this", "add to wiki" | Distill any source (article, tweet, repo, paper, screenshot, PDF) into `wiki/sources/`. Propagates through every relevant project/pattern/technology page. |
| [`wiki-query`](.claude/skills/wiki-query/) | Any question; "consult the brain", "what do I know about X" | Answer with citations. Cheap-first pipeline (index → section grep → full read). Index-only fast mode available. |
| [`weekly-digest`](.claude/skills/weekly-digest/) | "weekly digest", "what did I do this week", "stand-up" | Read-only synthesis across journals, projects, ingests. Writes to `wiki/digests/<range>.md` + inline output for Slack/email copy-paste. |

**Maintenance (periodic)**

| Skill | Trigger phrases | What it does |
|---|---|---|
| [`wiki-status`](.claude/skills/wiki-status/) | "what's the status", "delta", "wiki dashboard", "wiki insights" | Two modes: **delta** (what's pending to ingest, recommend append vs rebuild) and **insights** (graph analysis — hubs, bridges, fragmented topic clusters). |
| [`wiki-lint`](.claude/skills/wiki-lint/) | "lint the wiki", "audit", "what needs fixing" | 12-check health audit: orphans, broken links, missing frontmatter, stale projects, topic vocabulary issues, date format consistency, journal filename pattern. |
| [`cross-linker`](.claude/skills/cross-linker/) | "link my pages", "cross-reference", "find missing links" | Write-heavy companion to `wiki-lint` — actually inserts the missing `[[wikilinks]]`. Pair with lint: lint finds the problems, cross-linker fixes them. |

### Marketplace skills (install from [`YoniRaviv/claude-skills`](https://github.com/YoniRaviv/claude-skills))

| Skill | Trigger phrases | What it does |
|---|---|---|
| `idea-deep-research` | "research `<idea>`", "is X worth building", "what's out there for Y", "deep dive on Z" | **Research phase.** Multi-round web search → `## Idea Research` section in `wiki/ideas/<slug>.md`. Honest verdict required. |
| `claude-history-ingest` | "ingest my Claude history", "sync my work", "what have I been working on" | **Try / Evaluate phases.** Mines `~/.claude/projects/*` and desktop agent sessions. Two outputs: journal entries + **automatic project tracking** — advances feature statuses, flags blockers, surfaces decisions. |
| `standup` | "/standup", "where did I leave off", "start my day", "what's on my plate" | **Daily.** Reassembles cross-project state (hot.md, project STATUS, recent journals, PRs you owe) into `wiki/today.md`. On-demand; never hand-edit `today.md`. |
| `meeting-prep` | "/meeting-prep `<topic>`", "prep me for the X meeting", "summarize the meeting" | Carries a meeting through prep → live notes → summary as one note in `raw/meetings/`. |

> `global-skills/send-to-wiki` is a third skill category — installed **globally** (not via the marketplace) with `.scripts/install-global-skills.sh` so you can capture content into this vault from any other codebase. See [Getting started](#5-install-skills-marketplace--global).

## Prerequisites

### Required

| Tool | Why | Install |
|---|---|---|
| **[Claude Code](https://claude.ai/code)** | Runs all skills and wiki operations — the LLM that writes and queries the wiki | [claude.ai/code](https://claude.ai/code) |
| **[Obsidian](https://obsidian.md)** | The wiki UI — view, edit, navigate, and connect the markdown files. Graph view, backlinks, tag browser, and Dataview are how the wiki actually becomes browsable. | [obsidian.md](https://obsidian.md) → open the cloned repo root as a vault |
| **[Git](https://git-scm.com)** | Clone the repo, version-control your wiki | [git-scm.com](https://git-scm.com) |
| **bash / zsh** | Run `.scripts/` automation | Built into macOS and Linux. Windows: use [WSL](https://learn.microsoft.com/en-us/windows/wsl/install). |

Claude and Obsidian work together natively — both read and write the same plain markdown files. No API or special integration is needed.

### Optional

| Tool | Why | Install |
|---|---|---|
| **[Obsidian Web Clipper](https://obsidian.md/clipper)** | Browser extension that clips articles, tweets, and pages straight into `raw/articles/` (or `raw/tweets/`). Feeds the wiki without manual copy-paste. | [obsidian.md/clipper](https://obsidian.md/clipper) — Chrome, Firefox, Safari, Edge, Arc |
| **[Claude Code `obsidian` plugin](https://docs.claude.com/en/docs/claude-code/plugins)** + **[Obsidian Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api)** | Only needed if you want the `obsidian:obsidian-cli` skill — triggers Obsidian commands, runs JavaScript in the vault, reloads plugins. Wiki operations don't need this. | Install Local REST API in Obsidian (Community plugins → "Local REST API"), then install the obsidian plugin from the Claude Code marketplace |
| **[`YoniRaviv/claude-skills` marketplace](https://github.com/YoniRaviv/claude-skills)** | One-stop install for the marketplace skills this vault references (`idea-deep-research`, `claude-history-ingest`, `standup`, `meeting-prep`) plus `superpowers`, `ui-ux-pro-max`, and cherry-picked skills like `to-spec` / `grill-me`. | `/plugin marketplace add YoniRaviv/claude-skills` |

## Getting started

End-to-end walkthrough from zero to first ingest. Takes about 10 minutes.

### 1. Clone the repo

```sh
git clone https://github.com/YoniRaviv/dev-llm-wiki.git my-wiki
cd my-wiki
```

### 2. Open the folder as a vault in Obsidian

1. Launch Obsidian
2. Click **"Open folder as vault"** on the welcome screen (or **File → Open vault → Open folder as vault**)
3. Select the `my-wiki` directory you just cloned
4. Trust the vault when prompted

You'll see `wiki/` (the curated knowledge — what you read), `raw/` (the sources — what you drop in), and the support files. **The wiki/ folder is where you spend most of your time** — Obsidian's graph view and backlinks make the cross-links navigable.

### 3. Open the same folder in Claude Code

From inside the `my-wiki` directory:

```sh
claude
```

Claude Code auto-loads `CLAUDE.md` and the project-scoped skills under `.claude/skills/`. You should see the available skills listed when the session starts.

### 4. Personalize the vault

In the Claude session, say:

> **"Set up this wiki for me."**

This triggers the **`init-vault`** skill — walks you through ~10 questions (name, role, stack(s), date format, folder customization, journal opt-in, starter topics) and applies all the cascading edits across `CLAUDE.md`, `README.md`, templates, and scripts. End result: a vault that matches how you actually work. Writes `.vault-meta.json` so this only runs once.

### 5. Install skills (marketplace + global)

**Marketplace skills** — the lifecycle and daily skills that live outside this repo (`idea-deep-research`, `claude-history-ingest`, `standup`, `meeting-prep`) plus the planning plugins. In a Claude Code session:

```text
/plugin marketplace add YoniRaviv/claude-skills
/plugin install yoni-skills@yoni-marketplace
/plugin install superpowers@yoni-marketplace
```

**Global capture skill** — installs `global-skills/send-to-wiki` to `~/.claude/skills/` with your vault path baked in:

```sh
.scripts/install-global-skills.sh
```

After this, from **any project codebase** you can say "send to wiki" / "save to vault" and Claude will write the content to the right lifecycle slot in this vault without switching directories. Re-run any time to update.

> The 8 skills under `.claude/skills/` need no install — Claude Code auto-discovers them when you run it from the vault directory.

### 6. Try your first ingest

Drop a test source into `raw/articles/`. For example, save any article as markdown:

```sh
echo "# Test article\n\nA short note about something interesting." > raw/articles/test.md
```

Back in Claude, say:

> **"ingest raw/articles/test.md"**

Claude reads the source, asks you what to emphasize, then creates:
- A summary page at `wiki/sources/DD-MM-YYYY-test.md`
- Updates to `wiki/index.md` and `wiki/log.md`
- New or updated pages anywhere in `wiki/` the source is relevant to

Verify in Obsidian: open `wiki/sources/` — you should see the new file with citations linking back to other pages.

You're set up. From here, [start a real project](#starting-a-new-project--the-crafted-walkthrough) or just keep dropping sources into `raw/` and asking Claude to ingest them.

## Setting up daily journal ingest (optional)

`daily-ingest.sh` is a scheduled script that automatically creates yesterday's journal page and populates it with a summary of your Claude Code sessions. Without it, you run `claude-history-ingest` manually whenever you want a sync.

The script ships as a **stub** — you need to implement steps 2–4 (reading `.jsonl` files, summarizing, writing back to the journal). The comments inside explain the approach. Once implemented:

**macOS — one command:**

```sh
.scripts/install-launchd.sh
```

Installs a launchd plist that runs `daily-ingest.sh` at 9:30am every day. Logs go to `.scripts/daily-ingest.log`.

To uninstall:
```sh
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.user.dev-wiki.daily-ingest.plist && \
  rm ~/Library/LaunchAgents/com.user.dev-wiki.daily-ingest.plist
```

**Linux — add a crontab entry:**

```sh
crontab -e
# add:
30 9 * * * /absolute/path/to/.scripts/daily-ingest.sh >> /absolute/path/to/.scripts/daily-ingest.log 2>&1
```

If you don't want to implement the script, the `claude-history-ingest` skill does the same thing interactively — ask Claude "ingest my Claude history" any time.

## Starting a new project — the CRAFTED walkthrough

```sh
.scripts/new-project.sh my-new-project
```

Creates `raw/projects/my-new-project/` from the template with stamped dates. Then walk the phases:

1. **C — Conceive**: fill `00-idea.md`.
2. **R — Research**: ask Claude to `research my-new-project` → `idea-deep-research` produces a `## Idea Research` section in `wiki/ideas/<slug>.md` (or `01-research.md` inside the project).
3. **A — Architect**: write `02-prd.md` manually (what + why) — or use [`to-spec`](https://github.com/YoniRaviv/claude-skills) to draft it from a brainstorming conversation, then stress-test with [`grill-me`](https://github.com/YoniRaviv/claude-skills).
4. **F — Frame**: in your code repo, use Claude Code Plan Mode (Shift+Tab) or `brainstorming` + `writing-plans` from superpowers. Stress-test with [`grill-me`](https://github.com/mattpocock/skills). Save the resulting feature plans back into `raw/projects/my-new-project/features/<feature>.md`.
5. **T — Try**: build in your code repo. `claude-history-ingest` tracks progress.
6. **E — Evaluate**: test in your code repo. Same tracker.
7. **D — Deliver**: when a feature ships, ask Claude to `promote-feature <name>` → produces `wiki/projects/my-new-project/features/<name>.md` plus any decision/pattern pages worth keeping.

In between, periodically:

- `standup` at the start of the day to reassemble where you left off into `wiki/today.md`.
- `meeting-prep <topic>` before a meeting, then "summarize the meeting" after.
- `ingest <path>` to add sources you've clipped.
- `lint the wiki` + `cross-linker` to keep the graph healthy.
- `weekly-digest` for a Friday recap.

## Adding to it

This template is the starting point, not the destination. Expect to:

- Tune `CLAUDE.md` to your taste (add an operation, change schemas, add directories).
- Build out `wiki/topics.md` over the first few weeks — that's how SURFACE matches conversation to pages.
- Add or revise skills in `.claude/skills/` as you find workflows you want to automate.
- Customize `.scripts/` for your environment (especially if you want `daily-ingest.sh` to actually run on a schedule).

The wiki becomes more valuable the more you feed it. The first month is mostly investment; after that it pays you back on every task.
