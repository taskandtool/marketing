---
name: social-post
description: "Writes organic social posts in the owner's voice for Instagram, Facebook, LinkedIn, TikTok, Google Business, Pinterest and X, slideshows and carousels included, or one idea as a week of posts. Use for a post, a caption, this week's posts, or repurpose this. Not for paid ads (ad)."
---

# Social post

An ad buys attention from people who did not ask; a post earns it from
the people shown it, through sends, saves, comments and watch time. It opens with a moment, a number or a
question the reader recognises, gives something worth keeping, and asks for
the one small thing the platform rewards.

## Steps

Copy and tick:

- [ ] 1. **Pillar and platform.** Education, proof, behind the scenes,
      offer (at most one post in five) or community
      (`references/repurpose.md`). First read `references/<platform>.md`
      for the idea's platform.
- [ ] 2. **The idea**, from the sources below.
- [ ] 3. **The hook and the words** (the `copywriting` skill). The first
      line stands alone: the hook and its payoff before the platform's
      visible cutoff (in `specs/<platform>.md`; for X and Google Business, in
      their `references/` file).
- [ ] 4. **The ask**, one, matched to what the platform rewards: "Save
      this", "Send this to someone planning a kitchen", "Reply with yours".
      Links stay out of the body on Facebook, LinkedIn and X.
- [ ] 5. **The picture**: the owner's photo as it is or edited, a
      carousel of real job photos, a slideshow (`references/slideshow.md`),
      a short clip (the `video` skill), or one made from scratch (the
      Pictures section of `AGENTS.md`).
- [ ] 6. Write `creatives/YYYY-MM-DD-<slug>/creative.md` with `kind: post`,
      the whole caption as it will be pasted in `copy.caption`, and any
      hashtags in `copy.hashtags` as one line (`"#sarasotacoffee
      #downtownsarasota"`). Run `python3 scripts/check.py`, then
      `python3 scripts/preview.py <folder> --send "<line>"`: the owner sees
      it as the feed will show it. A week of posts is one call.
- [ ] 7. **Posting**, once approved: through a posting connection the
      owner has (Zernio, Hootsuite), scheduled for the time they chose,
      then `status: posted` and the live `url`. With none, the owner posts
      it.

## Where post ideas come from

Every enquiry and FAQ ("people always ask"); the job in hand (before and
after, a detail, one decision explained); reviews (the quote, then the story
behind it); the objection competitors leave unanswered; the season and the
local calendar; comments on the owner's own posts (answer them as posts);
the owner's own numbers and opinions; and any ad that won, recut for the
feed.

## One idea, a week of posts

Write the set as `references/repurpose.md` says: each platform's version
rewritten for that platform, never pasted across. Accounts that mostly
repost or cross-post unchanged lose reach on Instagram and Facebook.

## Rules

- Replying to comments is part of the post; suggest the owner does it in the
  first hour.
- No engagement bait ("tag a friend"), no hashtag walls, no watermarked
  reposts, no one-line-per-paragraph build to a moral.
- A review is quoted as written, with permission; customer photos with
  permission and credit.

## References

- `references/repurpose.md`: the pillars, one idea across platforms, the
  weekly cadence
- `references/<platform>.md` (instagram, facebook, linkedin, tiktok, gbp,
  pinterest, x): what performs, the norms, recipes
