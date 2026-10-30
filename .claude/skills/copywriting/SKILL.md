---
name: copywriting
description: "Writes the hook of an ad, post or email and fits its words to the platform: hook types by awareness stage, lengths and visible cutoffs. Use when a creative's words are written, for new hooks on a winning ad, or to fit a piece to its platform. Not for choosing the idea (ideas)."
---

# Copywriting

Read the `writing` skill first: the standard every word is held to, the
editing order and the cold read. This skill adds what an ad, a post or an
email needs on top of it.

The words come from `brand/voice.md` (the card, the owner's sentences, the
signatures, the never-list, the lexicon), `claims.md` for what may be said,
and the idea in `creative.md`.

## Hooks

The hook (the opening line, the first second of a video, or the first
frame) does two jobs: it interrupts, and it says who it is for. Pick the
hook type for the reader's awareness stage (`references/hooks.md`), write
five to eight openings in the customers' words (`research/audience.md`),
keep the best two and record the rest in `research/hooks.md`. The offer is
in the first line or the first three seconds and works muted; the body pays
it off.

## Lengths

The platform's sheet in `specs/` has the hard limits and visible cutoffs;
`scripts/check.py` enforces them. As a default: a headline under eight
words; primary text that makes its point before the visible cutoff; on a
picture, twelve words or fewer.

## Checking

`python3 scripts/check.py <folder>` holds the piece to the platform's
limits and runs the `tropes` check. Then the `writing` skill's cold read on
the piece this turn changed.
