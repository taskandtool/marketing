#!/usr/bin/env python3
"""Tests for the marketing scripts: check (with the tropes skill's copy
check), videogen's --check, the frontmatter helpers. Standard
library and node; no machine, no keys, no model calls. The copy rules
themselves are tested in the tropes skill (.claude/skills/tropes/test).

    python3 scripts/test_scripts.py
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from unittest import mock

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(SCRIPTS)
HOME = tempfile.mkdtemp()  # no ~/.env: the keys come only from each test
sys.path.insert(0, SCRIPTS)

import common  # noqa: E402

GOOD = """---
kind: ad
platform: meta
format: us-vs-them
angle: mechanism
hook: us-vs-them
status: draft
claims: [1]
files: [v1.png]
copy:
  headline: "The engineer who fitted it services it"
  primary_text: "Same two engineers since 2004, from Headingley to Horsforth. Book before the first cold week."
  cta: "Book a service"
---

## Idea
We send the engineer who fitted the boiler.
"""


def put(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb" if isinstance(content, bytes) else "w") as fh:
        fh.write(content)


def run(script, *args, cwd, app=APP, home=HOME, **extra):
    """Run app/scripts/<script>; the scripts find their app from their own path."""
    env = {k: v for k, v in os.environ.items() if not k.endswith("_API_KEY")}
    if script != "check.py":  # check reads no keys, and node's version manager needs the real HOME
        env["HOME"] = home
    env.update(extra)
    return subprocess.run([sys.executable, os.path.join(app, "scripts", script), *args], cwd=cwd, env=env,
                          capture_output=True, text=True)


def scratch_app():
    """A temporary app: a copy of scripts/ and the tropes skill it calls."""
    app = tempfile.mkdtemp()
    shutil.copytree(SCRIPTS, os.path.join(app, "scripts"), ignore=shutil.ignore_patterns("__pycache__", "test_*"))
    os.makedirs(os.path.join(app, ".claude", "skills"))
    os.symlink(os.path.join(APP, ".claude", "skills", "tropes"), os.path.join(app, ".claude", "skills", "tropes"))
    return app


class Check(unittest.TestCase):
    def setUp(self):
        self.app = scratch_app()
        for d in ["brand", "public", "creatives", "specs"]:
            os.makedirs(os.path.join(self.app, d))
        for f in ["brand/positioning.md", "brand/voice.md", "brand/visual-identity.md", "public/business.md", "public/proof.md"]:
            put(os.path.join(self.app, f), "# note\n")
        put(os.path.join(self.app, "specs", "meta.md"), f"---\nlast_verified: {date.today()}\n---\n")
        put(os.path.join(self.app, "claims.md"), "# Claims\n\n1. Same two engineers since 2004 (public/proof.md)\n")
        self.folder = os.path.join(self.app, "creatives", "2026-10-01-fitted-it")
        os.makedirs(self.folder)
        put(os.path.join(self.folder, "v1.png"), b"\x89PNG")

    def tearDown(self):
        shutil.rmtree(self.app)

    def write(self, text):
        put(os.path.join(self.folder, "creative.md"), text)

    def test_a_good_creative_passes(self):
        self.write(GOOD)
        r = run("check.py", cwd=self.app, app=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("1 creative", r.stdout)
        self.assertIn("2026-10-01-fitted-it  draft     ad meta", r.stdout)
        self.assertIn("\nNext: the tropes skill's eye pass on 2026-10-01-fitted-it", r.stdout)

    def test_status_lists_only_that_status(self):
        self.write(GOOD.replace("status: draft", "status: sent\ndeliverable: 12"))
        r = run("check.py", "--status", "sent", cwd=self.app, app=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("check: ok, 1 sent creative(s)", r.stdout)
        r = run("check.py", "--status", "approved", cwd=self.app, app=self.app)
        self.assertIn("check: ok, 0 approved creative(s)", r.stdout)
        self.assertNotIn("fitted-it", r.stdout)

    def test_a_stale_sheet_is_a_note_not_a_finding(self):
        put(os.path.join(self.app, "specs", "meta.md"), "---\nlast_verified: 2020-01-01\n---\n")
        self.write(GOOD)
        r = run("check.py", cwd=self.app, app=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("note: specs/meta.md was last verified 2020-01-01", r.stdout)

    def test_missing_claim_file_and_tell_are_findings(self):
        bad = GOOD.replace("claims: [1]", "claims: [1, 7]").replace("files: [v1.png]", "files: [v2.png]")
        bad = bad.replace('"Book a service"', '"Learn more"')
        self.write(bad)
        r = run("check.py", cwd=self.app, app=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("claim 7 is not in claims.md", r.stderr)
        self.assertIn("listed file v2.png is missing", r.stderr)
        self.assertIn('copy.cta: weak-cta "Learn more"', r.stderr)

    def test_copy_tells_and_hints(self):
        bad = GOOD.replace('"The engineer who fitted it services it"', '"It\'s not just a boiler, it\'s peace of mind"')
        bad = bad.replace("Book before the first cold week.", "Book before the first cold week. A trusted local firm.")
        bad = bad.replace("Same two engineers", "Struggling with debt? Same two engineers")
        self.write(bad)
        r = run("check.py", cwd=self.app, app=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("copy.headline: negation-pivot", r.stderr)
        self.assertIn("copy.primary_text: personal-attribute", r.stderr)
        self.assertIn("note: creatives/2026-10-01-fitted-it/creative.md: copy.primary_text: puffery", r.stdout)
        self.write(bad.replace("kind: ad", "kind: post"))
        self.assertNotIn("personal-attribute", run("check.py", cwd=self.app, app=self.app).stderr)

    def test_folder_name_kind_and_hard_limit(self):
        os.rename(self.folder, os.path.join(self.app, "creatives", "fitted-it"))
        self.folder = os.path.join(self.app, "creatives", "fitted-it")
        self.write(GOOD.replace("kind: ad", "kind: static").replace(
            '"The engineer who fitted it services it"', '"The engineer who fitted your boiler is the one who services it, every year"'))
        r = run("check.py", cwd=self.app, app=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("YYYY-MM-DD-<slug>", r.stderr)
        self.assertIn("kind must be one of", r.stderr)
        self.assertIn("over the limit", r.stderr)

    def test_claims_need_a_source_that_exists(self):
        put(os.path.join(self.app, "claims.md"), "1. No source here\n2. Wrong one (public/nope.md)\n")
        self.write(GOOD)
        r = run("check.py", cwd=self.app, app=self.app)
        self.assertIn("claims.md #1: no source", r.stderr)
        self.assertIn("claims.md #2: source public/nope.md does not exist", r.stderr)

    def test_sent_needs_files_and_posted_needs_a_url(self):
        self.write(GOOD.replace("status: draft", "status: posted"))
        r = run("check.py", cwd=self.app, app=self.app)
        self.assertIn("posted creative has the post's `url`", r.stderr)

    def test_hashtags_are_one_line(self):
        self.write(GOOD.replace("kind: ad", "kind: post").replace('  cta: "Book a service"', '  cta: "Book a service"\n  hashtags: [leeds, boilers]'))
        r = run("check.py", cwd=self.app, app=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn('copy.hashtags is one line as it will be pasted, "#one #two"', r.stderr)

    def test_sent_names_its_deliverable(self):
        self.write(GOOD.replace("status: draft", "status: sent"))
        r = run("check.py", cwd=self.app, app=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("a sent creative names its `deliverable`", r.stderr)
        self.assertIn("scripts/preview.py 2026-10-01-fitted-it --send", r.stderr)

    def test_the_app_is_found_from_the_script_not_the_cwd(self):
        self.write(GOOD)
        shutil.rmtree(os.path.join(self.app, "brand"))
        for cwd in (os.path.join(self.app, "scripts"), tempfile.gettempdir()):
            r = run("check.py", cwd=cwd, app=self.app)
            self.assertEqual(r.returncode, 1, cwd)
            self.assertIn("brand/voice.md is missing", r.stderr)
            self.assertIn("3 finding(s) in 1 creative", r.stderr)

    def test_summary_before_notes_and_capped_findings_keep_the_filter(self):
        self.write(GOOD.replace("Book before the first cold week.", "Book before the first cold week. A trusted local firm."))
        r = run("check.py", cwd=self.app, app=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertLess(r.stdout.index("check: ok"), r.stdout.index("note: "))
        bad = GOOD.replace("status: draft", "status: sent\ndeliverable: 12").replace("claims: [1]", "claims: [" + ", ".join(str(n) for n in range(10, 35)) + "]")
        self.write(bad)
        r = run("check.py", "--status", "sent", cwd=self.app, app=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("claim 29 is not in claims.md", r.stderr)
        self.assertNotIn("claim 30 is not", r.stderr)
        self.assertIn("5 more finding(s): python3 scripts/check.py --status sent --all", r.stderr)
        r = run("check.py", "--status", "sent", "--all", cwd=self.app, app=self.app)
        self.assertIn("claim 34 is not in claims.md", r.stderr)

    def test_the_shipped_claims_file_has_no_claim(self):
        shutil.copy(os.path.join(APP, "claims.md"), os.path.join(self.app, "claims.md"))
        r = run("check.py", cwd=self.app, app=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Next: the ideas skill", r.stdout)

    def test_a_tiktok_post_is_not_held_to_the_ad_caption(self):
        post = GOOD.replace("kind: ad", "kind: post").replace("platform: meta", "platform: tiktok").replace(
            '  headline: "The engineer who fitted it services it"\n', "").replace("primary_text", "caption").replace(
            "Book before", "Your boiler gets the same face at your door each year, and your call is answered by name. Book before")
        self.write(post)
        r = run("check.py", cwd=self.app, app=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.write(post.replace("kind: post", "kind: ad"))
        self.assertIn("over the limit (TikTok ad caption", run("check.py", cwd=self.app, app=self.app).stderr)

    def test_missing_brand_notes_are_named(self):
        os.remove(os.path.join(self.app, "brand", "voice.md"))
        r = run("check.py", cwd=self.app, app=self.app)
        self.assertIn("brand/voice.md is missing", r.stderr)


class Generators(unittest.TestCase):
    def test_no_key_fails_and_names_the_connection(self):
        r = run("videogen.py", "--check", cwd=APP)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("Try: python3 ~/tools/taskandtool.py request-connection openrouter-api --why", r.stderr)

    def test_help_and_misuse(self):
        for script in ("check.py", "videogen.py", "preview.py"):
            for flag in ("--help", "-h"):
                r = run(script, flag, cwd=APP)
                self.assertEqual(r.returncode, 0, script + flag)
                self.assertTrue(r.stdout.strip(), script + flag)
            r = run(script, "--nope", cwd=APP)
            self.assertEqual(r.returncode, 2, script)
            self.assertEqual(r.stdout, "", script)
            self.assertIn(f"Try: python3 scripts/{script} --help", r.stderr)
        r = run("videogen.py", "--out", "x.mp4", cwd=APP)
        self.assertEqual(r.returncode, 2)
        self.assertIn("Try:", r.stderr)
        r = run("videogen.py", "--prompt", "a", "--prompt-file", "b", "--out", "x.mp4", cwd=APP)
        self.assertEqual(r.returncode, 2)
        self.assertIn("Try:", r.stderr)

    def test_a_network_error_is_a_provider_failure(self):
        code = ("import sys; sys.path.insert(0, %r); import common, requests\n"
                "def gen(): raise requests.ConnectionError('no route to host')\n"
                "common.generate('videogen', 'openrouter', gen)") % SCRIPTS
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertIn("videogen: openrouter refused: ConnectionError: no route to host", r.stderr)
        self.assertIn("Nothing was written.", r.stderr)

    def test_provider_failure_says_nothing_was_written(self):
        code = ("import sys; sys.path.insert(0, %r); import common\n"
                "class R: status_code = 402; text = 'insufficient credit'\n"
                "common.http_failure('videogen', 'openrouter', R())") % SCRIPTS
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        lines = r.stderr.splitlines()
        self.assertEqual(lines[0], "videogen: openrouter refused: HTTP 402: insufficient credit")
        self.assertEqual(lines[1].strip(), "Nothing was written.")
        self.assertTrue(lines[2].strip().startswith("Try: python3 scripts/videogen.py --check"))

    def test_videogen_sends_the_named_shot(self):
        d = tempfile.mkdtemp()
        try:
            md = os.path.join(d, "creative.md")
            put(md, GOOD + "\n## Prompt\nThe hero still.\n\n## Shot 1\nA kettle boils.\n\n## Shot 2\nSteam rises.\n")
            self.assertEqual(common.read_prompt(md, "t", "x"), "The hero still.")
            self.assertEqual(common.read_prompt(md, "t", "x", "Shot 2"), "Steam rises.")
            r = run("videogen.py", "--prompt-file", md, "--section", "Shot 3", "--out", os.path.join(d, "s.mp4"), cwd=d)
            self.assertEqual(r.returncode, 2)
            self.assertIn("no `## Shot 3` section", r.stderr)
            self.assertIn("Sections there: Idea, Prompt, Shot 1, Shot 2", r.stderr)
            # past the prompt, it stops at the missing key (exit 1), not at the section
            r = run("videogen.py", "--prompt-file", md, "--out", os.path.join(d, "s.mp4"), cwd=d)
            self.assertEqual(r.returncode, 1, r.stderr)
            self.assertIn("no video model configured", r.stderr)
        finally:
            shutil.rmtree(d)

    def test_prompt_section_and_existing_out(self):
        d = tempfile.mkdtemp()
        try:
            put(os.path.join(d, "creative.md"), GOOD + "\n## Prompt\nA boiler at dawn.\n\n## Notes\nv1\n")
            self.assertEqual(common.read_prompt(os.path.join(d, "creative.md"), "t", "x"), "A boiler at dawn.")
            put(os.path.join(d, "bare.md"), GOOD)
            r = run("videogen.py", "--prompt-file", os.path.join(d, "bare.md"), "--out", os.path.join(d, "s.mp4"), cwd=d)
            self.assertEqual(r.returncode, 2)
            self.assertIn("no `## Shot 1` section", r.stderr)
            put(os.path.join(d, "shot-1.mp4"), b"\x00")
            r = run("videogen.py", "--prompt", "a", "--out", os.path.join(d, "shot-1.mp4"), cwd=d)
            self.assertEqual(r.returncode, 2, r.stderr)
            self.assertIn("already exists", r.stderr)
            self.assertIn("shot-2.mp4", r.stderr)
        finally:
            shutil.rmtree(d)


class Frontmatter(unittest.TestCase):
    def test_round_trip(self):
        fm, body = common.split_frontmatter(GOOD)
        data = common.parse_frontmatter(fm)
        self.assertEqual(data["claims"], [1])
        self.assertEqual(data["copy"]["cta"], "Book a service")
        self.assertIn("## Idea", body)

    def test_block_text_keeps_lines_and_hashtags(self):
        data = common.parse_frontmatter(
            "status: draft\ncopy:\n  caption: |-\n    Line one #local\n\n    Line two: still text\n"
            "  hashtags: []\nnote: >-\n  folded\n  here\nfiles: [v1.png]")
        self.assertEqual(data["copy"]["caption"], "Line one #local\n\nLine two: still text")
        self.assertEqual(data["copy"]["hashtags"], [])
        self.assertEqual(data["note"], "folded here")
        self.assertEqual(data["files"], ["v1.png"])
        self.assertEqual(data["status"], "draft")

    def test_folder_pattern(self):
        self.assertTrue(common.FOLDER.match("2026-10-01-us-vs-them"))
        self.assertFalse(common.FOLDER.match("us-vs-them"))


POST = """---
kind: post
platform: facebook
format: photo-and-short-story
angle: origin
hook: founder-story
status: draft
claims: [1]
files: [v1.png]
copy:
  caption: |-
    Same two engineers since 2004, from Headingley to Horsforth, and the one who fitted your boiler is the one who services it.

    Who fitted yours?
  hashtags: "#leedsheating"
---

## Idea
The engineer who fitted it.
"""

# the bridge, as a turn on a machine finds it: it records what it was asked
FAKE_BRIDGE = """import json, sys, os
items = json.loads(sys.stdin.read())
open(os.path.join(os.path.dirname(__file__), "calls.json"), "a").write(json.dumps({"argv": sys.argv[1:], "items": items}) + "\\n")
if os.environ.get("BRIDGE_FAILS"):
    print(json.dumps({"ok": False, "error": "the store is unreachable", "try": "the same command in a moment"}), file=sys.stderr)
    sys.exit(1)
print(json.dumps({"ok": True, "deliverables": [{"id": 40 + n, "title": i["title"]} for n, i in enumerate(items)]}))
"""


class Preview(unittest.TestCase):
    def setUp(self):
        self.app = scratch_app()
        for f in ["brand/positioning.md", "brand/voice.md", "brand/visual-identity.md", "public/proof.md"]:
            put(os.path.join(self.app, f), "# note\n")
        put(os.path.join(self.app, "public", "business.md"),
            '---\nname: Harlow Heating\nsame_as: ["https://www.instagram.com/harlowheat", "https://x.com/harlow_heat"]\n---\n')
        put(os.path.join(self.app, "brand", "logo", "logo.png"), b"\x89PNGlogo")
        put(os.path.join(self.app, "specs", "meta.md"), f"---\nlast_verified: {date.today()}\n---\n")
        put(os.path.join(self.app, "claims.md"), "# Claims\n\n1. Same two engineers since 2004 (public/proof.md)\n")
        self.home = tempfile.mkdtemp()
        put(os.path.join(self.home, "tools", "taskandtool.py"), FAKE_BRIDGE)
        self.make("2026-10-01-fitted-it", POST)

    def tearDown(self):
        shutil.rmtree(self.app)
        shutil.rmtree(self.home)

    def make(self, name, text):
        d = os.path.join(self.app, "creatives", name)
        put(os.path.join(d, "creative.md"), text)
        put(os.path.join(d, "v1.png"), b"\x89PNGpicture")
        return d

    def preview(self, *args, **env):
        # the check it runs calls node, which a version manager finds through the real HOME
        node = subprocess.run(["node", "-e", "console.log(process.execPath)"], capture_output=True, text=True).stdout.strip()
        path = os.path.dirname(node) + os.pathsep + os.environ["PATH"]
        return run("preview.py", *args, cwd=self.app, app=self.app, home=self.home, PATH=path, **env)

    def page(self, name):
        with open(os.path.join(self.app, "creatives", name, "preview.html")) as fh:
            return fh.read()

    def calls(self):
        path = os.path.join(self.home, "tools", "calls.json")
        if not os.path.exists(path):
            return []
        with open(path) as fh:
            return [json.loads(l) for l in fh]

    def test_a_post_is_drawn_as_the_feed_shows_it(self):
        r = self.preview("creatives/2026-10-01-fitted-it")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("preview: 1 preview written", r.stdout)
        self.assertIn("creatives/2026-10-01-fitted-it/preview.html", r.stdout)
        self.assertIn("Facebook post, 1 picture", r.stdout)
        self.assertIn("Next: open them to look, then python3 scripts/preview.py 2026-10-01-fitted-it --send", r.stdout)
        html = self.page("2026-10-01-fitted-it")
        self.assertIn("Harlow Heating", html)
        self.assertIn("data:image/png;base64,", html)  # the picture and logo travel inside the page
        self.assertIn(">See more</button>", html)       # cut where Facebook cuts it
        self.assertIn("Who fitted yours?", html)        # the rest is behind it, not lost
        self.assertNotIn("|-", html)
        self.assertIn("#leedsheating", html)              # the hashtags, as they will be pasted
        again = self.preview("2026-10-01-fitted-it")
        self.assertIn("unchanged", again.stdout)

    def test_each_platform_has_its_layout_and_others_are_a_plain_card(self):
        for platform, mark in [("instagram", "harlowheat"), ("x", "@harlow_heat"), ("linkedin", 'class="li"'),
                               ("tiktok", 'class="tt"'), ("gbp", "Google Business Profile")]:
            self.make(f"2026-10-02-{platform}", POST.replace("platform: facebook", f"platform: {platform}"))
            r = self.preview(f"2026-10-02-{platform}")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn(mark, self.page(f"2026-10-02-{platform}"), platform)
        self.assertIn("a plain card", r.stdout)

    def test_an_ad_shows_its_headline_and_call_to_action(self):
        self.make("2026-10-03-ad", GOOD.replace("platform: meta", "platform: facebook"))
        self.preview("2026-10-03-ad")
        html = self.page("2026-10-03-ad")
        self.assertIn("Sponsored", html)
        self.assertIn("The engineer who fitted it services it", html)
        self.assertIn('class="cta">Book a service', html)

    def test_send_shows_one_group_and_records_each_deliverable(self):
        self.make("2026-10-02-x", POST.replace("platform: facebook", "platform: x"))
        r = self.preview("2026-10-01-fitted-it", "2026-10-02-x", "--send", "Two posts for Friday")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("preview: 2 shown in this chat as deliverables, marked sent", r.stdout)
        self.assertIn("deliverable:40", r.stdout)
        (call,) = self.calls()
        self.assertEqual(call["argv"][:2], ["create-deliverables", "--file"])
        self.assertIn("Two posts for Friday", call["argv"])
        self.assertEqual([os.path.basename(os.path.dirname(i["path"])) for i in call["items"]],
                         ["2026-10-01-fitted-it", "2026-10-02-x"])
        self.assertEqual(call["items"][0]["title"], "Fitted it (Facebook post)")
        fm, _ = common.read_record(os.path.join(self.app, "creatives", "2026-10-02-x", "creative.md"))
        self.assertEqual((fm["status"], fm["deliverable"]), ("sent", 41))
        self.assertEqual(fm["copy"]["caption"].splitlines()[-1], "Who fitted yours?")  # the rest untouched
        self.assertEqual(run("check.py", cwd=self.app, app=self.app).returncode, 0)

        again = self.preview("2026-10-01-fitted-it", "--send", "Again")
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertIn("nothing new to show", again.stdout)
        self.assertIn("already shown as deliverable:40 (sent), left alone (--again shows a revision)", again.stdout)
        self.assertEqual(len(self.calls()), 1)
        revision = self.preview("2026-10-01-fitted-it", "--send", "v2", "--again")
        self.assertIn("deliverable:40", revision.stdout)
        self.assertEqual(len(self.calls()), 2)

    def test_send_refuses_what_fails_the_check_and_a_refused_upload(self):
        self.make("2026-10-04-bad", POST.replace("claims: [1]", "claims: [9]"))
        r = self.preview("2026-10-04-bad", "--send", "One post")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout, "")
        self.assertIn("nothing was sent", r.stderr)
        self.assertIn("claim 9 is not in claims.md", r.stderr)
        self.assertEqual(self.calls(), [])

        r = self.preview("2026-10-01-fitted-it", "--send", "One post", BRIDGE_FAILS="1")
        self.assertEqual(r.returncode, 1)
        self.assertIn("the deliverables were not created: the store is unreachable", r.stderr)
        self.assertIn("Nothing was marked sent", r.stderr)
        self.assertIn("Try:", r.stderr)
        fm, _ = common.read_record(os.path.join(self.app, "creatives", "2026-10-01-fitted-it", "creative.md"))
        self.assertEqual(fm["status"], "draft")

    def test_a_page_too_large_for_a_deliverable_is_refused(self):
        r = self.preview("2026-10-01-fitted-it", PREVIEW_MAX_BYTES="1000")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout, "")
        self.assertIn("a deliverable holds at most", r.stderr)
        self.assertIn("Try: list fewer files, or a shorter clip", r.stderr)

    def test_misuse(self):
        for args in (["2026-09-09-nope"], ["2026-10-01-fitted-it", "--again"], ["2026-10-01-fitted-it", "--send", " "], []):
            r = self.preview(*args)
            self.assertEqual(r.returncode, 2, args)
            self.assertEqual(r.stdout, "", args)
            self.assertIn("Try:", r.stderr, args)
        self.assertIn("Folders: 2026-10-01-fitted-it", self.preview("2026-09-09-nope").stderr)


import viewer  # noqa: E402


class Viewer(unittest.TestCase):
    """The viewer's own logic, against a scratch app and a fake Quartz; no
    Quartz install and no network."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.app = os.path.join(self.tmp, "app")
        shutil.copytree(os.path.join(APP, "viewer"), os.path.join(self.app, "viewer"))
        self.quartz = os.path.join(self.tmp, "quartz", "quartz-v5.0.0")
        os.makedirs(os.path.join(self.quartz, "quartz", "plugins", "pageTypes"))
        self.saved = (viewer.ROOT, viewer.VIEWER, viewer.QUARTZ_DIR)
        viewer.ROOT, viewer.VIEWER, viewer.QUARTZ_DIR = self.app, os.path.join(self.app, "viewer"), self.quartz

    def tearDown(self):
        viewer.ROOT, viewer.VIEWER, viewer.QUARTZ_DIR = self.saved
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_home_page_lists_every_section_from_the_start_and_takes_the_business_name(self):
        fresh = viewer.home_page()
        self.assertIn("title: \"Marketing\"", fresh)
        for target, label, _ in viewer.HOME_ROWS:
            self.assertIn(f"- [{label}]({target})", fresh)
        self.assertIn("Deliverables tab", fresh)
        put(os.path.join(self.app, "public", "business.md"), "---\nname: \"Joe's #1 Heating\"\n---\n")
        self.assertIn('title: "Joe\'s #1 Heating marketing"', viewer.home_page())

    def test_stage_links_the_folders_and_files_and_never_copies(self):
        put(os.path.join(self.app, "claims.md"), "# Claims\n")
        content = os.path.join(self.tmp, "content")
        viewer.stage(content)
        for name in viewer.FOLDERS:
            self.assertTrue(os.path.islink(os.path.join(content, name)), name)
            self.assertTrue(os.path.isdir(os.path.join(self.app, name)), name)
        self.assertTrue(os.path.islink(os.path.join(content, "claims.md")))
        self.assertFalse(os.path.exists(os.path.join(content, "results.md")))
        self.assertTrue(os.path.isfile(os.path.join(content, "index.md")))
        viewer.stage(content)  # again: the old links are replaced, not doubled
        self.assertTrue(os.path.islink(os.path.join(content, "claims.md")))

    def test_config_fills_the_local_plugins_and_the_title(self):
        text = viewer.config_text()
        self.assertIn('"**/*.[hH][tT][mM][lL]"', text)
        self.assertNotIn("@LEFT_OUT@", text)
        self.assertNotIn("@SAFE_TEXT@", text)
        self.assertNotIn("@CREATIVE_FILES@", text)
        self.assertNotIn("@SWATCHES@", text)
        self.assertIn(os.path.join(self.app, "viewer", "creative-files"), text)
        self.assertIn("pageTitle: Marketing", text)
        put(os.path.join(self.app, "public", "business.md"), "---\nname: Acme\n---\n")
        self.assertIn('pageTitle: "Acme marketing"', viewer.config_text())
        self.assertIn("baseUrl: localhost", viewer.config_text())
        self.assertIn("baseUrl: acme-marketing.taskandtool.app",
                      viewer.config_text("acme-marketing.taskandtool.app"))
        lock = json.loads(viewer.lock_text())

        self.assertEqual(lock["plugins"]["creative-files"]["commit"], "local")
        self.assertEqual(lock["plugins"]["safe-text"]["commit"], "local")
        self.assertEqual(lock["plugins"]["swatches"]["commit"], "local")

    def test_the_quartz_patches_apply_once_and_refuse_other_code(self):
        dispatcher = os.path.join(self.quartz, "quartz/plugins/pageTypes/dispatcher.ts")
        ignore = os.path.join(self.quartz, ".gitignore")
        shipped, listing = viewer.QUARTZ_PATCHES[0][1], viewer.QUARTZ_PATCHES[1][1]
        put(dispatcher, "before\n" + shipped + "between\n" + listing + "after\n")
        put(ignore, ".DS_Store\nnode_modules\npublic\nprof\ntsconfig.tsbuildinfo\n.quartz-cache\nprivate/\n.replit\n")
        viewer.patch_quartz()
        viewer.patch_quartz()
        with open(dispatcher) as f:
            self.assertEqual(f.read(), "before\n" + viewer.QUARTZ_PATCHES[0][2] + "between\n"
                             + viewer.QUARTZ_PATCHES[1][2] + "after\n")
        with open(ignore) as f:
            lines = f.read().split("\n")
        for gone in ("public", "prof", "private/"):
            self.assertNotIn(gone, lines)
        self.assertIn("node_modules", lines)
        # A Quartz whose dispatcher changed but kept the line we keep: refused.
        put(dispatcher, "      ve.tree.children = htmlAst.children\n      other\n      ve.vfile.data.htmlAst = htmlAst\n")
        with self.assertRaises(viewer.Failed):
            viewer.patch_quartz()

    def test_left_out_matches_any_letter_case(self):
        import fnmatch
        def left_out(path):
            return any(fnmatch.fnmatchcase(path, pat.replace("**/", "*")) for pat in viewer.LEFT_OUT)
        for path in ("raw/site/a/page.HTML", "raw/site/a/b.Htm", "raw/x/logo.SVG", "media/a.shtml",
                     "raw/a.xht", "raw/a.XSL", "raw/a.js", "raw/_cache/x.md", "raw/a.MHT", "raw/x/a.svgz"):
            self.assertTrue(left_out(path), path)
        for path in ("creatives/2026-10-01-a/v1.png", "brand/logo.svg", "raw/site/a/pages/home.md"):
            self.assertFalse(left_out(path), path)

    def test_a_plugin_link_to_another_folder_is_cleared(self):
        plugins = os.path.join(self.quartz, ".quartz", "plugins")
        os.makedirs(plugins)
        os.symlink(os.path.join(self.app, "viewer", "safe-text"), os.path.join(plugins, "safe-text"))
        self.assertFalse(viewer.clear_stale_plugin_links())
        os.symlink(os.path.join(self.tmp, "gone", "creative-files"), os.path.join(plugins, "creative-files"))
        self.assertTrue(viewer.clear_stale_plugin_links())
        self.assertFalse(os.path.lexists(os.path.join(plugins, "creative-files")))
        self.assertTrue(os.path.islink(os.path.join(plugins, "safe-text")))

    def test_serve_restarts_after_a_crash(self):
        marker = os.path.join(self.tmp, "runs")
        # Crashes on its first run, then exits clean: the loop starts it twice.
        script = (f"import os,sys; p={marker!r}; n=os.path.exists(p); open(p,'a').write('x'); "
                  "sys.exit(0 if n else 1)")
        os.makedirs(self.quartz, exist_ok=True)
        self.assertEqual(viewer.serve(lambda: [sys.executable, "-c", script], pause=lambda _s: None), 0)
        with open(marker) as f:
            self.assertEqual(f.read(), "xx")

    def test_serve_gives_up_on_a_crash_loop(self):
        os.makedirs(self.quartz, exist_ok=True)
        with self.assertRaises(viewer.Failed) as e:
            viewer.serve(lambda: [sys.executable, "-c", "raise SystemExit(1)"],
                         clock=lambda: 100.0, pause=lambda _s: None)
        self.assertIn("5 times in a minute", str(e.exception))

    def test_a_missing_or_misplaced_plugin_is_caught(self):
        plugins = os.path.join(self.quartz, ".quartz", "plugins")
        with open(os.path.join(self.app, "viewer", "quartz.lock.json")) as f:
            names = list(json.load(f)["plugins"])
        for name in names:
            put(os.path.join(plugins, name, "package.json"), "{}")
        self.assertEqual(viewer.plugins_missing(), list(viewer.LOCAL_PLUGINS))   # not linked yet
        for name in viewer.LOCAL_PLUGINS:
            os.symlink(os.path.join(self.app, "viewer", name), os.path.join(plugins, name))
        self.assertEqual(viewer.plugins_missing(), [])
        os.unlink(os.path.join(plugins, names[0], "package.json"))
        self.assertEqual(viewer.plugins_missing(), [names[0]])

    def test_a_build_without_its_plugins_fails_and_ships_nothing(self):
        def quartz_build(args, cwd, what):
            put(os.path.join(self.app, "dist", "index.html"), "<p>built</p>")
            return "Parsing input files\nFailed to load plugin safe-text: Cannot find module\n"
        with mock.patch.object(viewer, "install", lambda: False), \
                mock.patch.object(viewer, "stage", lambda content, base_url=None: None), \
                mock.patch.object(viewer, "production_host", lambda: None), \
                mock.patch.object(viewer, "run", quartz_build):
            with self.assertRaises(viewer.Failed) as e:
                viewer.build()
        self.assertIn("without all its plugins", str(e.exception))
        self.assertFalse(os.path.exists(os.path.join(self.app, "dist")))

    def test_creative_files_plugin(self):
        script = r"""
        import * as m from "./index.js"
        const out = {}
        out.title = m.titleFromFolder("us-vs-them-roof-leak")
        out.refused = ["../x.png", "a/b.png", "javascript:x", "", 3].map(m.fileNode)
        out.image = m.fileNode("v1.png").children[0].url
        out.video = m.fileNode("shot-1.mp4").data
        out.cta = m.label("cta")
        const nodes = m.pieceNodes({ copy: { headline: "Hi", cta: "Book" }, files: ["v1.png"] })
        out.headings = nodes.filter((n) => n.type === "heading").map((n) => n.children[0].value)
        // a post is one card, as the feed shows it: caption, then its picture; no separate Files
        const post = m.pieceNodes({ kind: "post", platform: "facebook", files: ["v1.png"],
                                    copy: { caption: "Line one\n\nWho fitted yours?", hashtags: "#local" } })
        out.postHeadings = post.filter((n) => n.type === "heading").map((n) => n.children[0].value)
        const card = post[1]
        out.card = [card.data.hName, card.children[0].children[0].value, card.children[1].children[0].url]
        out.ad = m.cardNodes({ kind: "ad", platform: "meta", files: [], copy: { primary_text: "P", headline: "H", cta: "Book" } })[0].children[0].value
        out.email = m.cardNodes({ kind: "newsletter", files: ["a.png"] })
        // the transform: a creative becomes its folder's page, titled by the folder
        const plugin = m.default().markdownPlugins({ allSlugs: [] })[0]()
        const tree = { type: "root", children: [] }
        const file = { data: { relativePath: "creatives/2026-10-01-us-vs-them/creative.md",
                               slug: "creatives/2026-10-01-us-vs-them/creative",
                               frontmatter: { title: "creative", files: ["v1.png"] } } }
        plugin(tree, file)
        out.inserted = tree.children.map((n) => n.type === "heading" ? n.children[0].value : n.data?.hName ?? n.type)
        out.slug = file.data.slug
        out.pageTitle = file.data.frontmatter.title
        const media = { data: { relativePath: "media/_index.md", frontmatter: { title: "_index" } } }
        plugin({ type: "root", children: [] }, media)
        out.mediaTitle = media.data.frontmatter.title
        console.log(JSON.stringify(out))
        """
        r = subprocess.run(["node", "--input-type=module", "-e", script], capture_output=True, text=True,
                           cwd=os.path.join(APP, "viewer", "creative-files"))
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        self.assertEqual(out["title"], "Us vs them roof leak")
        self.assertEqual(out["refused"], [None] * 5)
        self.assertEqual(out["image"], "v1.png")
        self.assertEqual(out["video"]["hName"], "video")
        self.assertEqual(out["cta"], "Call to action")
        self.assertEqual(out["headings"], ["Copy", "File"])
        self.assertEqual(out["postHeadings"], ["On Facebook", "Copy"])
        self.assertEqual(out["card"], ["div", "Line one\n\nWho fitted yours?\n\n#local", "v1.png"])
        self.assertEqual(out["ad"], "On Facebook, as an ad")
        self.assertEqual(out["email"], [])
        self.assertEqual(out["inserted"], ["File", "paragraph"])
        self.assertEqual(out["slug"], "creatives/2026-10-01-us-vs-them/index")
        self.assertEqual(out["pageTitle"], "Us vs them")
        self.assertEqual(out["mediaTitle"], "Media")

    def test_swatches_plugin(self):
        script = r"""
        import { swatch } from "./index.js"
        const code = (value) => ({ type: "inlineCode", value })
        const tree = { type: "root", children: [code("#4e3223"), code("#4e322"), code("#fff; x:url(y)"), code("npm run dev")] }
        swatch(tree)
        console.log(JSON.stringify(tree.children.map((n) => n.data?.hProperties?.style ?? null)))
        """
        r = subprocess.run(["node", "--input-type=module", "-e", script], capture_output=True, text=True,
                           cwd=os.path.join(APP, "viewer", "swatches"))
        self.assertEqual(r.returncode, 0, r.stderr)
        styles = json.loads(r.stdout)
        self.assertTrue(styles[0].startswith("border-left: 1.2em solid #4e3223;"))
        self.assertEqual(styles[1:], [None, None, None])


class Words(unittest.TestCase):
    def test_no_tells_of_ai_written_text(self):
        """Every line of the scripts, the skills and AGENTS.md, through the tropes skill's scan."""
        r = subprocess.run(["node", ".claude/skills/tropes/tropes.mjs", "--scan", "scripts", "specs", ".claude", "AGENTS.md"],
                           cwd=APP, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=1)
