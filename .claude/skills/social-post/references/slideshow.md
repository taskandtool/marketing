# Slideshows and carousels

Read when the post is a TikTok slideshow (photo mode) or an Instagram or
LinkedIn carousel. Each platform takes the slides as separate images and
plays them itself, so there is no video to render.

## The slides

- **Slide 1 is the hook**: the promise of the whole set in at most eight
  words ("5 signs you need one system"). Most people decide here.
- **One point per slide**, at most twelve words, big enough to read on a
  phone. Five to eight slides; the last one says what to do next ("Save
  this", "Follow for part 2").
- **One look across the set**: write the style once in the folder's
  `anchor.md` and pass it to every slide, so the set reads as one post.
- **Sizes**: 9:16 for TikTok, 4:5 for Instagram, 1:1 or 4:5 for LinkedIn.

## Making them

The owner's photos first: a slide may be their photo with the line set on
it (`--ref`). Otherwise the image model sets the line in the picture:

```bash
python3 scripts/imagegen.py --prompt-file creatives/<folder>/slide-1.md --ratio 9:16 --anchor creatives/<folder>/anchor.md --out creatives/<folder>/slide-1.png
```

One `slide-N.md` per slide, its prompt under a `## Prompt` heading (that is
the part `imagegen` sends), and the `slide-N.png` it makes, numbered in
order. The caption and hashtags go in `creative.md` as for any post, and
its `files` lists every `slide-N.png`. Read every slide at full size for
misspelt words before the owner sees the set.
