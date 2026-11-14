---
name: research
description: "Researches the market into research/ and a brief: competitors' sites, ads and posts, customers' reviews and comments, search questions and threads worth replying to. Use when the owner asks what competitors are doing, what customers say or where to reply, before the first ideas, or monthly. Not for the business's own facts (brand)."
---

# Research

Read competitors' ads for what they keep paying for, and posts, comments,
reviews and searches for what customers say. Do customers first, and end
with a brief for the `ad-ideas` skill.

Fetching:

- a competitor's site: `tt-crawl survey <url> --external` (into
  `raw/external/<host>/`)
- ad libraries, social posts and comments: the `scrapecreators` connection
- reviews on a site with no API (Google Maps), recent threads on Reddit,
  LinkedIn, Facebook groups and forums, and the TikTok Creative Center's
  top ads for the industry: `apify`
- People Also Ask, autocomplete and monthly search volume: `dataforseo`
- a business's Google listing: the brand skill's `tt-crawl places` line

Ask for any connection that is not granted, for example:

```bash
python3 ~/tools/taskandtool.py request-connection scrapecreators --why "competitors' ads and posts"
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
- [ ] 3. **Competitors' ads.** Read each competitor's ads in the libraries
      that apply (`references/libraries.md` says what each shows and how to
      read it).
      Save the raw pages or exports to `raw/<library>/<competitor>/`, then
      write `research/competitors/<name>.md`.
- [ ] 4. **Organic.** Find the top posts of each competitor and of the
      category, ranked by shares, saves and comments (not likes) relative to the
      account's size.
      Add the topic and hook of each to the competitor's file.
- [ ] 5. **Conversations.** Recent threads in the niche (Reddit, LinkedIn,
      Facebook groups, forums) where people ask a question the owner
      can answer or complain about a problem the owner fixes. Write the ten
      worth a reply to `research/conversations.md`: the link, the date, the
      question in a few words, and a draft reply in the owner's voice (the
      `copywriting` skill). Show it as a deliverable; the owner replies.
- [ ] 6. **The brief.** Write `research/brief.md` (shape below) and tell the
      owner the three things that change what you would make.

## What to record per competitor

- who they are, the offer and price, what the landing page promises
- active ads by library and the format mix
- their three to five longest-running active ads: hook, angle, format,
  start date, days running, variants, platforms, one line on why they keep
  running it
- the angles they repeat and the claim they lean on (price, speed, proof,
  identity)
- top organic posts: topic and hook
- what their customers praise and complain about, three to five phrases each
- their gap: a question or objection they never answer in their ads or
  comments

## Reading the signals

Strongest first:

1. the same angle from three or more competitors (proven by the market)
2. several variants of one concept (someone paid to test it)
3. days running on an active ad (`references/libraries.md` has the bands
   and the ads to discount)
4. reach, where a library shows it
5. the same ad on several platforms

No library shows how well an ad works. Only the owner's own account shows
that, and it outranks everything here.

## The brief

`research/brief.md`, one page:

- the three recurring angles, with who runs them and for how long
- the two longest-lived formats
- the top five customer phrases and the top three objections
- the angle nobody claims
- the searches worth a post
- five to eight hypotheses, ranked by signal strength and ease of
  production, each as "We believe [hook, format or angle] will work because
  [observation over time] suggests [what the audience does]."

Also note the market's sophistication: whether every competitor already makes
the same claim (the `ad-ideas` skill decides what that means).

## Lines not to cross

- **Record phrases, not people.** Keep comment and review text with its URL
  and date; keep no names, handles, photos or profile links here. A public
  post is still personal data. Lists of people to contact
  come from a connected service and are kept apart from `research/`.
- **Record the pattern, not the ad.** Write down the idea one level above
  the execution ("before and after of a real job, split frame"). Never copy
  a competitor's words or images, or paste either into a prompt.
- **Quote a customer in an ad only with their consent**, even when they
  wrote about a competitor. Use mined phrases to shape your wording; don't
  quote them.
- **Fetch only what the brief needs.** Set a results limit on every run and
  keep short quotes. Never like or comment automatically.
- **Stop at a login, an age gate or a CAPTCHA** and say so. The only way
  past one is a connection the owner grants, used as its instructions say.

## Cadence

A full pass at setup. Monthly: re-read competitors' active ads and note
what is new, what stopped, and what crossed 30 or 90 days. Weekly while
anything is live: the owner's own comments and results first, then new
conversations worth joining. Quarterly, or before a launch or a price
change: reviews, searches and organic again, and a new brief.
