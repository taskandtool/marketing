---
name: results
description: "Measures what ran: the owner's search, ad and post numbers from Google, Meta or their exports into results.md, and a monthly report ending in what to make next. Use when the owner asks how ads or posts did, for the monthly report, or to schedule it. Not for competitors' numbers (research)."
---

# Results

Only the owner's own accounts show what works. A competitor's ad
library does not. Never estimate a number;
leave out any the account does not give.

## Where the numbers come from

- **Search:** the `google-search-console` connection (queries, clicks and
  impressions by page) and the `google-analytics` connection, endpoint
  `google-analytics-data` (visits and conversions by source).
- **Meta ads and Facebook and Instagram posts:** the `meta` connection
  (endpoint `meta-graph`), when the owner ticked its insights and
  `ads_read` access on connecting. Ads: spend, impressions, clicks, leads. Posts: reach, saves,
  shares, comments. If a call is refused for a missing permission, the
  owner didn't tick it. Tell them which to add and use their export until
  then.
- **Every other platform:** the owner's export from the ads manager or the
  platform's insights (a CSV or a screenshot).
- **Public counts** for any post, through `scrapecreators`: views, likes,
  comments; never reach or saves.

A connection's own instructions say how to call it. Ask once for a
connection that is not granted, saying what it gives you:

```bash
python3 ~/tools/taskandtool.py request-connection google-search-console --why "your search traffic for the monthly report"
python3 ~/tools/taskandtool.py request-connection google-analytics --why "your visits and conversions for the monthly report"
```

## Tracking

You get only the numbers the site records, and ad platforms optimise for
those same events. Before ads run, or when numbers look wrong, check with
the owner that every action that matters (signup, booking, enquiry,
checkout) is sent to the analytics and to each ad platform in use. Send
the value and a hashed email where the platform accepts them. The usual
setup is an event in the site's code (the Website app's), tags in Google
Tag Manager, and Meta's Conversions API from the server, each through its
connection when there is one. Test it before it goes live, and publish the
tags only when the owner says yes.

## results.md

Newest first, one block per creative per period: a link to the creative's
folder (`[2026-10-01-roof-leak](creatives/2026-10-01-roof-leak/)`), the
platform, the dates, then the numbers the account gave. Link the folder,
not its `creative.md`: the viewer shows the piece at its folder. Link a
report the same way. Ads: spend, hook rate, hold rate, click-through, cost
per lead. Posts: reach, saves, shares, comments. Give each number its unit
and source. Put search in its own block per period: the queries and pages
that brought visits.

## The monthly report

`reports/YYYY-MM.md`, one page:

- what ran this month and what it cost in total
- the best and worst piece by cost per lead, and by saves and shares
- the searches and pages that brought visits, against last month
- three things to make next, each tied to a number above (on a winner, new
  hooks on the same body; on a loser, a new angle)

Run `python3 scripts/check.py` (it scans `reports/`), then show it as a deliverable:

```bash
echo '[{"path": "reports/2026-10.md", "title": "October report", "status": "info"}]' \
  | python3 ~/tools/taskandtool.py create-deliverables --file - --message "October's results and what to make next."
```

## On a schedule

When the owner wants it monthly, schedule a prompt, not a command: the
report needs judgement. Cron is UTC; pick an hour that is morning in the
business's zone.

```bash
python3 ~/tools/taskandtool.py schedule-job "Monthly results" --when "0 14 1 * *" --prompt "Pull last month's results and send the monthly report (results skill)."
```
