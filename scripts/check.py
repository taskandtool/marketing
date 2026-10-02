#!/usr/bin/env python3
"""The app's own checks, run before anything is shown to the owner:

    python3 scripts/check.py [<folder> …]

- the brand record the work draws on exists (brand/, public/)
- every creatives/<YYYY-MM-DD-slug>/creative.md has the fields the
  marketing skill lists, a known kind, platform and status, and every file
  it lists
- every claim it cites is a numbered entry in claims.md, and every entry
  there names a source file that exists
- the copy passes scripts/tropes.py and the platform's text limits
- the platform sheets in specs/ are not stale (90 days)

Exit 1 with the findings when something is off. A finding is fixed at
its source before the owner sees the work, never explained away.
"""

import argparse
import os
import re
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import FOLDER, KINDS, PLATFORMS, STATUSES, creative_dirs, read_record, root  # noqa: E402
from tropes import findings as trope_findings  # noqa: E402

REQUIRED = ["kind", "platform", "status", "angle", "hook", "claims", "files", "copy"]
NOTES = ["brand/positioning.md", "brand/voice.md", "brand/visual-identity.md", "public/business.md"]

# Hard limits and visible cutoffs; specs/<platform>.md carries the sources.
# (limit, hard?, why)
LIMITS = {
    "meta": {"headline": (40, True, "Meta headline: 40 characters"),
             "primary_text": (125, False, "Meta primary text shows about 125 characters before See more"),
             "description": (25, False, "Meta description shows 25 characters")},
    "linkedin": {"headline": (200, True, "LinkedIn headline: 200 max, 70 recommended"),
                 "primary_text": (600, True, "LinkedIn intro text: 600 max, 150 recommended")},
    "tiktok": {"caption": (100, True, "TikTok ad caption: 100 max, about 45 visible")},
    "google": {"headline": (30, True, "Google headline: 30 max"), "primary_text": (90, True, "Google description: 90 max")},
    "pinterest": {"headline": (100, True, "Pinterest title: 100 max"), "primary_text": (500, True, "Pinterest description: 500 max")},
    "youtube": {"headline": (70, False, "YouTube title: about 70 visible")},
    "gbp": {"primary_text": (1500, True, "Google Business Profile post: 1,500 max")},
}
LIMITS["facebook"] = LIMITS["instagram"] = LIMITS["meta"]


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


def check_creative(app, name, d, claims, findings):
    path = os.path.join(d, "creative.md")
    rel = os.path.relpath(path, app)
    fm, body = read_record(path)
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

    copy = fm.get("copy") or {}
    if not isinstance(copy, dict):
        findings.append(f"{rel}: copy must be a map")
        return
    ad = fm.get("kind") == "ad"
    if ad and copy.get("hashtags"):
        findings.append(f"{rel}: an ad carries no hashtags (they are an exit)")
    for field, text in copy.items():
        if isinstance(text, str):
            for rule, match in trope_findings(text, ad=ad):
                findings.append(f"{rel}: copy.{field}: {rule}: \"{match}\"")
    for field, (limit, hard, why) in LIMITS.get(fm.get("platform"), {}).items():
        text = copy.get(field)
        if isinstance(text, str) and len(text) > limit:
            if hard:
                findings.append(f"{rel}: copy.{field} is {len(text)} characters, over the limit ({why})")
            else:
                print(f"note: {rel}: copy.{field} is {len(text)} characters, past the visible cutoff ({why})")


def check_specs(app, findings):
    specs = os.path.join(app, "specs")
    if not os.path.isdir(specs):
        findings.append("specs/ is missing (the platform sheets)")
        return
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
            print(f"note: specs/{name} was last verified {d}, over 90 days ago; re-verify before building against it")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folders", nargs="*")
    args = ap.parse_args()
    app = root()
    findings = []
    for f in NOTES:
        if not os.path.exists(os.path.join(app, f)):
            findings.append(f"{f} is missing (the brand skill writes it)")
    check_specs(app, findings)
    claims = claim_numbers(app, findings)
    rows = creative_dirs(app)
    if args.folders:
        wanted = {os.path.basename(f.rstrip("/")) for f in args.folders}
        for m in wanted - {n for n, _ in rows}:
            findings.append(f"no creative folder {m}")
        rows = [r for r in rows if r[0] in wanted]
    for name, d in rows:
        check_creative(app, name, d, claims, findings)
    if findings:
        print(f"check: {len(findings)} finding(s)\n  - " + "\n  - ".join(findings), file=sys.stderr)
        sys.exit(1)
    print(f"check: ok ({len(rows)} creative(s))")


if __name__ == "__main__":
    main()
