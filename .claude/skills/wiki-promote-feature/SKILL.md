---
name: wiki-promote-feature
description: Promote a completed (or in-progress) feature from its working doc in `raw/projects/<slug>/features/<feature>.md` into a schema-compliant wiki page at `wiki/projects/<slug>/features/<feature>.md`. Use when the user says "promote feature X", "file the auth-flow feature", "the X feature is done — add it to the wiki", "wiki-promote-feature X", or otherwise asks to lift a finished feature from `raw/` into `wiki/`. Distills the working doc into the schema-required sections (Summary, Context, Decisions Made, Implementation Notes, Related Patterns, Related Features), surfaces decision-page and pattern-page candidates, cross-links the project page, and updates the index/log/hot. The raw doc stays in place — promotion is additive, not destructive.
---

# Wiki Promote Feature

Bridges the project lifecycle's `feature planning → ship → reflect` handoff. The working doc lives in `raw/projects/<slug>/features/<feature>.md` and accumulates messy details as you build; the wiki version is the distilled, schema-compliant record you'll cite from future projects.

This skill takes the working doc and produces the wiki page — without losing nuance and without flooding the wiki with unstructured content.

The raw file **stays in place** after promotion. It's the working doc; archiving it is a separate decision (offered at the end).

## When to use

- The user explicitly says "promote feature X" or similar.
- A feature was just marked `shipped` by `claude-history-ingest` and the user wants its wiki page created.
- The user finished a working doc in `raw/projects/<slug>/features/` and wants it filed.

## When NOT to use

- The feature is still in early ideation — the raw doc hasn't taken shape yet. Wait until it has a clear summary and at least one concrete decision.
- The user is just asking to *update* an existing wiki feature page. Direct edits or `wiki-ingest` are better fits.

## Prerequisites

- `wiki/index.md`, `wiki/topics.md`, `wiki/hot.md`, `wiki/log.md` present.
- `wiki/templates/feature.md`, `wiki/templates/decision.md`, `wiki/templates/pattern.md` present.
- The named project page exists at `wiki/projects/<slug>.md`. If not, surface this — don't auto-create.

## Step 1 — Locate the source

Resolve the user's reference to a concrete path:

- "promote `auth-flow` in `my-app`" → `raw/projects/my-app/features/auth-flow.md`
- "promote feature X" with no project named → search `raw/projects/*/features/X.md`. If multiple matches, ask the user which one.
- A folder-based feature (`raw/projects/<slug>/features/<feature>/`) — treat the folder's `plan.md` or `README.md` as the primary; mention the other files in Implementation Notes.

If the source doesn't exist, stop and tell the user.

## Step 2 — Read source + project context

Read in parallel:

1. The raw feature doc in full.
2. `wiki/projects/<slug>.md` — to confirm it exists, get the project's `topics:` for inheritance, see its Active Features section.
3. `raw/projects/<slug>/STATUS.md` — check if it references this feature.
4. `wiki/projects/<slug>/features/<feature>.md` — if it already exists, read it. Promotion in that case is a *merge*, not a fresh create.

## Step 3 — Ask for missing pieces

One `AskUserQuestion` call with the answers you couldn't infer from the doc:

1. **Status** — `planned` / `in-progress` / `shipped` / `abandoned`. Default to `shipped` if invoked after a completion event; otherwise ask. `header: "Status"`.
2. **Shipped date** (only if status is `shipped`) — default today. `header: "Shipped"`.
3. **Started date** — try to extract from the doc's first dated line, frontmatter, or STATUS.md. Ask if unclear. `header: "Started"`.
4. **Topics** — propose 3-7 topics by combining: the project's `topics:`, any explicit topics in the raw doc, and noun phrases from the doc body. Show your proposal; ask "Approve / edit / replace". `header: "Topics"`.

Cap at 4 questions. Date format comes from `.vault-meta.json`.

## Step 4 — Distill into schema sections

Build the wiki page content from the raw doc. Don't just copy — *distill*. The wiki page is the lasting reference; details that only mattered during the build belong in Implementation Notes, not Summary.

Required sections per `wiki/templates/feature.md`:

### Summary (one paragraph)

What this feature does and why it matters. Written for someone landing on this page cold in six months.

### Context

Why we built it. What it replaces or unblocks. Link to the project page and any relevant ideas/research:
- `[[projects/<slug>]]` — the parent project (always)
- `[[ideas/<idea-slug>]]` if the feature came from a wiki idea
- `[[sources/<source-slug>]]` if the feature was informed by an ingested source

### Decisions Made

Bulleted list of the decisions made during this feature's life. **For each significant decision, propose a standalone decision page** (Step 5). For minor decisions, leave them as bullets here:

```markdown
- Picked Stripe over Adyen — see [[projects/<slug>/decisions/use-stripe]]
- Inlined the retry logic instead of using a queue — see [[projects/<slug>/decisions/inline-retry]]
- Kept the form synchronous (minor) — needed for the user flow timing constraint
```

### Implementation Notes

How it actually got built. Surprises, dead ends, references to specific files or commits where useful. **This is the part that pays back on the next similar feature.** Be concrete:

```markdown
- Auth handshake lives in `src/auth/handshake.ts` — uses the token-rotation pattern
- Webhook signature verification was harder than expected — see [[patterns/webhook-signature-verification]]
- The integration test in `tests/auth.spec.ts` is worth reading first for any future work in this area
```

### Related Patterns

Patterns the feature *uses* or *introduces*. If the feature introduced a new reusable pattern, propose a pattern page (Step 5).

```markdown
- [[patterns/token-rotation]] — used for credential refresh
- [[patterns/idempotency-keys]] — introduced here, then used in payment-flow
```

### Related Features

Sibling features in the same project, or features in other projects that solve a similar problem.

```markdown
- [[projects/<slug>/features/payment-flow]] — depends on this feature's session model
- [[projects/other-project/features/auth-flow]] — different shape; we considered porting it
```

## Step 5 — Surface decision and pattern candidates

For each significant decision or reusable pattern you found, ask the user before creating standalone pages.

Format the question as a multi-select:

> **Create standalone pages for these?**
>
> Decisions:
> - [ ] `decisions/use-stripe.md` — Picked Stripe over Adyen for payment processing
> - [ ] `decisions/inline-retry.md` — Inlined retry logic instead of queueing
>
> Patterns:
> - [ ] `patterns/idempotency-keys.md` — Generalizable: introduced here, useful elsewhere

For each approved item, create the page from the appropriate template (`wiki/templates/decision.md` or `wiki/templates/pattern.md`) and fill in:
- **Context / Decision / Rationale** for decisions — extracted from the raw doc.
- **When to Use / How It Works / Gotchas** for patterns.

Update the new pages' frontmatter with the right `topics:` (inherited from the feature) and cross-link from the feature page.

## Step 6 — Write the wiki page

Path: `wiki/projects/<slug>/features/<feature-slug>.md`

Create the folder `wiki/projects/<slug>/features/` if it doesn't exist (with a `.gitkeep`-less direct write).

Write the file with proper frontmatter:

```yaml
---
project: <slug>
status: <chosen status>
topics: [topic-1, topic-2, topic-3]
started: <date>
shipped: <date or empty>
---
```

Body filled per Step 4.

**If the wiki page already exists**, merge:
- Don't overwrite Summary unless the user explicitly asks.
- Append new bullets to Decisions Made and Implementation Notes.
- Update frontmatter `shipped:` if it advanced.
- Update `topics:` only if the merged topics are a superset of the existing.

## Step 7 — Cross-link the project page

Edit `wiki/projects/<slug>.md`:

- **Active Features** section: if status is `planned` or `in-progress`, add `- [[projects/<slug>/features/<feature-slug>]] — one-line description`.
- If status is `shipped`, move the line out of Active Features. If a `## Shipped Features` section exists, append there; if not, *create it* below Active Features.
- If status is `abandoned`, log in a `## Abandoned Features` section (create if needed) — useful institutional memory.
- Bump `last_updated:` in frontmatter to today.
- Update **Current Status** block — bump `Last touched:`. If `Next up:` referenced this feature, update or clear it.

## Step 8 — Update tracking files

### `wiki/index.md`

Add the new feature page under the relevant project's section (or under a global Features section if you use one):

```
- [<Feature Title> (<project>)](projects/<slug>/features/<feature-slug>.md) — one-line description
```

Also add any decision or pattern pages you created in Step 5.

### `wiki/log.md`

Append:

```
## [DD-MM-YYYY] promote_feature | <feature-slug> (<project>) — status <new-status>; created N decision pages, M pattern pages
```

### `wiki/hot.md`

Update **Recent Activity**:

```
- **DD-MM-YYYY — Promoted <feature> (<project>)** — status <new-status>; surfaced <N> decisions, <M> patterns.
```

Rotate oldest out if >10 entries.

## Step 9 — Offer raw archival (optional)

Ask the user:

> "Archive the raw working doc? (Moves `raw/projects/<slug>/features/<feature>.md` → `raw/projects/<slug>/archive/<feature>.md`)"

- Default: **no** (keep both — raw is the working doc, wiki is the distilled record).
- If yes: `mv` the file. Update any `wiki/index.md` references if any.

## Edge cases

- **Folder-based feature** (`raw/projects/<slug>/features/<feature>/`) — promote the primary file (plan.md, README.md, or main.md). Reference the other files in Implementation Notes (e.g., "Detailed design lives in `raw/projects/<slug>/features/<feature>/design.md`").
- **Feature spans multiple projects** — pick a primary project, mention the others in Related Features. Don't create duplicate feature pages.
- **Existing wiki page is significantly different** — surface the conflict; let the user resolve before merging.
- **Raw doc is too thin** — if the working doc has only a one-line summary and nothing else, stop and ask if there's more context in another doc (notes, kanban, conversation history) before promoting a stub.

## Notes for the LLM

- **Distill, don't transcribe.** The raw doc is the working doc; the wiki page is the lasting reference. They serve different purposes; copying verbatim defeats the point.
- **Be precise about what's a decision vs an implementation detail.** "We used Stripe" is a decision. "We used the Stripe Node SDK v14" is an implementation note.
- **Cross-linking is mandatory.** A feature page that doesn't link to its project, its decisions, or any related patterns is broken — fix before considering the promotion done.
- **Date format from `.vault-meta.json`.** All dates in frontmatter and log entries must match.
- **If `claude-history-ingest` already moved the feature's status to `shipped` before this skill ran**, don't argue with that — accept and proceed. If the timeline disagrees, surface it to the user.
