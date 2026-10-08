# Marketing

A Task & Tool **Starter App**: ads, social posts and emails for one
business, made on its own machine from its brand and its market, and filed
for the owner to review.

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
  research/      competitors' ads and posts, customers' words, search questions,
                 conversations worth joining → a brief
  ideas/         angles and frameworks → ranked ideas worth making
  copywriting/   the words and the hook, in the owner's voice; fifteen hook types
  images/        the picture: the owner's photo, or a prompt for an image model
  video/         beats, show don't tell, sound and music, shot briefs for a video model
  ad/            a paid ad to a platform's specs; 45 static formats as recipes
  social-post/   organic posts per platform, one idea across a week
  email/         cold emails and newsletters, saved as drafts the owner sends
  results/       ad, post and search numbers from the owner's accounts; the monthly report
  tropes/        the audit for the tells of AI-made copy, pictures and video, and its
                 copy script (shared, like brand)
.taskandtool/setup.sh  Pillow, requests, tt-crawl and its browsers, and the viewer's web service
AGENTS.md        what the AI reads first; CLAUDE.md imports it
starter-app.json the manifest: the connections it can use and the suggestions an empty chat offers
```

## The app itself

```
brand/  public/          the brand record: look, voice, published facts
claims.md                every fact a creative may state, numbered, each with its source
media/                   the business's own photos and clips; _index.md says what may be used
raw/                     material as it arrived (crawls, downloads, what the owner said)
research/                competitors, hooks seen, customers' words, conversations, the brief
creatives/YYYY-MM-DD-<slug>/   one idea per folder: creative.md and its pictures and clips
emails/YYYY-MM-DD-<slug>/      one email or sequence per folder: email.md
results.md               what ran and what it did, newest first
reports/YYYY-MM.md       the monthly report
specs/<platform>.md      sizes, limits and policy per platform, dated
scripts/                 check · videogen · viewer, and their tests
viewer/                  the viewer's Quartz config, pinned plugins, and its two local plugins
```

`python3 scripts/check.py` checks every creative, the claims and the specs,
and runs the copy through the `tropes` skill's script (Node);
pictures come from the AI's own image tool, and `videogen.py` calls
OpenRouter's video models; a Higgsfield
connection (Seedance, Kling) brings its own instructions.

## The viewer

[Quartz](https://quartz.jzhao.xyz) shows all of it as one website: search
across the research, claims, copy and results, a folder explorer,
backlinks and a graph. Each creative opens as the piece: its title, its
copy, its pictures and its clips, with its kind, platform, angle and hook
beside them. What waits for approval stays on the app's Deliverables tab,
which is live; the viewer shows the files.

- **Dev:** the `web` service runs `npm run dev`, every edit on refresh at
  the app's team address.
- **Production:** `npm run deploy` builds a static site into `dist/` and
  deploys it to Cloudflare through the platform; search works there too,
  in the browser. The first deploy opens it to the team; only a person
  makes it public, and even then `/raw` and search stay the team's.
- **Safe with crawled text:** crawled HTML, scripts and SVGs are never
  built into the site; the `safe-text` plugin shows any HTML in markdown as
  text and strips it from titles and tags; `creative-files` shows only files
  named beside the creative.

The web service installs Quartz on its first start, outside the app
(`~/.local/share/marketing-viewer/`), so setup does not wait for it. It
is pinned to a tag, with its plugins pinned in `viewer/quartz.lock.json`;
the install fixes Quartz 5.0.0 listing a folder twice. It needs Node 22.

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
(OpenAI or OpenRouter), a video model (OpenRouter or Higgsfield), ScrapeCreators for
competitors' ads and posts, Apify for reviews on sites with no API and
for posts in the niche, DataForSEO for search questions, Google Places for
the business's listing, and for results Search Console, Google
Analytics and Meta's insights, and Klaviyo for newsletter drafts. Keys
arrive through the platform's Connections, never through this repository.

## Developing this Starter App

- **Tests, no machine:** `python3 scripts/test_scripts.py`
- **On the platform:** Task & Tool's own repo keeps a working clone under
  `starter_apps/` and runs it through the real install path on a real
  machine before a release is pinned.

A pre-push secret scan guards this repository.

## License

MIT. See `LICENSE`.
