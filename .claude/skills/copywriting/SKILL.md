---
name: copywriting
description: "Write and edit the words of an ad or post in the business's own voice: headline, primary text, captions, call to action, script lines. Use whenever words are written or rewritten for a creative, or when the owner says it doesn't sound like them. Not for choosing the idea (ideas) or the opening line (hooks)."
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
5. **Claims only from `claims.md`.** A rating carries its count and source.
   With no source, cut the claim and ask the owner; never soften it into a
   vaguer one, and never invent customers, results, awards or urgency.
6. **Vary the rhythm.** Mix four-word and forty-word sentences; at most one
   list of three; commas and the odd aside; no em dashes.
7. **One idea, one action.** The call to action names the outcome ("Book a
   service"), not the mechanism ("Learn more"), worded the same everywhere.

## Lengths

The platform's sheet in `specs/` has the hard limits and visible cutoffs;
`scripts/check.py` enforces them. As a default: a headline under eight
words; primary text that makes its point in the first 125 characters; on a
picture, twelve words or fewer; video captions at five to ten words a
second.

## Editing

Edit in this order: truth (is every fact in `claims.md`), meaning (one
idea), structure, voice, language, sound (read it aloud), compression.
Then `python3 scripts/tropes.py creatives/<folder>/creative.md` and the
`tropes` skill. Rewrite a flagged line whole; never patch the phrase, and
never add a fact to fill the gap a cut left.

## Example

Idea: we send the engineer who fitted it. Voice: plain, first person
plural, names streets.

Draft: "Experience seamless boiler care with our dedicated team of experts.
It's not just a service, it's peace of mind."

Rewrite: "The engineer who fitted your boiler services it. Same two of us
since 2004, from Headingley to Horsforth. Book your service before the
first cold week."
