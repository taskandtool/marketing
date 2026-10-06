---
name: copywriting
description: "Writes and edits the words of an ad or post in the business's own voice: the hook, headline, primary text, caption, call to action, script. Use whenever a creative's words are written or rewritten, for new hooks on a winning ad, or when the owner says it doesn't sound like them. Not for choosing the idea (ideas)."
---

# Copywriting

Read `brand/voice.md` first, every time: the card, the owner's sentences,
the signatures, the never-list, the lexicon. Then `claims.md` for what may
be said. The words come from those two files and the idea in `creative.md`.

## The standard

1. **Clear over clever.** Each line answers one reader question at a
   glance. The headline says what the reader can do here; a stranger could
   repeat the offer from it alone.
2. **Words a person would say aloud.** Would the owner say it on the phone
   to a customer? Plain verbs (use, fit, book), their contractions, no
   metaphor nouns. Invite, don't instruct.
3. **Specifics.** At least one particular per piece from the owner's
   material: a place, a material, a number with its unit, a name, a date.
   Numerals for numbers.
4. **Their voice.** The owner's sentences and customers' own words are the
   model. Where the owner's own copy is marketese, write plainer than they
   do.
5. **Facts as `AGENTS.md` says.** A rating carries its count and source. A
   claim cut for want of a source is never softened into a vaguer one, and
   customers, results, awards or urgency are never invented.
6. **Vary the rhythm.** Mix four-word and forty-word sentences; at most one
   list of three; commas and the odd aside; no em dashes.
7. **One idea, one action.** The call to action names the outcome ("Book a
   service"), not the mechanism ("Learn more"), worded the same everywhere.

## Hooks

The opening line, second or frame does two jobs: it interrupts, and it says
who it is for. One without the other is clickbait or invisible. Pick the type for the
reader's awareness stage (`references/hooks.md`), write five to eight
openings in the customers' words (`research/audience.md`), keep the best
two and record the rest in `research/hooks.md`. The proposition lands in
the first line or three seconds, works muted, and the body pays it off.

## Lengths

The platform's sheet in `specs/` has the hard limits and visible cutoffs;
`scripts/check.py` enforces them. As a default: a headline under eight
words; primary text that makes its point before the visible cutoff; on a
picture, twelve words or fewer.

## Editing

Edit in this order: truth (is every fact in `claims.md`), meaning (one
idea), structure, voice, language, sound (read it aloud), compression.
Then `python3 scripts/check.py <folder>` (it runs the `tropes` skill's
script on every copy field) and the `tropes` skill, which says how a
finding is fixed.

## Example

Idea: we send the engineer who fitted it. Voice: plain, first person
plural, names streets.

Draft: "Experience seamless boiler care with our dedicated team of experts.
It's not just a service, it's peace of mind."

Rewrite: "The engineer who fitted your boiler services it. Same two of us
since 2004, from Headingley to Horsforth. Book your service before the
first cold week."
