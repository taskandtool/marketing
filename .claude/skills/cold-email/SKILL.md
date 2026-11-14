---
name: cold-email
description: "Runs cold email for a business that sells to other businesses: finding and verifying the list, short sequences in the owner's voice, keeping it out of spam, the law and the replies. Use for cold email, outreach to prospects or finding leads to email. Not for newsletters or customers (email)."
---

# Cold email

Use cold email to book meetings for a business that sells to other
businesses. It rarely fits a business selling to households: in the UK and
EU it needs each person's consent. Few households answer. Say so and suggest
the `growth-plan` skill.

Done when the list is verified in `lists/`, the emails pass
`python3 scripts/check.py`, and the owner has approved the first batch.

## Steps

Copy and tick:

- [ ] 1. **The buyer**, agreed with the owner in one line: role, kind of
      business, size, place, and why they might want this now.
- [ ] 2. **The list**, in `lists/YYYY-MM-DD-<source>-<who>.csv`: name,
      company, email, and why this person. Take them from a contact
      database (Apollo, Hunter). Warmer: the people who liked or commented
      on a LinkedIn post (the owner's own posts first). Collect those with a
      scraper that needs no LinkedIn sign-in (Apify, PhantomBuster), then
      get their emails from the database. Leave out anyone in an earlier
      list or in `suppressed.csv`.
      Never guess an address. A row with no reason is a question for the
      owner.
- [ ] 3. **Verify every address** (MillionVerifier, ZeroBounce) and drop
      the invalid and risky ones. Bounces ruin a sending domain.
- [ ] 4. **Write the sequence** (below) to
      `emails/YYYY-MM-DD-<slug>/email.md` with `kind: cold`, `audience`
      and `status`, then each email's subject, preview line and body. Run
      `python3 scripts/check.py` and show `email.md` as a deliverable
      (`create-deliverables`, in the `work` skill).
- [ ] 5. **Send**, once approved:
      - a handful: one Gmail draft per person through the owner's `google`
        connection (`POST /gmail/v1/users/me/drafts`), sent only when the
        owner says (`POST /gmail/v1/users/me/drafts/send`);
      - at volume: a campaign in the owner's sending tool (`instantly`),
        from mailboxes on separate, warmed-up domains, never the main one.
        The owner starts it. Postmark and Resend are for transactional
        mail, and their terms forbid cold email;
      - neither connected: the files are the drafts, and the owner pastes
        them.
- [ ] 6. **Replies**, daily: draft an answer to each for the owner. A no
      goes into `suppressed.csv` the same day. Someone interested goes into
      the CRM if the business keeps one.

## The emails

- **Two or three over about ten days:** the first asks for a short
  conversation, a follow-up adds something new (a link to book, a result),
  and at most one last note.
- **Plain text, under 120 words.** The first line is about the reader. No
  images, and no link in the first email beyond the signature. Facts only
  from `claims.md`.
- **Put the business's postal address and a way to opt out in every email**
  ("Reply no and I won't write again"). The rest depends on where the reader
  lives. In the EU and UK, writing to a person at a company needs a real
  business reason. When unsure, ask the owner.

Example:

```
Subject: Your Larkfield office plants

Hi Dana,

I walked past Hartley & Co on Tuesday and saw the big fig in your window is losing leaves. That's usually a draught or too much water in winter.

I look after plants for six offices in Larkfield. A visit is every two weeks, £40 a month for up to ten plants, and I replace anything that dies.

Would a free check of the fig be useful? I can come by any morning next week.

Sam Okafor, Greenroom Plants, 14 Mill Lane, Larkfield
Reply no and I won't write again.
```

## Watching it

Replies and meetings booked per hundred sent, and visits from the
campaign. Bounces under about 2% and spam complaints near zero; above
that, stop and fix the list. Add each run's counts (found, sent, replied,
booked) to `results.md`.

Once a list works, repeat it ("Making it repeat" in the `marketing`
skill). A job per source finds, verifies and adds new people and skips
anyone already contacted. The owner approves the first batch of each new
list.
