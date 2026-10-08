---
name: marketing
description: "Maps the marketing app: its folders, the shape of a creative.md, and the order of work from research to results. Use at the start of a session here, when the owner asks what to do next, what is waiting for approval, or where something is filed. Not for making a piece (ad, social-post) or measuring one (results)."
---

# Marketing

This app turns one business's brand and its market into ads, posts and
emails, and files them for the owner to review.

## The loop

Each step has its own skill. Start wherever the folders say the work is.

1. **Brand.** `brand/` and `public/` filled (the `brand` skill). Nothing is
   made from notes that still say "to fill".
2. **Research.** What competitors run, what customers say, what people
   search (the `research` skill) into `research/`.
3. **Ideas.** Angles and frameworks turned into ranked ideas worth making
   (the `ideas` skill), each with a hook (the `copywriting` skill).
4. **Make.** An ad (the `ad` skill), a post (the `social-post` skill) or an
   email (the `email` skill):
   words through `copywriting`, pictures as `AGENTS.md` says, clips
   through `video`.
5. **Audit.** `python3 scripts/check.py`, then read the work by eye against
   the `tropes` skill. Fix every finding before the owner sees anything.
6. **Review.** Show the owner the files as deliverables and set `status:
   sent`. The owner's approval or rejection then changes `status` again.
7. **Results.** What ran and what it did goes in `results.md`, and a
   monthly report says what to make next (the `results` skill).

Beyond single pieces, the strategies a business could run for months are
the `playbooks` skill's; the chosen ones are in `plan.md`.

## Making it repeat

When the owner wants something done every week (a batch of posts, a list
job, a report), do it once by hand in chat until they like the result.
Then save what worked: the mechanical part (calls, files, counts) as a
script in `scripts/`, the part that needs judgement as a prompt in
`jobs/<name>.md`, and schedule it (the `schedule-job` skill). Write a
script when the same steps would be redone each time, or when it sends,
posts or spends; a one-off stays in chat.

- It keeps a record of what it has done, so a second run never sends,
  posts or spends twice. Most runs find nothing new and do nothing.
- It prints what it did in a line or two and exits non-zero on failure.
- What it sends, posts or spends stops at a draft or a paused ad for the
  owner, unless they said otherwise for that job.

## Where things are

```
brand/  public/         the brand record (the brand skill)
claims.md               every fact a creative may state, numbered, each with its source
media/                  the business's own photos and clips; _index.md says what may be used
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
`python3 scripts/check.py` checks the fields, the files, the claims and the
copy. A creative is never shown with a finding open.
