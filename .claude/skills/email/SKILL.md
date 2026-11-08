---
name: email
description: "Writes email to people who already know the business: the newsletter, follow-ups after a signup, booking or quote, and notes to past customers, as drafts in the owner's Gmail or Klaviyo. Use for a newsletter, a follow-up sequence, or an email to customers or the list. Not for cold email (cold-email)."
---

# Email

Email to people who signed up, booked, asked for a quote or bought. It
goes out from the owner's own account, never ours, and only to people who
agreed to hear from the business. Every email has one reason to open it and
one thing to do, and says how to stop getting them.

## Kinds

- **Newsletter:** one idea from recent work (a result, a lesson, a question
  customers keep asking), a subject under 50 characters, one link. Weekly
  or monthly at the same time; a week with nothing new is skipped, not
  padded. Material comes from `creatives/`, `results.md` and what the owner
  says.
- **Follow-ups** after a signup, booking or quote, starting the moment it
  happens:
  - straight away: thanks, and what happens next;
  - a day later: how to get the most from it, or what to have ready;
  - then a few days apart: why the business does it this way, one
    customer's story an email, and a check-in from the owner ("any
    questions?").

  Stop when they buy, book or reply. Replies come to a real inbox, and an
  answer is drafted for the owner.
- **Past customers:** the reminder they would want (a yearly service, the
  season's job), or one piece of news worth their time. Never a
  discount blast to everyone.

Example, a newsletter:

```
Subject: Why your radiators are cold at the top

Hi Ruth,

Three of the jobs we did this month were radiators cold at the top. All three needed bleeding, not a new boiler.

It takes two minutes with a radiator key. Turn the heating off, open the valve at the top corner a quarter turn until water comes out, then close it. Check the pressure gauge is back between 1 and 1.5.

If it's still cold after that, reply and I'll tell you what to check next.

Mark, Hollis Heating
Not useful? Unsubscribe here.
```

## Files

`emails/YYYY-MM-DD-<slug>/email.md`: frontmatter `kind: newsletter |
follow-up | customers`, `audience` and `status`, then each email's
subject, preview line and body (a follow-up sequence lists when each one
goes). Facts only from `claims.md`. Run `python3 scripts/check.py` (it
scans `emails/`), then show `email.md` as a deliverable
(`create-deliverables`, in the `work` skill).

## Drafts and sending

- **Klaviyo:** a newsletter goes in as a campaign, and a follow-up sequence
  as a flow, through the `klaviyo` connection. The owner sends or turns it
  on.
- **Gmail:** a note to a few customers goes as one draft each through the
  owner's `google` connection (`POST /gmail/v1/users/me/drafts`), sent only
  when the owner says.
- **Neither connected:** the files are the drafts. Say so, and the owner
  pastes them.
