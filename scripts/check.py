#!/usr/bin/env python3
"""The app's own checks, run before anything is shown to the owner:

    python3 scripts/check.py [<folder> …] [--status sent] [--all]

- the brand record the work draws on exists (brand/, public/)
- every creatives/<YYYY-MM-DD-slug>/creative.md has the fields the
  marketing skill lists, a known kind, platform and status, and every file
  it lists
- every claim it cites is a numbered entry in claims.md, and every entry
  there names a source file that exists
- the copy passes the tropes skill's script and the platform's text limits
- the platform sheet a draft is built against is not stale (90 days);
  "Do not build on a stale sheet" (specs/README.md), so that is a finding

Then it lists the creatives it checked, newest first, one line each:
folder, status, kind and platform (the newest 20, and the first 20
findings, unless --all); notes that do not fail the check come last. `--status
sent` checks and lists only what is waiting for the owner's approval.

Exit 1 with the findings when something is off. A finding is fixed at
its source before the owner sees the work, never explained away.
"""

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import FOLDER, KINDS, PLATFORMS, STATUSES, Parser, creative_dirs, die, read_record, root  # noqa: E402

# The shared copy check (the tropes skill), run over every copy field at once.
TROPES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".claude", "skills", "tropes", "tropes.mjs")
TROPES_RUN = """
const { check } = await import(process.argv[1]);
let input = "";
for await (const chunk of process.stdin) input += chunk;
const { sections, kind } = JSON.parse(input);
console.log(JSON.stringify(check(sections, { kind })));
"""

REQUIRED = ["kind", "platform", "status", "angle", "hook", "claims", "files", "copy"]
NOTES = ["brand/positioning.md", "brand/voice.md", "brand/visual-identity.md", "public/business.md"]

# An ad's hard limits and visible cutoffs; specs/<platform>.md carries the
# numbers and their sources.
# (limit, hard?, why)
LIMITS = {
    "meta": {"headline": (40, True, "Meta headline: 40 characters"),
             "primary_text": (125, False, "Meta primary text shows about 125 characters before See more"),
             "description": (25, False, "Meta description shows 25 characters")},
    "linkedin": {"headline": (200, True, "LinkedIn headline: 200 max, 70 recommended"),
                 "primary_text": (600, True, "LinkedIn intro text: 600 max, 150 recommended")},
    "tiktok": {"caption": (100, True, "TikTok ad caption: 100 max, about 45 visible")},
    "google": {"headline": (30, True, "Google headline: 30 max"), "primary_text": (90, True, "Google description: 90 max")},
    "pinterest": {"headline": (100, True, "Pinterest title: 100 max"), "primary_text": (800, True, "Pinterest description: 800 max")},
    "youtube": {"headline": (70, False, "YouTube title: about 70 visible")},
}
LIMITS["facebook"] = LIMITS["instagram"] = LIMITS["meta"]
# an organic post's caption where it is capped hard; x and gbp have no sheet,
# so their numbers are in social-post/references/ (x-threads.md, gbp.md)
POST_LIMITS = {"x": {"caption": (280, True, "X post: 280 max")},
               "gbp": {"caption": (1500, True, "Google Business Profile post: 1,500 max")}}
# the sheet in specs/ each platform is built against (x and gbp have none)
SHEETS = {"meta": "meta.md", "instagram": "meta.md", "facebook": "meta.md", "linkedin": "linkedin.md",
          "tiktok": "tiktok.md", "youtube": "youtube.md", "google": "google.md", "pinterest": "pinterest.md"}
SHOWN = 20


def trope_findings(fields, kind):
    """[(field, finding)] for the copy fields {name: text}, each one section
    of the creative; a phrase repeated across fields names the second."""
    names = list(fields)
    try:
        r = subprocess.run(["node", "--input-type=module", "-e", TROPES_RUN, pathlib.Path(TROPES).resolve().as_uri()],
                           input=json.dumps({"sections": [{"body": fields[n]} for n in names], "kind": kind}),
                           capture_output=True, text=True, timeout=60)
    except FileNotFoundError:
        die("check: node is not installed; the copy check (the tropes skill) needs it\n"
            "  Try: node --version (Node 20 or later), then python3 scripts/check.py again")
    if r.returncode != 0:
        die(f"check: the tropes skill's copy check failed, so nothing was checked\n  {r.stderr.strip()[:600]}\n"
            "  Try: node .claude/skills/tropes/tropes.mjs --help")
    out = []
    for f in json.loads(r.stdout):
        i = f["section"] if "section" in f else (f["sections"][-1] if "sections" in f else None)
        out.append((names[i] if i is not None else "all", f))
    return out


def claim_numbers(app, findings):
    """{number: source} from claims.md (`1. The claim (public/proof.md)`),
    checking each source exists."""
    path = os.path.join(app, "claims.md")
    if not os.path.isfile(path):
        return {}
    out = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r"^\s*(\d+)\.\s+(.*)$", line)
            if not m:
                continue
            src = re.findall(r"\(((?:public|brand|raw|research|media)/[^)\s#]+)(?:#[^)]*)?\)", m.group(2))
            if not src:
                findings.append(f"claims.md #{m.group(1)}: no source in brackets (public/…, brand/…, raw/…)")
            for s in src:
                if not os.path.exists(os.path.join(app, s)):
                    findings.append(f"claims.md #{m.group(1)}: source {s} does not exist")
            out[int(m.group(1))] = src
    return out


def check_creative(app, name, d, fm, body, claims, stale, findings, notes):
    rel = os.path.relpath(os.path.join(d, "creative.md"), app)
    if not FOLDER.match(name):
        findings.append(f"{rel}: the folder is named YYYY-MM-DD-<slug>")
    for k in REQUIRED:
        if k not in fm:
            findings.append(f"{rel}: missing `{k}`")
    if fm.get("kind") not in KINDS:
        findings.append(f"{rel}: kind must be one of {', '.join(KINDS)}")
    if fm.get("platform") not in PLATFORMS:
        findings.append(f"{rel}: platform must be one of {', '.join(PLATFORMS)}")
    if fm.get("status") not in STATUSES:
        findings.append(f"{rel}: status must be one of {', '.join(STATUSES)}")
    files = fm.get("files") or []
    if not isinstance(files, list):
        findings.append(f"{rel}: files must be a list")
        files = []
    for f in files:
        if not os.path.isfile(os.path.join(d, str(f))):
            findings.append(f"{rel}: listed file {f} is missing")
    if fm.get("status") in ("sent", "approved", "posted") and not files:
        findings.append(f"{rel}: a {fm.get('status')} creative lists the files the owner saw")
    if fm.get("status") == "posted" and not fm.get("url"):
        findings.append(f"{rel}: a posted creative has the post's `url`")
    for c in fm.get("claims") or []:
        if isinstance(c, int):
            if c not in claims:
                findings.append(f"{rel}: claim {c} is not in claims.md")
        elif not os.path.exists(os.path.join(app, str(c).split("#")[0])):
            findings.append(f"{rel}: claim source {c} does not exist")
    if "to fill" in body:
        findings.append(f"{rel}: the body still says 'to fill'")
    sheet = SHEETS.get(fm.get("platform"))
    if fm.get("status") == "draft" and sheet in stale:
        findings.append(f"{rel}: specs/{sheet} was last verified {stale[sheet]}, over 90 days ago; "
                        "re-verify it as specs/README.md says before building on it")

    copy = fm.get("copy") or {}
    if not isinstance(copy, dict):
        findings.append(f"{rel}: copy must be a map")
        return
    ad = fm.get("kind") == "ad"
    if ad and copy.get("hashtags"):
        findings.append(f"{rel}: an ad carries no hashtags (they are an exit)")
    fields = {k: v for k, v in copy.items() if isinstance(v, str) and v.strip()}
    for field, f in trope_findings(fields, "ad" if ad else "post"):
        line = f"{rel}: copy.{field}: {f['rule']} \"{f['match']}\" ({f['fix']})"
        if f["severity"] == "error":
            findings.append(line)
        else:
            notes.append(line)
    for field, (limit, hard, why) in (POST_LIMITS if fm.get("kind") == "post" else LIMITS).get(fm.get("platform"), {}).items():
        text = copy.get(field)
        if isinstance(text, str) and len(text) > limit:
            if hard:
                findings.append(f"{rel}: copy.{field} is {len(text)} characters, over the limit ({why})")
            else:
                notes.append(f"{rel}: copy.{field} is {len(text)} characters, past the visible cutoff ({why})")


def check_specs(app, findings, notes):
    """{sheet: last_verified} for the sheets over 90 days old."""
    stale = {}
    specs = os.path.join(app, "specs")
    if not os.path.isdir(specs):
        findings.append("specs/ is missing (the platform sheets)")
        return stale
    for name in sorted(os.listdir(specs)):
        if not name.endswith(".md") or name == "README.md":
            continue
        fm, _ = read_record(os.path.join(specs, name))
        try:
            d = date.fromisoformat(str(fm.get("last_verified")))
        except (TypeError, ValueError):
            findings.append(f"specs/{name}: last_verified must be a date")
            continue
        if (date.today() - d).days > 90:
            stale[name] = d
            notes.append(f"specs/{name} was last verified {d}, over 90 days ago; re-verify it before building on it")
    return stale


def main():
    ap = Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folders", nargs="*", help="creative folders to check (default: all)")
    ap.add_argument("--status", choices=STATUSES, help="only the creatives with this status")
    ap.add_argument("--all", action="store_true", help=f"list every creative and finding, not the first {SHOWN}")
    args = ap.parse_args()
    app = root()
    findings, notes = [], []
    for f in NOTES:
        if not os.path.exists(os.path.join(app, f)):
            findings.append(f"{f} is missing (the brand skill writes it)")
    stale = check_specs(app, findings, notes)
    claims = claim_numbers(app, findings)
    rows = creative_dirs(app)
    if args.folders:
        wanted = {os.path.basename(f.rstrip("/")) for f in args.folders}
        for m in sorted(wanted - {n for n, _ in rows}):
            findings.append(f"no creative folder {m} (ls creatives/)")
        rows = [r for r in rows if r[0] in wanted]
    checked = []
    for name, d in rows:
        fm, body = read_record(os.path.join(d, "creative.md"))
        if args.status and fm.get("status") != args.status:
            continue
        check_creative(app, name, d, fm, body, claims, stale, findings, notes)
        checked.append((name, fm))
    what = f"{len(checked)} {args.status + ' ' if args.status else ''}creative(s)"
    again = " ".join(["python3 scripts/check.py", *args.folders] + (["--status", args.status] if args.status else []))
    if findings:
        listed = findings if args.all else findings[:SHOWN]
        more = f"\n  {len(findings) - len(listed)} more finding(s): {again} --all" if len(findings) > len(listed) else ""
        print(f"check: {len(findings)} finding(s) in {what}\n  - " + "\n  - ".join(listed) + more
              + f"\n  Try: fix each at its source, then {again} again", file=sys.stderr)
        sys.stderr.flush()
    else:
        print(f"check: ok, {what}")
    shown = checked if args.all else checked[:SHOWN]
    width = max((len(n) for n, _ in shown), default=0)
    for name, fm in shown:
        print(f"  {name:<{width}}  {str(fm.get('status')):<8}  {fm.get('kind')} {fm.get('platform')}")
    if len(checked) > len(shown):
        print(f"  {len(checked) - len(shown)} more: {again} --all")
    for n in notes:
        print(f"note: {n}")
    if findings:
        sys.exit(1)
    drafts = [n for n, fm in checked if fm.get("status") == "draft"]
    if drafts:
        print(f"\nNext: the tropes skill's eye pass on {drafts[0]}" + (f" and {len(drafts) - 1} more draft(s)" if len(drafts) > 1 else "")
              + ", before the owner sees it")
    elif not checked:
        print("\nNext: the ideas skill writes the first creative")
    elif args.status == "sent":
        print("\nNext: the owner answers on the waiting deliverables (the work skill)")
    else:
        print("\nNext: python3 scripts/check.py --status sent lists what waits for the owner")


if __name__ == "__main__":
    main()
