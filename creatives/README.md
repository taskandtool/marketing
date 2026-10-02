# creatives/

One folder per idea, ad or post, named `YYYY-MM-DD-<slug>` so the newest
sorts first and the date survives a clone or a restore:

```
creatives/2026-10-01-us-vs-them-roof-leak/
  creative.md     frontmatter (kind, platform, angle, hook, framework, campaign, status,
                  claims, files, copy), then the prompt or shot brief and notes
  v1.png  v2.png  outputs, versioned in place
  shot-1.mp4      video shots, when there are any
```

The `marketing` skill holds the shape of `creative.md`. Status lives in the
frontmatter (`draft → sent → approved | rejected → posted`); the owner
approves through deliverables in the chat. `python3 scripts/check.py`
checks every folder.
