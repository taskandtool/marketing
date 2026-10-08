"""Shared helpers for the marketing scripts: the app root, the creative
folders, and reading creative.md (frontmatter + body).
Standard library only (PyYAML is not assumed: the frontmatter subset here
is scalars, lists, and one level of nested maps, which is what a
creative.md uses).
"""

import argparse
import base64
import json
import mimetypes
import os
import re
import shlex
import sys

# creative.md `status`, in order; the owner approves through deliverables
STATUSES = ["draft", "sent", "approved", "rejected", "posted"]
KINDS = ["ad", "post"]
PLATFORMS = ["meta", "instagram", "facebook", "linkedin", "tiktok", "youtube", "google", "pinterest", "x", "gbp"]
# creatives/YYYY-MM-DD-<slug>/
FOLDER = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*$")


def root():
    """The app root: the folder this scripts/ folder sits in, wherever the
    script is run from."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def die(msg, code=1):
    print(msg, file=sys.stderr)
    sys.exit(code)


class Parser(argparse.ArgumentParser):
    """argparse whose misuse (an unknown flag, a bad value) exits 2 with a
    Try: line, like every other refusal here."""

    def error(self, message):
        die(f"{self.prog}: {message}\n  Try: python3 scripts/{self.prog} --help", 2)


# ── the generators' shared arguments ────────────────────────────────────

def read_prompt(path, name, example, section="Prompt"):
    """The prompt in `path`: the `## <section>` part of a creative.md (up to
    the next `## ` heading), or the whole of any other file."""
    if not os.path.isfile(path):
        die(f"{name}: no prompt file {path}\n  Try: {example}", 2)
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    if path.endswith(".md"):
        _, body = split_frontmatter(text)
        m = re.search(rf"^## {re.escape(section)}[ \t]*\n(.*?)(?=^## |\Z)", body, re.S | re.M)
        if not m or not m.group(1).strip():
            have = re.findall(r"^## (.+?)[ \t]*$", body, re.M)
            die(f"{name}: {path} has no `## {section}` section with a prompt in it\n"
                f"  Sections there: {', '.join(have) or 'none'}\n"
                f"  Write the prompt under `## {section}` in the creative.md, or pick one with --section.\n"
                f"  Try: {example}", 2)
        return m.group(1).strip()
    if not text.strip():
        die(f"{name}: {path} is empty\n  Try: {example}", 2)
    return text.strip()


def next_free(path):
    """The first name like `path` that does not exist: v1.png → v2.png."""
    stem, ext = os.path.splitext(path)
    m = re.match(r"^(.*?)(\d+)$", stem)
    base, n = (m.group(1), int(m.group(2))) if m else (stem + "-", 1)
    while True:
        n += 1
        cand = f"{base}{n}{ext}"
        if not os.path.exists(cand):
            return cand


def refuse_overwrite(out, force, name):
    """Exit 2 when --out already exists and --force was not given."""
    if os.path.exists(out) and not force:
        die(f"{name}: {out} already exists; nothing was generated and it was left alone\n"
            f"  Try: --out {next_free(out)} (or --force to replace it)", 2)


def creative_folder(out):
    """The creative folder name a file goes into, or None."""
    parent = os.path.basename(os.path.dirname(os.path.abspath(out)))
    return parent if FOLDER.match(parent) else None


# ── the generators' providers ───────────────────────────────────────────

# the key that configures each provider
PROVIDER_ENV = {"openrouter": "OPENROUTER_API_KEY"}


def env(name):
    """`name` from the environment, else from ~/.env: a turn clears the AI
    provider names (OPENROUTER_API_KEY and the like) from the AI's own
    shell, but a key the owner granted stays in ~/.env."""
    if os.environ.get(name):
        return os.environ[name]
    try:
        with open(os.path.expanduser("~/.env"), encoding="utf-8") as fh:
            for line in fh:
                m = re.match(r"^\s*(?:export\s+)?([A-Z_][A-Z0-9_]*)=(.*)$", line)
                if m and m.group(1) == name:
                    return "".join(shlex.split(m.group(2), comments=True)) or None
    except (OSError, ValueError):
        pass
    return None


def configured(order):
    """The providers in `order` that have a key here, in that order."""
    return [p for p in order if env(PROVIDER_ENV[p])]


def provider_failure(name, provider, reason):
    """Exit 1 when a provider refused or failed: nothing was written."""
    die(f"{name}: {provider} refused: {reason}\n  Nothing was written.\n"
        f"  Try: python3 scripts/{name}.py --check, then the same command again later", 1)


def http_failure(name, provider, resp):
    provider_failure(name, provider, f"HTTP {getattr(resp, 'status_code', '?')}: {getattr(resp, 'text', str(resp))[:600]}")


def requests_module(name):
    try:
        import requests
        return requests
    except ImportError:
        die(f"{name}: the Python package requests is not installed\n  Try: bash .taskandtool/setup.sh")


def generate(name, provider, gen, *args):
    """gen(*args), with a network error or an answer of the wrong shape
    turned into provider_failure instead of a traceback."""
    requests = requests_module(name)
    try:
        return gen(*args)
    except (requests.RequestException, ValueError, KeyError, IndexError, TypeError) as e:
        provider_failure(name, provider, f"{type(e).__name__}: {e}"[:600])


def openrouter():
    """(base URL, headers) for OpenRouter."""
    headers = {"Content-Type": "application/json", "HTTP-Referer": "https://taskandtool.app",
               "X-Title": "Task & Tool marketing", "Authorization": "Bearer " + (env("OPENROUTER_API_KEY") or "")}
    return "https://openrouter.ai/api/v1", headers


def b64(path):
    with open(path, "rb") as fh:
        return base64.b64encode(fh.read()).decode()


def data_url(path):
    return f"data:{mimetypes.guess_type(path)[0] or 'image/png'};base64," + b64(path)


# ── frontmatter ─────────────────────────────────────────────────────────

def split_frontmatter(text):
    """(frontmatter_text, body) or ("", text) when there is none."""
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            return text[4:end], text[end + 4:].lstrip("\n")
    return "", text


def _parse_scalar(s):
    s = s.strip()
    if s == "" or s == "null" or s == "~":
        return None
    if s in ("true", "false"):
        return s == "true"
    if s.startswith('"') and s.endswith('"') and len(s) >= 2:
        try:
            return json.loads(s)
        except ValueError:
            return s[1:-1]
    if s.startswith("'") and s.endswith("'") and len(s) >= 2:
        return s[1:-1].replace("''", "'")
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        return [_parse_scalar(x) for x in _split_top(inner)] if inner else []
    if s.startswith("{") and s.endswith("}"):
        inner = s[1:-1].strip()
        out = {}
        for part in _split_top(inner):
            if ":" in part:
                k, v = part.split(":", 1)
                out[k.strip().strip('"')] = _parse_scalar(v)
        return out
    try:
        if re.fullmatch(r"-?\d+", s):
            return int(s)
        if re.fullmatch(r"-?\d+\.\d+", s):
            return float(s)
    except ValueError:
        pass
    return s


def _split_top(s):
    """Split on commas outside quotes, brackets and braces."""
    parts, depth, quote, cur = [], 0, None, ""
    escaped = False
    for ch in s:
        if quote:
            cur += ch
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
            cur += ch
        elif ch in "[{":
            depth += 1
            cur += ch
        elif ch in "]}":
            depth -= 1
            cur += ch
        elif ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur)
    return parts


def parse_frontmatter(text):
    """A small YAML subset: `key: scalar`, `key: [a, b]`, `key: {a: 1}`,
    block lists of scalars or flow maps (`- { ... }`), and one level of
    nested maps (`copy:` followed by indented `key: value` lines).
    Comments after `#` outside quotes are dropped."""
    data = {}
    lines = [_strip_comment(l) for l in text.split("\n")]
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, rest = m.group(1), m.group(2)
        if rest.strip() != "":
            data[key] = _parse_scalar(rest)
            i += 1
            continue
        # block: list or map follows
        block = []
        i += 1
        while i < len(lines) and (lines[i].startswith("  ") or lines[i].startswith("\t") or not lines[i].strip()):
            if lines[i].strip():
                block.append(lines[i])
            i += 1
        if not block:
            data[key] = None
        elif block[0].lstrip().startswith("- "):
            items = []
            for b in block:
                b = b.strip()
                if b.startswith("- "):
                    items.append(_parse_scalar(b[2:]))
            data[key] = items
        else:
            sub = {}
            for b in block:
                mm = re.match(r"^\s+([A-Za-z_][\w-]*):\s*(.*)$", b)
                if mm:
                    sub[mm.group(1)] = _parse_scalar(mm.group(2))
            data[key] = sub
    return data


def _strip_comment(line):
    out, quote, escaped = "", None, False
    for ch in line:
        if quote:
            out += ch
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            out += ch
        elif ch == "#":
            break
        else:
            out += ch
    return out.rstrip()


def read_record(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    fm, body = split_frontmatter(text)
    return parse_frontmatter(fm), body


# ── creatives on disk ───────────────────────────────────────────────────

def creative_dirs(app_root):
    """[(name, dir)] for every folder under creatives/ holding a creative.md,
    newest first (the names start with their date)."""
    base = os.path.join(app_root, "creatives")
    if not os.path.isdir(base):
        return []
    out = []
    for name in sorted(os.listdir(base), reverse=True):
        d = os.path.join(base, name)
        if os.path.isdir(d) and os.path.isfile(os.path.join(d, "creative.md")):
            out.append((name, d))
    return out
