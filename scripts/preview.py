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
MORE = {"facebook": "See more", "instagram": "more", "linkedin": "see more", "tiktok": "more"}
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


ICON = {
    "like": '<path d="M7 11v9H4v-9zm2 9h8.3a2 2 0 0 0 2-1.7l1.1-6A2 2 0 0 0 18.4 10H14V6a2 2 0 0 0-2-2l-3 7"/>',
    "comment": '<path d="M4 5h16v11H9l-5 4z"/>',
    "share": '<path d="M14 5l6 6-6 6M20 11H9a5 5 0 0 0-5 5v2"/>',
    "heart": '<path d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.5-7 10-7 10z"/>',
    "send": '<path d="M21 3L3 10l7 3 3 7z"/>',
    "save": '<path d="M6 3h12v18l-6-5-6 5z"/>',
    "repost": '<path d="M7 7h11l-3-3M17 17H6l3 3"/>',
    "views": '<path d="M5 20V12M10 20V8M15 20v-6M20 20V4"/>',
}


def icon(name):
    return (f'<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICON[name]}</svg>')


def card(platform, kind, name, handle, logo, w, items):
    ad = kind == "ad"
    tag = "Sponsored" if ad else "Just now"
    at = esc(handle or re.sub(r"[^a-z0-9]", "", name.lower()))
    if platform in ("facebook", "meta"):
        return (f'<article class="feed fb"><header>{avatar(logo, name)}<div><b>{esc(name)}</b><small>{tag}</small></div></header>'
                f'{caption(w["text"], "facebook")}{media_block(items)}{ad_bar(w, "fb")}'
                f'<footer>{icon("like")} Like {icon("comment")} Comment {icon("share")} Share</footer></article>')
    if platform == "instagram":
        sub = '<small>Sponsored</small>' if ad else ""
        return (f'<article class="feed ig"><header>{avatar(logo, name)}<div><b>{at}</b>{sub}</div></header>'
                f'{media_block(items, "cover")}{ad_bar(w, "ig")}'
                f'<div class="acts">{icon("heart")}{icon("comment")}{icon("send")}<span></span>{icon("save")}</div>'
                f'{caption(w["text"], "instagram", f"<b>{at}</b> ")}</article>')
    if platform == "x":
        body = w["text"] or w["headline"]
        return (f'<article class="feed x">{avatar(logo, name)}<div class="col"><div class="who"><b>{esc(name)}</b>'
                f'<small>@{at} · {"Ad" if ad else "now"}</small></div>{caption(body, "x")}{media_block(items, "cover")}'
                f'{ad_bar(w, "x")}<footer>{icon("comment")}{icon("repost")}{icon("heart")}{icon("views")}</footer></div></article>')
    if platform == "linkedin":
        return (f'<article class="feed li"><header>{avatar(logo, name)}<div><b>{esc(name)}</b>'
                f'<small>{"Promoted" if ad else "Now"}</small></div></header>{caption(w["text"], "linkedin")}'
                f'{media_block(items)}{ad_bar(w, "li")}'
                f'<footer>{icon("like")} Like {icon("comment")} Comment {icon("repost")} Repost {icon("send")} Send</footer></article>')
    if platform == "tiktok":
        cta = f'<span class="cta">{esc(w["cta"])}</span>' if ad and w["cta"] else ""
        return (f'<article class="feed tt">{media_block(items, "cover")}<div class="side">{avatar(logo, name)}'
                f'{icon("heart")}{icon("comment")}{icon("save")}{icon("share")}</div>'
                f'<div class="over"><b>@{at}</b>{" <small>Sponsored</small>" if ad else ""}'
                f'{caption(w["text"], "tiktok")}{cta}</div></article>')
    label = LABELS.get(platform, platform)
    return (f'<article class="feed plain"><header>{avatar(logo, name)}<div><b>{esc(name)}</b><small>{esc(label)}</small></div></header>'
            f'{caption(w["text"], platform)}{media_block(items)}{ad_bar(w, "fb")}</article>')


CSS = """
*{box-sizing:border-box}body{margin:0;background:#eef0f2;font:15px/1.4 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:#111;padding:16px;display:grid;gap:12px;justify-items:center}
.label{font-size:12px;color:#5b6168;letter-spacing:.02em;max-width:500px;width:100%}
.feed{background:#fff;width:100%;max-width:500px;border-radius:10px;overflow:hidden;box-shadow:0 1px 2px rgba(0,0,0,.12)}
header{display:flex;gap:10px;align-items:center;padding:12px}header div{display:grid}small{color:#65676b;font-size:12.5px}
.av{width:40px;height:40px;border-radius:50%;object-fit:contain;background:#fff;border:1px solid #e4e6eb;flex:none}
.av-letter{display:grid;place-items:center;font-weight:700;color:#fff;background:#6b7280;border:0}
.cap{margin:0;padding:0 12px 12px;white-space:pre-line;overflow-wrap:anywhere}
.more{border:0;background:none;padding:0;font:inherit;font-weight:600;color:#65676b;cursor:pointer}
.media{background:#000;display:flex}.media img,.media video{width:100%;display:block;max-height:640px}
.media.empty{background:#f3f4f6;color:#6b7280;padding:48px 16px;justify-content:center;font-size:13px}
.carousel{overflow-x:auto;scroll-snap-type:x mandatory}.slide{flex:0 0 100%;scroll-snap-align:start;display:flex}
.dots{display:flex;gap:4px;justify-content:center;padding:8px}.dots i{width:6px;height:6px;border-radius:50%;background:#c4c7cc}
.adbar{display:flex;gap:12px;align-items:center;justify-content:space-between;padding:10px 12px;background:#f0f2f5}
.adbar div{display:grid}.desc{color:#65676b;font-size:13px}
.cta{background:#e4e6eb;border-radius:6px;padding:8px 12px;font-weight:600;font-size:14px;white-space:nowrap}
footer{display:flex;gap:6px;align-items:center;justify-content:space-around;padding:8px 12px;border-top:1px solid #e4e6eb;color:#65676b;font-weight:600;font-size:14px}
footer svg{width:18px;height:18px}
.ig header{padding:10px 12px}.ig .av{width:32px;height:32px}.ig .media{background:#fff;aspect-ratio:4/5}.ig .media img{height:100%}
.ig .acts{display:flex;gap:14px;padding:10px 12px 6px}.ig .acts span{flex:1}.ig .cap{padding:0 12px 14px}.ig .more{color:#737373;font-weight:400}
.adbar-ig{background:#fff;border-bottom:1px solid #efefef}.adbar-ig .cta{background:none;color:#0095f6;padding:0}
.x{display:flex;gap:10px;padding:12px;border-radius:0}.x .col{flex:1;min-width:0;display:grid;gap:6px}.x .who{display:flex;gap:6px;align-items:baseline;flex-wrap:wrap}
.x .who small{color:#536471;font-size:15px}.x .cap{padding:0}.x .media{border-radius:16px;overflow:hidden;border:1px solid #cfd9de}
.x footer{border:0;justify-content:space-between;color:#536471;padding:4px 0 0}.adbar-x{border:1px solid #cfd9de;border-radius:12px;background:#fff}
.li header small{display:block}.li .more{color:#666}.li footer{font-size:13px}
.tt{position:relative;background:#000;color:#fff;aspect-ratio:9/16;max-width:360px;border-radius:14px}
.tt .media{position:absolute;inset:0}.tt .media img,.tt .media video{height:100%;max-height:none}
.tt .side{position:absolute;right:8px;bottom:110px;display:grid;gap:16px;justify-items:center}.tt .side svg{width:30px;height:30px}
.tt .over{position:absolute;left:12px;right:64px;bottom:14px;display:grid;gap:4px;text-shadow:0 1px 2px rgba(0,0,0,.6)}
.tt .over small{color:#ddd}.tt .cap{padding:0}.tt .more{color:#fff}.tt .cta{background:#fe2c55;color:#fff;text-align:center;text-shadow:none}
.tt .dots{position:absolute;bottom:4px;left:0;right:0}
"""

JS = """document.querySelectorAll('.more').forEach(b=>b.addEventListener('click',()=>{const p=b.closest('.cap');p.querySelector('.short').hidden=true;p.querySelector('.full').hidden=false}))"""


def page(title, label, article):
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title>'
            f'<style>{CSS}</style></head><body><div class="label">{esc(label)}</div>{article}'
            f'<script>{JS}</script></body></html>\n')


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
    doc = page(title, f"Preview: {label}, not posted", card(platform, kind, name, handles.get("facebook" if platform == "meta" else platform), logo, words(fm), items))
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
