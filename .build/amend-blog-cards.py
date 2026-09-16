#!/usr/bin/env python3
"""Point a blog index card at its article's current hero, without rebuilding the page.

gen-blog-index.py CANNOT do this. run() at :317 collects the cards that already
exist and only calls build_card() for slugs that have none (:331-335), so a hero
that changes after a card was built is never picked up. Three further reasons not
to delete the card and let it rebuild:

  - build_card() takes the excerpt from the target page's meta description
    (:166), which silently overwrites hand-written card copy nobody asked to
    change.
  - reindent() at :201-210 shifts every line with 10+ spaces of lead right by 4,
    so one run produces a ~92-card whitespace diff per tree and buries the real
    change.
  - a rebuilt card lands at 16 spaces of indent beside 52-space neighbours.

What this does instead: reads src, srcset, width, height and alt back off that
tree's already-updated hero page, exactly as build_card does, and rewrites only
those five things inside the one matching card.

Two invariants it protects by NOT participating in them:

  fetchpriority / loading / data-reveal-delay are never touched, so the single
  fetchpriority="high" stays on whichever card is first in DOM order and the LCP
  hint does not move.

  the ItemList "image" is patched by a regex anchored on the preceding "url", so
  the @type -> headline -> url -> image key order survives. Check 14 in
  verify-langs.ps1:375 matches ItemList entries with a literal regex over that
  order; reorder the keys and it matches zero items and PASSES VACUOUSLY, which
  is worse than failing.

    python .build/amend-blog-cards.py blog-social-media article-1
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
TREES = {"en": "", "it": "it", "es": "es", "sq": "sq"}
SITE_URL = "https://www.marketingpro-agency.com"

# Index pages that carry article cards. blog.html holds 23; services.html holds 2,
# for article-1 and article-2, and no script maintains those at all.
INDEX_PAGES = ["blog.html", "services.html"]


def hero_of(tree, slug):
    """src basename, webp basename, width, height and alt from the article's hero."""
    fp = os.path.join(SITE, tree, slug + ".html") if tree \
        else os.path.join(SITE, slug + ".html")
    s = io.open(fp, encoding="utf-8", newline="").read()
    main = s[s.index("<main"):s.index("</main>")]
    pic = re.search(r"<picture>(.*?)</picture>", main, re.S)
    if not pic:
        raise SystemExit("  ! %s: no <picture> in <main>" % slug)
    block = pic.group(1)

    def grab(pattern, label):
        m = re.search(pattern, block)
        if not m:
            raise SystemExit("  ! %s: no %s in the hero picture" % (slug, label))
        return m.group(1)

    return {
        "webp": os.path.basename(grab(r'srcset="([^"]+)"', "srcset")),
        "jpg": os.path.basename(grab(r'<img[^>]*\ssrc="([^"]+)"', "img src")),
        "w": grab(r'<img[^>]*\swidth="(\d+)"', "width"),
        "h": grab(r'<img[^>]*\sheight="(\d+)"', "height"),
        "alt": grab(r'<img[^>]*\salt="([^"]*)"', "alt"),
    }


def amend_card(page, tree, slug, hero):
    """Rewrite the five image attributes inside the one card linking to slug."""
    prefix = "../assets/img/" if tree else "assets/img/"
    cards = list(re.finditer(r"<article class=\"article-card[^\"]*\"[^>]*>.*?</article>",
                             page, re.S))
    hits = [m for m in cards
            if re.search(r'article-card__link" href="[^"]*/%s"' % re.escape(slug), m.group(0))]
    if len(hits) != 1:
        return page, "card for %s matched %d times" % (slug, len(hits))

    m = hits[0]
    card = m.group(0)
    new = card
    new = re.sub(r'srcset="[^"]*"', 'srcset="%s%s"' % (prefix, hero["webp"]), new, count=1)
    new = re.sub(r'(<img[^>]*\s)src="[^"]*"',
                 lambda x: x.group(1) + 'src="%s%s"' % (prefix, hero["jpg"]), new, count=1)
    new = re.sub(r'(<img[^>]*\s)height="\d+"',
                 lambda x: x.group(1) + 'height="%s"' % hero["h"], new, count=1)
    new = re.sub(r'(<img[^>]*\s)width="\d+"',
                 lambda x: x.group(1) + 'width="%s"' % hero["w"], new, count=1)
    new = re.sub(r'(<img[^>]*\s)alt="[^"]*"',
                 lambda x: x.group(1) + 'alt="%s"' % hero["alt"], new, count=1)
    return page[:m.start()] + new + page[m.end():], None


def amend_itemlist(page, tree, slug, hero):
    """Repoint the ItemList image, keeping the key order check 14 depends on."""
    url = "%s/%s%s" % (SITE_URL, (tree + "/") if tree else "", slug)
    pat = r'("url": "%s",\s*\n\s*"image": ")[^"]*(")' % re.escape(url)
    out, n = re.subn(pat, lambda x: x.group(1) + "%s/assets/img/%s" % (SITE_URL, hero["jpg"])
                     + x.group(2), page, count=1)
    return out, (None if n == 1 else "ItemList entry for %s matched %d times" % (slug, n))


def main():
    slugs = sys.argv[1:]
    if not slugs:
        raise SystemExit("usage: amend-blog-cards.py <slug> [<slug> ...]")

    plan, bad, touched = {}, [], 0
    for lang, tree in TREES.items():
        for index in INDEX_PAGES:
            fp = os.path.join(SITE, tree, index) if tree else os.path.join(SITE, index)
            rel = os.path.relpath(fp, SITE)
            page = plan.get(fp) or io.open(fp, encoding="utf-8", newline="").read()
            changed = False
            for slug in slugs:
                # Skip an index that has no CARD for this slug. Checking for the slug
                # anywhere is not enough: services.html links to blog posts in its body,
                # which is a link, not a card.
                if not re.search(r'article-card__link" href="[^"]*/%s"' % re.escape(slug), page):
                    continue
                hero = hero_of(tree, slug)
                page, err = amend_card(page, tree, slug, hero)
                if err:
                    bad.append("%s: %s" % (rel, err))
                    continue
                page, err = amend_itemlist(page, tree, slug, hero)
                if err:
                    # services.html has cards but no ItemList; only blog.html must have one.
                    if index == "blog.html":
                        bad.append("%s: %s" % (rel, err))
                changed = True
                touched += 1
            if changed:
                plan[fp] = page

    if bad:
        print("ABORTED, nothing written:")
        for b in bad:
            print("  " + b)
        return 1

    for fp, page in plan.items():
        io.open(fp, "w", encoding="utf-8", newline="").write(page)
        print("  wrote %s" % os.path.relpath(fp, SITE))
    print("done, %d cards amended across %d files" % (touched, len(plan)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
