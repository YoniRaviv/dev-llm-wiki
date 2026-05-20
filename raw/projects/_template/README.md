# Project Template

Skeleton for new projects under `raw/projects/`. Copy this folder when starting something new — easiest via `.scripts/new-project.sh <slug>`.

## Structure

```
<project-slug>/
├── STATUS.md         ← quick-glance status, touched most often
├── 00-idea.md        ← initial spark / brief
├── 01-research.md    ← research, competitive analysis, tech exploration
├── 02-prd.md         ← what + why
├── 03-plan.md        ← high-level how
├── kanban.md         ← Obsidian Kanban for small tasks
├── features/         ← one .md per feature, or a sub-folder for complex features
├── roadmaps/         ← versioned roadmaps (v1.md, v2.md, ...)
├── notes/            ← dated notes (DD-MM-YYYY-<topic>.md)
└── archive/          ← superseded docs worth keeping
```

## To start a new project

```sh
.scripts/new-project.sh <new-slug>
# or, manually:
cp -R raw/projects/_template raw/projects/<new-slug>
```

Then open `STATUS.md` and start filling in. Not every project needs all spine docs — `01-research.md` is optional; some projects are pure design or pure plan. The point is consistency, not bureaucracy.

## Conventions

- Folder slug: lowercase kebab-case, matches the wiki slug.
- Feature files: `features/<feature-slug>.md` (simple) or `features/<feature-slug>/` (complex, with its own plan.md, design.md, etc.).
- Notes: `notes/DD-MM-YYYY-<topic>.md`.
- Roadmaps: `roadmaps/v<N>.md` or `roadmaps/YYYY-MM-DD.md` — pick one per project.
- Archive: same filename as original; move when superseded.
