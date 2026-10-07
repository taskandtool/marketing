---
name: video
description: "Plans and makes short video ads and posts: the beat structure, show-don't-tell, the first two seconds, captions, sound and music, and shot briefs for a video model. Use when a creative is a video, Reel, TikTok or Short, or when the owner shares clips to cut. Not for stills."
---

# Video

The picture carries the idea, captions carry the words, sound adds energy.
A generated clip is a three-to-eight-second beat (a product close-up, a
setting, a reveal), never the whole ad.

## Steps

Copy and tick:

- [ ] 1. Pick the length and its beats (below) from the idea and the
      platform's sheet in `specs/`.
- [ ] 2. Write the script into `creative.md`: the hook word for word, the
      middle as beats, the call to action word for word. Mark each beat as
      the owner's footage (`media/clips/`), a still, or a generated shot.
- [ ] 3. For each generated shot, generate the hero still first (your image
      tool), then write a shot brief (below) that uses it as the
      reference or first frame.
- [ ] 4. Put each shot brief under its own heading in `creative.md`
      (`## Shot 1`, `## Shot 2`; `## Prompt` stays the still's) and
      generate: `python3 scripts/videogen.py --prompt-file
      creatives/<folder>/creative.md --section "Shot 1" --ratio 9:16
      --seconds 6 --out creatives/<folder>/shot-1.mp4`. With a Higgsfield
      connection, generate it the way its instructions say instead.
- [ ] 5. Check frames at 0, 25, 50, 75 and 100% (the `tropes` video
      checks). Regenerate what drifts.
- [ ] 6. List the shots, the script and the music choice in the creative;
      the owner or their editor assembles the cut with captions and the
      call to action card.

## Beats

| Length | Beats |
|---|---|
| 6 s | 0 to 2: the striking picture with the product or result in it. 2 to 5: one proof or reaction. 5 to 6: the name and the action, on screen and spoken. One idea. |
| 15 s | 0 to 3: the hook with the proposition. 3 to 6: the promise kept (how it works, a demo). 6 to 12: two or three proof beats, a change every 2 to 3 s. 12 to 15: the call to action card, spoken. |
| 30 s | 0 to 3: hook. 3 to 8: the problem made concrete. 8 to 20: demo or story in three or four beats, a new angle or number near 10 to 12 s. 20 to 26: proof. 26 to 30: offer and action. |

These are a working synthesis of TikTok's and Google's guidance, not a
platform spec.

## Rules

- Frame one is mid-action, never a logo, an establishing shot or a fade.
  The proposition is clear in three seconds, muted.
- Lo-fi and person-led for cold audiences; polish for people who already
  know the business.
- Captions burned in at five to ten words a second, inside the safe zone
  in `specs/`. Generated shots carry no words; they go on in the edit.
- Music is chosen where the ad runs (Ads Manager's library on Meta, the
  Commercial Music Library on TikTok) or licensed for paid social; never a
  trending song. Generated music off; generated ambience and effects are
  fine.
- The owner's own voice first. A synthetic voice or a realistic generated
  person must be disclosed where the platform requires it.

## The shot brief

```
HEADER       duration, aspect ratio, number of shots; the style in one line
REFERENCES   Image 1 = <role>; Image 2 = <role>
SUMMARY      one sentence: subject, place, event, style
SHOTS        Shot 1 [00:00-00:03]: framing, one camera move, the action (body part, speed),
             where in the space, the sound for this shot
CONSTANTS    what stays the same throughout (the product label, the light, the grade)
CONSTRAINTS  no subtitles, no text, no logo, no watermark, no music
```

`references/shot-brief.md` has what each model family changes (some take
timestamps, some only "Shot 1, Shot 2"), the common failures and their
fixes, and a worked brief.
