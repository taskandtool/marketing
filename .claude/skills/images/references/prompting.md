# Prompting image models

Checked October 2026 against OpenAI's image prompting guide and cookbook.
Model names and parameters change often: when a connection brings its own
instructions, those win.

## What current models do well

- **Text in the picture.** OpenAI's GPT Image models set words reliably
  when the prompt quotes them exactly, names their position and type, and
  says how often they appear: `Billboard text (EXACT, verbatim, no extra
  characters): "Fresh and clean"`. Use medium or high quality for small
  text. Still check every letter.
- **Edits that keep the product.** Give each input a number and a role
  (subject, style, background), say "change only X", and list everything to
  keep (shape, label, geometry, light, angle). Repeat the keep list on every
  turn; feed the last output back in for the next change, one change a
  turn.
- **Custom sizes.** Render each placement at its own ratio rather than
  cropping one master (the platform sheets in `specs/` give the sizes).

## Ads read like a brief

The cookbook's advice for ads: write the prompt "like a creative brief
rather than a purely technical image spec": the brand, the audience, the
feel, the scene, the exact line.

## Away from the stock look

Ask for a "real photograph" and "no glamorization, no heavy retouching";
avoid "cinematic lighting" and "dramatic colour grading". One real light
source, plausible depth of field, signs of use in the room, the subject off
centre.

## Worked prompts

**A product placed in a scene (edit, 4:5).** Image 1 is the owner's photo of
a jar of honey.

> Use: product photograph for a 4:5 Instagram feed ad. Image 1 is the
> product: keep its exact jar shape, lid, label artwork and label text
> unchanged. Scene: the jar on a scrubbed oak farmhouse table by a north
> window, early morning, a wooden dipper resting across a saucer with one
> slow drip, a cut slice of sourdough beside it. Light: soft overcast window
> light from the left, real shadows. The top third is a plain cream plaster
> wall with nothing on it. Real photograph, honest and unstaged, no
> glamorization. No added text, logos or watermarks.

**Words set in the picture (generate, 4:5).**

> Use: a 4:5 Facebook feed ad for a heating firm in Leeds. Scene: a
> terraced-house hallway in January, a radiator under the window, a pair of
> wellies by the door, morning light from the fanlight. On a plain paper tag
> tied to the radiator valve, handwritten in black marker, the text
> (EXACT, verbatim, once): "Bled and balanced. Hot by 9." Real photograph,
> no glamorization. No other text, logos or watermarks.
