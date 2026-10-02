---
name: ad
description: "Make a paid ad from an idea: pick the format, put the hook, copy and picture or video together for one platform's specs, and check it. Use when the owner asks for an ad, a static, a set to test, or a creative for Meta, Instagram, TikTok, LinkedIn, Google, Pinterest or YouTube. Not for organic posts (social-post) or choosing ideas (ideas)."
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
- [ ] 3. **Hook** (the `hooks` skill) and **copy** (the `copywriting` skill)
      into `copy:` (`headline`, `primary_text`, `description` or
      `caption`, `cta`).
- [ ] 4. **Picture or video** (the `images` or `video` skill), at the
      platform's sizes in `specs/<platform>.md`; vertical placements keep
      words inside the safe zone. Each ratio is its own generation.
- [ ] 5. **Audit.** `python3 scripts/check.py <folder>`, then the `tropes`
      skill. Fix everything.
- [ ] 6. **Show.** Attach the files as deliverables with one line each:
      the idea, the format, and what you changed in the audit. Set `status:
      sent`.

## Rules

- On the picture: twelve words or fewer, readable at phone size; the
  headline is larger than the logo.
- The call to action is a verb and an object ("Book a service"), the same
  wording in the copy and on the picture.
- No hashtags in an ad. No competitor named. No personal attributes ("Are
  you in debt?"). Health, finance and before-and-after claims follow the
  platform's sheet in `specs/`.
- A sheet over 90 days old is re-verified before building against it
  (`specs/README.md`).

## After it runs

Record the numbers in `results.md` (newest first): the folder, the
platform, the dates, hook rate, hold rate, click-through, cost per lead.
On a winner, new hooks on the same body first; on a loser, a new angle.

## References

- `references/formats.md`: 45 static formats as recipes, with when each
  works and its pitfalls
- `specs/<platform>.md`: sizes, text limits, safe zones and policy, dated
