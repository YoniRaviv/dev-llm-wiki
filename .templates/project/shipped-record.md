---
project: <project-slug>
status: shipped
topics: []
started: DD-MM-YYYY
shipped: DD-MM-YYYY
summary: "<one sentence: what now works that didn't before>"
shipped_in: <PR or commit ref>
---

## Summary

<What shipped, stated as a fact about the artifact. `status: shipped` is the only legal status
 in this folder — a record is written after the fact, never as a placeholder for work in
 flight. Put PR and commit refs in `shipped_in:`, never in `status:`.>

## Context

<Why it was built this way. What the alternative was.>

## Decisions Made

- **<decision>** — <the why, in one line>. Promote to `wiki/decisions/<slug>.md` if it will
  outlive this feature.

## Implementation Notes

<Gotchas, footguns, non-obvious fixes. The highest-value section a year from now.>

## Related

- `[[projects/<project-slug>]]`
- Patterns this is an instance of: `[[patterns/<slug>]]`
