#!/usr/bin/env python3
"""The marketing app as a website: Quartz over the brand, research, claims,
creatives, emails, results and reports, with search, backlinks and a graph,
each creative showing its pictures and clips. Standard library only; runs
from any directory.

    python3 scripts/viewer.py install          # Quartz and its plugins, once
    python3 scripts/viewer.py dev [--port N]   # serve it, rebuilt on every change
    python3 scripts/viewer.py build            # the static site in dist/

`install` puts Quartz outside the app (QUARTZ_DIR, default
~/.local/share/marketing-viewer/quartz-<tag>) and prints "already installed"
when it is. `dev` is the web service's command: it installs if needed, then
serves on $PORT (3000). `build` writes dist/ and leaves out any file
Cloudflare will not take.

The viewer's look is viewer/quartz.config.yaml (colours, fonts, panels);
its plugins are pinned in viewer/quartz.lock.json. Approvals are not here:
they are the Deliverables tab's, live.
"""
import fcntl
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from urllib.parse import urlparse

from common import Parser, die, root

ROOT = root()
CMD = "python3 scripts/viewer.py"
VIEWER = os.path.join(ROOT, "viewer")
QUARTZ_TAG = "v5.0.0"
QUARTZ_REPO = "https://github.com/jackyzha0/quartz.git"
QUARTZ_DIR = os.environ.get("QUARTZ_DIR") or os.path.expanduser(
    f"~/.local/share/marketing-viewer/quartz-{QUARTZ_TAG}")
# Quartz's content folders sit beside its clone, not in it: the build skips
# whatever the nearest git repository ignores, and Quartz's own .gitignore
# lists public/. One for the dev server, one for builds, so a deploy never
# rearranges what the running dev server watches.
DEV_CONTENT = os.path.join(os.path.dirname(QUARTZ_DIR), "content")
BUILD_CONTENT = os.path.join(os.path.dirname(QUARTZ_DIR), "content-build")
# What the site shows: these folders and files, linked in, never copied.
FOLDERS = ("creatives", "emails", "reports", "research", "brand", "public", "media", "specs", "raw")
FILES = ("claims.md", "results.md")
# The local plugins, beside the config: shown as text / a creative's files.
LOCAL_PLUGINS = ("safe-text", "creative-files")
DEFAULT_TITLE = "Marketing"
MAX_ASSET = 25 * 1024 * 1024      # Cloudflare's limit on one static file
MAX_FILES = 20_000                # and on the files in one deploy


class Failed(Exception):
    """A step that did not work: the message, its detail lines, the Try: line."""

    def __init__(self, msg, lines=(), try_cmd=None):
        super().__init__(msg)
        self.lines, self.try_cmd = list(lines), try_cmd


# ---------------------------------------------------------------- install

def node_major():
    try:
        out = subprocess.run(["node", "-p", "process.versions.node"], capture_output=True, text=True)
        return int(out.stdout.split(".")[0])
    except (OSError, ValueError):
        return None


def run(args, cwd, what):
    """Run a command quietly; on failure raise with the end of its output.
    Quartz and its plugins depend on two packages fetched from GitHub at
    pinned commits, which npm 12 refuses unless allowed."""
    env = {**os.environ, "npm_config_allow_git": "all"}
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=env)
    if r.returncode != 0:
        tail = (r.stdout + r.stderr).strip().splitlines()[-12:]
        raise Failed(f"{what} failed", tail, f"{CMD} install")
    return r.stdout


def lock_text():
    """Our pinned plugins plus the local ones, as Quartz's lock."""
    with open(os.path.join(VIEWER, "quartz.lock.json")) as f:
        lock = json.load(f)
    for name in LOCAL_PLUGINS:
        path = os.path.join(VIEWER, name)
        lock["plugins"][name] = {"source": path, "resolved": path, "commit": "local"}
    return json.dumps(lock, indent=2) + "\n"


def business_name():
    """public/business.md's `name:`, once it is filled in."""
    try:
        with open(os.path.join(ROOT, "public", "business.md")) as f:
            text = f.read()
    except OSError:
        return None
    front = text.split("---", 2)[1] if text.startswith("---") else ""
    m = re.search(r"^name:\s*(.+?)\s*(?:#.*)?$", front, re.M)
    name = m.group(1).strip("'\"") if m else ""
    return name if name and name != "to fill" else None


def production_host():
    """Production's host name from the bridge, or None off the platform or
    before there is one: link previews need it as an absolute address."""
    bridge = os.path.expanduser("~/tools/taskandtool.py")
    if not os.path.isfile(bridge):
        return None
    try:
        r = subprocess.run([sys.executable, bridge, "status", "--json"],
                           capture_output=True, text=True, timeout=30)
        url = json.loads(r.stdout or "{}").get("production_url") or ""
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None
    return urlparse(url).hostname or None


def config_text(base_url=None):
    """viewer/quartz.config.yaml with the local plugins' paths filled in,
    "<business> marketing" as the title while the title is the default, and
    `base_url` (production's host, for a build) as the address link previews
    name."""
    with open(os.path.join(VIEWER, "quartz.config.yaml")) as f:
        text = f.read()
    if base_url:
        text = re.sub(r"^(\s*baseUrl:).*$", lambda m: f"{m.group(1)} {base_url}", text, count=1, flags=re.M)
    for name in LOCAL_PLUGINS:
        text = text.replace(f"@{name.upper().replace('-', '_')}@", os.path.join(VIEWER, name))
    name = business_name()
    if name:
        text = re.sub(rf"^(\s*pageTitle:)\s*{DEFAULT_TITLE}\s*$",
                      lambda m: f"{m.group(1)} {json.dumps(name + ' marketing')}", text, flags=re.M)
    return text


def write_if_changed(path, text):
    try:
        with open(path) as f:
            if f.read() == text:
                return
    except OSError:
        pass
    with open(path, "w") as f:
        f.write(text)


# Fixes to the pinned Quartz, applied at every install: (file, the text as
# shipped, what it becomes). Quartz 5.0.0 stores a generated folder page's
# rendered listing as its content, then renders the listing again, so every
# folder showed its list twice.
QUARTZ_PATCHES = [
    ("quartz/plugins/pageTypes/dispatcher.ts",
     "      ve.tree.children = htmlAst.children\n      ve.vfile.data.htmlAst = htmlAst\n",
     "      ve.vfile.data.htmlAst = htmlAst\n"),
]


def patch_quartz():
    for name, shipped, fixed in QUARTZ_PATCHES:
        path = os.path.join(QUARTZ_DIR, name)
        with open(path) as f:
            text = f.read()
        if shipped in text:
            with open(path, "w") as f:
                f.write(text.replace(shipped, fixed, 1))
        elif fixed not in text:
            raise Failed(f"Quartz {QUARTZ_TAG} is not the code the viewer patches: {name}", [],
                         f"rm -rf {QUARTZ_DIR} && {CMD} install")


def clear_stale_plugin_links():
    """A local plugin is a link to this app's viewer/, so an edit to it needs
    no reinstall; one left by another app's folder (a removed checkout)
    points nowhere, and Quartz stops on it. Removes those; True if any."""
    cleared = False
    for name in LOCAL_PLUGINS:
        link = os.path.join(QUARTZ_DIR, ".quartz", "plugins", name)
        if os.path.islink(link) and os.path.realpath(link) != os.path.realpath(os.path.join(VIEWER, name)):
            os.unlink(link)
            cleared = True
    return cleared


def install():
    """Quartz at QUARTZ_TAG, its npm packages and the pinned plugins.
    Returns True when something was installed, False when all was there.
    One install at a time: the web service installs on its first start, and
    a build run meanwhile waits for it rather than writing the same folder."""
    os.makedirs(os.path.dirname(QUARTZ_DIR), exist_ok=True)
    with open(QUARTZ_DIR + ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        return _install()


def _install():
    major = node_major()
    if major is None or major < 22:
        found = f"Node {major}" if major else "no Node"
        raise Failed(f"Quartz needs Node 22 or newer; found {found}", [],
                     "nvm install 22 && nvm alias default 22")
    did = False
    if not os.path.isdir(os.path.join(QUARTZ_DIR, ".git")):
        os.makedirs(os.path.dirname(QUARTZ_DIR), exist_ok=True)
        shutil.rmtree(QUARTZ_DIR, ignore_errors=True)
        run(["git", "-c", "advice.detachedHead=false", "clone", "--quiet", "--depth", "1",
             "--branch", QUARTZ_TAG, QUARTZ_REPO, QUARTZ_DIR], ROOT, f"cloning Quartz {QUARTZ_TAG}")
        did = True
    # Written only after `npm ci` succeeds, so a half-finished install is redone.
    packages = os.path.join(QUARTZ_DIR, "node_modules", ".marketing-viewer-installed")
    if not os.path.exists(packages):
        run(["npm", "ci", "--no-audit", "--no-fund", "--loglevel=error"], QUARTZ_DIR,
            "installing Quartz's packages")
        open(packages, "w").close()
        did = True
    patch_quartz()
    lock = lock_text()
    write_if_changed(os.path.join(QUARTZ_DIR, "quartz.lock.json"), lock)
    write_if_changed(os.path.join(QUARTZ_DIR, "quartz.config.yaml"), config_text())
    stamp = os.path.join(QUARTZ_DIR, ".quartz", "marketing-viewer.stamp")
    want = hashlib.sha256(lock.encode()).hexdigest()
    try:
        with open(stamp) as f:
            have = f.read().strip()
    except OSError:
        have = None
    if clear_stale_plugin_links():
        have = None
    if have != want:
        run(["npx", "quartz", "plugin", "install"], QUARTZ_DIR, "installing Quartz's plugins")
        os.makedirs(os.path.dirname(stamp), exist_ok=True)
        with open(stamp, "w") as f:
            f.write(want + "\n")
        did = True
    return did


def plugin_count():
    with open(os.path.join(VIEWER, "quartz.lock.json")) as f:
        return len(json.load(f)["plugins"]) + len(LOCAL_PLUGINS)


# ---------------------------------------------------------------- staging

def has_notes(path):
    """A note, or a folder with a note somewhere under it."""
    if path.endswith(".md"):
        return os.path.isfile(path)
    return any(n.endswith(".md") for _d, _s, names in os.walk(path) for n in names)


# The home page, in the order an owner looks: the work, how it did, then
# what it was made from.
HOME_ROWS = [
    ("creatives", "Creatives", "every ad and post, newest first, with its pictures and clips"),
    ("emails", "Emails", "cold emails, sequences and newsletters"),
    ("results.md", "Results", "what ran and what it did, newest first"),
    ("reports", "Monthly reports", "each month's numbers and what to make next"),
    ("research/brief.md", "The brief", "what to test next, ranked"),
    ("research", "Research", "competitors, hooks and what customers say"),
    ("claims.md", "Claims", "every fact a piece may state, with its source"),
    ("brand", "Brand", "positioning, voice and visual identity"),
    ("public", "The business", "the facts about it"),
    ("media/_index.md", "Photos and clips", "the business's own, and what each may be used for"),
    ("specs", "Platform specs", "sizes, limits and policy per platform"),
    ("raw", "Raw material", "sites, reviews and transcripts as they arrived"),
]


def home_page():
    """content/index.md: the way in, linking what exists."""
    title = (business_name() + " marketing") if business_name() else DEFAULT_TITLE
    lines = ["---", f"title: {json.dumps(title)}", "---", ""]
    found = [(p, t, d) for p, t, d in HOME_ROWS if has_notes(os.path.join(ROOT, p))]
    if not found:
        lines.append("Nothing is here yet. Ask the AI in the chat to learn your brand from your website.")
    else:
        for path, label, desc in found:
            target = path if path.endswith(".md") else path + "/"
            lines.append(f"- [{label}]({target}): {desc}")
        lines += ["", "What is waiting for your approval is on the app's Deliverables tab."]
    return "\n".join(lines) + "\n"


def stage(content, base_url=None):
    """`content` as links to the app's folders and files, plus the home page.
    Each folder is made if missing, so one that fills later is watched."""
    os.makedirs(content, exist_ok=True)
    for name in os.listdir(content):
        path = os.path.join(content, name)
        if os.path.islink(path) or not os.path.isdir(path):
            os.unlink(path)
        else:
            shutil.rmtree(path)
    for folder in FOLDERS:
        source = os.path.join(ROOT, folder)
        os.makedirs(source, exist_ok=True)
        os.symlink(source, os.path.join(content, folder))
    for file in FILES:
        source = os.path.join(ROOT, file)
        if os.path.isfile(source):
            os.symlink(source, os.path.join(content, file))
    with open(os.path.join(content, "index.md"), "w") as f:
        f.write(home_page())
    write_if_changed(os.path.join(QUARTZ_DIR, "quartz.config.yaml"), config_text(base_url))


# ---------------------------------------------------------------- build

def prune(dist):
    """Remove what Cloudflare will not take; returns (files kept, dropped)."""
    kept, dropped = 0, []
    for dirpath, _dirs, names in os.walk(dist):
        for name in names:
            path = os.path.join(dirpath, name)
            size = os.path.getsize(path)
            if size > MAX_ASSET:
                os.unlink(path)
                dropped.append((os.path.relpath(path, dist), size))
            else:
                kept += 1
    return kept, sorted(dropped)


def build():
    install()
    # A build is for production: its link previews name production's address.
    stage(BUILD_CONTENT, production_host())
    dist = os.path.join(ROOT, "dist")
    run(["npx", "quartz", "build", "-d", BUILD_CONTENT, "-o", dist], QUARTZ_DIR, "the Quartz build")
    kept, dropped = prune(dist)
    pages = sum(1 for _d, _s, names in os.walk(dist) for n in names if n.endswith(".html"))
    return pages, kept, dropped


# ---------------------------------------------------------------- main

def size_mb(n):
    return f"{n / (1024 * 1024):.0f} MiB"


def main(argv):
    ap = Parser(prog="viewer.py", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True, metavar="{install,dev,build}")
    sub.add_parser("install", help="Quartz and its plugins, outside the app; safe to re-run")
    dv = sub.add_parser("dev", help="serve the viewer, rebuilt on every change (the web service)")
    dv.add_argument("--port", type=int, default=int(os.environ.get("PORT") or 3000))
    sub.add_parser("build", help="the static site in dist/, ready to deploy")
    args = ap.parse_args(argv)

    try:
        if args.cmd == "install":
            did = install()
            where = QUARTZ_DIR.replace(os.path.expanduser("~"), "~", 1)
            if did:
                print(f"viewer install: Quartz {QUARTZ_TAG} and its {plugin_count()} plugins in {where}")
            else:
                print(f"viewer install: Quartz {QUARTZ_TAG} already installed in {where}, left alone")
            print(f"\nNext: {CMD} build")
            return 0

        if args.cmd == "dev":
            if not os.path.isdir(os.path.join(QUARTZ_DIR, ".quartz")):
                print(f"viewer dev: installing Quartz {QUARTZ_TAG} first; minutes on a machine", flush=True)
            install()
            stage(DEV_CONTENT)
            print(f"viewer dev: serving the marketing files on port {args.port}, rebuilt on every change",
                  flush=True)
            os.chdir(QUARTZ_DIR)
            os.execvp("npx", ["npx", "quartz", "build", "--serve", "--port", str(args.port),
                              "-d", DEV_CONTENT])

        pages, kept, dropped = build()
        lines = [f"viewer build: {pages} pages and {kept - pages} other files in dist/"]
        for path, size in dropped:
            lines.append(f"  left out, over Cloudflare's 25 MiB a file: {path} ({size_mb(size)})")
        if kept > MAX_FILES:
            lines.append(f"  {kept} files: Cloudflare may refuse a deploy of more than {MAX_FILES:,}")
        lines.append("\nNext: npm run deploy publishes dist/ to production")
        print("\n".join(lines))
        return 0
    except Failed as e:
        die("\n".join([f"viewer {args.cmd}: {e}", *("  " + x for x in e.lines),
                       *([f"  Try: {e.try_cmd}"] if e.try_cmd else [])]))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
