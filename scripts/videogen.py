#!/usr/bin/env python3
"""Generate a short clip (four to eight seconds) with an OpenRouter video
model. Video is expensive and slow next to a picture; the
video skill says when a clip earns it and writes the shot brief.

    python3 scripts/videogen.py --prompt-file creatives/<folder>/creative.md --section "Shot 1" --ratio 9:16 --seconds 6 --out creatives/<folder>/shot-1.mp4
                                [--ref frame.png] [--model …] [--no-text] [--force]
    python3 scripts/videogen.py --prompt "…" --ratio 9:16 --seconds 6 --out …
    python3 scripts/videogen.py --check

--prompt-file on a .md sends its `## Shot 1` section (the shot brief; pick
another with --section "Shot 2"); any other file is sent whole. An
existing --out is never replaced without --force.

The model is OpenRouter's (OPENROUTER_API_KEY, from the environment, else
from ~/.env): POST https://openrouter.ai/api/v1/videos, then polled until
the clip is ready; default model google/veo-3.1, others with --model; a
reference image goes in as input_references. The bytes go to --out (mp4)
and the provider, model, cost and prompt to <out>.json. A Higgsfield
connection (Seedance, Kling and others) brings its own instructions and is
used instead of this script.
Exit 0 written, 1 failed (no key, the model refused or was unreachable),
2 misused (a bad flag, a missing file, an --out that exists).
"""

import argparse
import base64
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (  # noqa: E402
    Parser, configured, creative_folder, data_url, die, generate, http_failure, openrouter, provider_failure,
    read_prompt, refuse_overwrite, requests_module)

EXAMPLE = ('python3 scripts/videogen.py --prompt-file creatives/<folder>/creative.md --section "Shot 1" '
           "--ratio 9:16 --seconds 6 --out creatives/<folder>/shot-1.mp4")
ASK = 'Try: python3 ~/tools/taskandtool.py request-connection openrouter-api --why "short clips for ads and posts"'

NO_TEXT = " No text, no letters, no logos, no watermarks, no captions burnt into the picture."


def gen_openrouter(prompt, ratio, seconds, refs, model):
    requests = requests_module("videogen")
    base, headers = openrouter()
    body = {"model": model or "google/veo-3.1", "prompt": prompt, "aspect_ratio": ratio, "duration": seconds}
    if refs:
        body["input_references"] = [{"type": "image_url", "image_url": {"url": data_url(r)}} for r in refs]
    r = requests.post(base + "/videos", headers=headers, json=body, timeout=120)
    if r.status_code not in (200, 201, 202):
        http_failure("videogen", "openrouter", r)
    job = r.json()
    poll = job.get("polling_url") or (base + f"/videos/{job.get('id')}" if job.get("id") else None)
    if not poll:
        provider_failure("videogen", "openrouter", f"no job in the answer: {json.dumps(job)[:400]}")
    deadline = time.time() + 900
    while time.time() < deadline:
        time.sleep(5)
        res = requests.get(poll, headers=headers, timeout=60)
        if res.status_code != 200:
            http_failure("videogen", "openrouter", res)
        res = res.json()
        status = str(res.get("status", "")).lower()
        if status in ("completed", "succeeded", "done", "ready"):
            item = (res.get("data") or [res])[0]
            url = item.get("url") or item.get("video_url")
            if item.get("b64_json"):
                return base64.b64decode(item["b64_json"]), {"provider": "openrouter", "model": body["model"], "cost": (res.get("usage") or {}).get("cost")}
            if url:
                got = requests.get(url, timeout=300)
                if got.status_code != 200:
                    http_failure("videogen", "openrouter", got)
                return got.content, {"provider": "openrouter", "model": body["model"], "cost": (res.get("usage") or {}).get("cost")}
            provider_failure("videogen", "openrouter", f"finished without a file: {json.dumps(res)[:400]}")
        if status in ("failed", "error", "cancelled"):
            provider_failure("videogen", "openrouter", f"{status}: {json.dumps(res)[:400]}")
    provider_failure("videogen", "openrouter", "no clip after 15 minutes")


def main():
    ap = Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--prompt")
    src.add_argument("--prompt-file", help="a creative.md (its --section is sent) or a plain text file")
    ap.add_argument("--section", default="Shot 1", help='the creative.md heading whose text is sent (default "Shot 1")')
    ap.add_argument("--ratio", default="9:16", choices=["9:16", "16:9", "1:1"])
    ap.add_argument("--seconds", type=int, default=6, choices=[4, 5, 6, 8])
    ap.add_argument("--out")
    ap.add_argument("--force", action="store_true", help="replace --out when it exists")
    ap.add_argument("--ref", action="append", default=[], help="a first-frame or reference image")
    ap.add_argument("--model")
    ap.add_argument("--no-text", action="store_true", help="append a no-text rule")
    ap.add_argument("--check", action="store_true", help="say whether a video model is configured, and exit")
    args = ap.parse_args()

    if args.check:
        if not configured(["openrouter"]):
            die("videogen --check: no video model configured (OPENROUTER_API_KEY)\n  " + ASK)
        print("videogen --check: OpenRouter is configured; the default model is google/veo-3.1")
        return
    if not (args.prompt or args.prompt_file) or not args.out:
        die("videogen: --prompt-file (or --prompt) and --out are required, or --check\n  Try: " + EXAMPLE, 2)
    prompt = read_prompt(args.prompt_file, "videogen", EXAMPLE, args.section) if args.prompt_file else args.prompt.strip()
    for ref in args.ref:
        if not os.path.isfile(ref):
            die(f"videogen: reference image not found: {ref}\n  Try: ls creatives/<folder> media/photos", 2)
    refuse_overwrite(args.out, args.force, "videogen")
    if not configured(["openrouter"]):
        die("videogen: no video model configured; nothing was generated\n  " + ASK)
    prompt += NO_TEXT if args.no_text else ""
    clip, meta = generate("videogen", "openrouter", gen_openrouter, prompt, args.ratio, args.seconds, args.ref, args.model)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    with open(args.out, "wb") as fh:
        fh.write(clip)
    meta.update({"prompt": prompt, "ratio": args.ratio, "seconds": args.seconds, "refs": [os.path.basename(r) for r in args.ref],
                 "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    with open(args.out + ".json", "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)
    cost = f", ${meta['cost']:.2f}" if isinstance(meta.get("cost"), (int, float)) else ""
    print(f"videogen: wrote {args.out} ({len(clip) // 1000} KB, {args.seconds} s) via {meta['provider']} {meta['model']}{cost}")
    print(f"  the prompt sent and the details: {args.out}.json")
    folder = creative_folder(args.out)
    print(f"\nNext: check frames at 0, 25, 50, 75 and 100% of {args.out}"
          + (f", then python3 scripts/check.py {folder}" if folder else ""))


if __name__ == "__main__":
    main()
