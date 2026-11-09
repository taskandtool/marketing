---
name: growth-plan
description: "Plans how the business grows: which two or three strategies to run for months (paid ads, cold email, posting, creators, podcasts, search pages, follow-ups) and what each needs. Use when the owner asks how to grow, for more customers or leads, or a marketing plan. Not for one ad, post or email."
---

# Growth plan

A strategy is a way of winning customers that runs for months: a channel,
the services it runs on, and the number that says it works. Where this app
runs a strategy itself, the table names the skill that runs it. The files
here cover the others. The tools a file names are examples: whatever the
owner has connected that does the job works the same way.

## Choosing

Propose two or three, never the whole list. Start from who buys
(businesses or households) and where (nearby or anywhere), then what
exists already (a list, traffic, proof in `claims.md`, an ad budget, the
owner's time on camera) and how soon it has to pay. Read a strategy's
skill or file before proposing it.

Lay each one out with what it needs and its risks, including the automated
and paid versions, and let the owner decide how far to go. Never leave out
one that fits because it is automated or costs money.

| Strategy | Fits | How |
|---|---|---|
| Paid ads and remarketing | a clear offer and a budget; tracking first | `references/paid-ads.md` |
| Ad creative at scale | ads already running, a budget for testing | `references/ad-testing.md` |
| Cold email | sells to businesses; a reachable buyer | the `cold-email` skill |
| Cold DMs | buyers active on LinkedIn or X | `references/cold-dms.md` |
| A show and newsletter | sells to businesses; buyers worth interviewing | `references/show-and-newsletter.md` |
| Guest on podcasts | an owner with a story and an opinion | `references/podcast-guesting.md` |
| YouTube creators | a niche with creators who already teach it | `references/youtube-creators.md` |
| Short-form creator team | a consumer product people film themselves using | `references/creator-team.md` |
| Search pages that convert | people search for the problem or the category | `references/search-pages.md` |
| Posting every week | every business | the `social-post` skill |
| Follow-ups and a newsletter | a signup, quote or booking to follow up, or a list of customers | the `email` skill |

Several can share one list. A business selling to businesses might run cold
email, show the same list ads, invite its buyers onto a show, send a
newsletter from each episode, clip it for social, and grow the newsletter
from the cold email.

Write what the owner picks to `plan.md`: each strategy, why it fits, what
it needs, the number to watch and when to look again.

## Connections

Most strategies need a service or two. Before proposing,
`python3 ~/tools/taskandtool.py list-connections` shows what this app
holds. Tell the owner what is connected already and can do the job, what
else a strategy would want (the kind of tool, an example or two, that it
bills their account), and that they can look over and add connections on
the app's Connections tab. Once they choose, ask for what is missing by
its catalogue name (`apollo`, `listen-notes`, `brightdata`):
`python3 ~/tools/taskandtool.py request-connection apollo --why "find the
emails of practice managers"`. A tool the catalogue lacks is added there
as Build your own.

## Rules

- Collecting about people (contacts, engagers, profiles) is done by the
  connected service (Apify, PhantomBuster, Apollo), on its terms; this
  machine never signs in to a social site or scrapes behind a login.
- The people a strategy reaches go in `lists/` (its README), so a repeat
  run skips anyone already contacted and everyone who said no.
- Nothing is spent, sent, posted or launched without the owner's yes.
  Ads go up paused; emails and DMs go out from the owner's tools.
- Run it by hand once and show the owner; repeat it only when it works
  ("Making it repeat" in the `marketing` skill).
- A number in `plan.md` or a report comes from the owner's accounts, never
  from a strategy's example.
