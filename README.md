# Marketing

**Ads, social posts and emails for one business, written by your AI agent in
chat.** The agent learns your brand, studies your market and files each
piece for you to approve.

[![Deploy on Task & Tool](https://taskandtool.com/images/deploy-button.svg)](https://taskandtool.com/accounts/register?starter_app=marketing)

![Bellwork Boxing's Instagram slideshow, its TikTok and its First class $0 ad](https://taskandtool.com/images/starter-apps/marketing.webp)

It's made to run on Task & Tool. There, each app has its own computer for
your AI agent. The agent uses the skills and scripts in this repo to
research competitors, write ads, posts and emails, make their pictures and
check every fact before you see it. The work is plain text files. You can
browse all of it as a website built with Quartz.

## Get started

Click the button above, or pick Marketing when you create an app on [Task &
Tool](https://taskandtool.com/starter-apps/marketing). Then ask the agent to
learn your brand from your website. If you have no site, tell it about the
business in the chat.

See it in use on the [Marketing
page](https://taskandtool.com/starter-apps/marketing).

## Features

### Start from your site, your photos or a chat

The agent reads your website and your Google listing. It writes notes on
your voice, colors, audience, services, prices and reviews. The agent files
the photos you send in the chat. Every fact a piece may state is a numbered
line in `claims.md` with its source. When a fact is missing, the agent asks
you for it.

### Research on your competitors' ads and reviews

You and the agent agree on three to five competitors. With a ScrapeCreators
connection, it reads their posts and the ads they run in the Meta, Google
and LinkedIn ad libraries. With Apify it also reads Google Maps reviews,
Reddit and forum threads, and the TikTok Creative Center's top ads for your
industry. With DataForSEO it finds what people search for and how many
search each month.

Meta lists the start date of each active ad. The agent notes which ones a
competitor has kept running past 30 or 90 days. It writes a one-page brief:
the angles competitors repeat, your customers' own phrases and objections,
and five to eight ideas. The agent ranks the ideas by their evidence and how
easy they are to make. It also finds ten threads where people ask about what
you sell. It drafts replies in your voice. You post the replies.

### Ads sized to each platform's specs

A test set is three ideas in three formats each: nine ads. The agent picks
from 45 static ad formats and 15 kinds of hook. It sizes the pictures to the
specs for Meta, TikTok, LinkedIn, Google, Pinterest and YouTube. For a video
ad, the agent writes a script and shot briefs for the clips it generates.

<p>
  <img src="https://taskandtool.com/images/marketing/bellwork-boxing-ad-free.webp" width="240" alt="Bellwork Boxing's Facebook ad: First class $0">
  <img src="https://taskandtool.com/images/marketing/bellwork-boxing-ad-review.webp" width="240" alt="Bellwork Boxing's review ad: 4.9 from 380 Google reviews">
</p>

### A week of posts from one idea

The agent writes posts for Instagram, Facebook, LinkedIn, TikTok, Google
Business Profile, Pinterest and X. It rewrites the post for each platform.
It makes TikTok slideshows and Instagram and LinkedIn carousels. It starts
from your photos when they fit. Once you approve a post, the agent schedules
it through Zernio or Hootsuite if you've connected one. Otherwise you post
it.

<p>
  <img src="https://taskandtool.com/images/marketing/bellwork-boxing-instagram-renata.webp" width="240" alt="An Instagram post quoting Renata Alvarez's Google review">
  <img src="https://taskandtool.com/images/marketing/bellwork-boxing-tiktok-first-class.webp" width="240" alt="A TikTok on what to wear to your first boxing class">
</p>

### Email drafts in Gmail or Klaviyo

The agent puts newsletters and follow-ups after a signup, booking or quote
into Klaviyo as a campaign or a flow. It puts a note to a few customers in
your Gmail as one draft each. You send them. For a business that sells to
other businesses, the agent can also build a verified list and write a cold
email sequence of two or three emails. They're all under 120 words.

### Pictures and short clips

The agent starts from your own photo when one fits. It uses it as it is or
edits it. Otherwise it makes a picture from scratch in your brand's style.
Clips are 4 to 8 seconds long. The agent makes them from a shot brief
through OpenRouter (Veo by default) or a Higgsfield connection.

### Previews as they will look in the feed

The agent draws each piece as it will look on Facebook, Instagram, X,
LinkedIn or TikTok. It adds your name and logo and cuts the caption where
the platform does. The agent sends it to the chat for your approval. You
approve it or send it back with a note.

### Checks on every piece

Before you see any work, the agent runs `scripts/check.py` and fixes
anything that fails.

| Check | Fails when |
|---|---|
| Facts | A piece cites a claim that isn't a numbered line in `claims.md`, or a claim's source file is missing |
| Copy | Wording that sounds like AI, and copy over the platform's text limits |
| Pieces | A missing field, platform or file in a creative |
| Specs | Platform sheets last checked over 90 days ago |
| Brand | One of the four brand notes the work needs doesn't exist yet |

### Monthly reports on what worked

With a Meta connection, the agent reads your ads' spend, clicks and leads.
It also reads your posts' reach, saves and shares. With Search Console and
Google Analytics, it adds the searches and pages people found you through.
For other platforms, send the agent your export. Ask for a monthly report,
or have the agent schedule one. The report is one page. In it the agent
names the best and worst piece and three things to make next.

### Browse the work as a website

The viewer is a Quartz site of the app's notes. It has search, a folder
explorer, backlinks and a graph. Open an ad or post and you see the piece:
its copy, pictures and clips beside its platform, angle and hook. A brand
color written as a hex code gets a swatch next to it.

### Skills in this repo

The agent loads a skill, a file of instructions, when a task needs one.
There are 14 here:

| Skill | What it does |
|---|---|
| `marketing` | The folders, the shape of a piece and the order of work |
| `brand` | Gathers facts, photos and the brand's look |
| `research` | Competitors' ads and posts, customers' words, threads worth a reply |
| `ad-ideas` | Turns the research into ranked ideas |
| `copywriting` | Hooks and lengths for each platform |
| `writing` | Writes in the owner's voice and edits the draft |
| `ad` | Paid ads to each platform's specs |
| `social-post` | Organic posts, slideshows and a week from one idea |
| `video` | Beats, sound and shot briefs for clips |
| `email` | Newsletters and follow-ups as drafts |
| `cold-email` | Lists, verification, sequences and replies |
| `growth-plan` | Which two or three strategies to run for months |
| `results` | Your numbers and the monthly report |
| `tropes` | Spots copy, pictures and video that look machine-made |

### Prompts and scripts on a schedule

Ask the agent to schedule a job. A job can be a prompt the agent answers in
a fresh chat. It can also be a command the agent runs. For example:

| Job | What it does |
|---|---|
| Monthly report | Prompt: "Record how my ads did and tell me what to make next" |
| This week's posts | Prompt: "Write this week's social posts and show them to me" |

The agent leaves a scheduled job's work as a draft or a paused ad unless
you've told it to post, send or spend.

## Why run it on Task & Tool

Task & Tool is the easiest place to run it. The agent asks you for a
connection when a task needs it. You approve the work in the chat. Each app
gets:

- Its own computer for the agent
- A dev address where your team browses the work
- Publishing on your own domain with a free SSL certificate. Only your team
  sees production until you make it public. If you make it public, anyone
  can see all of it. That includes research and raw material.
- Connections to Meta, Google, Klaviyo, ScrapeCreators, Apify and any
  service with an API. Task & Tool holds their keys.
- Scheduled jobs for the reports and posts above
- Sign-in for your team on the viewer

## Make it your own

Ask the agent for any change in the chat. To start from your own copy, fork
this repo, change what you like, and start a new app from your fork on Task
& Tool. You can also copy its skills from `.claude/skills/` into another
repo.

## What's in the repo

```
brand/  public/   notes on the brand and the business's published facts
claims.md         every fact a piece may state, numbered, with its source
media/            your photos and clips, and which ones may be used
research/         competitors, customers' words, threads and the brief
creatives/        one ad or post per folder: creative.md, pictures, clips
emails/           one email or sequence per folder
results.md        what ran and what it did, newest first
plan.md           the strategies chosen, and why
lists/            the people a strategy reaches
reports/          the monthly reports
specs/            sizes, limits and policy for each platform
raw/              material as it arrived: crawls, downloads, notes
scripts/          the checks, previews, clips, the viewer and their tests
viewer/           the viewer's settings and its three plugins
.claude/skills/   the 14 skills
AGENTS.md         what the agent reads first
.taskandtool/     setup for an install on Task & Tool
starter-app.json  what the app needs and its chat suggestions
```

## Commands

The agent runs these on the app's computer.

- `npm run dev` serves the viewer on port 3000 and shows each edit on
  refresh. It installs Quartz on its first start. To run it on your own
  computer, you need Node 22 or later, Python 3 and
git.
- `npm run build` builds the viewer as a static site in `dist/`.
- `npm run deploy` builds the viewer and publishes it to production. It
  works only on Task & Tool.
- `python3 scripts/check.py` runs the checks above. `python3
  scripts/check.py --status sent` lists what is waiting for your approval.
- `python3 scripts/preview.py <folder>` draws a piece as it will look in the
  feed. `--send` puts it in the chat for approval. That works only on Task &
  Tool.
- `python3 scripts/make_video.py` makes a clip through OpenRouter.
- `python3 scripts/test_scripts.py` runs the tests on the scripts.

## Third-party tools

- [Quartz](https://quartz.jzhao.xyz) v5.0.0 (MIT), the viewer, with its
  plugins pinned in `viewer/quartz.lock.json`.
- [`tt-crawl`](https://github.com/taskandtool/crawler), our crawler, for
  reading sites and Google listings.
- `requests` (Apache-2.0), for the Python scripts.

## Contributing

Pull requests are welcome. The repo holds no credentials. We scan for
secrets before each push.

## License

MIT. See `LICENSE`.
