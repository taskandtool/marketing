---
name: ad
description: "Makes a paid ad from an idea: the format, the hook, copy and picture or video put together to one platform's specs, then checked. Use when the owner asks for ads, a static, a set to test, or a creative for Meta, Instagram, TikTok, LinkedIn, Google, Pinterest or YouTube. Not for organic posts (social-post)."
---

# Ad

One idea in one format with one hook, made to one platform's specs. A test
set is three ideas from the `ad-ideas` skill, each in three formats: nine
ads. For a service business, start with three formats: a photo with one
line on it, a testimonial, and a lo-fi one (a sticky note, a phone photo). With an
offer, one of the three is an offer-first banner.

## Steps

Copy and tick:

- [ ] 1. Start from a `creatives/<folder>/creative.md` from the `ad-ideas`
      skill, or write one with it first.
- [ ] 2. **Format** from `references/formats.md` (read only its entry).
- [ ] 3. **Hook and copy** with the `copywriting` skill, into `copy:`
      (`headline`, `primary_text`, `description` or `caption`, `cta`).
- [ ] 4. **Picture or video** (the Pictures section of `AGENTS.md`, or the
      `video` skill) at the sizes in `specs/<platform>.md`, words inside
      the safe zone, each ratio generated separately.
- [ ] 5. **Audit:** `python3 scripts/check.py <folder>`, then the `tropes`
      skill. Fix everything.
- [ ] 6. **Show:** `python3 scripts/preview.py <folders> --send "<line>"`
      once for the set, and one line per ad in the chat: the idea, the
      format, what the audit changed.

```yaml
copy:
  headline: "The engineer who fitted it services it"
  primary_text: "Same two engineers on every visit since 2004. Book your service before the first cold week."
  cta: "Book a service"
```

## Rules

- **One name for an ad everywhere:** its folder name in Ads Manager, with
  `utm_source=facebook&utm_medium=paid&utm_campaign={{campaign.name}}&utm_content={{ad.name}}`,
  so Meta's spend and the CRM's leads match on it.
- Words on the picture read at phone size, the headline is larger than the
  logo, and the call to action matches the copy.
- Health, finance and before-and-after claims follow `specs/`.
  `scripts/check.py` fails on hashtags and personal attributes ("Are you
  in debt?").
