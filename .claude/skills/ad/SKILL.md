---
name: ad
description: "Makes a paid ad from an idea: the format, the hook, copy and picture or video put together to one platform's specs, then checked. Use when the owner asks for ads, a static, a set to test, or a creative for Meta, Instagram, TikTok, LinkedIn, Google, Pinterest or YouTube. Not for organic posts (social-post)."
---

# Ad

An ad is one idea in one format with one hook, made to one platform's
specs. A test set for a new business or campaign is three angles in three
formats each: nine ads that differ in argument, not colour. The default
for a service business: outcome, social proof and problem, each as a photo
with one line on it (lifestyle / product in use), a testimonial, and one
lo-fi or native format; with an offer, the offer-first banner is in the
first nine.

## Steps

Copy and tick:

- [ ] 1. Start from a `creatives/<folder>/creative.md` the `ideas` skill
      wrote, or write one with it first.
- [ ] 2. **Format.** Pick from `references/formats.md` (read the entry, not
      the file). Lo-fi formats (a sticky note, a phone photo, a screenshot)
      win more often than they are used; they are a first choice.
- [ ] 3. **Hook and copy** (the `copywriting` skill) into `copy:`
      (`headline`, `primary_text`, `description` or `caption`, `cta`).
- [ ] 4. **Picture or video** (the Pictures section of `AGENTS.md`, or the
      `video` skill), at the platform's sizes in `specs/<platform>.md`;
      vertical placements keep words inside the safe zone. Generate each
      ratio separately.
- [ ] 5. **Audit.** `python3 scripts/check.py <folder>`, then the `tropes`
      skill. Fix everything.
- [ ] 6. **Show.** `python3 scripts/preview.py <folders> --send "<line>"`,
      a set to test in one call; in the chat, one line each: the idea, the
      format, and what you changed in the audit.

## Rules

- The words on the picture are readable at phone size, the headline larger
  than the logo, and the call to action worded as in the copy.
- Health, finance and before-and-after claims follow the platform's sheet
  in `specs/`. `scripts/check.py` fails on hashtags and personal attributes
  ("Are you in debt?") in an ad.
