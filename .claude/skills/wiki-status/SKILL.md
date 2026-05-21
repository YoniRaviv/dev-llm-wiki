---
name: wiki-status
description: Show the current state of the wiki — what's been ingested, what's pending, and the delta between sources and wiki content. Use when the user asks "what's the status", "how much is ingested", "what's left to process", "show me the delta", "what changed since last ingest", "wiki dashboard", or wants an overview of knowledge base health and completeness. Also use before deciding whether to append or rebuild. Includes an **insights mode** triggered by "wiki insights", "what's central", "show me the hubs", "central pages", "what's connected", "wiki structure" — analyzes the shape of the wiki itself to surface top hubs, cross-domain bridges, and orphan-adjacent pages.
---

# Wiki Status — Audit & Delta

Computes the current state of the wiki: what's been ingested, what's new since last ingest, and what the delta looks like. Helps the user decide whether to append (ingest the delta) or rebuild (archive and reprocess).

The skill only reads and reports — it does not modify the vault (except writing `wiki/_insights.md` in insights mode, which is regenerable).

## Before You Start

1. Read `.manifest.json` at repo root — the ingest tracking ledger. If it doesn't exist, the vault is fresh; report everything as "new" and recommend a full ingest.
2. Read `wiki/index.md` for the page inventory.
3. Read `.vault-meta.json` if present — confirms date format and folder structure.

## The Manifest

Lives at the repo root. Tracks every source file that's been ingested:

```json
{
  "version": "1.0",
  "ingested": [
    {
      "raw_path": "raw/articles/example.md",
      "source_page": "wiki/sources/15-04-2026-example.md",
      "ingested_at": "15-04-2026",
      "content_hash": "sha256:abc123…",
      "size_bytes": 4523,
      "title": "Example",
      "source_type": "article",
      "pages_created": ["wiki/patterns/foo.md"],
      "pages_updated": ["wiki/projects/bar.md"]
    }
  ]
}
```

If older entries lack `content_hash`, fall back to mtime comparison for those.

## Step 1 — Scan Current Sources

Build an inventory of everything in `raw/` available to ingest right now:

- Glob `raw/articles/*.md`, `raw/tweets/*.md`, `raw/repos/*.md`, `raw/ideas/*.md`
- Glob `raw/projects/*/notes/*.md` (project notes also count as sources)
- For each: record path, size, mtime

If the user has additional `raw/` subdirs (added via `init-vault` — `papers/`, `videos/`, etc.), scan those too. Use the actual folder list from `.vault-meta.json`'s `folders.raw` if available, otherwise glob `raw/*/`.

## Step 2 — Compute the Delta

For each source file, classify against the manifest:

| Status | Meaning | Action needed |
|---|---|---|
| **New** | File exists on disk, not in manifest | Needs ingesting |
| **Modified** | File in manifest, content hash differs | Needs re-ingesting |
| **Touched** | File in manifest, mtime newer but hash unchanged | Skip — content identical |
| **Unchanged** | File in manifest, mtime and hash both match | Nothing to do |
| **Deleted** | In manifest, but file no longer on disk | Note it — wiki pages may be stale |

For files lacking a stored `content_hash` (older entries), use mtime to decide modified vs unchanged.

## Step 3 — Report the Status

```markdown
# Wiki Status — DD-MM-YYYY

## Overview
- **Total wiki pages**: N across <list of populated subdirs>
- **Total sources ingested**: M
- **Active projects**: K (of L total projects)
- **Last ingest**: DD-MM-YYYY (or "never" if manifest is empty)

## Delta (changes since last ingest)

### New sources (never ingested): N
| Source | Type | Size |
|---|---|---|
| raw/articles/foo.md | article | 4.2 KB |
| raw/repos/bar.md | repo | 1.8 KB |

### Modified sources (need re-ingesting): N
| Source | Last ingested | Last modified |
|---|---|---|
| raw/ideas/baz.md | 01-04-2026 | 18-05-2026 |

### Deleted sources (ingested but gone): N
| Source page | Original raw path |
|---|---|
| wiki/sources/01-03-2026-old-thing.md | raw/articles/old-thing.md |

## Summary
- **Ready to ingest**: <new> + <modified> = N sources
- **Up to date**: K sources unchanged
- **Recommendation**: <see Step 4>
```

If a category has zero items, omit it from the report — don't pad with "0 deleted".

## Step 4 — Recommend Action

Pick based on the delta:

| Situation | Recommendation |
|---|---|
| Delta is small (<20% of total sources) | **Append** — just ingest the new/modified |
| Delta is large (>50% of total sources) | **Rebuild** — archive and reprocess everything |
| Many deleted sources | **Lint first** — orphan wiki pages may be lurking |
| First time / empty manifest | **Full ingest** — process everything |
| User just wants to see status | **No action** — report only |

End the report with a one-liner: "You have X new and Y modified sources — recommend `wiki-ingest` on the delta. Want me to run it?"

## Insights Mode

Triggered when the user asks for "wiki insights", "what's central", "show me the hubs", "cross-domain bridges", "wiki structure", or any analysis of the wiki's *shape* (not its delta).

This mode is **additive**, not a replacement. Insights mode complements the delta report: delta tells you what's pending; insights tell you what you've already built and where the interesting structure lives.

### Build the wikilink graph

Glob all `wiki/**/*.md` (exclude `templates/`, `index.md`, `log.md`, `hot.md`, `topics.md`). For each:

- Extract every `[[wikilink]]` from the body.
- Build:
  - `incoming[page]` — count of other pages linking to this one
  - `outgoing[page]` — count of pages this one links to
  - `topics[page]` — set of topics from frontmatter
  - `category[page]` — directory prefix (`projects/`, `patterns/`, etc.)

You'll reuse this graph across the sections below.

### 1. Anchor pages (top hubs)

Pages with the most incoming links — the load-bearing concepts.

- Rank by `incoming` count; take top 10.
- For each, note both incoming and outgoing:
  - High incoming AND high outgoing → **connector hub** (most valuable).
  - High incoming AND zero outgoing → **sink hub** — flag as cross-linker candidate.

### 2. Bridge pages

Pages that connect otherwise-disconnected topic clusters — removing them would partition the graph.

- For each page P, find pairs (A, B) where A links to P, B is linked from P (or vice versa), and A/B share no topics with each other.
- Rank P by how many cross-cluster pairs it bridges; show top 5.
- Label each: "P bridges `[topic-cluster-A]` ↔ `[topic-cluster-B]`"

### 3. Topic cluster cohesion

For each topic appearing on ≥5 pages:

- `n` = count of pages with this topic
- `actual_links` = wikilinks between any two pages in the topic group
- `cohesion = actual_links / (n × (n−1) / 2)`

Show:
- Top 5 most cohesive topics (well-linked clusters)
- Bottom 5 most fragmented (cross-linker targets — cohesion < 0.15)

### 4. Surprising connections

Cross-category wikilinks scored by how unexpected they are:

- **+2** if categories are in different layers (e.g., `projects/` ↔ `patterns/` is mundane; `projects/` ↔ `sources/` is more surprising)
- **+2** if source page has ≤2 total links (peripheral) but target has ≥8 (hub) — unexpected reach from edge to center

Show top 5 with a one-line reason for each.

### 5. Orphan-adjacent pages

Pages linked from a top-10 hub but with zero outgoing links of their own. Dead-ends in high-traffic areas — prime cross-linker candidates.

### 6. Rough clusters

Group anchor pages by dominant topic. Simple topic intersection — just for orientation.

### 7. Graph delta since last insights run

If a previous `_insights.md` exists at the vault root:

- Read the `<!-- GRAPH_SNAPSHOT: ... -->` HTML comment at the bottom (compact JSON edge list).
- Compute: new pages added, pages removed, new wikilinks created, wikilinks removed.
- Flag: pages that were isolated last run but now have incoming links ("newly connected").
- Flag: pages that lost incoming links since last run (likely renames or breaks).

Skip this section if there's no prior snapshot.

### 8. Suggested questions

Questions this wiki's structure is uniquely positioned to answer (or that reveal gaps):

- From bridge pages: "Explore: why does `P` connect `[cluster-A]` to `[cluster-B]`?"
- From pages with zero incoming links: "Link: `X` has no incoming references — what should reference it?"
- From fragmented topic clusters (cohesion < 0.15): "Audit: should topic `T` be split into more focused sub-topics?"

Show up to 7. Prioritize bridges, then isolates, then fragmented clusters.

### Insights output

Write the result to `wiki/_insights.md`. Overwrite freely — it's regenerable. At the very end, embed a compact graph snapshot as an HTML comment so the next run can diff against it.

```markdown
# Wiki Insights — DD-MM-YYYY

## Anchor Pages (top 10 hubs)
| Page | Incoming | Outgoing | Note |
|---|---|---|---|
| [[patterns/async-state-management]] | 14 | 7 | connector hub |
| [[technologies/postgres]] | 11 | 0 | sink hub — cross-linker candidate |

## Bridge Pages (top 5)
| Page | Bridges | Pairs |
|---|---|---|
| [[patterns/event-sourcing]] | `billing` ↔ `analytics` | 3 |

## Topic Cluster Cohesion
### Most cohesive
- **`auth`** — 6 pages, cohesion 0.40
### Most fragmented (cross-linker targets)
- **`postgres`** — 7 pages, cohesion 0.06 ⚠️

## Surprising Connections (top 5)
- [[patterns/circuit-breaker]] → [[sources/15-04-2026-stripe-postmortem]] — score 4
  - Reason: cross-layer (patterns ↔ sources), peripheral source → hub pattern

## Orphan-Adjacent (dead-ends near hubs)
- [[ideas/llm-driven-codegen]] — linked from 2 hubs, 0 outbound

## Rough Clusters
- **`auth`** — login-flow, token-rotation, oauth-callbacks
- **`scaling`** — partition-strategies, hot-shard-detection

## Graph Delta Since Last Run
- +3 new pages, +9 new wikilinks
- Newly connected: [[ideas/llm-driven-codegen]]
- Lost incoming: [[sources/01-03-2026-old-paper]] (likely renamed)

## Questions Worth Asking
1. Explore: why does `[[patterns/event-sourcing]]` bridge `billing` and `analytics`?
2. Link: `[[ideas/llm-driven-codegen]]` has no incoming references — what should reference it?
3. Audit: should topic `postgres` be split? (cohesion 0.06, 7 pages)

<!-- GRAPH_SNAPSHOT: {"nodes":["patterns/foo","technologies/bar"],"edges":[["patterns/foo","technologies/bar"]]} -->
```

After writing the file, append to `wiki/log.md`:

```
## [DD-MM-YYYY] status_insights | anchors=10 bridges=N cohesion_checked=T surprising=5 questions=7 delta="+N pages +M links"
```

### When to skip insights mode

- Vault has fewer than 20 pages — not enough graph structure. Tell the user and skip.
- The wiki was rebuilt recently and no ingest has happened since — wait until at least one ingest.

## Notes

- This skill only **reads and reports**. The only file it writes is `wiki/_insights.md` (regenerable). The actual ingest work happens in `wiki-ingest`.
- Delta size threshold (20% append vs 50% rebuild) is a heuristic; tune to your taste in `.vault-meta.json` if you find the recommendation consistently wrong for your workflow.
- If history-ingest skills (e.g. `claude-history-ingest`, `codex-history-ingest`) are installed, extend Step 1 to scan their source paths too — the manifest's `source_type` field will reflect the variety.
