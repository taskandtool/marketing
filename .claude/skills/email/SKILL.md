---
name: email
description: "Writes cold emails and newsletters in the owner's voice: a short outreach sequence to a list the owner provides, or this month's newsletter, as drafts in the owner's own Gmail or Klaviyo. Use for a cold email, an outreach sequence, a newsletter, or an email to past customers. Not for ads or posts (ad, social-post)."
---

# Email

Email goes out from the owner's own account, never ours. Every email has one
reason to open it and one thing to do.

## Cold email

- **The list** is the owner's, or one from a contact service (the
  `growth-plan` skill), in `lists/`: name, company, email, and why this
  person. Never guess an address, and verify a bought list before sending.
  A row with no reason is a question for the owner.
- **Plain text, under 120 words.** The first line is about the reader. No
  images, and no link in the first email beyond the signature.
- **A sequence is two or three emails over about ten days:** the first, a
  follow-up that adds something new, and at most one last note.
- **Every email carries the business's postal address and a way out**
  ("Reply no and I won't write again"). Where the reader lives decides the
  rest. In the EU and UK, writing to a person at a company needs a real
  business reason, and writing to a consumer needs their consent. When
  unsure, ask the owner.

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

## Newsletter

Only to people who signed up. One idea from this month's work (a result, a
lesson, a question customers keep asking), a subject under 50 characters,
and one link.

## Files

`emails/YYYY-MM-DD-<slug>/email.md`: frontmatter `kind: cold | newsletter`,
`audience` and `status`, then each email's subject, preview line and body.
Facts only from `claims.md`. Run `python3 scripts/check.py` (it scans
`emails/`), then show `email.md` as a deliverable (`create-deliverables`, in
the `work` skill).

## Drafts and sending

- **Gmail:** when the owner's `google` connection has Gmail compose access,
  make one draft per recipient on its `google-gmail` endpoint
  (`POST /gmail/v1/users/me/drafts`). `POST /gmail/v1/users/me/drafts/send`
  sends one, once the owner says so. A handful of cold emails go this way.
- **Klaviyo:** a newsletter goes in as a campaign through the `klaviyo`
  connection, and the owner sends it.
- **Cold email at volume:** the leads go into a campaign in a sending tool
  the owner connected (`instantly`). It sends from mailboxes on separate
  domains, never the main one, and the owner starts the campaign. Postmark
  and Resend are for transactional mail, and their terms forbid cold email.
- **Neither connected:** the files are the drafts. Say so, and the owner
  pastes them.
