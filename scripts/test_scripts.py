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
        self.write(GOOD.replace("status: draft", "status: sent"))
        r = run("check.py", "--status", "sent", cwd=self.app, app=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("check: ok, 1 sent creative(s)", r.stdout)
        r = run("check.py", "--status", "approved", cwd=self.app, app=self.app)
        self.assertIn("check: ok, 0 approved creative(s)", r.stdout)
        self.assertNotIn("fitted-it", r.stdout)

    def test_a_stale_sheet_stops_a_draft_on_its_platform(self):
        put(os.path.join(self.app, "specs", "meta.md"), "---\nlast_verified: 2020-01-01\n---\n")
        self.write(GOOD)
        r = run("check.py", cwd=self.app, app=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("specs/meta.md was last verified 2020-01-01", r.stderr)
        self.write(GOOD.replace("status: draft", "status: approved"))
        self.assertEqual(run("check.py", cwd=self.app, app=self.app).returncode, 0)

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
        bad = GOOD.replace("status: draft", "status: sent").replace("claims: [1]", "claims: [" + ", ".join(str(n) for n in range(10, 35)) + "]")
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

    def test_a_granted_key_in_dot_env_counts(self):
        home = tempfile.mkdtemp()
        try:
            put(os.path.join(home, ".env"), "export ORG_ID='o1'\nOPENROUTER_API_KEY='sk-or-from-env'\nPLAIN=v1 # a comment\n")
            r = run("videogen.py", "--check", cwd=APP, home=home)
            self.assertEqual(r.returncode, 0, r.stderr)
            sys.path.insert(0, SCRIPTS)
            old = os.environ.pop("OPENROUTER_API_KEY", None), os.environ.get("HOME")
            os.environ["HOME"] = home
            try:
                self.assertEqual(common.env("OPENROUTER_API_KEY"), "sk-or-from-env")
                self.assertIsNone(common.env("OPENAI_API_KEY"))
                self.assertEqual(common.env("PLAIN"), "v1")
            finally:
                os.environ["HOME"] = old[1]
                if old[0] is not None:
                    os.environ["OPENROUTER_API_KEY"] = old[0]
        finally:
            shutil.rmtree(home)

    def test_help_and_misuse(self):
        for script in ("check.py", "videogen.py"):
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

    def test_folder_pattern(self):
        self.assertTrue(common.FOLDER.match("2026-10-01-us-vs-them"))
        self.assertFalse(common.FOLDER.match("us-vs-them"))


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

    def test_home_page_links_only_what_exists_and_takes_the_business_name(self):
        self.assertIn("Nothing is here yet", viewer.home_page())
        put(os.path.join(self.app, "creatives", "2026-10-01-a", "creative.md"), GOOD)
        put(os.path.join(self.app, "claims.md"), "# Claims\n")
        put(os.path.join(self.app, "public", "business.md"), "---\nname: Brightwater Heating\n---\n")
        page = viewer.home_page()
        self.assertIn('title: "Brightwater Heating marketing"', page)
        self.assertIn("- [Creatives](creatives/)", page)
        self.assertIn("- [Claims](claims.md)", page)
        self.assertNotIn("Emails", page)
        self.assertIn("Deliverables tab", page)

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
        self.assertNotIn("@SAFE_TEXT@", text)
        self.assertNotIn("@CREATIVE_FILES@", text)
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

    def test_the_quartz_patch_applies_once_and_refuses_other_code(self):
        name, shipped, fixed = viewer.QUARTZ_PATCHES[0]
        path = os.path.join(self.quartz, name)
        put(path, "before\n" + shipped + "after\n")
        viewer.patch_quartz()
        viewer.patch_quartz()
        with open(path) as f:
            self.assertEqual(f.read(), "before\n" + fixed + "after\n")
        put(path, "some other Quartz\n")
        with self.assertRaises(viewer.Failed):
            viewer.patch_quartz()

    def test_a_plugin_link_to_another_folder_is_cleared(self):
        plugins = os.path.join(self.quartz, ".quartz", "plugins")
        os.makedirs(plugins)
        os.symlink(os.path.join(self.app, "viewer", "safe-text"), os.path.join(plugins, "safe-text"))
        self.assertFalse(viewer.clear_stale_plugin_links())
        os.symlink(os.path.join(self.tmp, "gone", "creative-files"), os.path.join(plugins, "creative-files"))
        self.assertTrue(viewer.clear_stale_plugin_links())
        self.assertFalse(os.path.lexists(os.path.join(plugins, "creative-files")))
        self.assertTrue(os.path.islink(os.path.join(plugins, "safe-text")))

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
        // the transform: a creative becomes its folder's page, titled by the folder
        const plugin = m.default().markdownPlugins({ allSlugs: [] })[0]()
        const tree = { type: "root", children: [] }
        const file = { data: { relativePath: "creatives/2026-10-01-us-vs-them/creative.md",
                               slug: "creatives/2026-10-01-us-vs-them/creative",
                               frontmatter: { title: "creative", files: ["v1.png"] } } }
        plugin(tree, file)
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
        self.assertEqual(out["slug"], "creatives/2026-10-01-us-vs-them/index")
        self.assertEqual(out["pageTitle"], "Us vs them")
        self.assertEqual(out["mediaTitle"], "Media")


if __name__ == "__main__":
    unittest.main(verbosity=1)
