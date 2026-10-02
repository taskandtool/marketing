"""Shared helpers for the marketing scripts: the app root, the creative
folders, and reading creative.md (frontmatter + body).
Standard library only (PyYAML is not assumed: the frontmatter subset here
is scalars, lists, and one level of nested maps, which is what a
creative.md uses).
"""

import json
import os
import re
import sys

# creative.md `status`, in order; the owner approves through deliverables
STATUSES = ["draft", "sent", "approved", "rejected", "posted"]
KINDS = ["ad", "post"]
PLATFORMS = ["meta", "instagram", "facebook", "linkedin", "tiktok", "youtube", "google", "pinterest", "x", "gbp"]
# creatives/YYYY-MM-DD-<slug>/
FOLDER = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*$")


def root():
    """The app root: the folder holding creatives/ and brand/, found upward
    from the working directory (so the scripts run from anywhere inside)."""
    d = os.path.abspath(os.getcwd())
    while True:
        if os.path.isdir(os.path.join(d, "creatives")) and os.path.isdir(os.path.join(d, "brand")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return os.path.abspath(os.getcwd())
        d = parent


def die(msg, code=1):
    print(msg, file=sys.stderr)
    sys.exit(code)


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
