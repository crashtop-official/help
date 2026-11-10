#!/usr/bin/env python3
"""CrashTop Help Center — static site builder for GitHub Pages.

Reads Markdown from _article/, _posts/ and _page/, settings from site.yml,
templates from _layouts/ and _includes/, and writes the finished site to _site/.

    python build.py            build into _site/
    python build.py --serve    build, then preview on http://localhost:8000
    python build.py --strict   fail the build on any content warning (used in CI)
    python build.py --drafts   also build files marked  public: false
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from markupsafe import Markup

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "_site"
UTC = dt.timezone.utc

# folder on disk → kind of content
SOURCES = {"article": "_article", "post": "_posts", "page": "_page"}
KIND_LABEL = {"article": "Guides", "post": "Updates", "page": "Pages"}
RESERVED = {"assets", "articles", "posts", "category", "tags", "404", "index"}

WARNINGS: list[str] = []


def warn(msg: str) -> None:
    WARNINGS.append(msg)
    print(f"  ! {msg}", file=sys.stderr)


# --------------------------------------------------------------------------- #
# Settings
# --------------------------------------------------------------------------- #
def load_site(serve: bool) -> dict:
    site = yaml.safe_load((ROOT / "site.yml").read_text(encoding="utf-8")) or {}

    # Overrides: repository Variables (passed as JSON in GH_VARS) and plain env,
    # both named SITE_<KEY>.  SITE_SUPPORT_EMAIL → site.support_email
    overrides: dict[str, str] = {}
    try:
        overrides.update(json.loads(os.environ.get("GH_VARS") or "{}") or {})
    except json.JSONDecodeError:
        warn("GH_VARS is not valid JSON; repository variables were ignored")
    overrides.update({k: v for k, v in os.environ.items() if k.startswith("SITE_")})
    for key, value in overrides.items():
        if not key.upper().startswith("SITE_"):
            continue
        name = key[5:].lower()
        try:
            parsed = yaml.safe_load(value)
        except yaml.YAMLError:
            parsed = value
        site[name] = parsed if isinstance(parsed, (bool, int, float)) else str(value)
        print(f"  variable override: site.{name}")

    # Address: explicit setting → value detected by the Pages action → localhost
    if serve:
        site["url"], site["base_path"] = "http://localhost:8000", ""
    else:
        site["url"] = (site.get("url") or os.environ.get("PAGES_ORIGIN") or "http://localhost:8000").rstrip("/")
        base = site.get("base_path") or os.environ.get("PAGES_BASE_PATH") or ""
        site["base_path"] = ("/" + base.strip("/")) if base.strip("/") else ""

    site.setdefault("paths", {})
    for kind, default in (("article", "articles"), ("post", "posts"), ("page", ""),
                          ("category", "category"), ("tag", "tags")):
        site["paths"][kind] = str(site["paths"].get(kind, default) or "").strip("/")
    site["build_time"] = dt.datetime.now(UTC)
    site["year"] = site["build_time"].year
    return site


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", str(text).strip().lower())
    return re.sub(r"[\s_-]+", "-", text).strip("-")


def as_list(value) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, str):
        return [v.strip() for v in value.split(",") if v.strip()]
    return [str(v).strip() for v in value if str(v).strip()]


def as_datetime(value) -> dt.datetime | None:
    if value in (None, "", "auto", "Auto"):
        return None
    if isinstance(value, dt.datetime):
        d = value
    elif isinstance(value, dt.date):
        d = dt.datetime(value.year, value.month, value.day)
    else:
        try:
            d = dt.datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
        except ValueError:
            return None
    return d if d.tzinfo else d.replace(tzinfo=UTC)


def git_date(path: Path, first: bool) -> dt.datetime | None:
    """Date of the first (publish) or latest (update) commit that touched a file."""
    cmd = ["git", "log", "--follow", "--format=%aI"]
    cmd += ["--diff-filter=A"] if first else ["-1"]
    cmd += ["--", str(path.relative_to(ROOT))]
    try:
        out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=20).stdout.split()
    except (OSError, subprocess.SubprocessError):
        return None
    if not out:
        return None
    return as_datetime(out[-1] if first else out[0])


FRONT_MATTER = re.compile(r"\A﻿?---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.S)


def split_front_matter(text: str, path: Path) -> tuple[dict, str]:
    m = FRONT_MATTER.match(text)
    if not m:
        warn(f"{path.relative_to(ROOT)}: no front matter block (--- … ---) found")
        return {}, text
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        raise SystemExit(f"{path.relative_to(ROOT)}: front matter is not valid YAML\n{e}")
    if not isinstance(meta, dict):
        raise SystemExit(f"{path.relative_to(ROOT)}: front matter must be key: value pairs")
    return meta, text[m.end():]


# --------------------------------------------------------------------------- #
# Shortcodes available inside Markdown:  {{ chip(2.4) }}  {{ badge("live") }} …
# --------------------------------------------------------------------------- #
def chip(value, label: str | None = None) -> Markup:
    """A multiplier chip coloured by band: <2× loss, 2–10× win, ≥10× gold."""
    try:
        num = float(str(value).replace("×", "").replace("x", ""))
    except ValueError:
        return Markup(f'<span class="chip chip--neutral">{html.escape(str(value))}</span>')
    band = "loss" if num < 2 else "win" if num < 10 else "gold"
    text = label or f"{num:.2f}×"
    return Markup(f'<span class="chip chip--{band}">{html.escape(text)}</span>')


def badge(state: str, label: str | None = None) -> Markup:
    """Round status badge: waiting, live or crashed."""
    state = state if state in ("waiting", "live", "crashed") else "waiting"
    text = label or state.capitalize()
    return Markup(f'<span class="badge badge--{state}"><span class="badge__dot"></span>{html.escape(text)}</span>')


def stats(pairs) -> Markup:
    """A stat grid from {"Label": "value", …}. Values starting with + / − are coloured."""
    items = pairs.items() if isinstance(pairs, dict) else pairs
    cells = []
    for label, value in items:
        value = str(value)
        tone = " is-win" if value.startswith("+") else " is-loss" if value[:1] in "-−" else ""
        cells.append(f'<div class="statgrid__cell"><span class="statgrid__label">{html.escape(str(label))}</span>'
                     f'<span class="statgrid__value{tone}">{html.escape(value)}</span></div>')
    return Markup('<div class="statgrid">' + "".join(cells) + "</div>")


ICONS = {
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "curve": '<path d="M3 20h18M4 17c7 0 12-3 16-13"/>',
    "card": '<rect x="3" y="6" width="18" height="13" rx="2"/><path d="M3 10h18M16 15h2"/>',
    "shield": '<path d="M12 3 4 6v6c0 4.500 3.200 7.700 8 9 4.800-1.300 8-4.500 8-9V6z"/><path d="m9 12 2 2 4-4"/>',
    "lock": '<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "book": '<path d="M5 4h11a3 3 0 0 1 3 3v13H8a3 3 0 0 1-3-3z"/><path d="M5 17a3 3 0 0 1 3-3h11"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.500-3.500"/>',
    "external": '<path d="M7 17 17 7M9 7h8v8"/>',
    "chevron": '<path d="m6 9 6 6 6-6"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 7.500v.500"/>',
    "pin": '<path d="M12 17v5M8 3h8l-1 6 3 4H6l3-4z"/>',
}


def icon(name: str, size: int = 20) -> Markup:
    body = ICONS.get(name, ICONS["book"])
    return Markup(f'<svg class="icon" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
                  f'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
                  f'aria-hidden="true">{body}</svg>')


# --------------------------------------------------------------------------- #
# Content
# --------------------------------------------------------------------------- #
def flatten_toc(tokens: list, out: list | None = None) -> list[dict]:
    out = [] if out is None else out
    for t in tokens:
        if t["level"] in (2, 3):
            out.append({"level": t["level"], "id": t["id"], "title": Markup(t["name"])})
        flatten_toc(t.get("children", []), out)
    return out


def load_documents(site: dict, env: Environment, drafts: bool) -> list[dict]:
    docs: list[dict] = []
    seen: dict[str, Path] = {}
    topic_by_key = {}
    for t in site.get("topics", []):
        topic_by_key[t["slug"]] = t
        topic_by_key[slugify(t["title"])] = t

    for kind, folder in SOURCES.items():
        for path in sorted((ROOT / folder).glob("*.md")):
            rel = path.relative_to(ROOT)
            meta, body = split_front_matter(path.read_text(encoding="utf-8"), path)

            public = meta.get("public", meta.get("published", True))
            if public is False and not drafts:
                print(f"  skipped (not public): {rel}")
                continue

            # slug = file name. A Jekyll-style date prefix (2026-01-31-name.md) is accepted.
            stem, name_date = path.stem, None
            m = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)", stem)
            if m:
                name_date, stem = as_datetime(m.group(1)), m.group(2)
            slug = slugify(stem)
            if slug != stem:
                warn(f"{rel}: file name should be lowercase words joined by '-'; using slug '{slug}'")
            if kind == "page" and slug in RESERVED:
                raise SystemExit(f"{rel}: '{slug}' is a reserved address, rename the file")

            prefix = site["paths"][kind]
            url = f"/{prefix}/{slug}/" if prefix else f"/{slug}/"
            if url in seen:
                raise SystemExit(f"{rel}: address {url} is already used by {seen[url].relative_to(ROOT)}")
            seen[url] = path

            layout = str(meta.get("layout") or kind).strip().lower()
            if not (ROOT / "_layouts" / f"{layout}.html").exists():
                warn(f"{rel}: layout '{layout}' not found, using '{kind}'")
                layout = kind

            date = as_datetime(meta.get("date")) or name_date or git_date(path, first=True)
            updated = as_datetime(meta.get("updated")) or git_date(path, first=False)
            mtime = dt.datetime.fromtimestamp(path.stat().st_mtime, UTC)
            date = date or mtime
            updated = max(updated or date, date)

            cats = []
            for c in as_list(meta.get("categories", meta.get("category"))):
                topic = topic_by_key.get(slugify(c))
                cats.append({"slug": topic["slug"], "title": topic["title"]} if topic
                            else {"slug": slugify(c), "title": c})
            tags = [{"slug": slugify(t), "title": t} for t in as_list(meta.get("tags", meta.get("keywords")))]

            title = str(meta.get("title") or stem.replace("-", " ").capitalize())
            if not meta.get("title"):
                warn(f"{rel}: no title in front matter")
            description = str(meta.get("description") or "")
            if not description and kind != "page":
                warn(f"{rel}: no description in front matter (used for search engines and lists)")

            doc = {
                "kind": kind, "layout": layout, "slug": slug, "url": url, "source": str(rel),
                "title": title, "description": description,
                "date": date, "updated": updated,
                "categories": cats, "tags": tags,
                "category": cats[0] if cats else None,
                "author": str(meta.get("author") or site.get("default_author") or ""),
                "pinned": bool(meta.get("pinned", False)),
                "sitemap": bool(meta.get("sitemap", True)),
                "toc_enabled": bool(meta.get("toc", kind != "page")),
                "noindex": bool(meta.get("noindex", False)),
                "public": public is not False,
                "order": meta.get("order", 1000),
                "stage": meta.get("stage"),
                "image": meta.get("image"),
                "meta": meta,
            }

            # Markdown body: variables and shortcodes first, then Markdown → HTML
            try:
                source = env.from_string(body).render(site=site, page=doc)
            except Exception as e:  # noqa: BLE001 - report which file broke
                raise SystemExit(f"{rel}: could not process {{{{ … }}}} in the text\n{e}")
            md = markdown.Markdown(
                extensions=["extra", "toc", "admonition", "sane_lists"],
                extension_configs={"toc": {"toc_depth": "2-4"}},
                output_format="html5",
            )
            content = md.convert(source)
            content = re.sub(r"<table>", '<div class="table-scroll"><table>', content)
            content = content.replace("</table>", "</table></div>")
            doc["content"] = Markup(content)
            doc["toc"] = flatten_toc(md.toc_tokens) if doc["toc_enabled"] else []
            words = len(re.findall(r"\w+", re.sub(r"<[^>]+>", " ", content)))
            doc["minutes"] = max(1, round(words / int(site.get("words_per_minute", 200))))
            doc["text"] = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", content))).strip()
            docs.append(doc)
    return docs


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #
def build(serve: bool = False, strict: bool = False, drafts: bool = False) -> None:
    print("Building CrashTop Help Center")
    site = load_site(serve)
    base = site["base_path"]

    def url(path: str = "/") -> str:
        """Site-relative link that respects base_path. External links pass through."""
        path = str(path)
        if re.match(r"^(?:[a-z][a-z0-9+.-]*:|//|#)", path, re.I):
            return path
        return base + "/" + path.lstrip("/")

    def abs_url(path: str = "/") -> str:
        u = url(path)
        return u if re.match(r"^[a-z][a-z0-9+.-]*:", u, re.I) else site["url"] + u

    def fmt_date(d: dt.datetime | None, fmt: str | None = None) -> str:
        return d.strftime(fmt or site.get("date_format", "%d %b %Y")) if d else ""

    env = Environment(
        loader=FileSystemLoader([ROOT / "_layouts", ROOT / "_includes"]),
        autoescape=select_autoescape(["html", "xml", "xsl"]),
        undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True,
    )
    env.globals.update(site=site, url=url, abs_url=abs_url, icon=icon, chip=chip, badge=badge, stats=stats)
    env.filters.update(date=fmt_date, iso=lambda d: d.isoformat(timespec="seconds") if d else "",
                       slugify=slugify, two=lambda n: f"{int(n):02d}")
    md_env = Environment(autoescape=False, undefined=StrictUndefined)
    md_env.globals.update(url=url, abs_url=abs_url, icon=icon, chip=chip, badge=badge, stats=stats)

    docs = load_documents(site, md_env, drafts)
    articles = [d for d in docs if d["kind"] == "article"]
    posts = sorted((d for d in docs if d["kind"] == "post"), key=lambda d: d["date"], reverse=True)
    pages = [d for d in docs if d["kind"] == "page"]

    # Topics in site.yml order, then any category that only exists in front matter
    topics, index = [], {}
    for t in site.get("topics", []):
        topic = {**t, "docs": [], "url": f"/{site['paths']['category']}/{t['slug']}/"}
        topics.append(topic)
        index[t["slug"]] = topic
    for d in docs:
        for c in d["categories"]:
            if c["slug"] not in index:
                topic = {"slug": c["slug"], "title": c["title"], "description": "", "icon": "book",
                         "docs": [], "url": f"/{site['paths']['category']}/{c['slug']}/"}
                topics.append(topic)
                index[c["slug"]] = topic
            index[c["slug"]]["docs"].append(d)
            c["url"] = index[c["slug"]]["url"]
    topic_order = {t["slug"]: i for i, t in enumerate(topics)}

    def doc_sort(d: dict):
        cat = topic_order.get(d["category"]["slug"], 999) if d["category"] else 999
        return (cat, d["order"], d["title"].lower())

    articles.sort(key=doc_sort)
    for t in topics:
        t["docs"].sort(key=lambda d: (d["kind"] != "article", d["order"], d["title"].lower()))
        t["articles"] = [d for d in t["docs"] if d["kind"] == "article"]
    topics = [t for t in topics if t["docs"]]

    tags: dict[str, dict] = {}
    for d in docs:
        for t in d["tags"]:
            t["url"] = f"/{site['paths']['tag']}/{t['slug']}/"
            tags.setdefault(t["slug"], {"slug": t["slug"], "title": t["title"], "url": t["url"], "docs": []})["docs"].append(d)

    for group in (articles, posts):
        for i, d in enumerate(group):
            d["prev"] = group[i - 1] if i > 0 else None
            d["next"] = group[i + 1] if i < len(group) - 1 else None
    for d in pages:
        d["prev"] = d["next"] = None

    stages = []
    for s in site.get("round_stages", []):
        target = next((a for a in articles if str(a["stage"]) == str(s["n"])), None)
        stages.append({**s, "doc": target})

    env.globals.update(articles=articles, posts=posts, pages=pages, topics=topics,
                       tags=sorted(tags.values(), key=lambda t: t["title"].lower()), stages=stages)

    # ---- write ---------------------------------------------------------------
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    written: list[dict] = []   # every HTML page, for the sitemaps

    def write(rel_url: str, template: str, sitemap: bool = True, group: str = "pages",
              lastmod: dt.datetime | None = None, **ctx) -> None:
        target = OUT / rel_url.strip("/") / "index.html" if rel_url.endswith("/") else OUT / rel_url.strip("/")
        target.parent.mkdir(parents=True, exist_ok=True)
        ctx.setdefault("page", {})
        text = env.get_template(template).render(current_url=rel_url, **ctx)
        target.write_text(text, encoding="utf-8")
        if sitemap:
            written.append({"url": rel_url, "group": group, "lastmod": lastmod or site["build_time"],
                            "title": ctx.get("page_title") or ctx["page"].get("title") or site["title"]})

    pinned = sorted((d for d in docs if d["pinned"]), key=lambda d: d["date"], reverse=True)
    newest = max((d["updated"] for d in docs), default=site["build_time"])
    write("/", "home.html", lastmod=newest, pinned=pinned,
          guides=sorted(articles, key=lambda d: (not d["pinned"],) + doc_sort(d)))

    for d in docs:
        write(d["url"], f"{d['layout']}.html", sitemap=d["sitemap"] and not d["noindex"],
              group={"article": "articles", "post": "posts", "page": "pages"}[d["kind"]],
              lastmod=d["updated"], page=d)

    if articles:
        write(f"/{site['paths']['article']}/", "list.html", lastmod=newest, page_title="All guides",
              heading="All guides", eyebrow="GUIDES", intro="Every guide, grouped by topic.",
              groups=[{"title": t["title"], "url": t["url"], "docs": t["articles"]} for t in topics if t["articles"]])
    if posts:
        write(f"/{site['paths']['post']}/", "list.html", lastmod=posts[0]["updated"], page_title="Updates",
              heading="Updates", eyebrow="UPDATES", intro="News and changes from the CrashTop team.",
              groups=[{"title": "", "url": "", "docs": posts}])
    for t in topics:
        write(t["url"], "list.html", lastmod=max(d["updated"] for d in t["docs"]), page_title=t["title"],
              heading=t["title"], eyebrow="TOPIC", intro=t.get("description", ""),
              groups=[{"title": "", "url": "", "docs": t["docs"]}])
    for t in tags.values():
        write(t["url"], "list.html", sitemap=False, page_title=f"Tagged “{t['title']}”",
              heading=f"Tagged “{t['title']}”", eyebrow="TAG", intro="",
              groups=[{"title": "", "url": "", "docs": t["docs"]}])
    write("/404.html", "404.html", sitemap=False, page_title="Page not found")

    # ---- machine files -------------------------------------------------------
    groups = [g for g in ("pages", "articles", "posts") if any(w["group"] == g for w in written)]
    xml = env.get_template("sitemap.xml")
    (OUT / "sitemap.xml").write_text(xml.render(entries=written), encoding="utf-8")
    for g in groups:
        (OUT / f"sitemap-{g}.xml").write_text(xml.render(entries=[w for w in written if w["group"] == g]), encoding="utf-8")
    (OUT / "sitemap_index.xml").write_text(env.get_template("sitemap_index.xml").render(
        maps=[{"url": f"/sitemap-{g}.xml", "count": sum(w["group"] == g for w in written),
               "lastmod": max(w["lastmod"] for w in written if w["group"] == g)} for g in groups]), encoding="utf-8")
    (OUT / "sitemap.xsl").write_text(env.get_template("sitemap.xsl").render(), encoding="utf-8")
    (OUT / "feed.xml").write_text(env.get_template("feed.xml").render(), encoding="utf-8")
    (OUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {abs_url('/sitemap_index.xml')}\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    if site.get("cname"):
        (OUT / "CNAME").write_text(str(site["cname"]).strip() + "\n", encoding="utf-8")

    print(f"  {len(articles)} articles, {len(posts)} posts, {len(pages)} pages, "
          f"{len(topics)} topics, {len(tags)} tags → {OUT.relative_to(ROOT)}/")
    print(f"  address: {site['url']}{base}/")
    if WARNINGS and strict:
        raise SystemExit(f"{len(WARNINGS)} warning(s) with --strict; fix them and build again")


def serve() -> None:
    import functools
    import http.server

    class Handler(http.server.SimpleHTTPRequestHandler):
        def send_error(self, code, message=None, explain=None):
            if code == 404 and (OUT / "404.html").exists():
                body = (OUT / "404.html").read_bytes()
                self.send_response(404)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                super().send_error(code, message, explain)

    print("Preview on http://localhost:8000  (Ctrl+C to stop)")
    http.server.ThreadingHTTPServer(("", 8000), functools.partial(Handler, directory=str(OUT))).serve_forever()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--serve", action="store_true", help="build, then preview on http://localhost:8000")
    ap.add_argument("--strict", action="store_true", help="treat content warnings as errors")
    ap.add_argument("--drafts", action="store_true", help="include files marked public: false")
    args = ap.parse_args()
    build(serve=args.serve, strict=args.strict, drafts=args.drafts)
    if args.serve:
        serve()
