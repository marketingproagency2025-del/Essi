#!/usr/bin/env python3
"""Build a decision post in all four trees, reusing gen-city-guide.py as the engine.

These four posts are structurally identical to a city guide: same donor (blog-seo), same head
rewrite, same JSON-LD graph, same <main> skeleton. Only the content differs. So this does NOT
fork gen-city-guide.py; it loads it and rebinds the handful of module globals that describe
WHICH post is being built. Any fix to the engine, and there have been several (the inherited
BlogPosting.about pointing at #service-seo, the collapsed inLanguage arrays, the escaping hole
in para()), lands on both families at once.

Loaded via importlib because the filename has a dash in it and cannot be imported by name. The
engine's work is all under `if __name__ == "__main__"`, so exec_module() defines without running.

WHAT DIFFERS FROM A CITY GUIDE, and why each is a rebind rather than an argument:

  CONTENT      answer-content/ rather than city-content/, so the two families cannot collide on
               a name and verify-city-content.py keeps validating exactly its own set.
  CITIES       the slug and hero per post. The engine only ever reads .slug and .img from it.
  IMG_W/IMG_H  750x1000, not the 1080x1258 every stock hero uses. These four heroes are the
               client's own Rika showroom photographs, which is why the dimensions move, and
               why the check below refuses to run if they ever stop being 750x1000.
  PUB/MOD      publication date of this batch.

    python .build/gen-answer-post.py                     # all four, all four languages
    python .build/gen-answer-post.py lead-quality        # one post
"""
import importlib.util
import io
import os
import struct
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))


def _engine():
    path = os.path.join(_HERE, "gen-city-guide.py")
    spec = importlib.util.spec_from_file_location("gen_city_guide", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


g = _engine()

# Heroes are the Rika Premium Store photographs the site already publishes on the portfolio,
# not stock. That is deliberate: these four posts are about getting a real business in front of
# real buyers, and the portfolio copy for Rika already names "the details that actually sell a
# stove in person". Each alt string in the content files is the one the site ALREADY uses for
# that image in that tree, copied rather than re-invented, so no page describes a photo twice
# in two different ways.
# Batch one, the decision posts. Heroes are the client's own Rika Premium Store photographs.
# Batch two, the trade verticals. Heroes are chosen for what they actually show: Fly System
# supplies outdoor systems, so the pergola terrace is the subject rather than decoration, and
# rika-fire is the exact product the stove post is about.
#
# WIDTH AND HEIGHT ARE PER POST, not per batch. They were one pair of module constants while
# every hero happened to be 750x1000; the verticals broke that (768x761 and 750x1000 in the
# same batch) and a single constant would have written the wrong dimensions into three pages.
# The numbers are a promise to the browser about the box to reserve, so check_heroes() measures
# every file and refuses to run if one disagrees.
POSTS = {
    "boost-or-campaign":  {"slug": "blog-boost-or-campaign",  "img": "rika-stove",   "w": 750, "h": 1000},
    "lead-quality":       {"slug": "blog-lead-quality",       "img": "rika-facade",  "w": 750, "h": 1000},
    "in-house-or-agency": {"slug": "blog-in-house-or-agency", "img": "rika-store",   "w": 750, "h": 1000},
    "showrooms":          {"slug": "blog-showrooms",          "img": "rika-range",   "w": 750, "h": 1000},
    "windows-and-doors":  {"slug": "blog-windows-and-doors",  "img": "solutions-3",  "w": 768, "h": 698},
    "stoves-and-heating": {"slug": "blog-stoves-and-heating", "img": "rika-fire",    "w": 750, "h": 1000},
    "builders":           {"slug": "blog-builders",           "img": "solutions-4",  "w": 768, "h": 761},
    "restaurants":        {"slug": "blog-restaurants",        "img": "solutions-6",  "w": 768, "h": 761},
}

PUB = MOD = "2026-08-29"

g.CONTENT = os.path.join(_HERE, "answer-content")
g.CITIES = POSTS
g.PUB = g.MOD = PUB


def jpeg_size(path):
    """Width and height from the SOF marker. The width/height attributes this script writes into
    every <img> are a promise about the file on disk; if they are wrong the browser reserves the
    wrong box and the page shifts under the reader. Measured, never assumed."""
    with io.open(path, "rb") as f:
        if f.read(2) != b"\xff\xd8":
            raise SystemExit(f"  ! {path}: not a JPEG")
        while True:
            b = f.read(1)
            while b and b != b"\xff":
                b = f.read(1)
            if not b:
                raise SystemExit(f"  ! {path}: no SOF marker")
            marker = f.read(1)
            while marker == b"\xff":
                marker = f.read(1)
            if marker in (b"\xc0", b"\xc1", b"\xc2", b"\xc3"):
                f.read(3)
                h, w = struct.unpack(">HH", f.read(4))
                return w, h
            length = struct.unpack(">H", f.read(2))[0]
            f.read(length - 2)


def check_heroes():
    for name, post in POSTS.items():
        img = post["img"]
        jpg = os.path.join(g.SITE_DIR, "assets", "img", img + ".jpg")
        webp = os.path.join(g.SITE_DIR, "assets", "img", img + ".webp")
        if not os.path.exists(jpg):
            raise SystemExit(f"  ! {name}: assets/img/{img}.jpg does not exist")
        # the <picture> emits a webp <source> unconditionally; without the sibling every
        # browser that prefers webp gets a 404 and falls back, which is slower than no source
        if not os.path.exists(webp):
            raise SystemExit(f"  ! {name}: assets/img/{img}.webp missing (run gen-webp.py)")
        w, h = jpeg_size(jpg)
        if (w, h) != (post["w"], post["h"]):
            raise SystemExit(f"  ! {name}: {img}.jpg is {w}x{h}, but POSTS declares "
                             f"{post['w']}x{post['h']}, which is what gets written into "
                             f"every tree")


if __name__ == "__main__":
    wanted = sys.argv[1:] or list(POSTS)
    for name in wanted:
        if name not in POSTS:
            raise SystemExit(f"unknown post {name!r}; known: {', '.join(POSTS)}")
    check_heroes()
    for name in wanted:
        missing = [l for l in g.TREES
                   if not os.path.exists(os.path.join(g.CONTENT, f"{name}-{l}.json"))]
        if missing:
            raise SystemExit(f"  ! {name}: missing content for {', '.join(missing)}")
        # rebound per post, not once per batch: the engine reads these as module globals
        # at render time, so they must be correct for THIS post when build() is called
        g.IMG_W, g.IMG_H = POSTS[name]["w"], POSTS[name]["h"]
        for lang, tree in g.TREES.items():
            g.build(name, lang, tree)
    print("done")
