---
name: research
description: "Researches a market before making creatives: competitors' sites, ads and posts, customers' reviews and comments, search questions, conversations worth joining, into research/ and a brief of ranked hypotheses. Use when the owner asks what competitors are doing, where to reply, before the first ideas, or monthly. Not for the business's own facts (brand)."
---

# Research

Ads show what competitors keep paying for. Posts, comments, reviews and
searches show what customers say. Do both, customers first, and end with a
brief the `ideas` skill can act on.

Fetching:

- a competitor's site: `tt-crawl survey <url> --external` (into
  `raw/external/<host>/`)
- ad libraries, social posts and comments: the `scrapecreators` connection
- reviews on a site with no API (Google Maps), recent threads on Reddit,
  LinkedIn, Facebook groups and forums, and the TikTok Creative Center's
  top ads for the industry: `apify`
- People Also Ask, autocomplete and monthly search volume: `dataforseo`
- a business's Google listing and reviews: `google-places`, as below

Ask for a connection that is not granted, as the first line below does for
scrapecreators.

```bash
python3 ~/tools/taskandtool.py request-connection scrapecreators --why "competitors' ads and posts"
GOOGLE_PLACES_API_URL=$PHOENIX_URL/api/machine/gateway/google-places/v1 GOOGLE_PLACES_API_KEY=$MACHINE_TOKEN tt-crawl places "Name, City"
```

## Steps

Copy and tick:

- [ ] 1. Agree the competitors with the owner (three to five, local first).
      Find more by reading the live results for the owner's own search terms.
- [ ] 2. **Customers' words.** Reviews of the owner and of competitors
      (five-star for hooks, one-star for objections), comments on the
      owner's own posts, People Also Ask and autocomplete for the owner's
      terms. Save what you read to `raw/`, then write verbatim phrases into
      `research/audience.md` under wants, dislikes, worries, objections.
- [ ] 3. **Competitors' ads.** For each, the ad libraries that apply
      (`references/libraries.md` says what each shows and how to read it).
      Save the raw pages or exports to `raw/<library>/<competitor>/`, then
      write `research/competitors/<name>.md`.
- [ ] 4. **Organic.** The top posts of each competitor and of the category,
      ranked by shares, saves and comments (not likes) relative to the
      account's size.
      Add the topic and hook of each to the competitor's file.
- [ ] 5. **Conversations.** Recent threads in the niche (Reddit, LinkedIn,
      Facebook groups, forums) where people ask a question the owner
      can answer or complain about a problem the owner fixes. Write the ten
      worth a reply to `research/conversations.md`: the link, the date, the
      question in a few words, and a draft reply in the owner's voice through
      `copywriting`. Show it as a deliverable; the owner replies.
- [ ] 6. **The brief.** Write `research/brief.md` (shape below) and tell the
      owner the three things that change what you would make.

## What to record per competitor

- who they are, the offer and price, what the landing page promises
- active ads by library and the format mix
- their three to five longest-running active ads: hook, angle, format,
  start date, days running, variants, platforms, one line on why it is kept
- the angles they repeat and the claim they lean on (price, speed, proof,
  identity)
- top organic posts: topic and hook
- what their customers praise and complain about, three to five phrases each
- their gap: a question or objection their ads and comments leave unanswered

## Reading the signals

Strongest first: the same angle across three or more competitors (the
market has validated it); several variants of one concept (someone paid to
iterate); days running while still active (30 means it survived testing, 90
is a staple); reach where a library shows it; the same ad across platforms.
Discount brand, retargeting and catalogue ads, which run for years by
design. A library never shows how well an ad works; only the owner's own
account does, and that outranks everything here.

## The brief

`research/brief.md`, one page: the three recurring angles with who runs
them and for how long; the two longest-lived formats; the top five customer
phrases; the top three objections; the angle nobody claims; the searches worth a post; and five to
eight hypotheses, ranked by signal strength and ease of production, each
as "We believe [hook, format or angle] will work because [observation over
time] suggests [what the audience does]."

Also note where the market sits: whether every competitor already makes
the same claim (the `ideas` skill decides what that means).

## Lines not to cross

- **Record phrases, not people.** Keep comment and review text with its URL
  and date; keep no names, handles, photos or profile links. Never build a
  list of individuals from comments. A public post is still personal data.
- **Patterns, never copies.** Write down the idea one level above the
  execution ("before and after of a real job, split frame"), never a
  competitor's words or images, and never paste either into a prompt.
- **A customer's words in an ad need their consent**, whoever they were
  written about. Mined language shapes the wording; it is not quoted.
- **Read, don't harvest.** A handful of pages, short quotes into a private
  note. No bulk collection from Yelp, Reddit or Amazon, no LinkedIn
  profiles or contact data, no automated likes or comments.
- **Stop at a login, an age gate or a CAPTCHA** and say so. A connection the
  owner grants is the sanctioned way past it, used the way its instructions
  say.

## Cadence

A full pass at setup. Monthly: re-read competitors' active ads and note
what is new, what stopped, and what crossed 30 or 90 days. Weekly while
anything is live: the owner's own comments and results first, then new
conversations worth joining. Quarterly, or
before a launch or a price change: reviews, searches and organic again, and
a new brief.

## References

- `references/libraries.md`: what Meta, Google, LinkedIn and TikTok's ad
  libraries show, where, for how long, and how to read each
