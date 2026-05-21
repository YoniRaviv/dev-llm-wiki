---
name: cross-linker
description: Scan the wiki and automatically insert missing `[[wikilinks]]` between pages that should reference each other but currently don't. Use when the user says "link my pages", "find missing links", "cross-reference", "connect my wiki", "add wikilinks", "what pages should be linked", or after any large ingestion to ensure new pages are woven into the existing knowledge graph. Also trigger when the user mentions "orphan pages" in the context of wanting to connect them, or says "my wiki feels disconnected" or "pages aren't linked well". This is a **write-heavy skill** — it actually modifies pages to add links, unlike `wiki-lint` which just reports issues. Pairs naturally with `wiki-lint`'s fragmented-topic-cluster finding.
---

# Cross-Linker — Automated Wiki Cross-Referencing

Weaves the wiki's knowledge graph tighter by finding and inserting missing `[[wikilinks]]` between pages that should reference each other.

**Cheap-first principle still applies.** Build the page registry in Step 1 by grepping frontmatter only — not full pages. Reserve full `Read` for the unlinked-mention detection pass, and even there, only read pages whose frontmatter/title makes them plausible link targets. Blind full-vault reads on every run are wasteful.

## Before You Start

1. Read `wiki/index.md` — full inventory of pages with one-line descriptions.
2. Skim `wiki/log.md` — see what was recently ingested (focus linking effort on new pages).
3. Read `.vault-meta.json` if present — confirms folder structure.

## Step 1 — Build the Page Registry

Glob `wiki/**/*.md` (excluding `wiki/templates/`, `wiki/index.md`, `wiki/log.md`, `wiki/hot.md`, `wiki/topics.md`). For each page, extract via frontmatter grep (don't read bodies):

- **Filename** without `.md` — the wikilink target
- **Title / name** from frontmatter
- **Topics** from frontmatter (`topics:` array)
- **Category** from directory prefix (`projects/`, `patterns/`, `technologies/`, `ideas/`, `sources/`, `decisions/`)
- **First-paragraph summary** — the first sentence of the body if useful

Build a lookup table:

```
page_slug → { path, title, topics, category, summary }
```

This is your "vocabulary" — every entry is a valid wikilink target.

## Step 2 — Scan for Missing Links

For each page in the vault (prioritize pages recently created or updated per `log.md`):

1. **Read the full content.**
2. **Extract existing wikilinks** — find all `[[...]]` already on the page.
3. **Search for unlinked mentions** — check the body text for any of:
   - Other page filenames (e.g., "circuit breaker" appears but `[[patterns/circuit-breaker]]` is missing)
   - Other page titles from frontmatter
   - Distinctive entity names, project names, pattern/technology names from the registry
4. **Check for semantic connections** — pairs of pages that share multiple topics or live in the same project directory but don't link to each other.

### Matching rules

- **Case-insensitive** for names (`MyProject` matches page `my-project`).
- **Diacritic-insensitive** — normalize both the page name and the body text with Unicode NFKD (decompose accents, strip combining marks) before comparing. So body text "Muller" matches `[[technologies/müller]]` and vice versa.
- **Skip self-references** — a page never links to itself.
- **Skip common words** — never link "the", "and", or other generic terms. Only match on distinctive names.
- **Prefer the shortest unambiguous wikilink path** — use `[[page-name]]` not `[[full/path/to/page-name]]` when the name is unique across the vault.
- **Don't link inside code blocks, fenced code, or YAML frontmatter.**
- **Don't double-link** — if `[[foo]]` already appears on the page, don't add another reference to the same page.
- **Don't touch templates** in `wiki/templates/`.

## Step 3 — Score and Rank Suggestions

Not every possible link is worth adding. Score each candidate using a composite signal, then tag with a confidence label.

### Scoring

| Signal | Points | Example |
|---|---|---|
| **Exact name match in text** | +4 | "circuit breaker" appears in body → link to `[[patterns/circuit-breaker]]` |
| **Shared topics (2+)** | +2 | Both pages tagged with topics `auth` and `oauth` but don't link |
| **Same project, no link** | +2 | Both under `wiki/projects/my-app/` but don't reference each other |
| **Mentioned by name in registry** | +2 | Page text mentions "Postgres" → link to `[[technologies/postgres]]` |
| **Cross-category connection** | +2 | Source is `patterns/`, target is `technologies/` — different knowledge layers |
| **Peripheral → hub reach** | +2 | Source has ≤2 total links, target has ≥8 — connecting a loose page to a load-bearing concept |
| **Partial name match** | +1 | "graph" appears but page is `knowledge-graphs` — plausible but ambiguous |

### Confidence labels

| Score | Label | Action |
|---|---|---|
| ≥6 | **HIGH** | Effectively certain. Apply inline. |
| 3-5 | **MEDIUM** | Reasonable inference. Apply inline or as Related-section bullet. |
| 1-2 | **LOW** | Weak/partial. Skip unless the user specifically asks to connect loose pages. |

Act on HIGH and MEDIUM only. Include the confidence label in the report so the user can review MEDIUM-linked pages before trusting them.

## Step 4 — Apply Links

### 4a. Inline linking (preferred)

Find the **first natural mention** of the term in the body and wrap it in wikilinks:

**Before:**
```markdown
This project uses knowledge graphs to connect entities.
```

**After:**
```markdown
This project uses [[patterns/knowledge-graphs|knowledge graphs]] to connect entities.
```

Use `[[path|display text]]` when the link path differs from the natural display text. Use bare `[[slug]]` when they match.

### 4b. Related section (fallback)

If the term isn't mentioned naturally in the body but the pages are semantically related (shared topics, same project), add a `## Related` section at the bottom:

```markdown
## Related

- [[projects/my-project]] — Uses this pattern in their auth flow
- [[technologies/redis]] — Underlies the rate-limiting implementation
```

If a `## Related` section already exists, append to it. Don't duplicate existing entries.

**Don't create a Related section just to add one link** — if there's exactly one cross-link candidate and it doesn't appear in the body, mention it inline somewhere natural instead.

## Step 5 — Report

```markdown
## Cross-Link Report — DD-MM-YYYY

### Links Added: N across M pages

| Page | Links Added | Confidence | Type |
|---|---|---|---|
| `wiki/projects/my-app.md` | 3 | HIGH | 2 inline, 1 related |
| `wiki/technologies/postgres.md` | 5 | MEDIUM | 3 inline, 2 related |

### Orphan Pages Remaining: K
- `wiki/patterns/old-foo.md` — no incoming or outgoing links found
- `wiki/ideas/something.md` — could not find related pages

### Pages Skipped: J
- `wiki/index.md`, `wiki/log.md`, `wiki/hot.md`, `wiki/topics.md` — meta files
- `wiki/templates/*` — templates
```

If `wiki-lint` previously flagged fragmented topic clusters, mention which ones this run improved:

```markdown
### Fragmented Clusters Improved
- **`postgres`** — cohesion 0.06 → 0.21 ✓
- **`auth`** — cohesion 0.10 → 0.18 ✓
```

## Step 6 — Update log and hot.md

Append to `wiki/log.md`:

```
## [DD-MM-YYYY] cross_link | <N> pages_scanned, <M> links_added, <P> pages_modified, <Q> orphans_remaining
```

Update `wiki/hot.md` Recent Activity:

```
- **DD-MM-YYYY — Cross-linked N pages** — added M wikilinks, P orphans remain.
```

Cap Recent Activity at 10 entries; rotate oldest out.

## Tips

- **Run after every large ingest.** New pages are almost always poorly connected at first. This is the fix.
- **Run after `wiki-lint`** when fragmented topic clusters were flagged. Target those clusters specifically by passing the topic name if the user asks for focused work.
- **Be conservative with inline links.** Only link the first natural mention, not every occurrence — pages with [[link]][[link]][[link]] sprinkled everywhere are unreadable.
- **Technology pages are link magnets.** A `technologies/postgres` page should be linked from almost every project that uses Postgres. Prioritize those.
- **Project pages should anchor a graph cluster.** A project page that doesn't link out to its own features, decisions, and key technologies is broken — fix those first.

## Notes for the LLM

- **Don't touch pages whose frontmatter shows `status: archived`.** Those are frozen snapshots.
- **Respect existing structure.** If a page carefully curates its links in a `## Key Decisions` or `## Related Patterns` section (per the template schema), add to those sections rather than creating a separate `## Related`.
- **Date format from `.vault-meta.json`.** All log entries must match.
- **Single-page mode.** If the user asks to cross-link a *specific* page ("link up my new auth-flow doc"), restrict the scan to that page — don't run the full vault sweep.
