#!/usr/bin/env python3
"""Fetch the nine new blog heroes from Unsplash, cropped by the CDN.

This table IS the provenance record. .build/ is excluded by .assetsignore so it is
never served, like citations.md.

WHY THE CDN DOES THE CROP. images.unsplash.com accepts w/h/fit/crop and returns
exactly the requested size, so there is no resize step and no new Pillow code.
1080x1258 is not an arbitrary pick: fourteen files already in originals/ are that
size, which is the parameter set this site was built with, and it is what
gen-city-guide.py:27 hardcodes as IMG_W/IMG_H for all four city guides.

WHY 1080x1258 MATTERS MORE THAN IT LOOKS. style.css:1141-1147 renders the blog
card at aspect-ratio 16/9 and :1188-1194 renders the hero at max-height 460px in
a 1200px container, both object-fit: cover. On a 1080x1258 source that shows rows
325-932 in the card and rows 404-854 in the hero. Only that band is ever seen, and
every image below was chosen by rendering that band, not by looking at the whole
frame. Several otherwise-good candidates were rejected because the subject sat
above or below it.

LICENCE. A direct CDN fetch is the Unsplash License: free commercial use,
attribution appreciated but not required. Do NOT switch to the Unsplash API for
fetching. Its API Guidelines DO require photographer attribution with utm_source
referral links and a call to /photos/:id/download, obligations this repo does not
meet. The credit strings below are provenance for whoever reads this file, not a
public attribution, and photographer names came from search-page metadata rather
than from the CDN response, so treat them as provenance-grade.

    python .build/fetch-unsplash.py --dry-run
    python .build/fetch-unsplash.py
    python .build/gen-webp.py
"""
import io
import os
import sys
import urllib.request

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
ORIGINALS = os.path.join(SITE, "originals")
IMG = os.path.join(SITE, "assets", "img")

# 1080x760, NOT the 1080x1258 the older heroes use.
#
# The hero renders at max-height 460px in a 1200px container and the card at
# aspect-ratio 16/9, both object-fit: cover. On a 1080x1258 source that means about
# 64 percent of the pixels are encoded, downloaded and then cropped away unseen. The
# card needs 1080x607 and the hero band about 1080x450, so 760 covers both with room
# and costs 40 percent fewer pixels.
#
# It is not vanity. At 1080x1258 these frames came back at 250 to 480 KB of WebP
# against a site whose thirty existing heroes have a MEDIAN of 43 KB and a maximum
# of 120. Dropping unseen pixels fixes that without touching quality, which is the
# right order to do it in: degrade what nobody sees before degrading what everybody
# does. gen-city-guide.py had 1080x1258 as a module constant, so this change is what
# forced IMG_W/IMG_H to become per-city there, the same way gen-answer-post.py:62
# already carries them per post.
W, H = 1080, 760
CDN = "https://images.unsplash.com/%s?w=%d&h=%d&fit=crop&crop=entropy&q=80&fm=jpg"
MASTER = "https://images.unsplash.com/%s?w=2400&q=85&fm=jpg"

PHOTOS = {
    "post-roma": dict(
        id="photo-1614354987493-a010f414d0d1", credit="Gabriella Clare Marino",
        shows="Pantheon portico, the M AGRIPPA inscription reading across the visible band"),
    "post-lugano": dict(
        id="photo-1689746128124-4ba7be467c12", credit="nika tchokhonelidze",
        shows="neoclassical lakefront palazzo, Monte Bre behind, a yellow Swiss PostBus at the "
              "quay. Chosen over a prettier alternative because the PostBus is the one "
              "unambiguous signal that this is Switzerland and not Italy"),
    "post-ticino": dict(
        id="photo-1628922421646-2622d831cabf", credit="Ronnie Schmutz",
        shows="Ponte dei Salti double stone arch at Lavertezzo over carved gneiss, Verzasca"),
    "post-milano": dict(
        id="photo-1617102827928-330322f68809", credit="Federico Di Dio photography",
        shows="Galleria Vittorio Emanuele II axis, barrel vault and dome centred, near empty"),
    "post-builders": dict(
        id="photo-1721614466238-d402fe79800f", credit="Alex Tyson",
        shows="a finished cream shaker kitchen in a real house, garden light through a window, "
              "no people. The post is 'Your Best Salesman Is a Finished Kitchen You Never "
              "Photographed', so it has to read as a completed install, not a showroom set"),
    "post-windows-and-doors": dict(
        id="photo-1707725669477-18feaba381f4", credit="Steffen Lemmerzahl",
        shows="floor-to-ceiling glazed unit in a concrete and CLT opening, site sheeting behind"),
    "post-ai-search": dict(
        id="photo-1675865254433-6ba341f0f00b", credit="Jonathan Kemper",
        shows="an assistant's opening screen, Examples / Capabilities / Limitations, with "
              "sample questions legible. The post is 'A Buyer Asked an Assistant. Your Name "
              "Was Not in the Answer', so a visible question is the subject. Two candidates "
              "were rejected after rendering the band: one had a Cyrillic keyboard and the "
              "words 'Change MotionElements Username' legible across it, an unrelated product "
              "on a client's page; the other's only readable copy was a safety refusal about "
              "cybersecurity and biology. This one is an older UI, which is the lesser cost"),
    "post-catalogues": dict(
        id="photo-1702450899637-a3c160a52916", credit="Tron Le",
        shows="a printed catalogue page held open, carrying a full bleed photograph of a fitted "
              "kitchen. Product photography on the page, which the old stationery shot was not"),
    "post-article-2": dict(
        id="photo-1686061592689-312bbfb5c055", credit="1981 Digital",
        shows="a cohort retention grid, All Users 100 percent falling to 1.4 across week "
              "columns. A literal drop off table for 'Fix the Leaks Before You Spend More'"),
}


# The jpg is only the fallback: the <picture> serves .webp to anything modern, and
# gen-webp.py makes it. So the jpg does NOT need to be squeezed to the last byte,
# and squeezing it is actively harmful. A first pass with a floor of q=55 produced
# jpgs so crushed that gen-webp.py SKIPPED three of them, because WebP at q=80
# came out LARGER than the mangled jpg. A missing .webp sibling fails gate check 6,
# since the <source srcset> would not resolve. Hence a real quality floor.
BUDGET_KB = 220
QUALITY_FLOOR = 72


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


# DO NOT re-encode the downloaded JPEG here. An earlier version did, to force it
# under BUDGET_KB, and it made things worse in a way worth recording: the jpg came
# out of the CDN already compressed, a second pass at q=72 added generation loss,
# and the result was so mangled that WebP could no longer beat it. gen-webp.py then
# SKIPPED three files, because its rule is never to ship a "saving" larger than the
# original. A missing .webp sibling fails gate check 6, since the <source srcset>
# stops resolving. So: the CDN compresses once, the jpg is only ever the fallback,
# and weight is controlled by fetching fewer pixels (see W, H above) and by the
# per-file WebP quality table in gen-webp.py.


def main():
    dry = "--dry-run" in sys.argv
    force = "--force" in sys.argv
    fail = 0

    for name, p in PHOTOS.items():
        out = os.path.join(IMG, name + ".jpg")
        if os.path.exists(out) and not force:
            print("  exists, skipping %s.jpg (use --force)" % name)
            continue

        data = get(CDN % (p["id"], W, H))
        size = Image.open(io.BytesIO(data)).size
        q = None
        ok = size == (W, H)
        print("  %-26s %s  %6.1f KB%s  %s"
              % (name + ".jpg", "x".join(map(str, size)), len(data) / 1024.0,
                 "" if q is None else "  (re-encoded q=%d from %.0f KB)" % (q, len(raw) / 1024.0),
                 "OK" if ok else "*** WRONG SIZE ***"))
        if not ok:
            fail += 1
            continue
        if dry:
            continue

        io.open(out, "wb").write(data)
        master = os.path.join(ORIGINALS, p["id"] + ".jpg")
        if not os.path.exists(master):
            io.open(master, "wb").write(get(MASTER % p["id"]))

    if fail:
        print("\n%d image(s) did not come back at %dx%d. Nothing downstream should run." % (fail, W, H))
        return 1
    print("\ndone%s. next: python .build/gen-webp.py" % (" (dry run, nothing written)" if dry else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
