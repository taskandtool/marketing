// A creative.md (or an email.md) lists its pictures and clips in `files:`
// and its words in `copy:`, and its body is the idea, the prompt and notes.
// Rendered as it is, a page would show the notes and none of the piece. This
// plugin runs after note-properties has read the frontmatter, and puts the
// piece first: a title from the folder's name, the copy, then each file.

const IMAGE = /\.(png|jpe?g|webp|gif|avif|svg)$/i
const VIDEO = /\.(mp4|webm|mov|m4v)$/i
// A file beside the note, by name: never a path, a parent or a scheme.
const PLAIN_NAME = /^[\w][\w.-]*$/
const PIECE = /(?:^|\/)(creatives|emails)\/(\d{4}-\d{2}-\d{2})-([^/]+)\/(creative|email)\.md$/

/** "2026-10-01-us-vs-them-roof-leak" → "Us vs them roof leak". */
export function titleFromFolder(slug) {
  const words = slug.replace(/-/g, " ").trim()
  return words.charAt(0).toUpperCase() + words.slice(1)
}

const text = (value) => ({ type: "text", value: String(value) })
const para = (...children) => ({ type: "paragraph", children })
const heading = (value) => ({ type: "heading", depth: 2, children: [text(value)] })

/** The nodes for one listed file, or null for a name it will not show. */
export function fileNode(name) {
  if (typeof name !== "string" || !PLAIN_NAME.test(name)) return null
  if (IMAGE.test(name)) return para({ type: "image", url: name, alt: name })
  if (VIDEO.test(name)) {
    return {
      type: "paragraph",
      children: [],
      data: { hName: "video", hProperties: { src: name, controls: true, preload: "metadata" } },
    }
  }
  return para({ type: "link", url: name, children: [text(name)] })
}

// Copy keys a person would not read as words.
const LABELS = { cta: "Call to action" }

/** "primary_text" → "Primary text"; "cta" → "Call to action". */
export function label(key) {
  if (LABELS[key]) return LABELS[key]
  const words = String(key).replace(/_/g, " ")
  return words.charAt(0).toUpperCase() + words.slice(1)
}

/** The nodes that go before the body: the copy, then the files. */
const PLATFORMS = { facebook: "Facebook", meta: "Facebook", instagram: "Instagram", x: "X", linkedin: "LinkedIn",
  tiktok: "TikTok", gbp: "Google Business Profile", pinterest: "Pinterest", youtube: "YouTube", google: "Google" }
const box = (style, children) => ({ type: "paragraph", children, data: { hName: "div", hProperties: { style } } })

/** A post or ad as one card, the way a feed shows it: the business, the
 * caption, then the pictures and clips. The feed's own look per platform is
 * scripts/preview.py's; this is the same piece in the viewer's colours. */
export function cardNodes(frontmatter) {
  const kind = frontmatter?.kind
  if (kind !== "post" && kind !== "ad") return []
  const copy = frontmatter.copy && typeof frontmatter.copy === "object" ? frontmatter.copy : {}
  const tags = Array.isArray(copy.hashtags) ? copy.hashtags.map((t) => (String(t).startsWith("#") ? t : "#" + t)).join(" ") : ""
  const words = [copy.caption || copy.primary_text || "", tags].filter((s) => String(s).trim()).join("\n\n")
  const files = (Array.isArray(frontmatter.files) ? frontmatter.files : []).map(fileNode).filter(Boolean)
  const where = PLATFORMS[frontmatter.platform] ?? String(frontmatter.platform ?? "")
  const children = []
  if (words) children.push(box("white-space:pre-line;margin:0 0 .75rem", [text(words)]))
  if (copy.headline) children.push(box("font-weight:600;margin:.75rem 0 0", [text(copy.headline)]))
  if (copy.cta) children.push(box("margin:.25rem 0 0;opacity:.8", [text(copy.cta)]))
  children.splice(words ? 1 : 0, 0, ...files)
  const style = "max-width:500px;padding:1rem;border:1px solid var(--lightgray);border-radius:10px;background:var(--light)"
  return [heading(`On ${where}${kind === "ad" ? ", as an ad" : ""}`), box(style, children)]
}

export function pieceNodes(frontmatter) {
  const card = cardNodes(frontmatter)
  const out = [...card]
  const copy = frontmatter?.copy
  if (copy && typeof copy === "object" && !Array.isArray(copy)) {
    const rows = Object.entries(copy).filter(([, v]) => v != null && String(v).trim() !== "")
    if (rows.length) {
      out.push(heading("Copy"))
      for (const [k, v] of rows) out.push(para({ type: "strong", children: [text(label(k))] }, text(": " + v)))
    }
  }
  // a post's pictures are in its card; any other piece lists its files
  const files = Array.isArray(frontmatter?.files) ? frontmatter.files : []
  const nodes = card.length ? [] : files.map(fileNode).filter(Boolean)
  if (nodes.length) out.push(heading(nodes.length === 1 ? "File" : "Files"), ...nodes)
  return out
}

// A folder's _index.md is its page: titled by the folder, not "_index".
const FOLDER_INDEX = /(?:^|\/)([^/]+)\/_index\.md$/

function remarkCreativeFiles(allSlugs) {
  return () => (tree, file) => {
    const where = String(file.data?.relativePath ?? file.path ?? "")
    const fm = file.data?.frontmatter
    const index = FOLDER_INDEX.exec(where)
    if (index && fm && (!fm.title || fm.title === "_index")) fm.title = titleFromFolder(index[1])
    const piece = PIECE.exec(where)
    if (!piece) return
    if (fm && (!fm.title || fm.title === piece[4])) fm.title = titleFromFolder(piece[3])
    // The piece is its folder's page, so the list of creatives (or emails)
    // names each by its title and opens it in one click. Links inside it
    // resolve as before: the folder is the same.
    const slug = file.data?.slug
    if (typeof slug === "string" && slug.endsWith("/" + piece[4])) {
      file.data.slug = slug.slice(0, -piece[4].length) + "index"
      allSlugs?.push(file.data.slug)
    }
    tree.children.unshift(...pieceNodes(fm))
  }
}

export default function CreativeFiles() {
  return {
    name: "CreativeFiles",
    markdownPlugins(ctx) {
      return [remarkCreativeFiles(ctx?.allSlugs)]
    },
  }
}
