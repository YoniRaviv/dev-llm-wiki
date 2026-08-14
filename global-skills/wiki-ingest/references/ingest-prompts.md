# Ingest Prompt Templates

The mental frameworks for distilling a source into vault pages. Page types are the ones this
vault actually has — see `CLAUDE.md` for each one's schema.

## Knowledge Extraction Frame

When reading a source, ask:

1. **What are the 3–5 most important ideas here?**
   A reusable technique → `wiki/patterns/`. A tool or library → `wiki/technologies/`.
   A cross-cutting subject you keep returning to → an existing `wiki/domains/` hub.

2. **Was a choice made, with alternatives rejected?**
   → `wiki/decisions/<slug>.md`, with `projects: [<slug>]`. A decision without its *why* and its
   rejected alternatives is not a decision record.

3. **Is this a thing we might build?**
   → `wiki/ideas/<slug>.md`. Only promote to `projects/` when the user decides to pursue it.

4. **Did something actually ship?**
   → `projects/<slug>/shipped/<feature>.md` with `status: shipped`. If it is in flight, it is a
   tracker issue — write nothing.

5. **What claims does this make?**
   Each needs attribution. If it contradicts an existing page, flag it — don't quietly overwrite.

6. **How does this connect to what the vault already knows?**
   The most important question. The vault compounds through connections, not volume.

## Synthesis Frame

When a source covers ground existing pages already cover:

- Don't duplicate — synthesize.
- Agrees with existing content → strengthen the claim, add the attribution.
- Disagrees → `> ⚠️ Contradiction: …` naming both sides and which is better evidenced.
- Adds nuance → weave it into the existing narrative rather than appending a new section.
- Already ~70% covered → say so, ingest only the delta. That is a good outcome.

## Cross-Reference Discovery

After extracting, look for these connection shapes and add the links both ways where it makes sense:

- **Is-a** — "a determinism gate is a kind of approval hook" → pattern → pattern
- **Uses** — "the opportunity agent uses GSC data" → project → technology
- **Contrasts-with** — "deterministic scoring vs LLM ranking" → mutual links
- **Part-of** — "stage 4 of the SEO suite loop" → project → programme project
- **Superseded-by** — "this replaced the merged audit agent" → link the `archive/` predecessor
- **Evidence-for** — a source backing a decision → decision page `_Sources:_` line

## What never goes in

- Execution state of any kind — `Working on`, `Next up`, `Blocked on`, `Phase:`, % complete.
- A plan. Sequence, estimates and task breakdowns live in the tracker.
- A new file under `projects/<slug>/` outside the six legal slots.
