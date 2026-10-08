---
type: reference
last_verified: 2026-10-08
sources:
  - https://x.com/codyschneider
  - https://developer.instantly.ai/
  - https://www.millionverifier.com/
  - https://docs.apollo.io/
  - https://apify.com/store
---

# Cold email

Email the people who could buy, at volume, from mailboxes built for it.
It is the most direct way a business selling to businesses gets meetings
and visits, and the same list feeds ads and a newsletter.

## Fits

Sells to businesses, and the buyer can be named by role, industry and
size. Rarely for a local business selling to households: there the law and
the buyer are against it.

## What it looks like

- **A list.** Contacts that match the buyer from a contact database, or
  warmer ones: the people who liked or commented on a LinkedIn post (the
  owner's own posts first, then posts in the niche), collected by a
  scraper and given emails by the database from their profile link.
- **Verified.** Every address checked before it is sent to; bad addresses
  ruin a sending domain.
- **Sent from a sending tool** across many mailboxes on separate domains,
  warmed up first. Cody's scale is about 100,000 emails a month to some
  50,000 people.
- **Short.** Cody sends two: the first asks for a meeting, the second
  sends a link to sign up or book.

## Tools

- A contact database (Apollo, Hunter) and a scraper for a post's engagers
  (Apify, PhantomBuster).
- A verifier (MillionVerifier, ZeroBounce).
- A sending tool (Instantly, Smartlead), with mailboxes on separate,
  warmed domains; Instantly can order them itself.
- The words: the `email` skill (cold email) and `copywriting`. Lists in
  `lists/`, one file per source and date.

## Watch

Replies, meetings booked and visits from the campaign, per hundred sent.
Bounce rate under about 2% and spam complaints near zero, or stop and fix
the list.

## Repeats

A list job (find, enrich, verify, add to the campaign) per source, with a
record of who is already in so nobody is emailed twice. The owner approves
the first batch of each new list. A daily job reads the replies, drafts
answers for the owner, and moves anyone interested into the CRM if the
business keeps one. Each run adds its counts (found, emailed, replied,
booked) to `results.md`.

## Gotchas

- Where it sends from and the law that follows the reader: the `email`
  skill's cold email lines.
- Every reply that says no goes on the suppression list the same day.
- Prefer a scraper that needs no LinkedIn sign-in; one that runs on the
  owner's own session puts their account at risk.
