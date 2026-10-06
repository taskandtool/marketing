---
name: ad
description: "Makes a paid ad from an idea: the format, the hook, copy and picture or video put together to one platform's specs, then checked. Use when the owner asks for ads, a static, a set to test, or a creative for Meta, Instagram, TikTok, LinkedIn, Google, Pinterest or YouTube. Not for organic posts (social-post)."
---

# Ad

An ad is one idea in one format with one hook, made to one platform's
specs. A test set is three ideas in three formats or hooks: nine ads that
differ in argument, not colour.

## Steps

Copy and tick:

- [ ] 1. Start from a `creatives/<folder>/creative.md` the `ideas` skill
      wrote, or write one with it first.
- [ ] 2. **Format.** Pick from `references/formats.md` (read the entry, not
      the file). Lo-fi formats (a sticky note, a phone photo, a screenshot)
      win more often than they are used; they are a first choice, not a
      fallback.
- [ ] 3. **Hook and copy** (the `copywriting` skill) into `copy:`
      (`headline`, `primary_text`, `description` or `caption`, `cta`).
- [ ] 4. **Picture or video** (the `images` or `video` skill), at the
      platform's sizes in `specs/<platform>.md`; vertical placements keep
      words inside the safe zone. Each ratio is its own generation.
- [ ] 5. **Audit.** `python3 scripts/check.py <folder>`, then the `tropes`
      skill. Fix everything.
- [ ] 6. **Show.** Attach the files as deliverables with one line each:
      the idea, the format, and what you changed in the audit. Set `status:
      sent`.

## Rules

- The words on the picture are readable at phone size, the headline larger
  than the logo, and the call to action worded as in the copy.
- Health, finance and before-and-after claims follow the platform's sheet
  in `specs/`. `scripts/check.py` fails on hashtags and personal attributes
  ("Are you in debt?") in an ad.

When it has run, the `marketing` skill records the results.

## References

- `references/formats.md`: 45 static formats as recipes, with when each
  works and its pitfalls
- `specs/<platform>.md`: sizes, text limits, safe zones and policy, dated
