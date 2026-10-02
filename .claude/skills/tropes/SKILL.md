---
name: tropes
description: "Audit a creative for the tells of AI-made work in its copy, pictures and video, and remove them before the owner sees it. Use after any creative is drafted or generated, before setting status sent, or when the owner says it looks or sounds like AI. Not for writing the first draft (copywriting, images, video)."
---

# Tropes

A tell is an unspecified default: the model's average where this business's
particular should be. Platforms now label AI-made ads and audiences trust
them less, so a creative that reads or looks generated costs the owner
twice. The fix is never a synonym; it is the specific thing that was missing.

## The audit

Copy and tick, for each creative:

- [ ] 1. **Copy, by script.** `python3 scripts/tropes.py
      creatives/<folder>/creative.md`. Rewrite every flagged line whole.
- [ ] 2. **Copy, by eye.** Read it aloud against `brand/voice.md`. Would the
      owner say it? Does it use their words? Could a competitor run it
      unchanged? Is a pattern the script let through (one triad, a
      contrast) actually earned? `references/copy.md` lists the tells.
- [ ] 3. **Pictures.** Open each image at full size and at 25%. Check every
      item in `references/images.md`: light with no source, waxy skin,
      symmetry, heavy blur behind the subject, teal and orange grading, stock
      poses, glossy 3D icons, letters that are wrong or extra. Any word in
      the picture is checked letter by letter against the copy.
- [ ] 4. **Video.** Look at frames at 0, 25, 50, 75 and 100% and compare the
      product, any logo and any face across them (`references/video.md`).
- [ ] 5. Fix at the source: rewrite the copy, re-prompt the picture with the
      missing specific, regenerate the shot. Then run the audit again.
- [ ] 6. Note what you changed in the creative's `## Notes`, one line.

## Rules

- Strongest tells first: invented proof, the negation pivot ("it's not X,
  it's Y"), significance inflation, then vocabulary.
- A real photograph of the business's own work beats any fix to a
  generated one. Offer that first when a picture keeps failing.
- Generated people never stand in for customers, staff or testimonials.
- The word lists date with each model generation; treat them as a dated
  list, and the structures as the lasting part.

## References

- `references/copy.md`: vocabulary, structures, rhythm and claims tells,
  each with its fix
- `references/images.md`: picture tells and their fixes
- `references/video.md`: video tells and their fixes
