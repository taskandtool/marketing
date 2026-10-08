---
name: playbooks
description: "Growth strategies a business could run for months: paid ads with remarketing, cold email, LinkedIn and X outreach, a show and newsletter, podcast guesting, creators, search pages, signup emails. Use when the owner asks how to grow, reach more buyers, find leads, for a marketing plan, or to set one up. Not for one ad, post or email."
---

# Playbooks

A playbook is a way of winning customers that runs for months: a channel,
the services it runs on, and the number that says it works. These come
from Cody Schneider's public posts (@codyschneider, 2025 to 2026),
rewritten for this app. They are ideas to offer, not procedures. The tools
a file names are examples: whatever the owner has connected that does the
job works the same way, and the flow does not change with the tool.

## Choosing

Propose two or three, never the whole list. What decides it: who buys
(businesses or people, local or national), what exists already (a list,
traffic, proof in `claims.md`, an ad budget, the owner's time on camera),
and how soon it has to pay. Read a playbook's file before proposing it.
Lay each one out with what it needs and its risks, the automated and paid
versions included, and let the owner decide how far to go; never leave a
fitting one out because it is automated or costs money.

| Playbook | Fits | File |
|---|---|---|
| Paid ads and remarketing | a clear offer and a budget; tracking first | `references/paid-ads.md` |
| Ad creative at scale | ads already running, a budget for testing | `references/ad-testing.md` |
| Cold email | sells to businesses; a reachable buyer | `references/cold-email.md` |
| Cold DMs | buyers active on LinkedIn or X | `references/cold-dms.md` |
| A show and newsletter | B2B, a niche of buyers worth interviewing | `references/show-and-newsletter.md` |
| Guest on podcasts | an owner with a story and an opinion | `references/podcast-guesting.md` |
| YouTube creators | a niche with creators who already teach it | `references/youtube-creators.md` |
| Short-form creator team | a consumer product people film themselves using | `references/creator-team.md` |
| Search pages that convert | people search for the problem or the category | `references/search-pages.md` |
| Signup emails | a free trial, signup, quote or booking to follow up | `references/signup-emails.md` |
| Weekly update email | a list of customers or signups | `references/weekly-update.md` |

They compound. A business selling to businesses might run cold email, show
the same list ads, invite its buyers onto a show, send a newsletter from
each episode, clip it for social, and grow the newsletter from the cold
email.

Write what the owner picks to `plan.md`: each playbook, why it fits, what
it needs, the number to watch and when to look again.

## Connections

Most playbooks need a service or two. Before proposing,
`python3 ~/tools/taskandtool.py list-connections` shows what this app
holds. Tell the owner what is connected already and can do the job, what
else a playbook would want (the kind of tool, an example or two, that it
bills their account), and that they can look over and add connections on
the app's Connections tab. Once they choose, ask for what is missing by
the vendor's name in lowercase (`python3 ~/tools/taskandtool.py
request-connection apollo --why "find the emails of practice managers"`);
a tool the catalogue lacks is added there as Build your own.

## Rules

- Collecting about people (contacts, engagers, profiles) is done by the
  connected service (Apify, PhantomBuster, Apollo), on its terms; this
  machine never signs in to a social site or scrapes behind a login.
- The people a playbook reaches go in `lists/` (its README), so a repeat
  run skips anyone already contacted and everyone who said no.
- Nothing is spent, sent, posted or launched without the owner's yes.
  Ads go up paused; emails and DMs go out from the owner's tools.
- Run it by hand once and show the owner; repeat it only when it works
  ("Making it repeat" in the `marketing` skill).
- A number in `plan.md` or a report comes from the owner's accounts, never
  from a playbook's example.
