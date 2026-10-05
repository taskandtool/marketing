# Marketing

A Task & Tool **Starter App**: ads and social posts for one business, made
on its own machine from its brand and its market, and approved by the
owner before anything is posted. It makes the work; it never posts it.

The repository *is* the app: what you clone is what runs. Installed with one
click on Task & Tool, or cloned into a project of your own (below). MIT
licensed.

## What is in the box

The app is mostly skills: written instructions the AI loads when the work
calls for them.

```
.claude/skills/
  marketing/     the folders, the shape of a creative.md, the order of work
  brand/         the brand record in brand/ and public/, from any source (shared with the
                 other Starter Apps that carry it)
  research/      competitors' ads and posts, customers' words, search questions → a brief
  ideas/         angles and frameworks → ranked ideas worth making
  hooks/         the opening line, frame or second, and fifteen hook types
  copywriting/   the words, in the owner's voice, claims only from sources
  images/        the picture: the owner's photo, or a prompt for an image model
  video/         beats, show don't tell, sound and music, shot briefs for a video model
  ad/            a paid ad to a platform's specs; 45 static formats as recipes
  social-post/   organic posts per platform, one idea across a week
  tropes/        the audit for the tells of AI-made copy, pictures and video, and its
                 copy script (shared, like brand)
.agents/skills/  thin Codex adapters: the same descriptions, pointing at the bodies above
.taskandtool/setup.sh  Pillow, requests, tt-crawl and its browsers
AGENTS.md        what the AI reads first; CLAUDE.md imports it
starter-app.json the manifest: the connections it can use and the suggestions an empty chat offers
```

## The app itself

```
brand/  public/          the brand record: look, voice, published facts
claims.md                every fact a creative may state, numbered, each with its source
media/                   the business's own photos and clips; _index.md says what may be used
raw/                     material as it arrived (crawls, downloads, what the owner said)
research/                competitors, hooks seen, customers' words, the brief
creatives/YYYY-MM-DD-<slug>/   one idea per folder: creative.md and its pictures and clips
results.md               what ran and what it did, newest first
specs/<platform>.md      sizes, limits and policy per platform, dated
scripts/                 check · imagegen · videogen
```

`python3 scripts/check.py` checks every creative, the claims and the specs,
and runs the copy through the `tropes` skill's script (Node);
`imagegen.py` and `videogen.py` call whichever image or video model the app
has a key for.

## Install

**On Task & Tool.** Pick Marketing when you create an app. The machine
clones this repository into the app and runs `.taskandtool/setup.sh`.

**Anywhere else.**

```
git clone https://github.com/taskandtool/marketing my-marketing
cd my-marketing
bash .taskandtool/setup.sh
```

Off the platform, `create_deliverables` (the bridge that puts a file in
front of the owner in the Task & Tool chat) is not there; the files are on
disk.

## What it connects to

Everything is optional and asked for when it is needed: an image model
(OpenAI, OpenRouter, Gemini, Black Forest Labs, fal), a video model, Apify
or Firecrawl for research, the owner's ad accounts for results. Keys arrive
through the platform's Connections, never through this repository.

## Developing this Starter App

- **Tests, no machine:** `python3 .claude/skills/marketing/test_scripts.py`
- **On the platform:** Task & Tool's own repo keeps a working clone under
  `starter_apps/` and runs it through the real install path on a real
  machine before a release is pinned.

A pre-push secret scan guards this repository.

## License

MIT. See `LICENSE`.
