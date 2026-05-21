---
name: weekly-digest
description: Produce a markdown digest of activity across all projects, journals, and ingests over a date range. Stand-up generator and retrospective input. Use when the user says "weekly digest", "what did I do this week", "what's been happening", "weekly summary", "show me the week", "stand-up", "what's shipped recently", "/weekly-digest", or asks for any activity summary spanning multiple days. Reads `wiki/log.md`, journal entries in range, project `Current Status` blocks, and feature status changes — then writes a one-screen summary to `wiki/digests/<start>-to-<end>.md` and prints it inline for easy copy/paste into Slack, email, or retrospective notes. Default range: last 7 days. Configurable via "digest for last N days" or explicit dates.
---

# Weekly Digest

A read-only synthesis of what happened in the vault across a date range. Designed for the moments when you need to:

- Send a stand-up update to a team
- Reflect on the past week before planning the next
- Catch up after time away
- Build a retrospective input from raw activity

Reads: `wiki/log.md`, journals in range, active project `Current Status`, features that changed status, `.manifest.json` ingest events.
Writes: one digest file at `wiki/digests/<start>-to-<end>.md` (creates the folder if it doesn't exist) plus an inline output for the conversation.

Doesn't modify any other wiki page — pure synthesis.

## Prerequisites

- `wiki/log.md`, `wiki/index.md`, `wiki/hot.md` present.
- `.vault-meta.json` present (for date format).

If the vault isn't initialized, stop and point at `init-vault`.

## Step 1 — Parse the date range

Default: **last 7 days**, ending today inclusive.

Other forms the user may use:
- "digest for last N days" → end = today, start = today − N
- "digest for May" → start = 01-05-<year>, end = 31-05-<year>
- "since DD-MM-YYYY" → start = that date, end = today
- "from DD-MM-YYYY to DD-MM-YYYY" → explicit
- "this week" → start = last Monday, end = today

Use the vault's configured date format from `.vault-meta.json` for both display and parsing.

**Sanity checks:** range must be valid (end ≥ start), and if the range is >90 days, warn the user that the digest may be too long to be useful — ask whether to proceed.

## Step 2 — Gather inputs

In parallel:

1. **`wiki/log.md`** — parse `## [DD-MM-YYYY] <op> | <summary>` headers and filter to in-range entries. The log is your timeline.
2. **`wiki/journal/<DD-MM-YYYY>.md`** — read every journal page whose date falls in range. Extract the user-filled sections (`What I Worked On`, `Key Decisions`, `Blockers / Open Questions`, `Notes`) — those are signal.
3. **`wiki/projects/*.md`** — read frontmatter (status, last_updated) and the Current Status block for any project whose `last_updated` is in-range or whose `Last touched:` is in-range.
4. **Feature status changes** — for each project touched in range, glob `wiki/projects/<slug>/features/*.md` and find features whose frontmatter `shipped:` is in range, OR whose `last_updated` is in range with status `in-progress`.
5. **`.manifest.json`** — find ingest entries with `ingested_at` in range. Bucket by `source_type`.

## Step 3 — Synthesize the digest

Build the markdown using the template below. Skip any section that has no in-range content — don't pad with empty headings.

```markdown
# Weekly Digest — DD-MM-YYYY to DD-MM-YYYY

_<N> days, N_events log events, N_projects projects touched_

## Headlines

The most important things, in one sentence each. ~3-5 bullets. Lead with shipped features, then big decisions, then blockers worth knowing about.

- Shipped `[[projects/<slug>/features/<feature>]]` — <one-line why it matters>
- Decided to `[[projects/<slug>/decisions/<slug>]]` after evaluating <alt>
- Blocked on <thing> for project `[[projects/<slug>]]` — <since-date>

## Projects

### Active (touched this week)

For each project whose `Last touched:` is in range:

**`[[projects/<slug>]]`** — _Phase:_ <phase>; _Working on:_ <one line>
- Touched: <count> times. Most recent: DD-MM-YYYY
- <any feature movements from Step 4>
- <any blockers from Current Status>

### Paused / Untouched

Projects with `status: active` but `Last touched:` outside range (>14d cap is the LINT threshold; surface anything beyond range):
- `[[projects/<slug>]]` — last touched DD-MM-YYYY (X days ago)

(Skip this subsection if all active projects were touched in range.)

## Features

### Shipped this week
- `[[projects/<slug>/features/<feature>]]` — <one-line> (shipped DD-MM-YYYY)

### Advanced to in-progress
- `[[projects/<slug>/features/<feature>]]` — was planned, now in-progress

### Abandoned
- `[[projects/<slug>/features/<feature>]]` — <reason if known>

## Decisions logged
- `[[projects/<slug>/decisions/<slug>]]` — <one-line decision>

## Blockers (open)

Aggregated from active projects' `Blocked on:` fields:
- `[[projects/<slug>]]` — <blocker> (since DD-MM-YYYY)

## Sources ingested

Group by type:
- **Articles** (N): `[[sources/<a>]]`, `[[sources/<b>]]`, …
- **Tweets** (M): …
- **Repos** (K): …
- **Papers** (J): …
- **Research** (R): `[[sources/DD-MM-YYYY-research-<topic>]]` — N rounds, M sources fetched

## Patterns & technologies surfaced

New or substantially updated this week:
- `[[patterns/<slug>]]` — new (introduced via `[[sources/<a>]]`)
- `[[technologies/<slug>]]` — new

## Journal highlights

Pulled from `What I Worked On` and `Key Decisions` sections of in-range journal entries. Two-three bullets per active day, max. Skip empty sections silently.

**DD-MM-YYYY**
- <bullet from "What I Worked On">
- <bullet from "Key Decisions">

## Open questions surfaced

Aggregated from journal `Blockers / Open Questions` sections and project `Open Questions`:
- <one-liner> ([[projects/<slug>]])
```

### Synthesis guidance

- **Headlines section** is the load-bearing part. The user should be able to copy that section alone into Slack and have a useful update.
- **Don't pad.** If no features shipped this week, omit "Shipped this week" entirely — don't write "No features shipped".
- **Citation discipline.** Every project/feature/decision/source/pattern/technology reference uses `[[wikilinks]]`. Names alone aren't useful in a digest the user might paste into another tool.
- **Date format from `.vault-meta.json`.** Every date in the digest must match the vault's format.
- **Be honest about thin weeks.** If the vault was quiet, the digest can be 10 lines — that's fine. Don't fabricate activity to fill space.

## Step 4 — Write and present

### Write to file

Path: `wiki/digests/<start-date>-to-<end-date>.md` — using vault's date format, slugified (replace `:`/spaces with `-`).

Create `wiki/digests/` if it doesn't exist. Don't add it to `wiki/index.md` (digests are ephemeral — they're snapshots in time, not knowledge to cite).

Frontmatter:
```yaml
---
type: digest
range_start: DD-MM-YYYY
range_end: DD-MM-YYYY
generated: DD-MM-YYYY
---
```

### Inline output

Print the digest in the conversation too, so the user can copy-paste without opening the file. Wrap in a code fence so formatting is preserved when copied to Slack/email/etc.

### Log it

Append to `wiki/log.md`:

```
## [DD-MM-YYYY] digest | DD-MM-YYYY to DD-MM-YYYY — N projects, M features shipped, K decisions
```

Don't touch `wiki/hot.md` — digests are summaries of what's already there; they don't introduce new activity.

## Edge cases

- **Empty range** (no log entries, no journals, no manifest changes in range) — produce a one-line digest: "No activity recorded between <start> and <end>." Still write the file and log it.
- **Range crosses date format change** (rare — if the user reconfigured date format via init-vault mid-range) — use the current format for the output; parse historical dates leniently.
- **User asks for a project-scoped digest** ("digest for project X this week") — restrict all sections to that one project. Drop the "Projects" overview; keep Features / Decisions / Blockers / Journal subsections filtered.
- **Privacy note** — the journal entries include user-filled sections that may have private notes. Surface a one-line caveat at the bottom of inline output: *"Digest includes journal entries — review before sharing externally if any contain private context."* No caveat needed if no journals were read.

## Notes for the LLM

- **This is read-only synthesis.** Don't update project pages, feature pages, or any wiki content. The only writes are `wiki/digests/<file>.md` and the one `wiki/log.md` entry.
- **Lead with the headlines section.** The user's most common use case is copying that 5-bullet block into a stand-up channel.
- **Aggressively skip empty sections.** A clean digest is more useful than a complete one.
- **Don't run other ops first.** If the user hasn't run `claude-history-ingest` recently, the digest will reflect that — note it ("Note: last `claude-history-ingest` was N days ago; project statuses may be stale.") but don't auto-run upstream ops.
- **One-screen target.** Aim for the inline output to fit in ~50-80 lines of markdown. If the week was huge, that's fine — the file holds detail; the user can scroll. But the headlines section stays terse.
