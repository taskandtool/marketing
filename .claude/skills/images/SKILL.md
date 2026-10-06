---
name: images
description: "Makes the picture for an ad or post: the owner's own photo or a written image prompt, generated and checked. Use when a creative needs a still, a product shot, an edit of the owner's photo, or words set in a picture. Not for video (video) or judging AI tells (tropes)."
---

# Images

Look in `media/_index.md` for the owner's own photo before generating
anything. Generate when there is no photo of the thing, or to place the
owner's product in a new scene.

## Steps

Copy and tick:

- [ ] 1. Read the creative's idea, the format's recipe
      (`ad/references/formats.md` or the post's form) and the Imagery block
      in `brand/visual-identity.md`.
- [ ] 2. Write the prompt under `## Prompt` in the creative's
      `creative.md`, in the shape below.
- [ ] 3. Generate: `python3 scripts/imagegen.py --prompt-file
      creatives/<folder>/creative.md --ratio 4:5 --out
      creatives/<folder>/v1.png [--ref <photo>] [--brand]`. Each
      placement's ratio is its own generation, never a crop.
- [ ] 4. Look at the result at full size and at 25%. Run the `tropes`
      picture checks. Change one thing and generate `v2.png`; two or three
      rounds is normal.
- [ ] 5. List the kept file in `files:`.

## The prompt

Write it like a creative brief, in plain sentences, labelled when it is
long:

1. **Use**: what it is for ("a product photograph for a 4:5 Instagram feed
   ad").
2. **Subject at a moment**: the owner's actual thing mid-action or just
   after, never the category word alone.
3. **Composition**: where the camera is, what is in frame, what is cropped.
4. **Place, materials, light**: one real light source with real shadow; the
   brand's colour on one object, not as a tint.
5. **Words**, if the picture carries any: in quotes, with position and
   type, and how many times ("render the headline exactly once"). Spell
   names letter by letter. Otherwise name the plain space the words will
   sit beside.
6. **Keep**, for an edit with references: number each image and give it a
   role ("Image 1 is the product: keep its shape, lid, label and label text
   unchanged"), then "change only" the one thing.
7. **Realism**: "real photograph, honest and unstaged, no glamorization, no
   heavy retouching". Camera details steer the look; quality adjectives
   ("8k, ultra-detailed, cinematic") make stock.

Six to ten sentences. `--brand` appends the brand's style anchor, so a set
looks like one brand.

## Rules

- No interface, chart or product the business does not make is painted.
- Every word in a picture is checked letter by letter against the copy.

## References

- `references/prompting.md`: what the current image models need, edits
  with references, and two worked prompts
