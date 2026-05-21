---
name: wiki-lint
description: Audit and maintain the health of the wiki. Use when the user wants to check their wiki for issues, find orphaned pages, detect contradictions, identify stale content, fix broken wikilinks, audit the controlled topic vocabulary, or perform general maintenance on the knowledge base. Triggers on "lint the wiki", "clean up the wiki", "audit my notes", "wiki health check", "what needs fixing", "find broken links", "check for orphans". Executes the LINT operation defined in `CLAUDE.md`.
---

# Wiki Lint — Health Audit

The executable procedure for the LINT operation in CLAUDE.md. Finds and (where safe) fixes structural issues that degrade the wiki's value over time. Outputs a markdown report; flags items needing user input.

Before scanning anything: **prefer frontmatter-scoped greps and section-anchored reads over full-page reads.** Blindly reading every page in a large vault is exactly what this skill exists to avoid.

## Before You Start

1. Read `wiki/index.md` for the full page inventory.
2. Read `wiki/log.md` for recent activity context.
3. Read `wiki/topics.md` — the controlled vocabulary (needed for topic checks).
4. Read `.vault-meta.json` if present — confirms the date format and the staleness threshold (default 14 days, may be customized).

If those files are missing, the vault isn't initialized. Tell the user to run `init-vault` and stop.

## Lint Checks

Run these in order. Report findings as you go.

### 1. Orphan Pages

Pages with zero incoming wikilinks. Knowledge islands that nothing connects to.

- Glob all `wiki/**/*.md` (exclude `index.md`, `log.md`, `hot.md`, `topics.md`, `templates/`).
- For each page, `Grep` the rest of `wiki/` for `[[<page-slug>]]` (and its subdir variant).
- Pages with zero incoming links are orphans.

**Auto-fix**: identify likely linkers from topic overlap; suggest links. Don't insert without user approval — orphans often signal that a page is genuinely useless and should be deleted instead of cross-linked.

### 2. Broken Wikilinks

`[[wikilinks]]` pointing to pages that don't exist.

- `Grep -r '\[\[.+?\]\]' wiki/`
- For each match, resolve the link target to a file path. If no `.md` file exists at the path, it's broken.

**Auto-fix**: if the target looks like a typo of an existing page (Levenshtein ≤ 2), suggest the correction. Otherwise list and ask.

### 3. Missing Frontmatter

Each page type has required frontmatter (see CLAUDE.md "Entity Schemas"). Check at minimum:

- **projects/**: `name`, `status`, `stack`, `topics`, `started`, `last_updated`
- **features/**: `project`, `status`, `topics`, `started`
- **decisions/**: `projects`, `topics`, `date`, `status`
- **patterns/**: `used_in`, `topics`, `tags`, `first_seen`
- **technologies/**: `type`, `used_in`, `topics`
- **ideas/**: `status`, `topics`
- **sources/**: `type`, `raw_path`, `topics`, `date_ingested`

Use `Grep` on frontmatter (pattern: `^[a-z_]+:` between two `^---$` markers) — don't read page bodies.

**Auto-fix**: add the field with a reasonable default (e.g., `topics: []` if none can be inferred), flag for the user to fill.

### 4. Stale Project `Current Status`

Any `status: active` project whose `Last touched:` is older than the staleness threshold (default 14 days; check `.vault-meta.json` for customization).

- Glob `wiki/projects/*.md`.
- For pages with `status: active`, parse the `Last touched:` line in the Current Status block.
- Flag any older than the threshold.

**Auto-fix**: suggest reaching out to the user or downgrading status to `paused`. Don't auto-update — staleness is a real signal.

### 5. Stale Sourced Claims

Pages whose `last_updated` is older than the modification time of the sources they cite.

- For each page with a `last_updated` frontmatter field, grep its body for `[[sources/...]]` citations.
- For each cited source page, read its `date_ingested`.
- If any source was ingested **after** the citing page's `last_updated`, flag the page as potentially stale.

**Auto-fix**: list candidates for re-ingest. Don't auto-rewrite.

### 6. Contradictions

Pages making conflicting claims.

- Scan pages for `> ⚠️ Contradiction:` blockquotes — these are already-flagged.
- Surface unresolved contradictions in the report.
- Optionally: skim pages that share ≥3 topics for sentence-level contradictions (this is expensive — only do if user asks for deep contradiction lint).

**Auto-fix**: none. Always surface for human resolution.

### 7. Index Consistency

`wiki/index.md` must match the actual page inventory.

- Glob `wiki/**/*.md` (excluding the meta files).
- Compare against entries in `index.md`.
- Flag: pages on disk but not indexed; entries in index pointing to deleted pages.

**Auto-fix**: add missing entries with a one-line description guessed from the page's first heading + summary; remove dead entries with user confirmation.

### 8. Topic Vocabulary Health

Three sub-checks on `wiki/topics.md`:

**8a. Unknown topics** — any `topics:` value on any wiki page that isn't in `topics.md`.

- Grep all wiki page frontmatter for `topics:` arrays.
- Compare against the vocabulary list in `topics.md`.
- Flag unknowns.

**Auto-fix**: append unknowns to `topics.md` in the same write — they likely should be there.

**8b. Near-duplicate topics** — pairs of topics in `topics.md` likely synonymous (`s3-uploads` vs `s3-storage`, `react-hooks` vs `react-hook-patterns`).

- Compute Levenshtein distance between all topic pairs.
- Flag pairs with distance ≤ 3 OR shared prefix ≥ 6 characters.

**Auto-fix**: none — propose merges to the user.

**8c. Single-use topics** — topics used on only one page.

- Count uses of each topic across the vault.
- Flag any with count = 1 as a consolidation candidate.

**Auto-fix**: none.

### 9. Missing Page Candidates

Concepts referenced by name in 2+ pages but lacking their own dedicated page:

- **Patterns** appearing in 2+ feature pages but not in `wiki/patterns/`.
- **Technologies** mentioned repeatedly but not in `wiki/technologies/`.
- **Decisions** referenced in feature pages but not having a standalone `decisions/` page.

Heuristic: look at frontmatter `used_in:`, `related_patterns:`, `stack:` arrays. Cross-reference against actual page existence.

**Auto-fix**: none — suggest creation with a stub, let the user decide.

### 10. Fragmented Topic Clusters

Pages that share a topic but don't link to each other. Topic clusters that aren't woven together are knowledge islands.

For each topic appearing on ≥5 pages:
- `n` = count of pages with this topic
- `actual_links` = count of wikilinks between any two pages in this topic group (check both directions)
- `cohesion = actual_links / (n × (n−1) / 2)`

Flag topic groups where cohesion < 0.15 and n ≥ 5.

**Auto-fix**: suggest running `cross-linker` (if installed) on the fragmented topic.

### 11. Date Format Consistency

All dates in the wiki must use the format from `.vault-meta.json` (default `DD-MM-YYYY`).

- Grep wiki pages for date-like patterns (`\d{2}-\d{2}-\d{4}`, `\d{4}-\d{2}-\d{2}`, etc.).
- Flag any that don't match the configured format.
- Special case: ISO-8601 timestamps with time (`2026-05-20T10:30:00Z`) in `.manifest.json` are fine — that's a JSON format choice, not a wiki page.

**Auto-fix**: bulk-rewrite if user confirms. Make sure the format change doesn't break other parsing.

### 12. Journal Filename Pattern

If `wiki/journal/` exists, every file there must match `DD-MM-YYYY.md` (or the configured date format).

- Glob `wiki/journal/*.md`.
- Validate filenames against the format.

**Auto-fix**: suggest renames; don't auto-rename without user approval.

## Output Format

```markdown
# Wiki Health Report — DD-MM-YYYY

## Orphan Pages (N found)
- `wiki/patterns/foo.md` — no incoming links

## Broken Wikilinks (N found)
- `wiki/technologies/bar.md:15` — links to `[[nonexistent-page]]`

## Missing Frontmatter (N found)
- `wiki/patterns/baz.md` — missing: `topics`, `used_in`

## Stale Project Status (N found)
- `wiki/projects/old-thing.md` — Last touched: 12-04-2026 (38 days ago)

## Stale Claims (N found)
- `wiki/patterns/auth.md` — last_updated 01-04-2026, but cites [[sources/15-04-2026-new-auth-spec]] ingested later

## Contradictions (N found)
- `wiki/patterns/scaling.md` flags an unresolved contradiction with [[sources/02-05-2026-cap-theorem-revisited]]

## Index Issues (N found)
- `wiki/patterns/new-thing.md` exists but not in index.md

## Topic Vocabulary (N found)
- Unknown topic `s3-uploads` used on [[technologies/aws-s3]] — not in topics.md
- Near-duplicate: `react-hooks` and `react-hook-patterns` — propose merge
- Single-use: `xeon-cache-line` used only on [[patterns/cpu-cache-alignment]]

## Missing Page Candidates (N found)
- Pattern `circuit-breaker` referenced in 3 feature pages but no patterns/circuit-breaker.md
- Technology `redis` mentioned 5 times but no technologies/redis.md

## Fragmented Topic Clusters (N found)
- **`postgres`** — 7 pages, cohesion 0.06 ⚠️ — consider cross-linker

## Date Format Issues (N found)
- `wiki/journal/2026-05-20.md` — uses ISO format; vault is configured for DD-MM-YYYY

## Journal Filename Issues (N found)
- `wiki/journal/may-20.md` doesn't match DD-MM-YYYY.md

## Summary
- **Auto-fixed**: K issues (orphans linked, frontmatter filled, index entries added)
- **Needs user input**: M issues (contradictions, near-duplicates, missing-page candidates)
```

## After Linting

Append to `wiki/log.md`:

```
## [DD-MM-YYYY] lint | <one-line summary, e.g. "12 issues found, 5 auto-fixed">
```

Offer to walk through the items needing user input, or let them tackle the report at their own pace.

## Notes for the LLM

- **Don't be precious about the checks.** Some will be wrong for a given vault. If a user disagrees with a finding, drop the check from this run; don't argue.
- **Auto-fix conservatively.** When in doubt, surface for human resolution. Wiki integrity costs more to fix later than to leave alone now.
- **Cheap-first principle still applies.** Use `Grep` on frontmatter patterns, not full-page reads. Read full pages only when contradictions or stale-claim checks demand it.
- **Skip checks that don't apply.** If the vault has no `wiki/journal/`, skip check 12 entirely. Don't pad the report with N/A sections.
