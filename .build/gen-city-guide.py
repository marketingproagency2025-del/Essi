#!/usr/bin/env python3
"""Build a city guide in all four MarketingPro trees from one content spec per language.

Generalised from build_milano.py, which hardcoded the Milan slug and image. Same method, and
the method is the point: every page is generated from its OWN tree's blog-seo.html, so the
chrome (header, nav, language switcher, footer, scripts) is that tree's real boilerplate rather
than something retyped. Only the head's page-specific fields, the JSON-LD graph and <main> are
replaced. That makes the four pages structurally identical by construction, which is what the
parity and boilerplate checks in .build/verify-langs.ps1 actually test.

    python build_city.py            # all three cities, all four languages
    python build_city.py roma       # one city
"""
import io
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.dirname(_HERE)          # the repo root, one level above .build
CONTENT = os.path.join(_HERE, "city-content")
SITE = "https://www.marketingpro-agency.com"

DONOR_SLUG = "blog-seo"
OLD_IMG = "svc-seo-1"
IMG_W, IMG_H = 1080, 1258
PUB = "2026-08-23"
MOD = "2026-08-23"
TREES = {"en": "", "it": "it", "es": "es", "sq": "sq"}

# Heroes are existing Mediterranean stock, 1080x1258 like every other blog hero, with .webp
# siblings already generated. Scenery rather than anything topical: the client accepted that
# rather than hold three posts for a photo shoot. The alt text in each content file is the
# real description of the image, copied from where the site already uses it, so no page
# claims a photograph of the city it is named for.
CITIES = {
    "roma":   {"slug": "blog-roma",   "img": "svc-renders-2"},
    "lugano": {"slug": "blog-lugano", "img": "svc-web-2"},
    "ticino": {"slug": "blog-ticino", "img": "svc-funnel-2"},
}

BACK_SVG = ('<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">'
            '<path fill="currentColor" d="M15 6l-6 6 6 6 1.4-1.4L11.8 12l4.6-4.6z"/></svg>')


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def attr(s):
    return esc(s).replace('"', "&quot;")


def page_path(tree, slug):
    return os.path.join(SITE_DIR, tree, slug + ".html") if tree \
        else os.path.join(SITE_DIR, slug + ".html")


def url_for(tree, slug):
    return f"{SITE}/{tree}/{slug}" if tree else f"{SITE}/{slug}"


def root_for(tree):
    return f"/{tree}" if tree else ""


def assets_for(tree):
    return "../assets/img" if tree else "assets/img"


def build_main(c, tree, donor_main, img_name):
    """<main> for one language. Breadcrumb aria-label is lifted from the donor so it stays native."""
    m = re.search(r'<nav class="breadcrumb" aria-label="([^"]*)"', donor_main)
    crumb_aria = m.group(1) if m else "Breadcrumb"
    root, img = root_for(tree), assets_for(tree)
    L = []
    L.append('  <main id="main" class="article-page">')
    L.append(f'    <nav class="breadcrumb" aria-label="{attr(crumb_aria)}">')
    L.append("      <ol>")
    L.append(f'        <li><a href="{root}/">{esc(c["breadcrumb_home"])}</a></li>')
    L.append(f'        <li><a href="{root}/blog">{esc(c["breadcrumb_blog"])}</a></li>')
    L.append(f'        <li><span aria-current="page">{esc(c["breadcrumb_last"])}</span></li>')
    L.append("      </ol>")
    L.append("    </nav>")
    L.append("    <article>")
    L.append('      <header class="section article-hero">')
    L.append('        <div class="container">')
    L.append(f'          <p class="article-hero__meta"><time datetime="{PUB}">{esc(c["date_display"])}</time> '
             f'· {esc(c["read_time"])} · {esc(c["by"])} <a href="{root}/about">Essi Papajorgji</a></p>')
    L.append(f'          <h1 class="article-hero__title">{esc(c["h1"])}</h1>')
    L.append('          <div class="article-hero__media">')
    L.append("            <picture>")
    L.append(f'              <source srcset="{img}/{img_name}.webp" type="image/webp" />')
    L.append(f'              <img src="{img}/{img_name}.jpg" alt="{attr(c["hero_alt"])}" width="{IMG_W}" '
             f'height="{IMG_H}" fetchpriority="high" decoding="async" />')
    L.append("            </picture>")
    L.append("          </div>")
    L.append("        </div>")
    L.append("      </header>")
    L.append("")
    L.append('      <div class="container">')
    L.append('        <div class="article article__body">')
    for p in c["intro"]:
        L.append(f"          <p>{esc(p)}</p>")
    for sec in c["sections"]:
        L.append("")
        L.append(f'          <h2>{esc(sec["h2"])}</h2>')
        for p in sec["p"]:
            L.append(f"          <p>{esc(p)}</p>")
    L.append("")
    L.append(f'          <h2>{esc(c["summary_h2"])}</h2>')
    L.append("          <ul>")
    for s in c["summary"]:
        L.append(f"            <li>{esc(s)}</li>")
    L.append("          </ul>")
    L.append("")
    L.append(f'          <h2>{esc(c["faq_h2"])}</h2>')
    L.append('          <div class="faq__list">')
    for qa in c["faq"]:
        L.append('            <details class="faq__item">')
        L.append(f'              <summary>{esc(qa["q"])}</summary>')
        L.append(f'              <p>{esc(qa["a"])}</p>')
        L.append("            </details>")
    L.append("          </div>")
    L.append("")
    L.append(f'          <h2>{esc(c["related_h2"])}</h2>')
    L.append("          <ul>")
    for r in c["related"]:
        L.append(f'            <li><a href="{root}/{r["slug"]}">{esc(r["label"])}</a></li>')
    L.append("          </ul>")
    L.append("")
    L.append(f'          <p class="post-service"><strong>{esc(c["service_label"])}</strong> '
             f'<a href="{root}/{c["service_slug"]}">{esc(c["service_name"])}</a></p>')
    L.append(f'          <p><a class="btn btn--green" href="{root}/contact">{esc(c["cta_label"])}</a></p>')
    L.append("")
    L.append(f'          <a class="article__back" href="{root}/blog">')
    L.append(f"            {BACK_SVG}")
    L.append(f"            {esc(c['back_label'])}")
    L.append("          </a>")
    L.append("        </div>")
    L.append("      </div>")
    L.append("    </article>")
    L.append("  </main>")
    return "\n".join(L)


def collapse_lang_arrays(s):
    """Put inLanguage and availableLanguage back on one line.

    json.dumps(indent=2) explodes every array, but gate check 9 compares these two against the
    literal string '["en", "it", "es", "sq"]'. Every other array in the graph (keywords,
    areaServed, sameAs, itemListElement) is expanded in the shipped files, so only these two
    are collapsed.
    """
    def fix(m):
        items = re.findall(r'"([^"]*)"', m.group(2))
        return '"%s": [%s]' % (m.group(1), ", ".join('"%s"' % i for i in items))
    return re.sub(r'"(inLanguage|availableLanguage)":\s*\[([^\]]*)\]', fix, s)


def rewrite_jsonld(head, c, tree, slug, img_name):
    """Re-point the four page-specific nodes. @ids already carry the new slug after the swap."""
    tag = '<script type="application/ld+json">'
    i = head.index(tag) + len(tag)
    j = head.index("</script>", i)
    graph = json.loads(head[i:j])
    page_url = url_for(tree, slug)
    img_url = f"{SITE}/assets/img/{img_name}.jpg"
    for n in graph["@graph"]:
        t = n.get("@type")
        if t == "WebPage":
            n["url"] = page_url
            n["name"] = c["h1"]
            n["primaryImageOfPage"] = img_url
        elif t == "BreadcrumbList":
            n["itemListElement"][-1]["name"] = c["breadcrumb_last"]
        elif t == "BlogPosting":
            n["headline"] = c["h1"]
            n["description"] = c["og_description"]
            n["image"] = img_url
            n["datePublished"] = PUB
            n["dateModified"] = MOD
            n["articleSection"] = c["articleSection"]
            n["keywords"] = c["keywords"]
        elif t == "FAQPage":
            n["mainEntity"] = [
                {"@type": "Question", "name": qa["q"],
                 "acceptedAnswer": {"@type": "Answer", "text": qa["a"]}}
                for qa in c["faq"]
            ]
    body = collapse_lang_arrays(json.dumps(graph, ensure_ascii=False, indent=2)).replace("\n", "\n  ")
    return head[:i] + "\n  " + body + "\n  " + head[j:]


def sub1(s, pattern, replacement, label):
    out, n = re.subn(pattern, lambda _m: replacement, s, count=1)
    if n != 1:
        raise SystemExit(f"  ! {label}: expected 1 replacement, made {n}")
    return out


def build(city, lang, tree):
    slug, img_name = CITIES[city]["slug"], CITIES[city]["img"]
    c = json.load(io.open(os.path.join(CONTENT, f"{city}-{lang}.json"), encoding="utf-8"))
    donor = io.open(page_path(tree, DONOR_SLUG), encoding="utf-8", newline="").read()

    a = donor.index('  <main id="main"')
    b = donor.index("  </main>") + len("  </main>")
    before, donor_main, after = donor[:a], donor[a:b], donor[b:]

    # the slug and hero image appear in canonical, hreflang, og, twitter, preload, JSON-LD @ids
    # and the language switcher; all of them must move together
    before = before.replace(DONOR_SLUG, slug).replace(OLD_IMG, img_name)
    after = after.replace(DONOR_SLUG, slug).replace(OLD_IMG, img_name)

    before = sub1(before, r"<title>.*?</title>", f"<title>{esc(c['title'])}</title>", "title")
    before = sub1(before, r'<meta name="description" content="[^"]*" />',
                  f'<meta name="description" content="{attr(c["description"])}" />', "description")
    before = sub1(before, r'<meta property="og:title" content="[^"]*" />',
                  f'<meta property="og:title" content="{attr(c["h1"])}" />', "og:title")
    before = sub1(before, r'<meta property="og:description" content="[^"]*" />',
                  f'<meta property="og:description" content="{attr(c["og_description"])}" />', "og:description")
    before = sub1(before, r'<meta property="og:image:alt" content="[^"]*" />',
                  f'<meta property="og:image:alt" content="{attr(c["hero_alt"])}" />', "og:image:alt")
    before = sub1(before, r'<meta property="article:published_time" content="[^"]*" />',
                  f'<meta property="article:published_time" content="{PUB}" />', "published")
    before = sub1(before, r'<meta property="article:modified_time" content="[^"]*" />',
                  f'<meta property="article:modified_time" content="{MOD}" />', "modified")
    before = sub1(before, r'<meta property="article:section" content="[^"]*" />',
                  f'<meta property="article:section" content="{attr(c["articleSection"])}" />', "section")
    before = sub1(before, r'<meta name="twitter:title" content="[^"]*" />',
                  f'<meta name="twitter:title" content="{attr(c["h1"])}" />', "twitter:title")
    before = sub1(before, r'<meta name="twitter:description" content="[^"]*" />',
                  f'<meta name="twitter:description" content="{attr(c["og_description"])}" />', "twitter:description")
    before = sub1(before, r'<meta name="twitter:image:alt" content="[^"]*" />',
                  f'<meta name="twitter:image:alt" content="{attr(c["hero_alt"])}" />', "twitter:image:alt")
    before = rewrite_jsonld(before, c, tree, slug, img_name)

    out = before + build_main(c, tree, donor_main, img_name) + after
    path = page_path(tree, slug)
    io.open(path, "w", encoding="utf-8", newline="").write(out)
    rel = os.path.relpath(path, SITE_DIR).replace("\\", "/")
    print(f"  wrote {rel:26} title {len(c['title']):>2}  desc {len(c['description']):>3}  "
          f"{len(out):>6} bytes")


if __name__ == "__main__":
    wanted = sys.argv[1:] or list(CITIES)
    for city in wanted:
        if city not in CITIES:
            raise SystemExit(f"unknown city {city!r}; known: {', '.join(CITIES)}")
        missing = [l for l in TREES
                   if not os.path.exists(os.path.join(CONTENT, f"{city}-{l}.json"))]
        if missing:
            raise SystemExit(f"  ! {city}: missing content for {', '.join(missing)}")
        for lang, tree in TREES.items():
            build(city, lang, tree)
    print("done")
