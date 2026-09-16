#!/usr/bin/env python3
"""Promote three unused masters in originals/ to blog heroes.

These three were already on the machine and are better matched to their posts
than what those posts carry:

  post-in-house-or-agency  an agency office behind glass, lit CREATIVE DEPARTMENT
                           sign, people at desks. The post asks "The Question Is
                           Not Who Posts. It Is Who Answers." A Rika shop sign was
                           illustrating it, which is a different subject entirely.
  post-social-media        a hand holding a phone showing a brand community page.
                           The post is "Turning Followers into Loyal Customers".
  post-article-1           a hand-lettered "Marketing Strategy" note on a bench.
                           The post is "Marketing That Works as One System".

CROPPING IS NOT COSMETIC HERE. style.css:1141-1147 renders the blog card at
aspect-ratio 16/9 with object-fit: cover, and :1188-1194 renders the hero at
max-height 460px inside a 1200px container, about 2.4:1. Both crop from the
centre, so only the middle horizontal band of a hero is ever seen.

Each file below was opened and looked at before a crop was chosen:

  1567080185975  the storefront and the sign occupy the TOP of a square frame and
                 the lower 40 percent is bare floor tile. Left alone, the hero band
                 would be mostly floor. Cropped to the top 650px, which puts the
                 sign and the studio in the middle of what survives.
  1585592049294  1212x720, subject fills the frame, already near 16:9. Untouched.
  1533750349088  the paper sits dead centre with only a strip of empty bench below.
                 The centre band already lands on the lettering. Untouched.

New filenames rather than overwriting: every existing blog hero is also in use on
services.html, index.html or portfolio.html, and /assets/img/* is served with
max-age 2592000, so replacing bytes in place would leave a month of stale cache.

    python .build/make-post-heroes.py
    python .build/gen-webp.py
"""
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
SRC = os.path.join(SITE, "originals")
DST = os.path.join(SITE, "assets", "img")

# name -> (master, crop box or None)
JOBS = {
    "post-in-house-or-agency": ("photo-1567080185975-88eedc2b273a.jpg", (0, 0, 1080, 650)),
    "post-social-media": ("photo-1585592049294-8f466326930a.jpg", None),
    "post-article-1": ("photo-1533750349088-cd871a92f312.jpg", None),
}


def main():
    force = "--force" in sys.argv
    for name, (master, box) in JOBS.items():
        src = os.path.join(SRC, master)
        out = os.path.join(DST, name + ".jpg")
        if not os.path.exists(src):
            print("  MISSING master %s" % master)
            return 1
        if os.path.exists(out) and not force:
            print("  exists, skipping %s.jpg (use --force)" % name)
            continue
        im = Image.open(src)
        before = im.size
        if box:
            im = im.crop(box)
        im.convert("RGB").save(out, "JPEG", quality=82, optimize=True, progressive=True)
        kb = os.path.getsize(out) / 1024.0
        print("  %-26s %s -> %s  %6.1f KB%s"
              % (name + ".jpg", "x".join(map(str, before)),
                 "x".join(map(str, im.size)), kb,
                 "   OVER 220 KB" if kb > 220 else ""))
    print("done. run gen-webp.py next; the webp sibling is required by gate check 6")
    return 0


if __name__ == "__main__":
    sys.exit(main())
