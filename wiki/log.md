---
title: Event Log
---

# Event Log

Append-only log of operations the LLM has performed on this wiki. One section per event. Newest at the bottom.

Format:
- `## [DD-MM-YYYY] ingest | <source title>`
- `## [DD-MM-YYYY] query | <short question>`
- `## [DD-MM-YYYY] surface | <topic> → [[page1]], [[page2]]`
- `## [DD-MM-YYYY] lint | <one-line summary>`

---
