#!/usr/bin/env python3
"""A post or ad as it will look in the feed, to show the owner:

    python3 scripts/preview.py <folder> [<folder> …]
    python3 scripts/preview.py <folder> [<folder> …] --send "one line for the owner"

Writes creatives/<folder>/preview.html: one page that stands alone (its
pictures and clips inside it), laid out like the platform's feed from the
creative.md's platform, copy and files, with the business's name and logo
from public/business.md and brand/logo/. Facebook, Instagram, X, LinkedIn
and TikTok have layouts of their own; any other platform is a plain card.
The caption is cut where the platform cuts it, with its "more".

--send checks the folders (scripts/check.py), shows every preview in this
chat as one group of deliverables, one per creative, and writes `status:
sent` and `deliverable: <id>` into each creative.md. A creative already
sent is left alone; --again shows a revision as a new deliverable.

Output:

    preview: 1 preview written
      creatives/2026-10-14-donuts/preview.html  Facebook post, 1 picture, 2.1 MB

    Next: python3 scripts/preview.py 2026-10-14-donuts --send "<one line for the owner>"

Exit 0 when done (an unchanged preview included), 1 when a folder fails
its check or the deliverables were refused, 2 on a bad folder or flag.
"""

import argparse
import html
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import Parser, data_url, die, read_record, root, split_frontmatter  # noqa: E402

NAME = "preview.py"
BRIDGE = os.path.expanduser("~/tools/taskandtool.py")
# The deliverable store takes a page up to 20 MB, pictures and clips inside it.
MAX_BYTES = int(os.environ.get("PREVIEW_MAX_BYTES") or 19 * 1024 * 1024)
IMAGE = re.compile(r"\.(png|jpe?g|webp|gif|avif|svg)$", re.I)
VIDEO = re.compile(r"\.(mp4|webm|mov|m4v)$", re.I)

LABELS = {"facebook": "Facebook", "meta": "Facebook", "instagram": "Instagram", "x": "X",
          "linkedin": "LinkedIn", "tiktok": "TikTok", "gbp": "Google Business Profile",
          "pinterest": "Pinterest", "youtube": "YouTube", "google": "Google"}
# Characters shown before "more" (specs/meta.md, specs/linkedin.md, specs/tiktok.md); X shows it all.
CUTOFF = {"facebook": 125, "instagram": 125, "linkedin": 140, "tiktok": 45}
MORE = {"facebook": "See more", "instagram": "more", "linkedin": "more", "tiktok": "more"}
# where a profile's handle is, in public/business.md `same_as`
HANDLE = {"instagram": r"instagram\.com/([\w.]+)", "x": r"(?:x|twitter)\.com/(\w+)",
          "tiktok": r"tiktok\.com/@([\w.]+)", "linkedin": r"linkedin\.com/company/([\w-]+)",
          "facebook": r"facebook\.com/([\w.]+)"}


def example(folder="<folder>"):
    return f"python3 scripts/{NAME} {folder}"


# ── what goes into a preview ────────────────────────────────────────────

def business(app):
    """(name, {platform: handle}, logo data URL or None)."""
    path = os.path.join(app, "public", "business.md")
    fm = read_record(path)[0] if os.path.isfile(path) else {}
    name = fm.get("name") if isinstance(fm.get("name"), str) and fm.get("name") != "to fill" else ""
    links = " ".join(str(u) for u in fm.get("same_as") or [])
    handles = {p: m.group(1) for p, rx in HANDLE.items() if (m := re.search(rx, links))}
    logo = None
    logo_dir = os.path.join(app, "brand", "logo")
    if os.path.isdir(logo_dir):
        found = sorted(f for f in os.listdir(logo_dir) if IMAGE.search(f))
        if found:
            logo = data_url(os.path.join(logo_dir, found[0]))
    return name or "Your business", handles, logo


def words(fm):
    """The text a reader sees, by role: caption (or primary text), headline,
    description, call to action."""
    copy = fm.get("copy") if isinstance(fm.get("copy"), dict) else {}
    text = copy.get("caption") or copy.get("primary_text") or ""
    tags = copy.get("hashtags")
    if isinstance(tags, str) and tags.strip():
        text = (text + "\n\n" + tags.strip()).strip()
    return {"text": str(text), "headline": str(copy.get("headline") or ""),
            "description": str(copy.get("description") or ""), "cta": str(copy.get("cta") or "")}


def media(folder, fm):
    """[(kind, data URL, name)] for the listed pictures and clips."""
    out = []
    for f in fm.get("files") or []:
        f = str(f)
        path = os.path.join(folder, f)
        if not os.path.isfile(path) or not (IMAGE.search(f) or VIDEO.search(f)):
            continue
        out.append(("video" if VIDEO.search(f) else "image", data_url(path), f))
    return out


# ── the page ────────────────────────────────────────────────────────────

def esc(s):
    return html.escape(str(s), quote=True)


def avatar(logo, name):
    if logo:
        return f'<img class="av" src="{logo}" alt="">'
    return f'<span class="av av-letter">{esc(name[:1].upper())}</span>'


def caption(text, platform, lead=""):
    """The caption cut where the platform cuts it, with the rest behind its "more"."""
    cut = CUTOFF.get(platform)
    if not text:
        return ""
    if not cut or len(text) <= cut:
        return f'<p class="cap">{lead}{esc(text)}</p>'
    head = text[:cut]
    if " " in head and not text[cut].isspace():
        head = head.rsplit(" ", 1)[0]  # at a word, as the feeds cut
    head = head.rstrip(" \n.,;:")
    return (f'<p class="cap">{lead}<span class="short">{esc(head)}… <button class="more" type="button">'
            f'{esc(MORE[platform])}</button></span><span class="full" hidden>{esc(text)}</span></p>')


def media_block(items, fit="contain"):
    if not items:
        return '<div class="media empty">No picture or clip listed in files:</div>'
    slides = []
    for kind, url, name in items:
        if kind == "video":
            slides.append(f'<video src="{url}" controls muted playsinline preload="metadata" aria-label="{esc(name)}"></video>')
        else:
            slides.append(f'<img src="{url}" alt="{esc(name)}" style="object-fit:{fit}">')
    if len(slides) == 1:
        return f'<div class="media">{slides[0]}</div>'
    dots = "".join("<i></i>" for _ in slides)
    return (f'<div class="media carousel">{"".join(f"<div class=slide>{s}</div>" for s in slides)}</div>'
            f'<div class="dots" aria-label="{len(slides)} slides">{dots}</div>')


def ad_bar(w, platform):
    if not (w["headline"] or w["cta"]):
        return ""
    cta = f'<span class="cta">{esc(w["cta"])}</span>' if w["cta"] else ""
    desc = f'<span class="desc">{esc(w["description"])}</span>' if w["description"] else ""
    return f'<div class="adbar adbar-{platform}"><div><b>{esc(w["headline"])}</b>{desc}</div>{cta}</div>'


# Line icons in each feed's own manner, drawn here (no platform's artwork).
ICON = {
    "like": '<path d="M7 10v11H3V10zm2 11h8.6a2 2 0 0 0 2-1.6l1.3-7A2 2 0 0 0 18.9 10H14V5.5A2.5 2.5 0 0 0 11.5 3L9 10z"/>',
    "comment": '<path d="M20 12a8 8 0 0 1-11.6 7.1L4 20l1-4.2A8 8 0 1 1 20 12z"/>',
    "share": '<path d="M13 5l8 7-8 7v-4c-5 0-8 1.5-10 5 .5-6 3.5-10 10-11z"/>',
    "send": '<path d="M22 3L2 10.5l8 3 3 8.5z M10 13.5L22 3"/>',
    "reply": '<path d="M21 11.5a8.4 8.4 0 0 1-8.5 8.4H11l-5 3v-3.6A8.4 8.4 0 0 1 12.5 3h0A8.5 8.5 0 0 1 21 11.5z"/>',
    "repost": '<path d="M4 9V7a2 2 0 0 1 2-2h11l-3-3M20 15v2a2 2 0 0 1-2 2H7l3 3"/>',
    "heart": '<path d="M12 20.5s-8-4.8-8-11A4.5 4.5 0 0 1 12 6.7a4.5 4.5 0 0 1 8 2.8c0 6.2-8 11-8 11z"/>',
    "views": '<path d="M4 20V11M9.5 20V4M15 20v-7M20.5 20V8"/>',
    "save": '<path d="M6 3h12v18l-6-5-6 5z"/>',
    "upload": '<path d="M12 3v12M7 8l5-5 5 5M4 15v4a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-4"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18"/>',
    "dots": '<circle cx="5" cy="12" r="1.3"/><circle cx="12" cy="12" r="1.3"/><circle cx="19" cy="12" r="1.3"/>',
    "close": '<path d="M6 6l12 12M18 6L6 18"/>',
    "music": '<path d="M9 18V5l11-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="17" cy="16" r="3"/>',
    "home": '<path d="M3 11l9-8 9 8v10h-6v-6H9v6H3z"/>',
    "people": '<circle cx="9" cy="8" r="4"/><path d="M2 21c0-4 3-6 7-6s7 2 7 6M16 4a4 4 0 0 1 0 8M22 21c0-3-1.5-5-4-5.7"/>',
    "inbox": '<path d="M4 4h16v12H9l-5 4z"/>',
    "person": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.5 3.5-7 8-7s8 2.5 8 7"/>',
}


def icon(name, size=20):
    return (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="currentColor" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICON[name]}</svg>')


def card(platform, kind, name, handle, logo, w, items):
    """The post as `platform`'s feed lays it out: its header, its caption and
    cut, its picture frame and its action row."""
    ad = kind == "ad"
    at = esc(handle or re.sub(r"[^a-z0-9]", "", name.lower()))
    nm = esc(name)
    if platform in ("facebook", "meta"):
        when = "Sponsored" if ad else "Just now"
        return (f'<article class="fb"><header>{avatar(logo, name)}<div class="who"><b>{nm}</b>'
                f'<small>{when} · {icon("globe", 12)}</small></div>'
                f'<span class="tools">{icon("dots")}{icon("close")}</span></header>'
                f'{caption(w["text"], "facebook")}{media_block(items)}{ad_bar(w, "fb")}'
                f'<footer><span>{icon("like")}Like</span><span>{icon("comment")}Comment</span>'
                f'<span>{icon("share")}Share</span></footer></article>')
    if platform == "instagram":
        sub = '<small>Sponsored</small>' if ad else ""
        return (f'<article class="ig"><header><span class="ring">{avatar(logo, name)}</span>'
                f'<div class="who"><b>{at}</b> <small>· now</small>{sub}</div>'
                f'<span class="tools">{icon("dots")}</span></header>'
                f'{media_block(items, "cover")}{ad_bar(w, "ig")}'
                f'<div class="acts">{icon("heart", 24)}{icon("comment", 24)}{icon("send", 24)}<i></i>{icon("save", 24)}</div>'
                f'{caption(w["text"], "instagram", f"<b>{at}</b> ")}'
                f'<div class="add">Add a comment…</div></article>')
    if platform == "x":
        body = w["text"] or w["headline"]
        return (f'<article class="x">{avatar(logo, name)}<div class="col">'
                f'<div class="who"><b>{nm}</b><span>@{at} · {"Ad" if ad else "now"}</span>'
                f'<span class="tools">{icon("dots", 18)}</span></div>'
                f'{caption(body, "x")}{media_block(items, "cover")}{ad_bar(w, "x")}'
                f'<footer>{icon("reply", 18)}{icon("repost", 18)}{icon("heart", 18)}{icon("views", 18)}'
                f'<span class="end">{icon("save", 18)}{icon("upload", 18)}</span></footer></div></article>')
    if platform == "linkedin":
        when = "Promoted" if ad else f"Now · {icon('globe', 12)}"
        return (f'<article class="li"><header>{avatar(logo, name)}<div class="who"><b>{nm}</b>'
                f'<small>Company page</small><small>{when}</small></div>'
                f'<span class="follow">+ Follow</span><span class="tools">{icon("dots")}</span></header>'
                f'{caption(w["text"], "linkedin")}{media_block(items)}{ad_bar(w, "li")}'
                f'<footer><span>{icon("like")}Like</span><span>{icon("comment")}Comment</span>'
                f'<span>{icon("repost")}Repost</span><span>{icon("send")}Send</span></footer></article>')
    if platform == "tiktok":
        cta = f'<span class="cta">{esc(w["cta"])}</span>' if ad and w["cta"] else ""
        return (f'<article class="tt">{media_block(items, "cover")}'
                f'<nav class="tabs"><span>Following</span><b>For You</b></nav>'
                f'<div class="side"><span class="me">{avatar(logo, name)}<i>+</i></span>'
                f'{icon("heart", 34)}{icon("comment", 32)}{icon("save", 30)}{icon("share", 32)}'
                f'<span class="disc"></span></div>'
                f'<div class="over"><b>@{at}</b>{" <small>Sponsored</small>" if ad else ""}'
                f'{caption(w["text"], "tiktok")}<small class="sound">{icon("music", 13)} original sound · {at}</small>{cta}</div>'
                f'<nav class="bar"><span>{icon("home")}Home</span><span>{icon("people")}Friends</span>'
                f'<span class="plus">+</span><span>{icon("inbox")}Inbox</span><span>{icon("person")}Profile</span></nav></article>')
    label = LABELS.get(platform, platform)
    return (f'<article class="plain"><header>{avatar(logo, name)}<div class="who"><b>{nm}</b><small>{esc(label)}</small></div></header>'
            f'{caption(w["text"], platform)}{media_block(items)}{ad_bar(w, "fb")}</article>')


# The page around the post is the feed's own ground: Facebook's grey,
# LinkedIn's warm grey, X's and Instagram's white, TikTok's black.
CSS = """
*{box-sizing:border-box}
body{margin:0;padding:20px 16px;display:grid;gap:12px;justify-items:center;font:15px/1.35 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:#050505;background:#f0f2f5}
.label{font-size:12px;color:#65676b;width:100%;max-width:500px}
svg{flex:none}.tools{margin-left:auto;display:flex;gap:14px;color:#65676b}
.av{width:40px;height:40px;border-radius:50%;object-fit:contain;background:#fff;flex:none}
.av-letter{display:grid;place-items:center;font-weight:700;color:#fff;background:#6b7280}
.who{display:grid;min-width:0}.who small{display:flex;align-items:center;gap:4px}
.cap{margin:0;white-space:pre-line;overflow-wrap:anywhere}
.more{border:0;background:none;padding:0;font:inherit;cursor:pointer}
.media{display:flex;background:#000}.media img,.media video{width:100%;display:block}
.media.empty{background:#f3f4f6;color:#6b7280;padding:48px 16px;justify-content:center;font-size:13px}
.carousel{overflow-x:auto;scroll-snap-type:x mandatory}.slide{flex:0 0 100%;scroll-snap-align:start;display:flex}
.dots{display:flex;gap:4px;justify-content:center;padding:8px}.dots i{width:6px;height:6px;border-radius:50%;background:#c4c7cc}
.adbar{display:flex;gap:12px;align-items:center;justify-content:space-between;padding:10px 16px}.adbar div{display:grid}
.desc{font-size:13px;color:#65676b}.cta{border-radius:6px;padding:8px 14px;font-weight:600;font-size:14px;white-space:nowrap}

/* Facebook */
body.p-fb{font-family:"Segoe UI Historic","Segoe UI",Helvetica,Arial,sans-serif}
.fb{width:100%;max-width:500px;background:#fff;border-radius:8px;box-shadow:0 1px 2px rgba(0,0,0,.2);overflow:hidden}
.fb header{display:flex;gap:8px;align-items:center;padding:12px 16px 0}
.fb .who b{font-size:15px;font-weight:600}.fb .who small{font-size:13px;color:#65676b}
.fb .cap{padding:12px 16px 14px;font-size:15px}.fb .more{font-weight:600;color:#65676b}
.fb .media img{max-height:700px}.fb .adbar{background:#f0f2f5}.fb .cta{background:#e4e6eb}
.fb footer{display:flex;margin:0 16px;padding:4px 0;border-top:1px solid #ced0d4}
.fb footer span{flex:1;display:flex;gap:8px;justify-content:center;align-items:center;padding:8px 0;color:#65676b;font-weight:600;font-size:15px}

/* Instagram */
body.p-ig{background:#fff}.p-ig .label{max-width:470px}
.ig{width:100%;max-width:470px;padding-bottom:16px;border-bottom:1px solid #dbdbdb}
.ig header{display:flex;gap:10px;align-items:center;padding:0 4px 12px}
.ig .ring{padding:2px;border-radius:50%;background:linear-gradient(45deg,#f9ce34,#ee2a7b,#6228d7);display:flex}
.ig .ring .av{width:32px;height:32px;border:2px solid #fff}
.ig .who{display:flex;gap:4px;align-items:baseline;font-size:14px}.ig .who b{font-weight:600}.ig .who small{color:#737373;font-size:14px}
.ig .tools{color:#000}.ig .media{background:#fff;aspect-ratio:4/5;border:1px solid #dbdbdb;border-radius:4px;overflow:hidden}.ig .media img{height:100%}
.ig .acts{display:flex;gap:16px;padding:12px 0 8px;color:#000}.ig .acts i{flex:1}
.ig .cap{font-size:14px;line-height:18px}.ig .cap b{font-weight:600}.ig .more{color:#737373}
.ig .add{margin-top:8px;font-size:14px;color:#737373}
.adbar-ig{padding:12px 0;border-bottom:1px solid #efefef}.adbar-ig .cta{padding:0;color:#0095f6}

/* X */
body.p-x{background:#fff;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:#0f1419}
.p-x .label{max-width:600px}
.x{width:100%;max-width:600px;display:flex;gap:12px;padding:12px 16px;border-top:1px solid #eff3f4;border-bottom:1px solid #eff3f4}
.x .col{flex:1;min-width:0;display:grid;gap:4px}
.x .who{display:flex;gap:4px;align-items:center;font-size:15px;white-space:nowrap}.x .who b{font-weight:700}.x .who span{color:#536471}
.x .tools{color:#536471}.x .cap{font-size:15px;line-height:20px}.x .more{color:#1d9bf0}
.x .media{margin-top:8px;border:1px solid #cfd9de;border-radius:16px;overflow:hidden}.x .media img{max-height:510px}
.adbar-x{margin-top:4px;padding:8px 12px;border:1px solid #cfd9de;border-radius:12px;background:#fff}.adbar-x .cta{padding:0;color:#536471;font-weight:400}
.x footer{display:flex;justify-content:space-between;color:#536471;padding:10px 0 0;max-width:100%}
.x footer .end{display:flex;gap:16px}

/* LinkedIn */
body.p-li{background:#f4f2ee;font-family:-apple-system,system-ui,"Segoe UI",Roboto,"Helvetica Neue",sans-serif;color:rgba(0,0,0,.9)}
.p-li .label{max-width:555px}
.li{width:100%;max-width:555px;background:#fff;border-radius:8px;box-shadow:0 0 0 1px rgba(140,140,140,.2);overflow:hidden}
.li header{display:flex;gap:8px;align-items:flex-start;padding:12px 16px 0}
.li .av{width:48px;height:48px;border-radius:4px;border:1px solid #e8e8e8}
.li .who b{font-size:14px;font-weight:600}.li .who small{font-size:12px;color:rgba(0,0,0,.6);line-height:16px}
.li .follow{margin-left:auto;color:#0a66c2;font-weight:600;font-size:16px;white-space:nowrap}.li .tools{margin-left:12px;color:rgba(0,0,0,.6)}
.li .cap{padding:8px 16px 12px;font-size:14px;line-height:20px}.li .more{color:rgba(0,0,0,.6)}
.li .media{background:#f3f2ef}.li .media img{max-height:700px}
.adbar-li{background:#eef3f8}.adbar-li .cta{border:1px solid #0a66c2;color:#0a66c2;border-radius:16px;padding:4px 14px}
.li footer{display:flex;margin:0 16px;padding:4px 0;border-top:1px solid #e8e8e8}
.li footer span{flex:1;display:flex;gap:6px;justify-content:center;align-items:center;padding:12px 0;color:rgba(0,0,0,.6);font-weight:600;font-size:14px}

/* TikTok */
body.p-tt{background:#121212}.p-tt .label{color:#a8a8a8;max-width:360px}
.tt{position:relative;width:100%;max-width:360px;aspect-ratio:9/16;background:#000;color:#fff;border-radius:18px;overflow:hidden;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
.tt .media{position:absolute;inset:0;background:#000}.tt .media img,.tt .media video{height:100%}
.tt .tabs{position:absolute;top:14px;left:0;right:0;display:flex;gap:18px;justify-content:center;font-size:16px;text-shadow:0 1px 2px rgba(0,0,0,.5)}
.tt .tabs span{color:rgba(255,255,255,.7);font-weight:600}.tt .tabs b{border-bottom:2px solid #fff;padding-bottom:4px}
.tt .side{position:absolute;right:8px;bottom:96px;display:grid;gap:18px;justify-items:center;filter:drop-shadow(0 1px 2px rgba(0,0,0,.5))}
.tt .me{position:relative;display:flex}.tt .me .av{width:46px;height:46px;border:2px solid #fff}
.tt .me i{position:absolute;left:50%;bottom:-8px;transform:translateX(-50%);width:20px;height:20px;border-radius:50%;background:#fe2c55;color:#fff;font:700 15px/20px sans-serif;text-align:center;font-style:normal}
.tt .disc{width:40px;height:40px;border-radius:50%;background:radial-gradient(circle,#555 25%,#222 26%,#222 60%,#444 62%)}
.tt .over{position:absolute;left:12px;right:72px;bottom:72px;display:grid;gap:6px;font-size:15px;text-shadow:0 1px 2px rgba(0,0,0,.6)}
.tt .over small{color:#eee;font-size:13px;display:flex;gap:6px;align-items:center}.tt .cap{font-size:14px}.tt .more{color:#fff;font-weight:600}
.tt .cta{background:#fe2c55;color:#fff;text-align:center;text-shadow:none}
.tt .bar{position:absolute;left:0;right:0;bottom:0;height:56px;background:#000;display:flex;justify-content:space-around;align-items:center;font-size:10px}
.tt .bar span{display:grid;justify-items:center;gap:2px;color:#bbb}.tt .bar span:first-child{color:#fff}
.tt .bar .plus{width:42px;height:28px;border-radius:8px;background:#fff;color:#000;font:700 22px/28px sans-serif;box-shadow:-3px 0 0 #25f4ee,3px 0 0 #fe2c55}
.tt .dots{position:absolute;bottom:60px;left:0;right:0}

/* any other platform */
.plain{width:100%;max-width:500px;background:#fff;border-radius:8px;box-shadow:0 1px 2px rgba(0,0,0,.2);overflow:hidden}
.plain header{display:flex;gap:8px;align-items:center;padding:12px 16px}.plain .who small{color:#65676b;font-size:13px}
.plain .cap{padding:0 16px 12px}.plain .more{font-weight:600;color:#65676b}.plain .adbar{background:#f0f2f5}.plain .cta{background:#e4e6eb}
"""

JS = """document.querySelectorAll('.more').forEach(b=>b.addEventListener('click',()=>{const p=b.closest('.cap');p.querySelector('.short').hidden=true;p.querySelector('.full').hidden=false}))"""

THEME = {"facebook": "fb", "meta": "fb", "instagram": "ig", "x": "x", "linkedin": "li", "tiktok": "tt"}


def page(title, label, article, platform):
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title>'
            f'<style>{CSS}</style></head><body class="p-{THEME.get(platform, "plain")}">'
            f'<div class="label">{esc(label)}</div>{article}<script>{JS}</script></body></html>\n')


def title_of(slug):
    words_ = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", slug).replace("-", " ").strip()
    return words_[:1].upper() + words_[1:]


def build(app, folder, who):
    """(path, html, summary) for one creative folder."""
    fm, _ = read_record(os.path.join(folder, "creative.md"))
    platform = str(fm.get("platform") or "")
    kind = "ad" if fm.get("kind") == "ad" else "post"
    items = media(folder, fm)
    name, handles, logo = who
    label = f'{LABELS.get(platform, platform or "No platform")} {kind}'
    title = f"{title_of(os.path.basename(folder))} ({label})"
    note = "" if platform in ("facebook", "meta", "instagram", "x", "linkedin", "tiktok") else ", a plain card (no layout of its own)"
    pics = sum(1 for k, *_ in items if k == "image")
    clips = len(items) - pics
    parts = [f"{pics} picture{'s' if pics != 1 else ''}"] + ([f"{clips} clip{'s' if clips != 1 else ''}"] if clips else [])
    doc = page(title, f"Preview: {label}, not posted",
               card(platform, kind, name, handles.get("facebook" if platform == "meta" else platform), logo, words(fm), items),
               platform)
    if len(doc) > MAX_BYTES:
        die(f"preview: {os.path.relpath(folder, app)} would be a {len(doc) / 1048576:.1f} MB page; "
            f"a deliverable holds at most {MAX_BYTES // 1048576} MB\n"
            f"  Try: list fewer files, or a shorter clip, in its creative.md, then {example(os.path.basename(folder))}", 1)
    return os.path.join(folder, "preview.html"), doc, title, f"{label}, {', '.join(parts)}, {len(doc) / 1048576:.1f} MB{note}"


# ── sending ─────────────────────────────────────────────────────────────

def set_fields(path, fields):
    """Write `key: value` lines into a creative.md's frontmatter, replacing
    any line for the same key and adding the rest after `status:`."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    fm, _ = split_frontmatter(text)
    head = fm
    for key, value in fields.items():
        line = f"{key}: {value}"
        if re.search(rf"^{key}:.*$", head, re.M):
            head = re.sub(rf"^{key}:[^\n]*", line, head, count=1, flags=re.M)
        elif re.search(r"^status:.*$", head, re.M):
            head = re.sub(r"^(status:[^\n]*)", lambda m: m.group(1) + "\n" + line, head, count=1, flags=re.M)
        else:
            head = head.rstrip("\n") + "\n" + line
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text.replace(fm, head, 1))


def send(app, built, message):
    """Show the previews as one group of deliverables; their ids, in order."""
    if not os.path.isfile(BRIDGE):
        die(f"preview: the platform's bridge is not on this machine ({BRIDGE}); the previews were written, nothing was sent\n"
            f"  Try: open the preview.html files, or run this on the app's machine", 1)
    items = [{"path": path, "title": title} for path, title in built]
    r = subprocess.run([sys.executable, BRIDGE, "create-deliverables", "--file", "-", "--message", message, "--json"],
                       input=json.dumps(items), capture_output=True, text=True, timeout=600)
    try:
        result = json.loads(r.stdout or r.stderr or "{}")
    except ValueError:
        result = {}
    ids = [d.get("id") for d in result.get("deliverables") or []]
    if r.returncode != 0 or not result.get("ok") or len(ids) != len(items):
        reason = result.get("error") or (r.stderr or r.stdout).strip()[:400] or f"exit {r.returncode}"
        die(f"preview: the deliverables were not created: {reason}\n  Nothing was marked sent.\n"
            f"  Try: {result.get('try') or 'the same command again in a moment'}", 1)
    return ids


def main():
    ap = Parser(prog=NAME, description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folders", nargs="+", help="creative folders (creatives/<folder> or just its name)")
    ap.add_argument("--send", metavar="MESSAGE", help="show them in this chat as deliverables, with this line for the owner")
    ap.add_argument("--again", action="store_true", help="with --send: show creatives already sent, as a revision")
    args = ap.parse_args()
    if args.again and args.send is None:
        die(f"{NAME}: --again goes with --send\n  Try: {example()} --send \"<one line for the owner>\" --again", 2)
    if args.send is not None and not args.send.strip():
        die(f"{NAME}: --send needs a line for the owner\n  Try: {example()} --send \"Two posts for Friday\"", 2)
    app = root()
    folders = []
    for f in args.folders:
        name = os.path.basename(f.rstrip("/"))
        d = os.path.join(app, "creatives", name)
        if not os.path.isfile(os.path.join(d, "creative.md")):
            have = sorted(n for n in os.listdir(os.path.join(app, "creatives"))
                          if os.path.isfile(os.path.join(app, "creatives", n, "creative.md"))) \
                if os.path.isdir(os.path.join(app, "creatives")) else []
            die(f"{NAME}: no creative folder {name}\n  Folders: {', '.join(have[:10]) or 'none yet'}\n"
                f"  Try: {example(have[0] if have else '<folder>')}", 2)
        if d not in folders:
            folders.append(d)

    who = business(app)
    lines, built = [], []
    for d in folders:
        path, doc, title, summary = build(app, d, who)
        old = open(path, encoding="utf-8").read() if os.path.isfile(path) else None
        if old != doc:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(doc)
        lines.append([os.path.relpath(path, app), summary + ("" if old != doc else ", unchanged")])
        built.append((d, path, title))

    if args.send is None:
        print(f"preview: {len(built)} preview{'s' if len(built) != 1 else ''} written")
        width = max(len(p) for p, _ in lines)
        for p, s in lines:
            print(f"  {p:<{width}}  {s}")
        names = " ".join(os.path.basename(d) for d, *_ in built)
        print(f"\nNext: open them to look, then python3 scripts/{NAME} {names} --send \"<one line for the owner>\"")
        return

    to_send, left, ids = [], [], []
    for (d, path, title), line in zip(built, lines):
        fm, _ = read_record(os.path.join(d, "creative.md"))
        if fm.get("deliverable") and fm.get("status") in ("sent", "approved", "rejected", "posted") and not args.again:
            left.append(f"  {line[0]}  already shown as deliverable:{fm['deliverable']} ({fm.get('status')}), left alone (--again shows a revision)")
        else:
            to_send.append((d, path, title, line))
    if to_send:
        check = subprocess.run([sys.executable, os.path.join(app, "scripts", "check.py"),
                                *[os.path.basename(d) for d, *_ in to_send]], capture_output=True, text=True)
        if check.returncode != 0:
            die(f"{NAME}: the check found something to fix first; nothing was sent\n"
                + "\n".join("  " + l for l in check.stderr.strip().splitlines()), 1)
        ids = send(app, [(path, title) for _, path, title, _ in to_send], args.send.strip())
        for (d, _, _, _), i in zip(to_send, ids):
            set_fields(os.path.join(d, "creative.md"), {"status": "sent", "deliverable": i})
    print(f"preview: {len(to_send)} shown in this chat as deliverables, marked sent" if to_send
          else "preview: nothing new to show")
    for (d, _, _, line), i in zip(to_send, ids):
        print(f"  {line[0]}  deliverable:{i}, {line[1]}")
    for l in left:
        print(l)
    print("\nNext: say in this chat what approval will do; the owner's answer arrives here "
          "(python3 ~/tools/taskandtool.py get-deliverables)" if to_send
          else f"\nNext: python3 scripts/check.py --status sent lists what waits for the owner")


if __name__ == "__main__":
    main()
