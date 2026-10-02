#!/usr/bin/env python3
"""Tests for the marketing scripts: check, tropes, imagegen and videogen's
--check, the frontmatter helpers. Standard library only; no machine, no keys.

    python3 .claude/skills/marketing/test_scripts.py
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date

APP = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
SCRIPTS = os.path.join(APP, "scripts")
sys.path.insert(0, SCRIPTS)

import common  # noqa: E402
import tropes  # noqa: E402

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
    with open(path, "wb" if isinstance(content, bytes) else "w") as fh:
        fh.write(content)


def run(script, *args, cwd):
    env = {k: v for k, v in os.environ.items() if not k.endswith("_API_KEY") and k not in ("OPENROUTER_BASE_URL", "FAL_KEY")}
    return subprocess.run([sys.executable, os.path.join(SCRIPTS, script), *args], cwd=cwd, env=env,
                          capture_output=True, text=True)


class Tropes(unittest.TestCase):
    def rules(self, text, ad=True):
        return [r for r, _ in tropes.findings(text, ad=ad)]

    def test_clean_copy_passes(self):
        self.assertEqual(self.rules("Book a survey this week: we measure, quote and fit within ten days."), [])

    def test_negation_pivot(self):
        self.assertTrue(any("negation" in r for r in self.rules("It's not just a roof, it's peace of mind.")))
        self.assertTrue(any("negation" in r for r in self.rules("Our roofers are licensed, not cheap.")))

    def test_phrases_and_em_dash(self):
        rules = self.rules("Say goodbye to leaks — elevate your home.")
        self.assertTrue(any("refused phrase" in r for r in rules))
        self.assertTrue(any("em dash" in r for r in rules))

    def test_rhetorical_question_answered(self):
        self.assertTrue(any("rhetorical" in r for r in self.rules("Tired of leaks? We fix them fast.")))

    def test_one_triad_is_allowed_two_are_not(self):
        self.assertEqual(self.rules("We measure, quote and fit."), [])
        self.assertTrue(any("triad" in r for r in self.rules("Fast. Simple. Effective. Roofs, gutters, and skylights.")))

    def test_personal_attributes_only_in_ads(self):
        self.assertTrue(any("personal attribute" in r for r in self.rules("Struggling with debt?", ad=True)))
        self.assertFalse(any("personal attribute" in r for r in self.rules("Struggling with debt?", ad=False)))


class Check(unittest.TestCase):
    def setUp(self):
        self.app = tempfile.mkdtemp()
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
        r = run("check.py", cwd=self.app)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("1 creative", r.stdout)

    def test_missing_claim_file_and_tell_are_findings(self):
        bad = GOOD.replace("claims: [1]", "claims: [1, 7]").replace("files: [v1.png]", "files: [v2.png]")
        bad = bad.replace('"Book a service"', '"Learn more"')
        self.write(bad)
        r = run("check.py", cwd=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("claim 7 is not in claims.md", r.stderr)
        self.assertIn("listed file v2.png is missing", r.stderr)
        self.assertIn("refused phrase", r.stderr)

    def test_folder_name_kind_and_hard_limit(self):
        os.rename(self.folder, os.path.join(self.app, "creatives", "fitted-it"))
        self.folder = os.path.join(self.app, "creatives", "fitted-it")
        self.write(GOOD.replace("kind: ad", "kind: static").replace(
            '"The engineer who fitted it services it"', '"The engineer who fitted your boiler is the one who services it, every year"'))
        r = run("check.py", cwd=self.app)
        self.assertEqual(r.returncode, 1)
        self.assertIn("YYYY-MM-DD-<slug>", r.stderr)
        self.assertIn("kind must be one of", r.stderr)
        self.assertIn("over the limit", r.stderr)

    def test_claims_need_a_source_that_exists(self):
        put(os.path.join(self.app, "claims.md"), "1. No source here\n2. Wrong one (public/nope.md)\n")
        self.write(GOOD)
        r = run("check.py", cwd=self.app)
        self.assertIn("claims.md #1: no source", r.stderr)
        self.assertIn("claims.md #2: source public/nope.md does not exist", r.stderr)

    def test_sent_needs_files_and_posted_needs_a_url(self):
        self.write(GOOD.replace("status: draft", "status: posted"))
        r = run("check.py", cwd=self.app)
        self.assertIn("posted creative has the post's `url`", r.stderr)

    def test_missing_brand_notes_are_named(self):
        os.remove(os.path.join(self.app, "brand", "voice.md"))
        r = run("check.py", cwd=self.app)
        self.assertIn("brand/voice.md is missing", r.stderr)


class Generators(unittest.TestCase):
    def test_no_key_exits_3(self):
        for script in ("imagegen.py", "videogen.py"):
            r = run(script, "--check", cwd=APP)
            self.assertEqual(r.returncode, 3, script + r.stdout + r.stderr)


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


if __name__ == "__main__":
    unittest.main(verbosity=1)
