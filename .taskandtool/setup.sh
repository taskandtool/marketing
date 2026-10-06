#!/usr/bin/env bash
# Marketing Starter App setup. Task & Tool runs this in ~/app after the
# repository is cloned onto the machine, and again whenever the machine is
# replaced. Safe to re-run any time:
#
#     bash ~/app/.taskandtool/setup.sh
#
# The app's own files are not this script's business: they arrive with the
# clone. What it does, each step skipped when already done:
#   1. makes sure the working copy is a git repo with a commit in it
#   2. installs the Python tools the scripts use (Pillow, requests) and
#      tt-crawl (the site reader the brand and research skills use)
#   3. runs tt-crawl setup: the launcher and the browsers it reads sites
#      with (Chrome, and Obscura)
set -euo pipefail

APP="$(pwd)"
CRAWLER_REF="${CRAWLER_REF:-main}"
CRAWLER="git+https://github.com/taskandtool/crawler@$CRAWLER_REF"

echo "== marketing starter app: setup in $APP"

# 1. Git: the app is the owner's repo from the first minute. A clone already
# is one; a working copy written in some other way is made one here.
if [ ! -d .git ]; then
  git init -q
fi
if ! git rev-parse --verify HEAD >/dev/null 2>&1 && [ -f AGENTS.md ]; then
  git add -A
  git -c user.name="${GIT_AUTHOR_NAME:-$(git config user.name || echo 'Task & Tool')}" \
      -c user.email="${GIT_AUTHOR_EMAIL:-$(git config user.email || echo 'marketing@taskandtool.app')}" \
      commit -q -m "Marketing Starter App" && echo "== first commit made"
fi

# 2. Python tools.
echo "== python tools (Pillow, requests) + tt-crawl $CRAWLER_REF"
python3 -m pip install --quiet --upgrade Pillow requests 2>&1 | tail -1 || true
# The crawler's main, every run: the first install brings its dependencies;
# the second replaces its own code even when its version number did not move.
python3 -m pip install --quiet --upgrade "ttcrawl @ $CRAWLER" 2>&1 | tail -1 || true
python3 -m pip install --quiet --force-reinstall --no-deps "ttcrawl @ $CRAWLER" 2>&1 | tail -1 || true
python3 -c "import PIL, requests; print('Pillow', PIL.__version__, 'requests', requests.__version__)"
# 3. tt-crawl on the PATH, then the browsers it drives: Chrome reads a site
# and its screenshots, Obscura is its fallback.
python3 -m ttcrawl setup || echo "tt-crawl setup did not finish every step; its output above says which"
tt-crawl --version || echo "== warning: tt-crawl is not on the PATH; the brand and research skills cannot read sites until bash .taskandtool/setup.sh runs clean"
echo "== marketing setup done"
