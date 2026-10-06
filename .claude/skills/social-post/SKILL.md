---
name: social-post
description: "Writes organic social posts in the business's voice for Instagram, Facebook, LinkedIn, TikTok, Google Business, Pinterest, X and Threads, or turns one idea into a week of posts. Use when the owner says write a post or caption, what should we post this week, or repurpose this. Not for paid ads (ad)."
---

# Social post

Organic is not an ad with the price taken out. An ad buys attention from
people who did not ask; a post earns it from the people shown it, through
sends, saves, comments and watch time. It opens with a moment, a number or a
question the reader recognises, gives something worth keeping, and asks for
the one small thing the platform rewards.

## Steps

Copy and tick:

- [ ] 1. **Pillar and platform.** Education, proof, behind the scenes,
      offer (at most one post in five) or community
      (`references/repurpose.md`). Read `references/<platform>.md` for the
      platform the idea is for first.
- [ ] 2. **The idea**, from the sources below.
- [ ] 3. **The hook and the words** (the `copywriting` skill). The first
      line stands alone: the hook and its payoff before the platform's
      visible cutoff (`specs/<platform>.md`; for X and Google Business, their
      reference).
- [ ] 4. **The ask**, one, matched to what the platform rewards: "Save
      this", "Send this to someone planning a kitchen", "Reply with yours".
      Links stay out of the body on Facebook, LinkedIn, X and Threads.
- [ ] 5. **The picture**: the owner's own photo first, a carousel of real
      job photos, or a short clip (the `video` skill). Generated pictures
      only for illustrations and backgrounds (the `images` skill).
- [ ] 6. Write `creatives/YYYY-MM-DD-<slug>/creative.md` with `kind: post`,
      the whole caption as it will be pasted in `copy.caption`, and any
      hashtags in `copy.hashtags`. Run `python3 scripts/check.py`, then show
      the owner the picture and the caption as it will appear.

## Where post ideas come from

Every enquiry and FAQ ("people always ask"); the job in hand (before and
after, a detail, one decision explained); reviews (the quote, then the story
behind it); the objection competitors leave unanswered; the season and the
local calendar; comments on the owner's own posts (answer them as posts);
the owner's own numbers and opinions; and any ad that won, recut for the
feed.

## One idea, a week of posts

Write the set in `references/repurpose.md`: each platform's version
rewritten for that platform, never pasted across. Accounts that mostly
repost or cross-post unchanged lose reach on Instagram and Facebook.

## Rules

- The owner posts on LinkedIn and the company page reshares; personal
  profiles reach further there.
- Replying to comments is part of the post; suggest the owner does it in the
  first hour.
- No engagement bait ("tag a friend"), no hashtag walls, no watermarked
  reposts, no one-line-per-paragraph build to a moral.
- A review is quoted as written, with permission; customer photos with
  permission and credit.

## References

- `references/repurpose.md`: the pillars, one idea across platforms, the
  weekly cadence
- `references/<platform>.md`: instagram, facebook, linkedin, tiktok, gbp,
  pinterest, x-threads: what performs, the norms, recipes
