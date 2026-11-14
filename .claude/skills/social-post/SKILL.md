---
name: social-post
description: "Writes organic social posts, slideshows and carousels in the owner's voice for Instagram, Facebook, LinkedIn, TikTok, Google Business, Pinterest and X. Turns one idea into a week of posts. Use when asked for a post, a caption, this week's posts, or \"repurpose this\". Not for paid ads (the ad skill)."
---

# Social post

More people see a post when the first viewers send it, save it, comment
or keep watching. So open with a moment, a number or a question the
reader recognises, give something worth keeping, and ask for one small
thing the platform rewards.

Example, for Instagram:

```
Three of the five boilers we saw this week had the same problem: pressure under 1 bar.

Check yours now. The gauge is on the front, usually bottom left. Between 1 and 1.5 is right when the heating's off. Under 1, top it up with the filling loop (a video on how is in our highlights).

Save this for the first cold morning.
```

## Steps

Copy and tick:

- [ ] 1. **Platform and pillar.** Read `references/<platform>.md` for the
      platform. Pick the pillar: education, proof, behind the scenes, offer
      (at most one post in five) or community (`references/repurpose.md`).
- [ ] 2. **The idea**, from the sources below.
- [ ] 3. **The hook and the words** (the `copywriting` skill). The first
      line stands alone: the hook and its payoff before the platform's
      visible cutoff (in `specs/<platform>.md`; for X and Google Business, in
      their `references/` file).
- [ ] 4. **One ask**, matched to what the platform rewards: "Save
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
- [ ] 7. **Posting**, once the owner approves. Schedule it through a
      posting connection the owner has (Zernio, Hootsuite) for the time
      they chose, then set `status: posted` and the live `url`. With no
      connection, the owner posts it.

## Where post ideas come from

Every enquiry and FAQ ("people always ask"); the job in hand (before and
after, a detail, one decision explained); reviews (the quote, then the story
behind it); the objection competitors leave unanswered; the season and the
local calendar; comments on the owner's own posts (answer them as posts);
the owner's own numbers and opinions; and any ad that won, recut for the
feed.

## One idea, a week of posts

Follow `references/repurpose.md`: write each platform's version fresh for
that platform. Accounts that mostly
repost or cross-post unchanged lose reach on Instagram and Facebook.

## Rules

- Replies to comments count as part of the post. Suggest the owner replies
  in the first hour.
- No engagement bait ("tag a friend"), no hashtag walls, no watermarked
  reposts.
- Quote a review as written, with permission. Use customer photos with
  permission and credit.

## References

- `references/repurpose.md`: the pillars, one idea across platforms, the
  weekly cadence
- `references/<platform>.md` (instagram, facebook, linkedin, tiktok, gbp,
  pinterest, x): what performs, the norms, recipes
