---
name: wiki-lint
description: >
  Audit and maintain the health of the Dev Brain vault. Use when the user says "lint the wiki",
  "wiki health check", "audit my notes", "what needs fixing", "clean up the wiki", or wants to find
  orphaned pages, broken wikilinks, contradictions, stale claims, missing decision/pattern pages, or
  topic-vocabulary drift. Runs the structural gate first, then the semantic checks it cannot do.
---

# LINT — vault health audit

The vault is `{{VAULT_PATH}}`. Read `CLAUDE.md` first — it is the schema this
audits against. Two layers:

- **Structural** — `.scripts/vault-check.py` already encodes every mechanical invariant. Run it;
  do not re-implement it by hand.
- **Semantic** — everything below. These need judgement and reading, so scope them.

**Scope your reads.** Prefer frontmatter-scoped greps and section-anchored reads over full-page
reads. Reading every content page to lint it is the failure mode this vault is built to avoid.

## Step 1 — Structural gate

```bash
cd {{VAULT_PATH}} && python3 .scripts/vault-check.py
```

Exit 0 means clean. Otherwise it reports, per check: `whitelist`, `plan-gate`, `spine-gate`,
`spine-owner`, `prd-purity`, `tracker-state`, `vault-skills`, `secrets`, `today-committed`,
`shipped-status`, `broken-links`, `orphans`.

`broken-links` and `orphans` only run on a full scan, not in `--staged` (pre-commit) mode — a
brand-new project page with no inbound wikilink yet will show up here without having blocked a
commit. Link it; do not exempt it.

Fix what it reports before going further — a broken link makes half the semantic checks noisy.
**Never loosen a check to make it pass.** If a check is genuinely wrong, say so and explain why;
its rules are load-bearing, and the same script backs the pre-commit hook.

For orphans specifically: link the page from a related page or from `wiki/index.md`. Do not exempt it.

## Step 2 — Topic vocabulary

`wiki/topics.md` is a controlled vocabulary. Every `topics:` entry must be listed there.

```bash
cd {{VAULT_PATH}}
python3 - <<'EOF'
import os,re
used={}
for dp,dn,fn in os.walk('.'):
    dn[:]=[d for d in dn if d not in ('.git','.obsidian','node_modules','docs','.scripts','.templates','.claude','.context','.superpowers')]
    for f in fn:
        if not f.endswith('.md'): continue
        p=os.path.join(dp,f)
        if os.path.relpath(p,'.')=='CLAUDE.md': continue
        m=re.search(r'^topics:\s*\[(.*?)\]',open(p,encoding='utf-8',errors='replace').read(),re.M|re.S)
        if not m: continue
        for x in m.group(1).split(','):
            x=x.strip().strip('`"\'')
            if x: used.setdefault(x,[]).append(os.path.relpath(p,'.'))
listed=set(re.findall(r'^- `([^`]+)`', open('wiki/topics.md',encoding='utf-8').read(), re.M))
u=set(used)
print("UNKNOWN (used, not listed):", sorted(u-listed) or "none")
print("UNUSED (listed, not used):", sorted(listed-u) or "none")
print("SINGLE-USE:", sorted(t for t in u if len(used[t])==1))
EOF
```

- **Unknown** → add to `topics.md` with a one-line description, in the same pass.
- **Single-use** → consolidation candidates. Report, don't auto-merge.
- **Near-duplicates** → eyeball the list for synonym pairs (`s3-uploads` vs `s3-storage`). Flag with ❓.

## Step 3 — Missing pages the content is asking for

Grep-driven, cheap:

| Signal | Missing page |
|---|---|
| A decision referenced in 2+ pages with no `wiki/decisions/<slug>.md` | decision record |
| A technique appearing in 2+ `shipped/` records with no `wiki/patterns/<slug>.md` | pattern |
| A tool/library named repeatedly with no `wiki/technologies/<slug>.md` | technology |
| A concept in 2+ pages with no page of its own | concept page |

Report as suggestions with the evidence pages. Do not create pages unprompted — creating one
requires an `index.md` entry and an inbound wikilink in the same write.

## Step 4 — Contradictions and stale claims

- **Contradictions** — focus on pages sharing `topics:` or heavily cross-linked. Where two pages
  make incompatible claims, add a `> ⚠️ Contradiction: …` blockquote on the newer page naming both,
  rather than silently picking a winner.
- **Stale claims** — a page asserting something a newer `wiki/sources/` page contradicts. Compare
  the source's `date_ingested:` against the claim.
- **Present-tense claims about archived projects** — `archive/` projects are dead. Any page in
  `wiki/` or `projects/` describing one as active is a bug. Check `technologies/` and `domains/`
  especially; they age this way.

## Step 5 — Date and filename conventions

```bash
cd {{VAULT_PATH}}
# journal filenames must be DD-MM-YYYY.md
ls wiki/journal | grep -vE '^[0-9]{2}-[0-9]{2}-[0-9]{4}\.md$' || echo "journal: ok"
# sources must be DD-MM-YYYY-<slug>.md
ls wiki/sources | grep -vE '^[0-9]{2}-[0-9]{2}-[0-9]{4}-.+\.md$' || echo "sources: ok"
# notes must be DD-MM-YYYY-<topic>.md
find projects archive -path '*/notes/*.md' | grep -vE '/[0-9]{2}-[0-9]{2}-[0-9]{4}-' || echo "notes: ok"
# YYYY-MM-DD anywhere in vault content is wrong — the vault is DD-MM-YYYY
grep -rlE '\b20[0-9]{2}-[0-9]{2}-[0-9]{2}\b' --include='*.md' wiki projects archive meetings | head
```

`docs/` is exempt — plan and spec *filenames* use `YYYY-MM-DD` by superpowers convention.

## Step 6 — Domain hubs (`wiki/domains/*.md`)

- Every wikilink resolves (Step 1 covers this).
- `updated:` is not older than the newest `wiki/sources/` page whose `topics:` hit the hub's
  `trigger_topics:`.
- No Distilled Core claim is contradicted by a newer source — flag with ⚠️.
- Any page on a `trigger_topics:` subject is present *somewhere* in the hub (Reading Index,
  Landscape, or a Core `_Sources:_` line).
- Distilled Core ≤ 250 lines. Over that, flag ❓ for re-distillation.
- Archived projects appear under a past-tense `### Archived` sub-list in Landscape.

## Step 7 — Index consistency

`wiki/index.md` should list every page in `projects/`, `wiki/decisions|patterns|technologies|domains|ideas|sources`,
and `archive/`. Check for entries pointing at deleted files, and files missing an entry. Descriptions
should still match the page.

## What NOT to check

This vault deliberately has none of these; flagging them is a bug in this skill:

- `Current Status`, `Last touched`, `Working on`, `Next up`, `Blocked on` — the tracker owns
  execution. Their *presence* under `projects/` is a violation, not a gap (Step 1's
  `tracker-state` catches it).
- `wiki/hot.md`, `wiki/today.md` — they do not exist by design. `today.md` lives at the vault
  root, is derived, and is gitignored.
- Staleness of `archive/` pages — they are epitaphs, not open work.
- `raw/` wikilinks — web-clipper artifacts, and `CLAUDE.md` forbids editing `raw/`.
- Anything under `docs/`, `.scripts/`, `.templates/`, `.obsidian/`, `.claude/`, `.context/`.

## Output

```markdown
## Vault Health Report — DD-MM-YYYY

### Structural (vault-check.py)
✓ clean   — or the per-check breakdown

### Topic Vocabulary
- unknown: …   · single-use: …   · near-duplicate ❓: …

### Missing Pages (N)
| Signal | Suggested page | Evidence |

### Contradictions (N)
### Stale Claims (N)
### Convention Violations (N)
### Domain Hubs (N)
### Index Issues (N)
```

Fix what you can autonomously. Flag anything needing a judgement call with ❓.

Then append one line to `wiki/log.md`:

```
## [DD-MM-YYYY] lint | <one-line summary>
```

`log.md` records only `ingest`, `query`, `lint`. Never write status into it.
