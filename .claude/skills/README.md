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

## Recommended skills for this workflow

The vault works fine without any skills — the operations in `CLAUDE.md` (INGEST, QUERY, SURFACE, LINT, BOOTSTRAP) are baseline behaviors. But these skills make daily use noticeably better:

- **research** — autonomous multi-round web research that files findings directly into `wiki/`.
- **ingest-url** — fetch a URL, distill the content, and file it as a wiki source page in one step.
- **wiki-capture** — turn the current conversation into a permanent wiki note.
- **cross-linker** — scan the wiki for missing `[[wikilinks]]` between related pages.
- **wiki-status** — quick health/coverage dashboard for the vault.

Add them as you decide which ones you actually use. Start with none and pull them in deliberately — extra skills add noise to the LLM's choice surface, which can hurt more than the skills help.

## Where to find skills

- This vault's curated set (when filled in): browse the folders here.
- Skills shipped with Claude Code or plugins: see Claude Code's docs.
- Build your own: see the `skill-creator` skill if available, or just drop a folder with a `SKILL.md` here.
