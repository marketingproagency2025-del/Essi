#!/usr/bin/env python3
"""Register blog-roma, blog-lugano and blog-ticino with every hardcoded slug list.

Discovery on this site is explicit, not by glob: the sitemap, the parity gate, the feed, llms.txt
and the translation status each name their pages. A post missing from any one of them is broken
in a different way, and only some of those ways fail the gate:

  .build/lib-chrome.ps1   $PAGES      drives BOTH verify-langs.ps1 and the sitemap generator
                          $PRIORITY   sitemap priority, 0.7 to match the other guides
  .build/gen-feed.py      SLUGS       or the post never enters feed.xml
  .build/gen-llms.py      GUIDES      or gate check 21 fails
  translation-status.json _slugs      or gate check 1 (bidirectional parity) fails
                          translated  per language, or the page counts as not shipped

register_milano.py only knew about the last three. lib-chrome.ps1 was a fourth list nobody had
noticed, and the gate caught it. It is handled here.

holdback stays {} on purpose: the client's standing instruction is that all four languages go
live together, and per .build/cutover.md emptying holdback IS the act of publishing.

Idempotent.

    python register_city.py
"""
import io
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.dirname(_HERE)          # the repo root, one level above .build
CONTENT = os.path.join(_HERE, "city-content")
SLUGS = ["blog-roma", "blog-lugano", "blog-ticino"]
AFTER = "blog-milano"          # keep the city guides together, in publication order
LANGS = ["it", "es", "sq"]     # 'translated' has no 'en' key: English is the source tree


def patch_py_list(path, label):
    """Insert after AFTER inside a python list literal. The trailing comma is not optional:
    adjacent string literals in a python list silently concatenate without it, which is exactly
    how 'blog-milanoblog-sales-funnel' got shipped once."""
    p = os.path.join(SITE_DIR, path)
    s = io.open(p, encoding="utf-8", newline="").read()
    have = [g for g in SLUGS if f"'{g}'" in s]
    if len(have) == len(SLUGS):
        print(f"  {path:26} already lists all three")
        return
    if have:
        raise SystemExit(f"  ! {path}: partially registered ({have}); fix by hand")
    marker = f"'{AFTER}',"
    if s.count(marker) != 1:
        raise SystemExit(f"  ! {path}: found {s.count(marker)} copies of {marker!r}, expected 1")
    s = s.replace(marker, marker + " " + " ".join(f"'{g}'," for g in SLUGS), 1)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print(f"  {path:26} + {', '.join(SLUGS)} ({label})")


def patch_ps1():
    p = os.path.join(SITE_DIR, ".build", "lib-chrome.ps1")
    s = io.open(p, encoding="utf-8", newline="").read()
    if all(f"'{g}'" in s for g in SLUGS):
        print("  .build/lib-chrome.ps1      already lists all three")
        return

    pages_marker = f"  '{AFTER}',\n"
    if s.count(pages_marker) != 1:
        raise SystemExit(f"  ! lib-chrome.ps1: $PAGES marker not unique")
    s = s.replace(pages_marker,
                  pages_marker + "  " + " ".join(f"'{g}'," for g in SLUGS) + "\n", 1)

    prio_marker = f"'{AFTER}' = '0.7'"
    if s.count(prio_marker) != 1:
        raise SystemExit(f"  ! lib-chrome.ps1: $PRIORITY marker not unique")
    s = s.replace(prio_marker,
                  prio_marker + "\n  " + "; ".join(f"'{g}' = '0.7'" for g in SLUGS), 1)

    # the comment states the count; it is load-bearing for the next person, not for the code
    s = s.replace("# The 25 page slugs,", "# The 28 page slugs,", 1)

    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print(f"  .build/lib-chrome.ps1      + {', '.join(SLUGS)} ($PAGES and $PRIORITY, 0.7)")


def patch_status():
    p = os.path.join(SITE_DIR, ".build", "translation-status.json")
    d = json.load(io.open(p, encoding="utf-8"))
    changed = []

    for g in SLUGS:
        if g not in d["_slugs"]:
            prev = SLUGS[SLUGS.index(g) - 1] if SLUGS.index(g) else AFTER
            d["_slugs"].insert(d["_slugs"].index(prev) + 1, g)
            changed.append(f"_slugs/{g}")

    for lang in LANGS:
        lst = d["translated"].get(lang)
        if lst is None:
            continue
        for g in SLUGS:
            if g in lst:
                continue
            prev = SLUGS[SLUGS.index(g) - 1] if SLUGS.index(g) else AFTER
            lst.insert(lst.index(prev) + 1 if prev in lst else len(lst), g)
            changed.append(f"{lang}/{g}")

    if not changed:
        print("  translation-status.json    already current")
        return
    io.open(p, "w", encoding="utf-8", newline="\n").write(
        json.dumps(d, ensure_ascii=False, indent=2) + "\n")
    print(f"  translation-status.json    {len(changed)} insertions "
          f"({len(d['_slugs'])} slugs x 4 trees = {len(d['_slugs']) * 4} pages)")
    print(f"  holdback stays {d['holdback']} (client asked for all languages live)")


if __name__ == "__main__":
    patch_ps1()
    patch_py_list(".build/gen-feed.py", "feed.xml")
    patch_py_list(".build/gen-llms.py", "llms.txt")
    patch_status()
    print("done")
