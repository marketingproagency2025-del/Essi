#!/usr/bin/env python3
"""Add the Rome, Lugano and Ticino cards to blog.html in all four MarketingPro trees.

THE THREE GO IN AFTER MILAN, NOT ABOVE IT. All four posts carry the same date, so ordering is
an editorial choice rather than a chronological fact, and putting them second, third and fourth
is better on three counts:

  1. Milan is the city the client actually wants to attract, and it is the only one of the four
     carrying a named case study (OFYR Italia).
  2. Milan keeps fetchpriority="high" on its card image, so the LCP element of the blog index
     does not move and no existing <img> tag is touched.
  3. A shift of exactly three preserves every later card's reveal delay mod 3, so no existing
     card needs rewriting either. Inserting above Milan would have shifted Milan itself.

Three things still move with the insertion: the reveal delays cycle 0,1,2 down the grid, exactly
one card image carries fetchpriority (the first), and the ItemList in the page's JSON-LD gains
three ListItems at positions 2, 3 and 4 with everything after them renumbered.

Idempotent: running it twice does not add the cards twice.

    python index_city.py
"""
import io
import json
import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.dirname(_HERE)          # the repo root, one level above .build
CONTENT = os.path.join(_HERE, "city-content")
SITE = "https://www.marketingpro-agency.com"
IMG_W, IMG_H = 1080, 1258
PUB = "2026-08-23"
TREES = {"en": "", "it": "it", "es": "es", "sq": "sq"}
GRID = '<div class="articles articles--blog">'

# order on the index, and the hero each card shows
CITIES = [
    ("roma",   "blog-roma",   "svc-renders-2"),
    ("lugano", "blog-lugano", "svc-web-2"),
    ("ticino", "blog-ticino", "svc-funnel-2"),
]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def attr(s):
    return esc(s).replace('"', "&quot;")


def card(c, tree, slug, img_name):
    """One card, matching the shape the existing cards already have on disk.

    loading="lazy" here rather than fetchpriority: these are not the LCP, Milan is. The
    normalisation pass below re-asserts that invariant over the whole grid anyway.
    """
    root = f"/{tree}" if tree else ""
    img = "../assets/img" if tree else "assets/img"
    return (
        f'          <article class="article-card reveal" data-reveal>\n'
        f'            <a class="article-card__link" href="{root}/{slug}">\n'
        f'              <figure class="article-card__media"><picture>\n'
        f'  <source srcset="{img}/{img_name}.webp" type="image/webp" />\n'
        f'  <img src="{img}/{img_name}.jpg" height="{IMG_H}" width="{IMG_W}" '
        f'alt="{attr(c["hero_alt"])}" loading="lazy" decoding="async" />\n'
        f'</picture></figure>\n'
        f'              <div class="article-card__body">\n'
        f'                <h3 class="article-card__title">{esc(c["h1"])}</h3>\n'
        f'                <p class="article-card__excerpt">{esc(c["card_excerpt"])}</p>\n'
        f'                <p class="article-card__meta"><time datetime="{PUB}">{esc(c["date_display"])}</time>'
        f' \u00b7 {esc(c["read_time"])}</p>\n'
        f'              </div>\n'
        f'            </a>\n'
        f'          </article>'
    )


def renumber_delays(html):
    """Cards cycle data-reveal / delay 1 / delay 2 down the grid."""
    start = html.index(GRID)
    end = html.index("</div>", html.rindex("</article>", start))
    head, body, tail = html[:start], html[start:end], html[end:]
    n = [0]

    def fix(m):
        i = n[0] % 3
        n[0] += 1
        return '<article class="article-card reveal" data-reveal>' if i == 0 else \
               f'<article class="article-card reveal" data-reveal data-reveal-delay="{i}">'

    body = re.sub(r'<article class="article-card reveal" data-reveal(?: data-reveal-delay="\d")?>',
                  fix, body)
    return head + body + tail, n[0]


def normalise_loading(html):
    """The rule from .build/fix-lcp.py: exactly ONE fetchpriority="high" image per index, the
    first card, and that one alone omits loading. Every other card is loading="lazy".

    Re-asserted over the whole grid rather than trusted, because it broke silently once already:
    when the Milan card was prepended, the demoted card lost fetchpriority and never got
    loading="lazy" back, so card 2 loaded eagerly on all four indexes for a while.
    """
    start = html.index(GRID)
    end = html.index("</div>", html.rindex("</article>", start))
    head, body, tail = html[:start], html[start:end], html[end:]
    n = [0]

    def strip_attr(tag, a):
        return re.sub(r'\s+%s="[^"]*"' % a, "", tag)

    def one(m):
        tag = m.group(0)
        i = n[0]
        n[0] += 1
        tag = strip_attr(strip_attr(tag, "fetchpriority"), "loading")
        if i == 0:
            return tag.replace("<img ", '<img fetchpriority="high" ', 1)
        if ' decoding="async"' in tag:
            return tag.replace(' decoding="async"', ' loading="lazy" decoding="async"', 1)
        return tag.replace("<img ", '<img loading="lazy" ', 1)

    body = re.sub(r"<img\b[^>]*>", one, body)
    return head + body + tail


def collapse_lang_arrays(s):
    def fix(m):
        items = re.findall(r'"([^"]*)"', m.group(2))
        return '"%s": [%s]' % (m.group(1), ", ".join('"%s"' % i for i in items))
    return re.sub(r'"(inLanguage|availableLanguage)":\s*\[([^\]]*)\]', fix, s)


def add_itemlist(html, specs, tree):
    """Three ListItems straight after Milan's, then renumber the whole list."""
    tag = '<script type="application/ld+json">'
    i = html.index(tag) + len(tag)
    j = html.index("</script>", i)
    graph = json.loads(html[i:j])
    new_urls = {(f"{SITE}/{tree}/{s}" if tree else f"{SITE}/{s}") for _c, s, _g in specs}

    for node in graph["@graph"]:
        if node.get("@type") != "ItemList":
            continue
        items = [e for e in node["itemListElement"] if e["item"].get("url") not in new_urls]
        fresh = []
        for c, slug, img_name in specs:
            url = f"{SITE}/{tree}/{slug}" if tree else f"{SITE}/{slug}"
            fresh.append({
                "@type": "ListItem",
                "position": 0,
                "item": {
                    "@type": "BlogPosting",
                    "headline": c["h1"],
                    "url": url,
                    "image": f"{SITE}/assets/img/{img_name}.jpg",
                    "datePublished": PUB,
                    "inLanguage": c["lang"],
                    "author": {"@id": f"{SITE}/about#author"},
                    "publisher": {"@id": f"{SITE}/#organization"},
                },
            })
        items[1:1] = fresh          # after Milan, which stays position 1
        for pos, e in enumerate(items, 1):
            e["position"] = pos
        node["itemListElement"] = items
        if "numberOfItems" in node:
            node["numberOfItems"] = len(items)

    body = collapse_lang_arrays(json.dumps(graph, ensure_ascii=False, indent=2)).replace("\n", "\n  ")
    return html[:i] + "\n  " + body + "\n  " + html[j:]


def run(lang, tree):
    path = os.path.join(SITE_DIR, tree, "blog.html") if tree \
        else os.path.join(SITE_DIR, "blog.html")
    specs = []
    for city, slug, img_name in CITIES:
        c = json.load(io.open(os.path.join(CONTENT, f"{city}-{lang}.json"), encoding="utf-8"))
        specs.append((c, slug, img_name))

    html = io.open(path, encoding="utf-8", newline="").read()

    added = []
    for c, slug, img_name in specs:
        href = f'href="/{tree}/{slug}"' if tree else f'href="/{slug}"'
        if href in html:
            continue
        added.append((c, slug, img_name))

    if added:
        # straight after the first card, so Milan keeps position 1 and the LCP image
        at = html.index("</article>", html.index(GRID)) + len("</article>")
        block = "\n\n" + "\n\n".join(card(c, tree, s, g) for c, s, g in added)
        html = html[:at] + block + html[at:]

    html, n = renumber_delays(html)
    html = normalise_loading(html)
    html = add_itemlist(html, specs, tree)
    io.open(path, "w", encoding="utf-8", newline="").write(html)

    rel = os.path.relpath(path, SITE_DIR).replace("\\", "/")
    print(f"  {rel:16} {n} cards total, {len(added)} added"
          f"{'' if added else ' (already present, order refreshed)'}")


if __name__ == "__main__":
    for lang, tree in TREES.items():
        run(lang, tree)
    print("done")
