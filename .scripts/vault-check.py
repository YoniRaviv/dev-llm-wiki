#!/usr/bin/env python3
"""Vault structural invariants. Exit 0 clean, 1 on violation.

--staged   check only files staged in git (pre-commit mode)
--quiet    suppress the OK line

Every check here encodes a rule from CLAUDE.md. Read that file before changing one:
loosening a check to make a commit pass defeats the point of having a gate.
"""
import os, re, sys, subprocess, collections

VAULT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLOTS_FILE = {"00-idea.md", "01-research.md", "02-prd.md", "03-plan.md", "spine.md"}
SLOTS_DIR = {"shipped", "notes", "assets", "roadmaps", "features"}

# The how/when slots. Legal only while `tracker: none` — with no tracker the vault holds
# the only copy of the plan, and deleting it deletes the plan. Once a project reaches a
# tracker, the tracker owns how/when and these must move there.
PLAN_SLOTS = {"03-plan.md", "roadmaps", "features"}

# Tooling, not vault content — see "Directories vault operations ignore" in CLAUDE.md.
# These are never ingested, indexed, wikilinked, linted, or counted as orphans. Their
# markdown is *about* the vault (specs, plans, templates), so its [[example]] links and
# documented secret-probe strings are prose, not claims about real pages.
# The content zones — raw/ wiki/ projects/ archive/ meetings/ — are all still checked.
IGNORE_DIRS = ("docs/", ".scripts/", ".templates/", ".obsidian/", ".claude/",
               ".context/", ".superpowers/", ".playwright-mcp/")
IGNORE_FILES = {"CLAUDE.md", "README.md"}


def ignored(rel):
    p = rel.replace(os.sep, "/")
    return p in IGNORE_FILES or p.startswith(IGNORE_DIRS)

SECRET = re.compile(
    r"AKIA[0-9A-Z]{16}"
    r"|sk-ant-[A-Za-z0-9_-]{20,}"
    r"|BEGIN [A-Z ]*PRIVATE KEY"
    r"|^[ \t]*password:[ \t]*\S",
    re.M,
)
# Tracker state — scoped to projects/ only. wiki/ prose legitimately says "Phase A" / "70%".
# Matches the status *label* at line start regardless of bold markup: `Blocked on:`,
# `**Blocked on:** none` (colon inside the asterisks) and `**Blocked on**: none` (outside).
# The trailing colon is required — without it this also fires on ordinary prose and diagram
# labels ("Phase 1: ANALYZE", "Phase plans written", "Phase State Machine"), which are not state.
STATE = re.compile(r"^\s*\**(Blocked on|Next up|Working on|Phase)\**\s*:", re.M)
PRD_TASK = re.compile(r"^\s*[-*] \[[ xX]\]", re.M)
PRD_PHASE = re.compile(r"^#+\s*Phase\b", re.M | re.I)
PRD_DATE = re.compile(r"\b\d{2}-\d{2}-\d{4}\b")
# A date inside a filename or path is an identifier, not a schedule. The vault's own
# convention names notes `notes/DD-MM-YYYY-<topic>.md`, and a PRD citing its evidence is
# not the "signature of a plan" the date ban exists to catch. Everything else still fails.
PRD_DATE_IN_PATH = re.compile(r"[\w./-]*/[\w.-]*\b\d{2}-\d{2}-\d{4}\b[\w.-]*|\b[\w-]*\d{2}-\d{2}-\d{4}[\w-]*\.(?:md|html|csv|pdf)\b")
WIKILINK = re.compile(r"\[\[([^\]|#]+)")

# A [[…]] inside code is documentation *about* link syntax, not a link. log.md and the
# journal both write patterns like `[[projects/<slug>...]]` in backticks on purpose.
CODE_FENCE = re.compile(r"^```.*?^```", re.M | re.S)
CODE_SPAN = re.compile(r"`[^`\n]*`")


def wikilinks(text):
    return WIKILINK.findall(CODE_SPAN.sub("", CODE_FENCE.sub("", text)))


def staged_files():
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        cwd=VAULT, capture_output=True, text=True,
    ).stdout
    return [l for l in out.splitlines() if l.strip()]


def all_files():
    found = []
    for dp, dn, fn in os.walk(VAULT):
        dn[:] = [d for d in dn if d not in (".git", ".obsidian", "node_modules")]
        for f in fn:
            found.append(os.path.relpath(os.path.join(dp, f), VAULT))
    return found


def read(rel):
    try:
        with open(os.path.join(VAULT, rel), encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except (OSError, IsADirectoryError):
        return None


def check_whitelist(files, add):
    """Nothing may exist in a project folder but the legal slots."""
    for rel in files:
        parts = rel.split(os.sep)
        if parts[0] != "projects" or len(parts) < 2:
            continue
        if len(parts) == 2:
            if parts[1] != ".gitkeep" and not parts[1].endswith(".md"):
                add("whitelist", f"{rel} — only <slug>.md may sit beside project folders")
            continue
        slot = parts[2]
        if len(parts) == 3:
            if slot not in SLOTS_FILE:
                add("whitelist", f"{rel} — '{slot}' is not a legal slot")
        elif slot not in SLOTS_DIR:
            add("whitelist", f"{rel} — '{slot}/' is not a legal slot dir")


TRACKER = re.compile(r"^tracker:\s*(\S+)", re.M)


def tracker_of(slug):
    """The `tracker:` value on projects/<slug>.md — 'none' when the page or field is absent."""
    t = read(f"projects/{slug}.md") or ""
    m = TRACKER.search(t.split("---", 2)[1] if t.startswith("---") else t)
    return m.group(1) if m else "none"


def check_plan_gate(files, add):
    """A plan slot may only exist while the project has no tracker."""
    seen = set()
    for rel in files:
        parts = rel.replace(os.sep, "/").split("/")
        if len(parts) < 3 or parts[0] != "projects" or parts[2] not in PLAN_SLOTS:
            continue
        slug, slot = parts[1], parts[2]
        if (slug, slot) in seen:
            continue
        seen.add((slug, slot))
        tracker = tracker_of(slug)
        if tracker != "none":
            add("plan-gate", f"projects/{slug}/{slot} — tracker is '{tracker}': how/when belongs there")


def check_spine(files, add):
    """The mirror of check_plan_gate: a spine may only exist once a tracker owns the issues.

    A trackerless project keeps its plan slots, which already carry the build order — a
    spine would duplicate them. The spine exists to restore ordering a tracker discarded.

    Every table row must also name a tracker ID or say plainly that nothing owns it, so a
    stage can never read as a gap with no way to find the work.
    """
    for rel in files:
        if not re.fullmatch(r"projects/([^/]+)/spine\.md", rel):
            continue
        slug = rel.split("/")[1]
        if tracker_of(slug) == "none":
            add("spine-gate", f"{rel} — tracker is 'none': the plan slots hold the order")
        t = read(rel)
        if t is None:
            continue
        for line in t.splitlines():
            # A stage row opens with `| <digit>` — the separator and header rows do not.
            if not re.match(r"^\|\s*\d+\s*\|", line):
                continue
            if not re.search(r"[A-Z]{2,}-\d+|—|not built", line):
                add("spine-owner", f"{rel} — stage row names no owner: {line.strip()[:60]}")


def check_prd(files, add):
    for rel in files:
        if not re.fullmatch(r"projects/[^/]+/02-prd\.md", rel):
            continue
        t = read(rel)
        if t is None:
            continue
        if PRD_TASK.search(t):
            add("prd-purity", f"{rel} — checkbox: tasks belong in the tracker")
        if PRD_PHASE.search(t):
            add("prd-purity", f"{rel} — '## Phase': phases are tracker milestones")
        bare = PRD_DATE_IN_PATH.sub("", CODE_SPAN.sub("", CODE_FENCE.sub("", t)))
        m = PRD_DATE.search(bare)
        if m:
            add("prd-purity", f"{rel} — a date ({m.group(0)}): schedule belongs in the tracker")


def check_state(files, add):
    for rel in files:
        if not rel.startswith("projects/") or not rel.endswith(".md"):
            continue
        # Plan slots are the how/when by definition — check_plan_gate already bounds them
        # to trackerless projects, so a phase label inside one is the plan, not stale state.
        parts = rel.replace(os.sep, "/").split("/")
        if len(parts) >= 3 and parts[2] in PLAN_SLOTS:
            continue
        t = read(rel)
        if t is None:
            continue
        m = STATE.search(t)
        if m:
            add("tracker-state", f"{rel} — '{m.group(1)}:' is tracker state")


# Any harness's skills dir, not just .claude — a vault can accumulate several copies of the
# same skills (.claude/skills, .agents/skills, …). Guarding only one is useless.
SKILLS_DIR = re.compile(r"^\.[A-Za-z0-9_-]+/skills/")


def check_skills(files, add):
    for rel in files:
        if SKILLS_DIR.match(rel.replace(os.sep, "/")):
            add("vault-skills", f"{rel} — skills live in ~/.claude/skills/, never in the vault")


# Add a filename here to exempt it from the credential scan — and only with a reason
# beside it. Anything not listed is still checked, including files added later.
SECRET_EXEMPT = set()


def check_secrets(files, add):
    for rel in files:
        if rel in SECRET_EXEMPT or ignored(rel):
            continue
        if rel.endswith((".png", ".jpg", ".jpeg", ".pdf", ".excalidraw")):
            continue
        t = read(rel)
        if t and SECRET.search(t):
            add("secrets", f"{rel} — possible credential")


def is_today(rel):
    """today.md is derived wherever it sits — match by basename, not just the root path."""
    return os.path.basename(rel) == "today.md"


def check_today(files, add, staged_mode):
    """today.md is derived and gitignored. Its mere presence on disk is correct and expected —
    only staging or having committed it is a violation."""
    if not staged_mode:
        tracked = subprocess.run(
            ["git", "ls-files", "-z", "*today.md"],
            cwd=VAULT, capture_output=True, text=True,
        ).stdout
        files = [f for f in tracked.split("\0") if f.strip()]
    for rel in files:
        if is_today(rel):
            add("today-committed", f"{rel} is a derived view — never commit it")


def check_shipped(files, add):
    for rel in files:
        if not re.fullmatch(r"projects/[^/]+/shipped/.+\.md", rel):
            continue
        t = read(rel)
        if t is None:
            continue
        if not re.search(r"^status:\s*shipped\s*$", t, re.M):
            add("shipped-status", f"{rel} — shipped/ requires 'status: shipped'")


def _link_index(every):
    """Map every resolvable wikilink target to itself, Obsidian-style."""
    md = [f for f in every if f.endswith(".md")]
    idx = set()
    for rel in md:
        noext = rel[:-3]
        idx.add(noext)
        idx.add(os.path.basename(noext))
        # wiki/ pages are addressed relative to wiki/
        if noext.startswith("wiki" + os.sep):
            idx.add(noext[len("wiki" + os.sep):])
    return idx


def check_links(every, add):
    # The index spans every file — a wiki page may legitimately link a tooling doc.
    # Only the *scanning* of ignored files is skipped: their [[…]] are syntax examples.
    #
    # raw/ is excluded as a link *source* (still a valid link target). It is clipped
    # source material whose [[…]] are Web Clipper artifacts from URLs and bylines
    # ([[blog.jetbrains]], [[platform.openai]], [[Some Author]]) rather than vault
    # links — and CLAUDE.md forbids the agent editing raw/, so they are unfixable by
    # design. The link graph this check defends is wiki/ + projects/ + archive/ + meetings/.
    idx = _link_index(every)
    for rel in [f for f in every if f.endswith(".md")]:
        if is_today(rel) or ignored(rel) or rel.startswith("raw" + os.sep):
            continue
        t = read(rel)
        if t is None:
            continue
        for raw in wikilinks(t):
            tgt = raw.strip().rstrip("/")
            if not tgt or tgt.startswith(("http", "#")):
                continue
            if tgt not in idx and os.path.basename(tgt) not in idx:
                add("broken-links", f"{rel} → [[{tgt}]]")


def check_orphans(every, add):
    # Only the compounding layer and project pages must be reachable. Files inside a
    # project folder (00-idea, notes/, assets/, shipped/) are reached via their project
    # page or by path — flagging them as orphans would be noise, not signal.
    def in_scope(f):
        if not f.endswith(".md"):
            return False
        if f.startswith("wiki" + os.sep):
            return True
        return bool(re.fullmatch(r"projects/[^/]+\.md", f))

    md = [f for f in every if in_scope(f)]
    linked = set()
    for rel in [f for f in every if f.endswith(".md")]:
        # An ignored tooling doc mentioning a page does not rescue it from orphanhood.
        if ignored(rel):
            continue
        t = read(rel)
        if t is None:
            continue
        for raw in wikilinks(t):
            tgt = raw.strip().rstrip("/")
            linked.add(tgt)
            linked.add(os.path.basename(tgt))
    exempt = {"wiki/index.md", "wiki/log.md", "wiki/topics.md"}
    for rel in md:
        if rel in exempt or is_today(rel) or os.sep + "journal" + os.sep in rel:
            continue
        noext = rel[:-3]
        cands = {noext, os.path.basename(noext)}
        if noext.startswith("wiki" + os.sep):
            cands.add(noext[len("wiki" + os.sep):])
        if not (cands & linked):
            add("orphans", rel)


def main():
    staged_mode = "--staged" in sys.argv
    quiet = "--quiet" in sys.argv
    every = all_files()
    scope = staged_files() if staged_mode else every

    problems = collections.defaultdict(list)

    def add(check, msg):
        problems[check].append(msg)

    check_whitelist(scope, add)
    check_plan_gate(scope, add)
    check_prd(scope, add)
    check_state(scope, add)
    check_skills(scope, add)
    check_secrets(scope, add)
    check_today(scope, add, staged_mode)
    check_shipped(scope, add)
    check_spine(scope, add)
    if not staged_mode:
        check_links(every, add)
        check_orphans(every, add)

    if not problems:
        if not quiet:
            print("vault-check: ✓ clean")
        return 0

    total = sum(len(v) for v in problems.values())
    print(f"vault-check: ✗ {total} violation(s)\n")
    for check in sorted(problems):
        items = problems[check]
        print(f"  [{check}] {len(items)}")
        for m in items[:15]:
            print(f"      {m}")
        if len(items) > 15:
            print(f"      … and {len(items)-15} more")
        print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
