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
import socket
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
def any_case(ext):
    """A glob for an extension in any case: Quartz matches case-sensitively."""
    return "".join(f"[{c.lower()}{c.upper()}]" if c.isalpha() else c for c in ext)


# Never built into the site: data files, crawl caches, and anything a browser
# would run on the viewer's own address (raw/ holds other people's sites).
LEFT_OUT = (["**/_cache/**"]
            + [f"**/*.{any_case(ext)}" for ext in (
                "json", "jsonl", "html", "htm", "shtml", "xhtml", "xht",
                "xml", "xsl", "xslt", "js", "mjs", "cjs")]
            + [f"raw/**/*.{any_case('svg')}"])
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
    try:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=env)
    except FileNotFoundError:
        raise Failed(f"{what} failed: {args[0]} is not installed", [], f"{args[0]} --version")
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
    m = re.search(r"""^name:\s*(?:"([^"]*)"|'([^']*)'|([^#\n]*?))\s*(?:#.*)?$""", front, re.M)
    name = next((g for g in m.groups() if g is not None), "").strip() if m else ""
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
    text = text.replace('"@LEFT_OUT@"', json.dumps(LEFT_OUT))
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
# shipped, what it becomes, a text that must be gone afterwards).
QUARTZ_PATCHES = [
    # 5.0.0 stores a generated folder page's rendered listing as its content,
    # then renders the listing again, so every folder showed its list twice.
    ("quartz/plugins/pageTypes/dispatcher.ts",
     "      ve.tree.children = htmlAst.children\n      ve.vfile.data.htmlAst = htmlAst\n",
     "      ve.vfile.data.htmlAst = htmlAst\n",
     "ve.tree.children = htmlAst.children"),
    # The dev server's watcher skips what Quartz's own .gitignore names, and
    # that names public, private/ and prof: edits to public/ never showed.
    (".gitignore", "\npublic\nprof\n", "\n", "\npublic\n"),
    (".gitignore", "\nprivate/\n", "\n", "\nprivate/\n"),
]


def patch_quartz():
    for name, shipped, fixed, gone in QUARTZ_PATCHES:
        path = os.path.join(QUARTZ_DIR, name)
        with open(path) as f:
            text = f.read()
        if shipped in text:
            text = text.replace(shipped, fixed, 1)
            with open(path, "w") as f:
                f.write(text)
        if gone in text:
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
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("viewer: waiting for the Quartz install already running (the web service's first "
                  "start); minutes on a machine", file=sys.stderr, flush=True)
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
        if os.path.exists(QUARTZ_DIR):
            # Not something this script made: say so rather than delete it.
            raise Failed(f"{QUARTZ_DIR} is there but is not a Quartz clone", [],
                         f"move it aside, then {CMD} install")
        # Cloned beside it and renamed into place, so a clone cut off by a
        # sleep or a replacement never leaves a half Quartz that looks whole.
        partial = QUARTZ_DIR + ".partial"
        shutil.rmtree(partial, ignore_errors=True)
        run(["git", "-c", "advice.detachedHead=false", "clone", "--quiet", "--depth", "1",
             "--branch", QUARTZ_TAG, QUARTZ_REPO, partial], ROOT, f"cloning Quartz {QUARTZ_TAG}")
        os.rename(partial, QUARTZ_DIR)
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

# The home page, in the order an owner looks: the work, how it did, then
# what it was made from. Every row is there from the first start (stage
# makes the folders, and the two ledgers ship with the app), so the dev
# server never shows a stale page; a section fills in as the work arrives.
HOME_ROWS = [
    ("creatives/", "Creatives", "every ad and post, newest first, with its pictures and clips"),
    ("emails/", "Emails", "cold emails, sequences and newsletters"),
    ("results.md", "Results", "what ran and what it did, newest first"),
    ("reports/", "Monthly reports", "each month's numbers and what to make next"),
    ("research/", "Research", "competitors, hooks, what customers say, and the brief"),
    ("claims.md", "Claims", "every fact a piece may state, with its source"),
    ("brand/", "Brand", "positioning, voice and visual identity"),
    ("public/", "The business", "the facts about it"),
    ("media/", "Photos and clips", "the business's own, and what each may be used for"),
    ("specs/", "Platform specs", "sizes, limits and policy per platform"),
    ("raw/", "Raw material", "sites, reviews and transcripts as they arrived"),
]


def home_page():
    """content/index.md: the way in."""
    title = (business_name() + " marketing") if business_name() else DEFAULT_TITLE
    lines = ["---", f"title: {json.dumps(title)}", "---", ""]
    lines += [f"- [{label}]({target}): {desc}" for target, label, desc in HOME_ROWS]
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
    host = production_host()
    if host is None and os.path.isfile(os.path.expanduser("~/tools/taskandtool.py")):
        print("viewer build: production's address did not come back from the platform; "
              "link previews say localhost until the next build", file=sys.stderr, flush=True)
    stage(BUILD_CONTENT, host)
    dist = os.path.join(ROOT, "dist")
    run(["npx", "quartz", "build", "-d", BUILD_CONTENT, "-o", dist], QUARTZ_DIR, "the Quartz build")
    kept, dropped = prune(dist)
    pages = sum(1 for _d, _s, names in os.walk(dist) for n in names if n.endswith(".html"))
    return pages, kept, dropped


def free_port():
    """A port nothing holds. Quartz's dev server also opens a live-reload
    socket (3001 unless told), and dies when that port is taken; through the
    dev address the socket is never reached, so any free port will do."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


# ---------------------------------------------------------------- main

def size_mb(n):
    return f"{n / (1024 * 1024):.0f} MiB"


def main(argv):
    ap = Parser(prog="viewer.py", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True, metavar="{install,dev,build}")
    sub.add_parser("install", help="Quartz and its plugins, outside the app; safe to re-run")
    dv = sub.add_parser("dev", help="serve the viewer, rebuilt on every change (the web service)")
    dv.add_argument("--port", type=int, help="default $PORT, else 3000")
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
            port = args.port or os.environ.get("PORT") or "3000"
            if not str(port).isdigit():
                die(f"viewer dev: PORT is {port!r}, not a number\n  Try: PORT=3000 {CMD} dev", 2)
            if not os.path.isdir(os.path.join(QUARTZ_DIR, ".quartz")):
                print(f"viewer dev: installing Quartz {QUARTZ_TAG} first; minutes on a machine", flush=True)
            install()
            stage(DEV_CONTENT)
            print(f"viewer dev: serving the marketing files on port {port}, rebuilt on every change",
                  flush=True)
            os.chdir(QUARTZ_DIR)
            try:
                os.execvp("npx", ["npx", "quartz", "build", "--serve", "--port", str(port),
                                  "--wsPort", str(free_port()), "-d", DEV_CONTENT])
            except FileNotFoundError:
                raise Failed("npx is not installed", [], "node --version")

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
