#!/usr/bin/env python3
"""Register blog-ai-search with every hardcoded slug list.

Same job and same five lists as register-city-guide.py, which is where the reasoning is written
down: discovery on this site is explicit, not by glob, and a post missing from any one of these
is broken in a different way, only some of which fail the gate.

  .build/lib-chrome.ps1   $PAGES      drives BOTH verify-langs.ps1 and the sitemap generator
                          $PRIORITY   sitemap priority, 0.7 to match the other answer posts
  .build/gen-feed.py      SLUGS       or the post never enters feed.xml
  .build/gen-llms.py      GUIDES      or gate check 21 fails
  translation-status.json _slugs      or gate check 1 (bidirectional parity) fails
                          translated  per language, or the page counts as not shipped

A SIXTH place exists and no script has ever owned it: the cards on blog.html, in all four trees,
with the group count in the heading. register-city-guide.py did not touch it and the previous
batches were carded by hand, so that part is done by add-ai-search-card.py beside this file.

holdback stays {} on purpose: the client's standing instruction is that all four languages go
live together, and per .build/cutover.md emptying holdback IS the act of publishing.

Idempotent.

    python .build/register-ai-search.py
"""
import io
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.dirname(_HERE)
SLUG = "blog-ai-search"
AFTER = "blog-restaurants"     # the last answer post, so the batch stays in publication order
LANGS = ["it", "es", "sq"]     # 'translated' has no 'en' key: English is the source tree


def patch_py_list(path, label):
    """Insert after AFTER inside a python list literal. The trailing comma is not optional:
    adjacent string literals in a python list silently concatenate without it, which is exactly
    how 'blog-milanoblog-sales-funnel' got shipped once."""
    p = os.path.join(SITE_DIR, path)
    s = io.open(p, encoding="utf-8", newline="").read()
    if f"'{SLUG}'" in s:
        print(f"  {path:26} already lists it")
        return
    marker = f"'{AFTER}',"
    if s.count(marker) != 1:
        raise SystemExit(f"  ! {path}: found {s.count(marker)} copies of {marker!r}, expected 1")
    s = s.replace(marker, marker + f" '{SLUG}',", 1)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print(f"  {path:26} + {SLUG} ({label})")


def patch_ps1():
    p = os.path.join(SITE_DIR, ".build", "lib-chrome.ps1")
    s = io.open(p, encoding="utf-8", newline="").read()
    if f"'{SLUG}'" in s:
        print("  .build/lib-chrome.ps1      already lists it")
        return

    pages_marker = f"'{AFTER}',\n"
    if s.count(pages_marker) != 1:
        raise SystemExit("  ! lib-chrome.ps1: $PAGES marker not unique")
    s = s.replace(pages_marker, f"'{AFTER}', '{SLUG}',\n", 1)

    prio_marker = f"'{AFTER}' = '0.7'"
    if s.count(prio_marker) != 1:
        raise SystemExit("  ! lib-chrome.ps1: $PRIORITY marker not unique")
    s = s.replace(prio_marker, prio_marker + f"; '{SLUG}' = '0.7'", 1)

    # the comment states the count; it is load-bearing for the next person, not for the code
    s = s.replace("# The 36 page slugs,", "# The 37 page slugs,", 1)

    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print(f"  .build/lib-chrome.ps1      + {SLUG} ($PAGES and $PRIORITY, 0.7)")


def patch_status():
    p = os.path.join(SITE_DIR, ".build", "translation-status.json")
    d = json.load(io.open(p, encoding="utf-8"))
    changed = []

    if SLUG not in d["_slugs"]:
        d["_slugs"].insert(d["_slugs"].index(AFTER) + 1, SLUG)
        changed.append("_slugs")

    for lang in LANGS:
        lst = d["translated"].get(lang)
        if lst is None or SLUG in lst:
            continue
        lst.insert(lst.index(AFTER) + 1 if AFTER in lst else len(lst), SLUG)
        changed.append(lang)

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
