---
name: marketing
description: "The marketing app's folders, the shape of a creative.md, the order of work from research to results, and recording results. Use at the start of a session here, when the owner asks what to do next, what is waiting for approval, how an ad did, or where something is filed. Not for making a piece itself (ad, social-post)."
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
   (the `ideas` skill), each with a hook (the `copywriting` skill).
4. **Make.** An ad (the `ad` skill) or a post (the `social-post` skill):
   words through `copywriting`, pictures through `images`, clips through
   `video`.
5. **Audit.** `python3 scripts/check.py`, then the `tropes` skill's eye pass.
   Fix every finding before the owner sees anything.
6. **Review.** Show the owner the files as deliverables and set `status:
   sent`. Their approval or rejection sets it again.
7. **Results.** What ran and what it did goes in `results.md`, newest
   first: the folder, the platform, the dates, hook rate, hold rate,
   click-through, cost per lead. Only the owner's own account says what
   works. On a winner, new hooks on the same body first, then the same angle
   in a new format; on a loser, a new angle, not a new colour.

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
hook: us-vs-them             # from copywriting/references/hooks.md
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
(the image prompt, exactly as sent)

## Shot 1
(a video's shot brief, exactly as sent; the next is ## Shot 2)

## Notes
v1: headline too long at phone size; v2 shortened it.
```

One idea per creative; a second idea is the next folder.
`python3 scripts/check.py` checks the fields, the files, the claims and the
copy. A creative is never shown with a finding open.
