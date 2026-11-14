---
name: ad
description: "Makes a paid ad from an idea: picks the format, writes the hook and copy, makes the picture or video to one platform's specs, and checks it. Use when the owner asks for ads, a static, a set to test, or a creative for Meta, Instagram, TikTok, LinkedIn, Google, Pinterest or YouTube. Not for organic posts (social-post)."
---

# Ad

An ad is one idea from the `ad-ideas` skill in one format, with one hook,
made to one platform's specs. A test set is three ideas, each in three
formats: nine ads. For a service business, start with three formats: a
photo with one line on it, a testimonial, and a lo-fi ad (a sticky note, a
phone photo). With an offer, make one of the three an offer-first banner.

## Steps

Copy and tick:

- [ ] 1. Start from a `creatives/<folder>/creative.md` from the `ad-ideas`
      skill, or write one with it first.
- [ ] 2. **Format** from `references/formats.md` (read only its entry).
- [ ] 3. **Hook and copy** with the `copywriting` skill, into `copy:`
      (`headline`, `primary_text`, `description` or `caption`, `cta`).
- [ ] 4. **Picture or video:** make the picture (the Pictures section of
      `AGENTS.md`) or the video (the `video` skill) at each size in
      `specs/<platform>.md`. Generate each ratio separately, and keep the
      words inside the safe zone.
- [ ] 5. **Audit:** `python3 scripts/check.py <folder>`, then the `tropes`
      skill. Fix everything.
- [ ] 6. **Show:** run `python3 scripts/preview.py <folders> --send "<line>"`
      once for the whole set. In the chat, write one line per ad: the idea,
      the format and what the audit changed.

```yaml
copy:
  headline: "The engineer who fitted it services it"
  primary_text: "Same two engineers on every visit since 2004. Book your service before the first cold week."
  cta: "Book a service"
```

## Rules

- **Name the ad by its folder.** Use the folder name as the ad name in Ads
  Manager, and add
  `utm_source=facebook&utm_medium=paid&utm_campaign={{campaign.name}}&utm_content={{ad.name}}`
  to its link. With one name in both, you can match Meta's spend to the
  CRM's leads.
- Make the words on the picture legible at phone size and the headline
  larger than the logo. The call to action on the picture matches the one
  in the copy.
- Follow `specs/` for health, finance and before-and-after claims.
  `scripts/check.py` fails on hashtags and personal attributes ("Are you
  in debt?").
