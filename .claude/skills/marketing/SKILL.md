---
name: marketing
description: "The marketing app's folders, the shape of a creative.md, and the order of work from research to results. Use at the start of any session here, when the owner asks what to do next, what is waiting for approval, or how something is filed. Not for making a piece itself (ad, social-post) or writing words (copywriting)."
---

# Marketing

This app turns one business's brand and its market into ads and posts the
owner approves. It makes and files the work; it never posts it.

## The loop

Each step has its own skill. Start wherever the folders say the work is.

1. **Brand.** `brand/` and `public/` filled (the `brand` skill). Nothing is
   made from notes that still say "to fill".
2. **Research.** What competitors run, what customers say, what people
   search (the `research` skill) into `research/`.
3. **Ideas.** Angles and frameworks turned into ranked ideas worth making
   (the `ideas` skill), each with a hook (the `hooks` skill).
4. **Make.** An ad (the `ad` skill) or a post (the `social-post` skill):
   words through `copywriting`, pictures through `images`, clips through
   `video`.
5. **Audit.** `python3 scripts/check.py`, then the `tropes` skill's eye pass.
   Fix every finding before the owner sees anything.
6. **Review.** Show the owner the files as deliverables and set `status:
   sent`. Their approval or rejection sets it again.
7. **Results.** What ran and what it did goes in `results.md`, newest first.
   Only the owner's own account says what works.

## Where things are

```
brand/  public/         the brand record (the brand skill)
claims.md               every fact a creative may state, numbered, each with its source
media/                  the business's own photos and clips; _index.md says what may be used
raw/                    material as it arrived: raw/site/<host>/, raw/<source>/<who>/
research/               competitors/<name>.md, hooks.md, audience.md, brief.md
creatives/YYYY-MM-DD-<slug>/   one idea per folder: creative.md, v1.png, v2.png, shot-1.mp4
results.md              numbers per creative and what to try next, newest first
specs/<platform>.md     sizes, limits and policy, each with last_verified
```

Names: dates first (`YYYY-MM-DD-<slug>`), lowercase, hyphens. A clone or a
restore resets file times, so the date in the name is the only reliable
order. A campaign is a frontmatter field, never a folder, so one grep finds
it.

## creative.md

```markdown
---
kind: ad                     # ad | post
platform: meta               # meta | instagram | facebook | linkedin | tiktok | youtube | google | pinterest | x | gbp
format: us-vs-them           # from ad/references/formats.md, or the post's form
angle: mechanism             # the argument, in a word or two
hook: us-vs-them             # from hooks/references/catalogue.md
framework: pas               # optional: pas | bab | storybrand | jtbd | objection
awareness: solution          # unaware | problem | solution | product | most
campaign: winter-2026        # optional
status: draft                # draft | sent | approved | rejected | posted
claims: [2, 5]               # numbers in claims.md
files: [v1.png]
url: ""                      # the live post, once posted
copy:
  headline: "The engineer who fitted it services it"
  primary_text: "Same two engineers, every visit since 2004. Book your service before the first cold week."
  cta: "Book a service"
---

## Idea
Big firms send whoever is free; we send the engineer who fitted the boiler.
For solution-aware homeowners comparing firms.

## Prompt
(the image prompt or the shot brief, exactly as sent)

## Notes
v1: headline too long at phone size; v2 shortened it.
```

`python3 scripts/check.py` checks the fields, the files, the claims and the
copy. A creative is never shown with a finding open.

## Rules

- Every fact on a creative is a numbered line in `claims.md` citing
  `public/`, `brand/` or `raw/`. A fact with no source is a question for
  the owner, asked once with the others.
- Real material first: the owner's photos and clips in `media/` beat
  anything generated, and a generated picture never shows a real person,
  a customer's home, or a testimonial face.
- One idea per creative. A second idea is the next folder.
- Never post from here, and never name a competitor in a creative.
- Keys arrive through Connections; never ask for one in chat. A connection
  that brings its own instructions (an image or video model, Apify,
  Firecrawl) is used the way those instructions say.

## Scripts

Run them; their output is the instruction.

```
python3 scripts/check.py [folder …]          every creative, claims.md, specs freshness
python3 scripts/tropes.py <creative.md>      the copy tells a pattern can find
python3 scripts/imagegen.py --check          which image model is configured
python3 scripts/videogen.py --check          which video model is configured
```
