#!/usr/bin/env python3
"""The mechanical half of the tropes audit: the generated-text tells a
pattern can find. The other half (voice, images, video) is a model's eye,
in the tropes skill.

    python3 scripts/tropes.py creatives/<folder>/creative.md   # the copy in its frontmatter and body
    python3 scripts/tropes.py --text "Say goodbye to leaks."   # any text
    python3 scripts/tropes.py --post file.md                   # organic post: no ad-only rules

Prints one line per finding (rule, then the words that tripped it) and
exits 1 when there is any. A finding is a line to rewrite whole, never a
phrase to patch. The word lists date: re-check them every six months.
"""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import read_record  # noqa: E402

PHRASES = [
    # openers and sweeps
    r"\bin today'?s (fast-paced|digital|competitive|ever-changing) world\b", r"\bin a world where\b",
    r"\bimagine a world\b", r"\bwelcome to (our|my|the)\b", r"\bare you looking for\b", r"\bwhen it comes to\b",
    r"\bwhether you'?re\b", r"\blook no further\b", r"\bsomething for everyone\b",
    # fake-casual reveals
    r"\bhere'?s the thing\b", r"\band honestly\?", r"\byou know what'?s wild\b", r"\bthat changes everything\b",
    r"\bhere'?s what nobody\b", r"\blet'?s dive in\b",
    # ad cliches
    r"\bsay goodbye to\b", r"\bto the next level\b", r"\bgame-?chang(er|ing)\b", r"\ball-in-one\b",
    r"\beverything you need\b", r"\bwhere \w+ meets \w+\b", r"\b\w+, (reimagined|redefined)\b",
    # verb cosplay and inflated adjectives
    r"\b(unlock|unleash|elevate|empower|revolutioni[sz]e|supercharge|transform) your\b", r"\bleverage\b",
    r"\bseamless(ly)?\b", r"\bcutting-edge\b", r"\bworld-class\b", r"\bnext-level\b", r"\brobust\b",
    r"\bholistic\b", r"\bbespoke\b",
    # significance inflation and brochure puffery
    r"\bstands? as a testament\b", r"\bplays? an? (crucial|pivotal|vital|key) role\b", r"\bevolving landscape\b",
    r"\bnestled\b", r"\bin the heart of\b", r"\brich heritage\b", r"\bdiverse array\b",
    r"\b(tapestry|realm|ecosystem)\b",
    # copula avoidance, hedges, closers
    r"\bserves as\b", r"\bstands as\b", r"\bmore than just\b", r"\bit'?s worth noting\b",
    r"\bit'?s important to note\b", r"\bit goes without saying\b", r"\bin conclusion\b", r"\bultimately,",
    # small-business cliches
    r"\bwe'?re passionate about\b", r"\bwe pride ourselves\b", r"\bwe do things differently\b",
    r"\byour (trusted )?partner in\b", r"\bwe believe\b",
    # a call to action that says nothing
    r"\b(learn more|click here|read more|find out more)\b",
]

NEGATION = [
    r"\bit'?s not (just )?(about )?[^.;:!?]{1,40}[,.;:] it'?s\b",
    r"\bnot (just|only|merely) [^.;:!?]{1,40},? but\b",
    r"\bnot because [^.;:!?]{1,60}[.;,] because\b",
    r"\b\w+(?: \w+)?, not \w+(?: \w+)?[.!]",
]

ING_RIDER = r", (highlighting|ensuring|fostering|showcasing|reflecting|contributing to|underscoring|emphasizing|enhancing)\b"

# Meta refuses copy that asserts or implies the reader's personal attributes.
PERSONAL_ATTRIBUTES = [
    r"\b(struggling|suffering) with\b", r"\bdo you have (diabetes|anxiety|depression|debt|acne)\b",
    r"\byour (weight|debt|depression|anxiety|diabetes|condition|diagnosis|credit score)\b",
    r"\bare you (overweight|bankrupt|depressed|in debt|pregnant)\b",
]

ERA_WORDS = r"\b(delve|intricate|meticulous|testament|garnered|align with|enhance|fostering|showcasing|highlighting|bolstered|emphasizing)\b"


def sentences(text):
    flat = re.sub(r"\s+", " ", text).strip()
    return [s for s in re.split(r"(?<=[.!?])\s+", flat) if len(s.split()) > 1]


def findings(text, ad=True):
    """[(rule, match)] for the copy tells in `text`."""
    out = []
    if not text or not text.strip():
        return out
    if "—" in text:
        out.append(("em dash (house rule: a comma, colon or new sentence)", "—"))
    for rx in PHRASES:
        for m in re.finditer(rx, text, re.I):
            out.append(("refused phrase", m.group(0)))
    for rx in NEGATION:
        for m in re.finditer(rx, text, re.I):
            out.append(("negation pivot (state the claim; nobody proposed the other)", m.group(0)))
    for m in re.finditer(ING_RIDER, text, re.I):
        out.append(("-ing rider (cut it, or give it a subject)", m.group(0).lstrip(", ")))
    for m in re.finditer(r"[^.!?\n]{3,80}\?\s+[A-Z][^.!?\n]{0,60}[.!]", text):
        out.append(("rhetorical question, then its answer (say the answer)", m.group(0).strip()))
    triads = re.findall(r"\b\w+(?: \w+)?, \w+(?: \w+)?,? and \w+(?: \w+)?\b", text)
    staccato = re.findall(r"(?:\b[A-Z]\w*(?: \w+){0,2}\. ){2}[A-Z]\w*(?: \w+){0,2}\.", text)
    if len(triads) + len(staccato) > 1:
        out.append(("more than one triad (use the number of things there are)", "; ".join((triads + staccato)[:3])))
    era = re.findall(ERA_WORDS, text, re.I)
    words = len(text.split())
    if words and len(era) * 100 / words >= 1.5:
        out.append(("dated model vocabulary, dense", ", ".join(sorted({e.lower() for e in era}))))
    ss = sentences(text)
    if len(ss) >= 6:
        lengths = [len(s.split()) for s in ss]
        if max(lengths) - min(lengths) < 12:
            out.append(("uniform sentence length (mix short and long)", f"{min(lengths)} to {max(lengths)} words"))
    we = len(re.findall(r"\b(we|our|us)\b", text, re.I))
    you = len(re.findall(r"\b(you|your)\b", text, re.I))
    if we >= 3 and we > you:
        out.append(("talks about itself more than the reader", f"we/our {we}, you/your {you}"))
    if ad:
        for rx in PERSONAL_ATTRIBUTES:
            m = re.search(rx, text, re.I)
            if m:
                out.append(("personal attribute (Meta refuses it)", m.group(0)))
    return out


def creative_text(path):
    """The words of a creative.md: every string under `copy:`, then the body
    sections the owner will read (the prompt and notes are not copy)."""
    fm, body = read_record(path)
    parts = []
    copy = fm.get("copy") or {}
    if isinstance(copy, dict):
        parts += [v for v in copy.values() if isinstance(v, str)]
        parts += [x for v in copy.values() if isinstance(v, list) for x in v if isinstance(x, str)]
    return "\n".join(parts), fm.get("kind") != "post"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?")
    ap.add_argument("--text")
    ap.add_argument("--post", action="store_true", help="organic post: skip the ad-only rules")
    args = ap.parse_args()
    if args.text is not None:
        text, ad = args.text, not args.post
    elif args.file and args.file.endswith("creative.md"):
        text, ad = creative_text(args.file)
    elif args.file:
        with open(args.file, encoding="utf-8") as fh:
            text, ad = fh.read(), not args.post
    else:
        ap.error("a file or --text")
    found = findings(text, ad=ad)
    for rule, match in found:
        print(f"{rule}: \"{match}\"")
    if found:
        sys.exit(1)
    print("tropes: clean")


if __name__ == "__main__":
    main()
