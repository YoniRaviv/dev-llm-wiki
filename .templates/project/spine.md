# Spine — <what this pipeline is>

> Reference skeleton. `spine.md` is legal **only while a tracker is set** — it is the mirror of
> the plan gate. Not copied by `new-project.sh`; write it at promotion time.

The stages in pipeline order, and whether each works end to end. Every cell here is answerable
by reading or running the code — never by remembering the plan. If a cell cannot be checked
against the repo, it does not belong on this page.

**Repo this describes:** `<repo>/<path>` @ `<commit>`

**Reading rule: no stage starts while a lower-numbered stage reads NO.**

## The loop

| # | Stage | Works end to end? | Owner |
|---|---|---|---|
| 1 | <stage> | yes — <what you can run to see it> | — |
| 2 | <stage> | **partial** — <the exact gap> | `ABC-12` |
| 3 | <stage> | not built | — |

Every stage row must name a tracker ID or say plainly that nothing owns it (`—`), so a stage
can never read as a gap with no way to find the work.

Banned here, as everywhere outside the plan slots: dates, percentages, checkboxes, assignees,
`Phase:` / `Blocked on:` / `Next up:`.

## Where the line actually is

<Per-stage prose for anything the table can't hold: which of N cases have a rule, which ship
 inert, what a "yes" does and does not mean. Cite files and symbols so a reader can re-derive
 the claim.>

## Related

- Project page: `[[projects/<slug>]]`
- What and why: `02-prd.md` · how and when: the tracker's issues and milestones
