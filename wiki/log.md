---
title: Event Log
---

# Event Log

Append-only log of wiki operations. One section per event. Newest at the bottom.

Three entry types, and only these three:
- `## [DD-MM-YYYY] ingest | <source title>`
- `## [DD-MM-YYYY] query | <short question>`
- `## [DD-MM-YYYY] lint | <one-line summary>`

**Never write status here.** Not progress, not "still working on X", not a phase. This log records
what the vault *did*, not what the work is doing — that lives in the tracker.

---
