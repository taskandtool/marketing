# Shot briefs for video models

Checked October 2026 against BytePlus's Seedance guides, Google's Veo 3.1
guide and fal's Kling 3.0 guide. When a connected model brings its own
instructions, those win.

## What each family changes

- **Seedance 2.0.** Order the story as "Shot 1, Shot 2, Shot 3"; its own
  guide says timing in seconds is unstable. Bind each subject to its image
  every time ("the woman in Image 1"), or define a label once and reuse it
  word for word. Describe actions by body part, speed and force; prefer
  slow, continuous, small movements. One camera move per shot. Show emotion
  as behaviour ("lets out a long breath, shoulders drop").
- **Seedance 2.5.** Up to 30 s and many references; a one-sentence summary
  first, then whole-second timestamps or Shot N. Too little in a range and
  it improvises; too much and it adds cuts. A 480p draft can be checked
  before paying for the final render.
- **Seedance, both.** Reference images or video containing a real person's
  face are refused. An owner who wants to appear needs real footage.
- **Veo 3.1.** Cinematography, subject, action, context, style. Timestamp
  blocks (`[00:00-00:02]`) give several shots in one 4, 6 or 8 s clip.
  Audio as `A woman says, "…"`, `SFX: …`, `Ambient noise: …`. Write
  negatives as positives ("an empty street").
- **Kling 3.0.** Up to 15 s and six shots; label each shot's framing,
  subject and motion; give characters stable labels.

## Keeping shots consistent

1. Make the hero still first with the image model and use it as the
   reference or first frame of every clip.
2. Repeat the same subject labels and the same CONSTANTS paragraph word for
   word in every brief.
3. Make several shots inside one generation where the model allows it,
   rather than stitching separate clips.
4. Keep reference images at or below the output resolution.

## Failures and fixes

| Failure | Fix |
|---|---|
| Subtitles nobody asked for | Don't repeat dialogue words; generate landscape and crop when it persists |
| Logos or watermarks | Say so in the constraints; turn the watermark option off |
| Music despite "no music" | List music, BGM, score, instrumental, melody; repeat at the start and the end; strip it in the edit |
| A face drifts, or the wrong person | A close-up headshot reference first; references in order of appearance; four people at most |
| Duplicated people | Bind each name to its image; "no duplicate characters" |
| Words on screen come out garbled | Don't ask for them; add text in the edit |
| Plastic effects, glowing eyes | "no 3D, no cartoon, no visual effects"; tone down emotion words |
| Big actions break physics | Slow, small, continuous motion; one camera move per shot |

## A worked brief (Seedance 2.5, 10 s, 9:16)

Image 1 is the product still made first; Image 2 is the kitchen.

> Image 1 is the honey jar; keep its label exactly. Image 2 is the kitchen
> setting. A 10-second vertical video of morning breakfast at a farmhouse
> table, natural documentary style. 0 to 3 s: macro close-up, slow push-in
> on the wooden dipper lifting from the jar, a thick ribbon of honey folding
> back into itself; soft window light from the left. 3 to 7 s: medium shot,
> static camera; a hand enters from the right and drizzles honey across a
> slice of sourdough, the drip catching the light. 7 to 10 s: the camera
> slowly pulls back to show the jar from Image 1 beside the plate. Audio:
> quiet kitchen ambience, a spoon set down on a saucer, birdsong outside; no
> music, no BGM, no score, no voice. Keep the label, the light and the warm
> natural grade the same throughout. No subtitles, no text, no logo, no
> watermark.

On Seedance 2.0, write the three beats as Shot 1, Shot 2, Shot 3 instead of
seconds.
