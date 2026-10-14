---
name: marketing
description: "Maps the marketing app: its folders, the shape of a creative.md, and the order of work. Use at the start of a session, when the owner asks what next, what is waiting for approval, or where something is filed. Not for making a piece (ad, social-post) or measuring one (results)."
---

# Marketing

This app turns one business's brand and its market into ads, posts and
emails, and files them for the owner to review.

## The loop

Brand (`brand`) → research → ideas (hooks by `copywriting`) → make (`ad`,
`social-post`, `email`; clips by `video`) → `python3 scripts/check.py` and
the `tropes` audit → review → `results`. Start wherever the folders say the
work is; nothing is made from notes that still say "to fill".

Review: show the files as deliverables and set `status: sent`; when the
owner answers (`get-deliverables`), set approved or rejected.

Months-long strategies are `playbooks`'; the chosen ones are in `plan.md`.

## Making it repeat

Something the owner wants every week: do it by hand in chat until they
like it, then put the mechanical part in `scripts/`, the judgement in
`jobs/<name>.md`, and schedule it (`schedule-job`). A job keeps a record so
a rerun never sends, posts or spends twice, and stops at a draft or a
paused ad unless the owner said otherwise.

## Where things are

```
brand/  public/         the brand record (the brand skill)
claims.md               every fact a creative may state, numbered, each with its source
media/                  the owner's photos and clips sent here; _index.md says what may be used
                        (the brand's curated photos are brand/images.md)
raw/                    material as it arrived: raw/site/<host>/, raw/<source>/<who>/
research/               competitors/<name>.md, hooks.md, audience.md, brief.md
creatives/YYYY-MM-DD-<slug>/   one idea per folder: creative.md, v1.png, v2.png, shot-1.mp4
emails/YYYY-MM-DD-<slug>/      one email or sequence per folder: email.md (the email skill)
results.md              numbers per creative and per month, newest first
plan.md                 the playbooks chosen, and why (the playbooks skill)
lists/                  the people a playbook reaches: prospects, engagers, who said no
jobs/<name>.md          the prompt a scheduled job follows
reports/YYYY-MM.md      the monthly report
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
