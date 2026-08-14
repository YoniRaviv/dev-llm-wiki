---
title: Topics
updated: DD-MM-YYYY
---

# Topics — Controlled Vocabulary

Every wiki page's `topics:` frontmatter draws from this list. The vocabulary stays tight on purpose:
SURFACE matches conversation context to wiki pages by topic overlap, and a domain hub fires on its
`trigger_topics:`. Noise here means noisy citations.

## Rules

- Lowercase kebab-case (`s3-uploads`, not `S3 Uploads` or `s3_uploads`).
- Noun phrases, not adjectives (`async-state`, not `asynchronous`).
- 3–7 topics per page.
- When you add a topic to any page, append it here **in the same write**, with a one-line
  description. A topic with no description drifts into meaning whatever the last page needed.
- Merge near-duplicates aggressively — `s3-uploads` and `s3-storage` should not both exist.
- One entry per line, in this exact shape (the lint skill parses it):

  ```
  - `topic-name` — what this topic covers, and where its edge is.
  ```

## Vocabulary

<!--
Seed this as you ingest. `init-vault` can populate a starter set for your stack.
Keep it flat and alphabetical — grouping headings drift faster than the list does, and the
lint skill reads the whole file as one namespace anyway.

Examples of the shape, including the useful part — the boundary:

- `api-design` — HTTP and RPC interface design: resource shape, versioning, error contracts.
- `async-state` — client-side handling of in-flight server state: caching, invalidation,
  optimistic updates. Not general state management.
- `observability` — traces, metrics, structured logs and their correlation. Use for the
  instrumentation, not for the incident.
-->
