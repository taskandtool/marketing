---
name: results
description: "Measures what ran: search numbers from the owner's Google accounts, ad and post numbers from Meta or their exports, into results.md, and a monthly report that ends with what to make next. Use when the owner asks how ads or posts did, for the monthly report, or to put it on a schedule. Not for competitors' numbers (research)."
---

# Results

Only the owner's own accounts say what works; a competitor's ad library
never does. Never estimate a number: leave out any the account does not
give.

## Where the numbers come from

- **Search:** `google-gsc` (queries, clicks and impressions by page) and
  `google-ga4` (visits and conversions by source).
- **Meta ads and Facebook and Instagram posts:** the `meta-graph`
  connection, when the owner ticked its insights and `ads_read` access on
  connecting. Ads: spend, impressions, clicks, leads. Posts: reach, saves,
  shares, comments. A call refused for a missing permission means it was
  not ticked: say which to add, and use their export meanwhile.
- **Every other platform:** the owner's export from the ads manager or the
  platform's insights (a CSV or a screenshot).
- **Public counts** for any post, through `scrapecreators`: views, likes,
  comments; never reach or saves.

A connection's own instructions say how to call it. Ask once for a
connection that is not granted, saying what it unlocks:

```bash
python3 ~/tools/taskandtool.py request-connection google --why "your search traffic and visits for the monthly report"
```

## Tracking

Every number here depends on the site recording what matters; ads optimise
for whatever it records. Before ads run, or when numbers look wrong, check
with the owner that each action that matters (signup, booking, enquiry,
checkout) reaches every ad platform in use and the analytics, with the
value and a hashed email where the platform takes them. The usual way: an
event in the site's code (the Website app's), tags in Google Tag Manager,
and Meta's Conversions API from the server, each through its connection
when there is one. Test it before it goes live; publishing the tags is the
owner's yes.

## results.md

Newest first, one block per creative per period: the folder as a link to
it (`[2026-10-01-roof-leak](creatives/2026-10-01-roof-leak/)`, never to its
`creative.md`: the viewer shows the piece at its folder), the platform, the
dates, then what the account gave. A report links the same way. Ads: spend, hook rate,
hold rate, click-through, cost per lead. Posts: reach, saves, shares,
comments. Each number with its unit and its source. Search goes in its own
block per period: the queries and pages that brought visits.

## The monthly report

`reports/YYYY-MM.md`, one page:

- what ran this month and what it cost in total
- the best and worst piece by cost per lead, and by saves and shares
- the searches and pages that brought visits, against last month
- three things to make next, each tied to a number above (on a winner, new
  hooks on the same body; on a loser, a new angle)

Read it with the `tropes` skill, then show it as a deliverable:

```bash
echo '[{"path": "reports/2026-10.md", "title": "October report", "status": "info"}]' \
  | python3 ~/tools/taskandtool.py create-deliverables --file - --message "October's results and what to make next."
```

## On a schedule

When the owner wants it monthly, schedule a prompt, not a command: the
report needs judgement. Cron is UTC; pick an hour that is morning in the
business's zone.

```bash
python3 ~/tools/taskandtool.py schedule-job monthly-results --when "0 14 1 * *" --prompt "Pull last month's results and send the monthly report (results skill)."
```
