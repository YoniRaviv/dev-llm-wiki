---
name: wiki-query
description: Answer questions by searching the wiki — uses a cheap-first retrieval pipeline (index/frontmatter scan → section grep → full page read) so a query touches the minimum necessary pages. Use whenever the user asks a question about their knowledge base, wants to find information across the wiki, asks "what do I know about X", "find everything related to Y", "consult the brain", "have we decided about Z", "what did we learn about W", or wants synthesized answers with citations. Also use when the user explicitly asks for connections between topics. Includes an index-only fast mode triggered by "quick answer", "just scan", "don't read the pages", "fast lookup" — returns answers from page titles and `wiki/index.md` entries without reading bodies. Always reads `wiki/hot.md` first so recent activity informs the answer.
---

# Wiki Query — Knowledge Retrieval

You are answering questions against the compiled wiki, not raw source documents. The wiki contains pre-synthesized, cross-referenced knowledge — that's the whole point.

Reading is the dominant cost of this skill. Use the **cheapest primitive that answers the question** and escalate only when it can't. Never jump straight to full-page reads. The pipeline below is what makes the wiki affordable to consult on every question.

## Before You Start

1. Read `wiki/hot.md` — instant context on recent activity. If the user's question is about something ingested recently, hot.md may answer it before you even open `wiki/index.md`.
2. Read `wiki/index.md` — the content catalog. Tells you the wiki's scope and structure.
3. Read `.vault-meta.json` if present — confirms the date format for the log entry at the end.

If `wiki/index.md` or `wiki/hot.md` are missing, the vault isn't initialized. Stop and point the user at `init-vault`.

## Retrieval Protocol

### Step 1 — Understand the Question

Classify the query:

- **Factual lookup** — "What is X?" → find the relevant page(s)
- **Relationship query** — "How does X relate to Y?" → find both pages and their cross-references
- **Synthesis query** — "What's the current thinking on X?" → find all pages touching X, synthesize
- **Gap query** — "What don't I know about X?" → find what's missing; check Open Questions sections

Decide the **mode**:

- **Index-only mode** — triggered by "quick answer", "just scan", "don't read the pages", "fast lookup". Stops at Step 2. Answers from `index.md` entries and page frontmatter only.
- **Normal mode** — the full tiered pipeline below.

### Step 2 — Index Pass (cheap)

Build a candidate set *without opening any page bodies*:

- You've already read `wiki/index.md`. Use it as the first filter — it lists every page with a one-line description.
- Use `Grep` to scan page **frontmatter only** for title, tag, and topic matches. A pattern like `^(title|name|topics):` scoped to `wiki/**.md` is far cheaper than content grep.
- Collect the top 5-10 candidate page paths, ranked by:
  1. Exact title match
  2. `topics:` overlap with the question's noun phrases (≥2 topics = strong signal)
  3. `index.md` entry contains the query term
  4. Recency — pages with recent `wiki/log.md` mentions are more current

If you're in **index-only mode**, stop here. Answer from `index.md` descriptions, frontmatter `name` fields, and any frontmatter summary fields. Label the answer clearly: **"(index-only answer — page bodies not read; details may be incomplete)"**. Then skip to Step 5.

### Step 3 — Section Pass (medium cost — only if Step 2 is inconclusive)

For each of the top candidates, pull the relevant section *without reading the whole page*:

- Use `Grep -A 10 -B 2 "<query-term>" <candidate-file>` to get just the lines around the match.
- This usually returns 15-30 lines per hit instead of 100-500.
- If the section grep gives a clear answer, go straight to Step 5.

### Step 4 — Full Read (expensive — last resort)

Only when Steps 2 and 3 don't answer the question:

- `Read` the top **3** candidates in full. Not 10. If you find yourself wanting to read 10 pages, the question is probably ambiguous — clarify with the user before continuing.
- Follow at most **one hop** of `[[wikilinks]]` from those pages if the answer requires cross-references.
- Check **Open Questions** sections — they often pinpoint exactly what the wiki doesn't know.
- If you're still short, **then** fall back to a broad content grep across the vault. Tell the user you escalated — this is the expensive path and they should know.

### Step 5 — Synthesize an Answer

Compose your answer from wiki content:

- Cite specific wiki pages using `[[subdir/page]]` notation. Every load-bearing claim must be traceable.
- Note where the answer came from ("found in summary" vs "grepped section" vs "full page read") — helps the user gauge confidence.
- If the wiki has **contradictions**, present both sides. Resolving a contradiction is itself a file-worthy event (see Step 6).
- If the wiki **doesn't cover** something, say so explicitly. Suggest which sources might fill the gap — and offer to run `wiki-ingest` if a source exists in `raw/` but isn't in `.manifest.json`.

### Step 6 — Offer to File (conditional)

Not every QUERY ends with a write. File the answer back when the synthesis is:

- A **comparison** ("X vs Y, when to pick which") and no comparison page exists.
- A **decision analysis** the user is acting on.
- A **discovered connection** — two pages relate in a way neither one notes.
- A **new gotcha or reusable claim** the answer itself produced.

Don't file when the answer is:

- A simple lookup.
- A restatement of one existing page.
- Speculative or pre-decisional.

If you do offer:

> "Should I file this back? Suggested location: `wiki/patterns/<slug>.md` (new pattern) / `wiki/projects/<slug>/decisions/<slug>.md` (new ADR) / appended to `[[existing-page]]`."

If yes, create or update the page using the appropriate template. Cross-link properly. Update `wiki/index.md` if you created a new page.

### Step 7 — Log the Query

Append to `wiki/log.md`:

```
## [DD-MM-YYYY] query | <short question>
```

If you filed the answer back, also append a `## [DD-MM-YYYY] ingest | answer to: <question>` (treat the synthesis as a tiny self-ingest) and update `wiki/hot.md`'s Recent Activity.

## Answer Format

Structure your response to the user like this:

> **Based on the wiki:**
>
> [Your synthesized answer with `[[wikilinks]]` to source pages]
>
> **Pages consulted:** `[[page-a]]`, `[[page-b]]`, `[[page-c]]`
>
> **Confidence:** *answered from page summaries / section greps / full reads* (one of these)
>
> **Gaps:** [what the wiki doesn't cover that might be relevant]

## Edge Cases

- **Ambiguous question** — ask one clarifying follow-up before reading 15 pages. "Are you asking about X or Y?" beats reading 15 pages and answering the wrong one.
- **No matches in the wiki** — say so plainly. Don't fabricate. Then optionally answer from general knowledge with that fact stated up front: "Not in the wiki — drawing from general knowledge: …"
- **Contradictions across pages** — surface them, quote both, link both. Ask which resolution to record.
- **Source exists in `raw/` but not ingested** — the question implies an article/tweet/repo the user clipped but never ingested. Suggest `wiki-ingest` first.
- **User says "just answer, don't consult the wiki"** — fine, skip the procedure.

## Notes for the LLM

- **The index is the primary lookup.** If `wiki/index.md` is missing relevant pages, that's a wiki-maintenance bug — surface it.
- **Cite specifically.** `[[patterns/async-state-management]]` is useful; "the wiki says so" is not.
- **Don't pad with citations that don't carry the claim.** A citation is load-bearing, not decoration.
- **When in doubt about whether to file, don't.** Filing low-value answers makes the wiki noisier and future queries slower.
