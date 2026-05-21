---
name: wiki-research
description: Phase 1 of the idea lifecycle — research a seed idea to figure out what already exists in the space, whether it's worth pursuing, and what to understand before brainstorming implementation. Use whenever the user mentions an idea they want to research, validate, or explore — even casually. Triggers on "research <idea>", "deep dive on <idea>", "explore <idea>", "what's out there for X", "what already exists for X", "is X a solved problem", "is X worth building", "should I build X", "validate this idea", "I'm thinking about building X", "what do I need to understand before building X", "/wiki-research <idea>", or any idea slug from `raw/ideas/` or `raw/projects/<slug>/00-idea.md` paired with research intent. Produces a structured research doc — `raw/projects/<slug>/01-research.md` if the idea lives in a project, or an `## Idea Research` section in `wiki/ideas/<slug>.md` otherwise. Do NOT use for implementation planning, package selection, architecture decisions, writing PRDs, or general topic research — those happen later or elsewhere.
---

# Wiki Research

Phase 1 of the idea lifecycle. Takes a seed idea — from a project's `00-idea.md`, a standalone `raw/ideas/<slug>.md`, or even a quick verbal pitch — and turns it into a validated, well-understood concept ready for a brainstorming session.

The lifecycle this fits into:

1. **Capture** → rough idea written into the vault
2. **Research** ← *this skill* — understand the space, validate the idea, decide whether to pursue
3. **Brainstorm** → if yes, explore implementation and architecture in a dedicated session
4. **Plan** → detailed implementation planning (the project's `03-plan.md`)

**What belongs in this skill's output:** landscape, validation, key concepts, honest concerns.
**What does NOT belong:** stack choices, package selection, architecture decisions, PRDs. Those come later.

## Prerequisites

- `wiki/index.md`, `wiki/topics.md`, `wiki/hot.md`, `wiki/log.md` all present.
- `.vault-meta.json` at repo root (for date format).
- WebSearch and WebFetch tools available.

If the vault isn't initialized, stop and point the user at `init-vault`.

## Step 1 — Locate the Idea

Look in three places, in order:

1. **In a project** — `raw/projects/<slug>/00-idea.md`. If the user named a project slug or you can infer one from context, check there first.
2. **As a standalone idea** — `raw/ideas/<slug>.md` (rough draft) or `wiki/ideas/<slug>.md` (already promoted).
3. **In the user's message** — no file yet. The idea was described in conversation.

Read whichever you find in full. Extract before searching:

- The core concept in **one sentence**.
- What problem does it solve, or what capability does it create?
- Who would use it?
- What's genuinely unclear or unvalidated about it?

If the idea is fuzzy, ask **one** clarifying question before searching. Don't waste WebSearch budget chasing a vague concept.

## Step 2 — Research in Parallel

Run searches concurrently. You're building a **picture of the space** — not prescribing a solution.

### Web Searches (4-6 queries)

Shape queries to understand the landscape, not to find an implementation:

- `"<concept> open source github"` — what's already been built?
- `"<concept> existing tools alternatives"` — what are people already using?
- `"<concept> use cases examples"` — how are others framing this problem?
- `"<concept> challenges problems"` — what makes this hard?
- `"<concept> 2025 2026"` — is the space active or stale?
- `"<concept> lessons learned"` or `"<concept> why failed"` — if this is a crowded space

Prioritize:

- Projects with **real usage** (stars, recent activity, community discussion).
- **Honest retrospectives** — "we built X, here's what we learned".
- **Market or community signals** — active forums, recent launches, accelerator portfolios.

For each result you plan to include in the output: name/URL, one-line relevance, any signal about traction or problems.

### Context7 (when a named technology is central)

If the idea is specifically about a named library or platform (e.g., "RAG with LlamaIndex", "agent using LangChain"), use Context7:

1. `resolve-library-id` — look up the library.
2. `query-docs` — ask what the library actually enables/supports for this use case.

Use Context7 **only** when a specific technology is already part of the idea. Don't reach for it during general discovery.

### Stop When You Have

- A clear picture of what already exists in this space.
- 2-3 signals the idea is either worth pursuing or isn't.
- An understanding of the key concepts someone would need to grasp to work on this.
- At least 2 real concerns or open questions — not "do more research".

## Step 3 — Write the Output

Two output paths, depending on where the idea lives:

### Path A — Idea is tied to a project

Write or update `raw/projects/<slug>/01-research.md`. This file may already exist as a stub from `.scripts/new-project.sh` — replace its body. Keep the file's top-level intent: research for that project's idea.

```markdown
# Research

> Market research, competitive analysis, technical exploration for <project-slug>.

_Researched: DD-MM-YYYY_

## What It Actually Is

1-2 sentences clarifying the concept, especially if 00-idea.md was vague. What problem does this solve? For whom?

## What Already Exists

- **[Name](url)** — what it is, why it's relevant, how active it is
- **[Name](url)** — ditto
- **[Name](url)** — ditto (2-4 items total — curated, not exhaustive)

## Why This Is Interesting

2-3 bullets: what signals suggest this is worth pursuing — unmet need, active community, no good open-source option, strong personal fit, etc.

## Concerns & Open Questions

- Specific concern — crowded space, unclear differentiation, hard technical problem
- Another one — be honest, don't inflate

## Key Concepts to Understand

- **Concept** — one-sentence explanation of why it matters for this idea
- **Concept** — ditto (2-4 concepts max — just enough for a productive brainstorm)

## Worth Pursuing?

One honest sentence or two. Take a position. If unclear, say so and name what would resolve it.

## References

- [Name](url)
- [Name](url)
```

Don't write a PRD here. Don't pick a stack. Those come later.

### Path B — Standalone idea (no project)

Write or update `wiki/ideas/<slug>.md`. If the page doesn't exist, create it from `wiki/templates/idea.md` first.

**Frontmatter:**

```yaml
---
status: exploring
related_projects: []
related_patterns: []
topics: [3-5 relevant topics, from wiki/topics.md]
updated: DD-MM-YYYY
---
```

Then add or replace this section in the body:

```markdown
## Idea Research

_Researched: DD-MM-YYYY_

### What It Actually Is
[1-2 sentences]

### What Already Exists
- **[Name](url)** — what it is, why it's relevant, how active it is
- **[Name](url)** — ditto

### Why This Is Interesting
- Signal 1
- Signal 2

### Concerns & Open Questions
- Concern 1
- Concern 2

### Key Concepts to Understand
- **Concept** — why it matters

### Worth Pursuing?
[One sentence taking a position]
```

If a stale `## Implementation Research` section exists on the page (from a prior workflow), **remove it** — that belongs to the brainstorming phase, not here.

## Quality Bar

- **"What Already Exists" items must have URLs** and say something specific about usage/activity. "Some startups are doing this" is not enough.
- **Concerns must be honest.** Don't pad with minor issues; don't skip real ones to look enthusiastic.
- **"Worth Pursuing?" must take a position.** Not just a list of pros and cons.
- **Key concepts are scoped to the next phase.** Only the things someone needs to grasp to have a productive brainstorm — not an exhaustive education.

## Step 4 — Finalize

1. If a **new wiki page** was created (Path B with a fresh idea), add it to `wiki/index.md` under the Ideas section.
2. Append to `wiki/log.md`:
   ```
   ## [DD-MM-YYYY] research | <idea title> — verdict: <worth pursuing / not yet / no>
   ```
3. If the idea is tied to an `status: active` project, update that project's `Current Status` block — bump `Last touched` and add a line under `Recent Updates` referencing the research.
4. Tell the user the **one-line verdict** and the **most important open question** — two sentences max. The full research is in the file.

## Notes for the LLM

- **Don't drift into implementation.** If you find yourself naming packages or sketching architecture, stop. That belongs to brainstorming or planning.
- **Honest verdicts beat enthusiastic ones.** "Crowded space, three solid open-source projects already, differentiation unclear" is more useful than "Promising area, lots of potential!"
- **Date everything in the vault's chosen format.** Read `.vault-meta.json` if unsure.
- **Don't re-research what the wiki already covers deeply.** Check `wiki/index.md` first. If the topic has 5+ existing pages, the research is "what's *new* since these were written?" instead of a from-scratch landscape.
- **One run = one research doc.** If the user asks to research a different angle on the same idea, append a new dated section to the existing file rather than overwriting.
