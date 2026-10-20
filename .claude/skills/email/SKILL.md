---
name: email
description: "Writes cold emails and newsletters in the owner's voice: a short outreach sequence to a list the owner provides, or this month's newsletter, as drafts in the owner's own Gmail or Klaviyo. Use for a cold email, an outreach sequence, a newsletter, or an email to past customers. Not for ads or posts (ad, social-post)."
---

# Email

Email goes out from the owner's own account, never ours.

## Cold email

- **The list:** one the owner gives, or one built through a contact
  service (the `playbooks` skill, cold email), in `lists/`: name, company,
  email, and why this person. Never guess an address; a list from a
  contact service is verified before anything is sent. A row with no
  reason is a question for the owner.
- **One reader, one reason, one ask.** Plain text, under 120 words. The
  first line is about them (the reason), never about the business. No
  images, and no link in the first email beyond the signature.
- **A sequence is two or three emails over about ten days:** the first, a
  short follow-up that adds something new, and at most a last note that
  closes the loop.
- **Every email carries the business's postal address and a way out**
  ("Reply no and I won't write again"). Where the reader lives decides the
  rest: in the EU and UK, writing to a person at a company needs a real
  business reason, and writing to a consumer needs their consent. When
  unsure, ask the owner.

## Newsletter

Only to people who signed up. One idea per issue from this month's work (a
result, a lesson, a question customers keep asking), a subject line under
50 characters, and one link.

## Files

`emails/YYYY-MM-DD-<slug>/email.md`, frontmatter `kind: cold | newsletter`,
`audience` and `status`, then each email with its subject, preview line and
body. The words go through `copywriting`, facts only from `claims.md`, then
the `tropes` audit. Show `email.md` as a deliverable (`create-deliverables`,
the `work` skill).

## Drafts and sending

- **Gmail:** when the owner's `google` connection has Gmail compose
  access, one draft per recipient on its `google-gmail` endpoint
  (`POST /gmail/v1/users/me/drafts`); `POST /gmail/v1/users/me/drafts/send`
  sends one, once the owner says so. A handful of cold emails go this way.
- **Klaviyo:** a newsletter goes in as a campaign through the `klaviyo`
  connection; the owner sends it.
- **Cold email at volume:** the leads go into a campaign in a sending tool
  the owner connected (`instantly`), sending from mailboxes on separate
  domains, never the main one. The owner starts the campaign. Postmark and
  Resend are for transactional mail, and their terms forbid cold email.
- **Neither connected:** the files are the drafts; say so, and the owner
  pastes them.
