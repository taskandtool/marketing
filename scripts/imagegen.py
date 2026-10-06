#!/usr/bin/env python3
"""Generate a picture for a creative with whichever image model this app
has a key for. The images skill writes the prompt; this sends it.

    python3 scripts/imagegen.py --prompt-file creatives/<folder>/creative.md --ratio 4:5 --out creatives/<folder>/v1.png
                                [--ref photo.png …] [--brand] [--no-text] [--force]
                                [--provider openai|openrouter] [--model …]
                                [--size 512|1K|2K|4K] [--seed N]
    python3 scripts/imagegen.py --prompt "…" --ratio 4:5 --out …
    python3 scripts/imagegen.py --check          # which providers are configured

--prompt-file on a .md sends its `## Prompt` section; any other file is
sent whole. An existing --out is never replaced without --force.

Providers, in the order tried (the first with a key wins):

  OPENAI_API_KEY       gpt-image-2 (the strongest at rendering words in the picture);
                       during an AI turn, through Task & Tool's metered gateway
  OPENROUTER_API_KEY   POST https://openrouter.ai/api/v1/images; one key for Gemini,
                       GPT Image and FLUX; default model google/gemini-3.1-flash-image

Each key is read from the environment, else from ~/.env (a granted
connection puts it there; a turn keeps it out of the AI's own shell).
The bytes are written to --out as PNG; the provider, model, cost (when
reported) and the prompt go to <out>.json beside it.
Exit 0 written, 1 failed (no provider configured, the model refused or
was unreachable), 2 misused (a bad flag, a missing file, an --out that
exists).
"""

import argparse
import base64
import json
import mimetypes
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (  # noqa: E402
    Parser, configured, creative_folder, data_url, die, generate, http_failure, openai, openrouter, provider_failure,
    read_prompt, refuse_overwrite, requests_module, root, split_frontmatter)

EXAMPLE = "python3 scripts/imagegen.py --prompt-file creatives/<folder>/creative.md --ratio 4:5 --out creatives/<folder>/v1.png"
ASK = 'Try: python3 ~/tools/taskandtool.py request-connection openrouter-api --why "pictures for ads and posts"'

NO_TEXT = " No text, no letters, no numbers, no logos, no watermarks anywhere in the image."


def style_anchor(app_root, anchor_path=None):
    """The brand's style anchor from brand/visual-identity.md (the Imagery
    block's 'Style anchor' line, else its filled bullets joined), or the
    campaign's own from --anchor. Empty when nothing is filled."""
    if anchor_path:
        with open(anchor_path, encoding="utf-8") as fh:
            text = fh.read()
        _, body = split_frontmatter(text)
        return " ".join(line.strip() for line in body.splitlines() if line.strip() and not line.startswith("#"))
    note = os.path.join(app_root, "brand", "visual-identity.md")
    if not os.path.isfile(note):
        return ""
    with open(note, encoding="utf-8") as fh:
        text = fh.read()
    block = text.split("## Imagery")[1] if "## Imagery" in text else ""
    block = block.split("\n## ")[0]
    lines = [l.strip()[2:].strip() for l in block.splitlines() if l.strip().startswith("- ")]
    lines = [l for l in lines if "to fill" not in l]
    for l in lines:
        plain = l.replace("**", "")
        if plain.lower().startswith("style anchor") and ":" in plain:
            return plain.split(":", 1)[1].strip()
    if not lines:
        return ""
    return " ".join(l.replace("**", "") for l in lines)


RATIOS = ["1:1", "4:5", "9:16", "16:9", "1.91:1", "2:3", "3:2", "4:3", "3:4"]
OPENAI_SIZES = {"1:1": "1024x1024", "4:5": "1024x1536", "9:16": "1024x1536", "2:3": "1024x1536", "3:4": "1024x1536",
                "16:9": "1536x1024", "1.91:1": "1536x1024", "3:2": "1536x1024", "4:3": "1536x1024"}


ORDER = ["openai", "openrouter"]


def gen_openrouter(prompt, ratio, refs, model, size, seed):
    requests = requests_module("imagegen")
    base, headers = openrouter()
    body = {"model": model or "google/gemini-3.1-flash-image", "prompt": prompt, "aspect_ratio": ratio,
            "resolution": size or "1K", "output_format": "png", "n": 1}
    if seed is not None:
        body["seed"] = seed
    if refs:
        body["input_references"] = [{"type": "image_url", "image_url": {"url": data_url(r)}} for r in refs]
    r = requests.post(base + "/images", headers=headers, json=body, timeout=240)
    if r.status_code != 200:
        http_failure("imagegen", "openrouter", r)
    data = r.json()
    item = data["data"][0]
    if item.get("b64_json"):
        img = base64.b64decode(item["b64_json"])
    elif item.get("url"):
        img = requests.get(item["url"], timeout=120)
        if img.status_code != 200:
            http_failure("imagegen", "openrouter", img)
        img = img.content
    else:
        provider_failure("imagegen", "openrouter", f"no image in the answer: {json.dumps(data)[:400]}")
    return img, {"provider": "openrouter", "model": body["model"], "cost": (data.get("usage") or {}).get("cost")}


def gen_openai(prompt, ratio, refs, model, size, seed):
    requests = requests_module("imagegen")
    base, headers = openai()
    model = model or "gpt-image-2"
    px = OPENAI_SIZES.get(ratio, "1024x1024")
    quality = {"1K": "medium", "2K": "high", "4K": "high"}.get(size or "1K", "medium")
    if refs:
        files = [("image[]", (os.path.basename(p), open(p, "rb").read(), mimetypes.guess_type(p)[0] or "image/png")) for p in refs]
        r = requests.post(base + "/images/edits", headers=headers, files=files,
                          data={"model": model, "prompt": prompt, "size": px, "quality": quality}, timeout=300)
    else:
        r = requests.post(base + "/images/generations", headers={**headers, "Content-Type": "application/json"},
                          json={"model": model, "prompt": prompt, "size": px, "quality": quality, "output_format": "png"}, timeout=300)
    if r.status_code != 200:
        http_failure("imagegen", "openai", r)
    data = r.json()
    return base64.b64decode(data["data"][0]["b64_json"]), {"provider": "openai", "model": model, "cost": None}


GENERATORS = {"openrouter": gen_openrouter, "openai": gen_openai}


def main():
    ap = Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--prompt")
    src.add_argument("--prompt-file", help="a creative.md (its ## Prompt section is sent) or a plain text file")
    ap.add_argument("--ratio", default="4:5", choices=RATIOS)
    ap.add_argument("--out")
    ap.add_argument("--force", action="store_true", help="replace --out when it exists")
    ap.add_argument("--ref", action="append", default=[], help="a reference image (the product, the place); repeatable")
    ap.add_argument("--provider", choices=sorted(GENERATORS))
    ap.add_argument("--model")
    ap.add_argument("--size", choices=["512", "1K", "2K", "4K"])
    ap.add_argument("--seed", type=int)
    ap.add_argument("--no-text", action="store_true", help="append a no-text rule (a scene the words go beside, not in)")
    ap.add_argument("--brand", action="store_true", help="append the brand's style anchor (brand/visual-identity.md, Imagery)")
    ap.add_argument("--anchor", help="a file whose body is a style anchor for this piece of work")
    ap.add_argument("--check", action="store_true", help="print the configured providers and exit")
    args = ap.parse_args()

    avail = configured(ORDER)
    if args.check:
        anchor = style_anchor(root())
        anchor = "  style anchor: " + (anchor[:120] + ("…" if len(anchor) > 120 else "") if anchor else "not filled (brand/visual-identity.md, Imagery)")
        if not avail:
            die("imagegen --check: no image model configured (OPENAI_API_KEY, OPENROUTER_API_KEY)\n"
                + anchor + "\n  " + ASK)
        print("imagegen --check: image providers configured, in the order tried: " + ", ".join(avail))
        print(anchor)
        return
    if not (args.prompt or args.prompt_file) or not args.out:
        die("imagegen: --prompt-file (or --prompt) and --out are required, or --check\n  Try: " + EXAMPLE, 2)
    prompt = read_prompt(args.prompt_file, "imagegen", EXAMPLE) if args.prompt_file else args.prompt.strip()
    for ref in args.ref:
        if not os.path.isfile(ref):
            die(f"imagegen: reference image not found: {ref}\n  Try: ls media/photos", 2)
    if args.anchor and not os.path.isfile(args.anchor):
        die(f"imagegen: style anchor file not found: {args.anchor}\n  Try: --brand for the brand's own anchor, or ls research/", 2)
    refuse_overwrite(args.out, args.force, "imagegen")
    provider = args.provider or (avail[0] if avail else None)
    if not provider:
        die("imagegen: no image model configured; nothing was generated\n  " + ASK)
    if provider not in avail:
        die(f"imagegen: {provider} has no key here; configured: {', '.join(avail) or 'none'}\n  "
            + (f"Try: --provider {avail[0]}" if avail else ASK))

    if args.brand or args.anchor:
        anchor = style_anchor(root(), args.anchor)
        if anchor:
            prompt += " " + anchor
        else:
            print("note: no style anchor filled in brand/visual-identity.md (Imagery); the prompt goes without one", file=sys.stderr)
    if args.no_text:
        prompt += NO_TEXT
    img, meta = generate("imagegen", provider, GENERATORS[provider], prompt, args.ratio, args.ref, args.model, args.size, args.seed)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    with open(args.out, "wb") as fh:
        fh.write(img)
    # a PNG whatever the provider sent, with the sRGB tag, when Pillow is there
    try:
        from PIL import Image, ImageCms
        im = Image.open(args.out).convert("RGB")
        icc = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
        im.save(args.out, "PNG", icc_profile=icc)
        meta["size"] = f"{im.size[0]}x{im.size[1]}"
    except Exception:  # noqa: BLE001
        pass
    meta.update({"prompt": prompt, "ratio": args.ratio, "refs": [os.path.basename(r) for r in args.ref], "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    with open(args.out + ".json", "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)
    cost = f", ${meta['cost']:.3f}" if isinstance(meta.get("cost"), (int, float)) else ""
    size = f" {meta['size']}" if meta.get("size") else ""
    print(f"imagegen: wrote {args.out}{size} via {meta['provider']} {meta['model']}{cost}")
    print(f"  the prompt sent and the details: {args.out}.json")
    folder = creative_folder(args.out)
    print(f"\nNext: look at {args.out} at full size and at 25%"
          + (f", then python3 scripts/check.py {folder}" if folder else ""))


if __name__ == "__main__":
    main()
