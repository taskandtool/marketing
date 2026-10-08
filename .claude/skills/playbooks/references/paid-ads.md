---
type: reference
last_verified: 2026-10-08
sources:
  - https://x.com/codyschneider
  - https://developers.facebook.com/docs/marketing-api/audiences/guides/custom-audiences
  - https://support.google.com/google-ads/answer/6299717
---

# Paid ads and remarketing

Buy attention from people who have never heard of the business, then
follow everyone who visits with ads on every platform they use. Cold ads
fill the top; remarketing turns visits into signups, because most people
need several sightings before they act.

## Fits

A clear offer, a page that converts, and a budget the owner can lose while
it learns. Conversion tracking comes first (the `results` skill,
"Tracking"); without it the platforms optimise for clicks, not customers.

## What it looks like

- Cold campaigns on Meta and Google aimed at the event that matters
  (signup, booking, paid), not traffic.
- A pixel on the site for every platform the buyers use: Meta, Google,
  LinkedIn, Reddit, X.
- Remarketing everywhere to visitors and to the business's own customer
  list, uploaded as an audience.
- New creative and landing pages tested all the time (`ad-testing.md`).

## Tools

- Making the ads: the `ad` skill, as a set of distinct ideas.
- Launching and audiences: Meta with ads management, Google with Google
  Ads (its developer token needs Google's approval), or the owner in each
  ads manager. Ads go up paused for the owner to switch on.
- Tracking: the `results` skill, "Tracking".

## Watch

Cost to win a customer against what a customer is worth, and how many
months a customer takes to pay back their cost. Judge a campaign after it
has spent enough to win some customers, not after a day. Stop or change
the offer when the cost stays above what a customer is worth.

## Repeats

A weekly job reads spend and results into `results.md` and proposes what
to pause and what to make next. It changes nothing on the account without
the owner.

## Gotchas

- Customer lists are hashed (SHA-256, lowercased, trimmed) on this machine
  before upload, as the platforms require.
- Google's Customer Match targeting needs a long, well-spent account
  history; a small account can still use a list to exclude customers.
- Health, finance, housing and before-and-after ads follow the platform's
  sheet in `specs/`.
