# Skills

Project-scoped skills for this vault. Skills are automatically discovered by Claude Code when you run it from this directory.

## Layout

Each skill is its own folder with a `SKILL.md` at the root:

```
.claude/skills/
├── README.md            ← this file
├── <skill-name>/
│   └── SKILL.md
└── <another-skill>/
    ├── SKILL.md
    └── references/      ← any extra files the skill needs
```

`SKILL.md` is a markdown file with frontmatter that names and describes the skill:

```markdown
---
name: <skill-name>
description: One-line description of when this skill should be used.
---

# <Skill Name>

(The body of the skill — instructions Claude follows when the skill is invoked.)
```

## Bundled skills

The vault works fine without any skills — the operations in `CLAUDE.md` (INGEST, QUERY, SURFACE, LINT, BOOTSTRAP) are baseline behaviors. These 8 skills, bundled here and auto-discovered when you run Claude Code from the vault, make daily use noticeably better:

- **init-vault** — one-time personalization after cloning the template.
- **wiki-ingest** — distill any source (article, tweet, repo, PDF, screenshot) into `wiki/sources/` and propagate it.
- **wiki-query** — answer questions from the wiki with citations.
- **wiki-promote-feature** — lift a finished feature from `raw/` into a schema-compliant `wiki/` page.
- **weekly-digest** — synthesize activity across journals/projects/ingests into a copy-pasteable recap.
- **wiki-status** — delta + graph-insights dashboard for the vault.
- **wiki-lint** — health audit (orphans, broken links, stale projects, topic vocabulary).
- **cross-linker** — write-heavy companion to lint; inserts the missing `[[wikilinks]]`.

## Skills that live elsewhere

- **Marketplace** — `idea-deep-research`, `claude-history-ingest`, `standup`, `meeting-prep` install from [`YoniRaviv/claude-skills`](https://github.com/YoniRaviv/claude-skills) (`/plugin marketplace add YoniRaviv/claude-skills`). They're referenced here but not bundled, so they stay auto-updatable.
- **Global** — `send-to-wiki` lives in `../../global-skills/` and installs to `~/.claude/skills/` via `.scripts/install-global-skills.sh`.
- **Build your own** — drop a folder with a `SKILL.md` here, or use a `skill-creator` skill if you have one.
