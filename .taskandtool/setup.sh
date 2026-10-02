#!/usr/bin/env bash
# Creatives Starter App setup. Task & Tool runs this in ~/app after the
# repository is cloned onto the machine, and again whenever the machine is
# replaced. Safe to re-run any time:
#
#     bash ~/app/.taskandtool/setup.sh
#
# The app's own files are not this script's business: they arrive with the
# clone. What it does, each step skipped when already done:
#   1. makes sure the working copy is a git repo with a commit in it
#   2. installs the Python tools the scripts use (Pillow, requests,
#      fontTools for the caption fonts) and tt-crawl (the site reader the
#      sources skill uses). faster-whisper, for timing captions to a voice
#      track, is not installed here: it is a large download and only some
#      apps need it, so captions.py says how when it is asked for.
#   3. runs tt-crawl setup: the launcher and the browsers (Chrome, and
#      Obscura, the renderer behind scripts/render.py)
#   4. reports what is and is not available (ffmpeg for video, an image
#      model key)
set -euo pipefail

APP="$(pwd)"
CRAWLER_REF="${CRAWLER_REF:-main}"
CRAWLER="git+https://github.com/taskandtool/crawler@$CRAWLER_REF"

echo "== creatives starter app: setup in $APP"

# 1. Git: the app is the owner's repo from the first minute. A clone already
# is one; a working copy written in some other way is made one here.
if [ ! -d .git ]; then
  git init -q
fi
if ! git rev-parse --verify HEAD >/dev/null 2>&1 && [ -f CREATIVES.md ]; then
  git add -A
  git -c user.name="${GIT_AUTHOR_NAME:-$(git config user.name || echo 'Task & Tool')}" \
      -c user.email="${GIT_AUTHOR_EMAIL:-$(git config user.email || echo 'creatives@taskandtool.app')}" \
      commit -q -m "Creatives Starter App" && echo "== first commit made"
fi

# 2. Python tools.
echo "== python tools (Pillow, requests) + tt-crawl $CRAWLER_REF"
python3 -m pip install --quiet --upgrade Pillow requests 2>&1 | tail -1 || true
# fontTools converts a fetched woff2 into the TTF libass needs for video captions
python3 -m pip install --quiet --upgrade fonttools brotli 2>&1 | tail -1 || true
# The crawler's main, every run: the first install brings its dependencies;
# the second replaces its own code even when its version number did not move.
python3 -m pip install --quiet --upgrade "ttcrawl @ $CRAWLER" 2>&1 | tail -1 || true
python3 -m pip install --quiet --force-reinstall --no-deps "ttcrawl @ $CRAWLER" 2>&1 | tail -1 || true
python3 -c "import PIL, requests; print('Pillow', PIL.__version__, 'requests', requests.__version__)"
# 3. tt-crawl on the PATH, then the browsers it drives: Chrome reads a site
# and its screenshots, Obscura renders the templates (scripts/render.py).
python3 -m ttcrawl setup || echo "tt-crawl setup did not finish every step; its JSON line says which"

# Where machine-wide binaries go (ffmpeg below): system-wide when we can,
# else ~/.local/bin.
if [ -w /usr/local/bin ]; then
  BIN=/usr/local/bin
elif command -v sudo >/dev/null 2>&1 && sudo -n true 2>/dev/null; then
  BIN=/usr/local/bin
  SUDO="sudo -n"
else
  BIN="$HOME/.local/bin"
fi
SUDO="${SUDO:-}"
$SUDO mkdir -p "$BIN"

# 4. ffmpeg, for the slideshow cuts (scripts/video.py): a static build into
# the same bin, when the machine has none. About 80 MB, once.
if command -v ffmpeg >/dev/null 2>&1; then
  echo "== ffmpeg: $(ffmpeg -version 2>/dev/null | head -1 | cut -d' ' -f1-3)"
else
  case "$(uname -s)-$(uname -m)" in
    Linux-x86_64|Linux-amd64) ff="ffmpeg-release-amd64-static.tar.xz" ;;
    Linux-aarch64|Linux-arm64) ff="ffmpeg-release-arm64-static.tar.xz" ;;
    *) ff="" ;;
  esac
  if [ -n "$ff" ]; then
    echo "== ffmpeg (static build) -> $BIN"
    tmpf="$(mktemp -d)"
    if curl -fsSL --retry 3 "https://johnvansickle.com/ffmpeg/releases/$ff" -o "$tmpf/ffmpeg.tar.xz" && tar xJf "$tmpf/ffmpeg.tar.xz" -C "$tmpf"; then
      ffbin="$(find "$tmpf" -type f -name ffmpeg | head -1)"; ffprobe="$(find "$tmpf" -type f -name ffprobe | head -1)"
      [ -n "$ffbin" ] && $SUDO install -m 755 "$ffbin" "$BIN/ffmpeg"
      [ -n "$ffprobe" ] && $SUDO install -m 755 "$ffprobe" "$BIN/ffprobe"
      "$BIN/ffmpeg" -version 2>/dev/null | head -1 || echo "ffmpeg install did not produce a working binary"
    else
      echo "== ffmpeg: download failed; video.py will say so when it is needed"
    fi
    rm -rf "$tmpf"
  else
    echo "== ffmpeg: not installed and no static build for $(uname -s)/$(uname -m)"
  fi
fi
if [ -f CREATIVES.md ]; then
  python3 scripts/imagegen.py --check 2>/dev/null || echo "== no image model key yet (the static-ad skill asks the owner through Connections when one is needed)"
fi
echo "== creatives setup done"
