#!/usr/bin/env python3
"""Register blog-riccione-office with every hardcoded slug list.

Same job and same lists as register-ai-search.py, which says why each one matters. The one
difference: this is a news post, so it joins the two articles rather than the answer posts. It
goes BEFORE article-1, newest first, the order the "articles" group on blog.html uses.

  .build/lib-chrome.ps1   $PAGES      drives BOTH verify-langs.ps1 and the sitemap generator
                          $PRIORITY   sitemap priority, 0.5 to match the two articles
  .build/gen-feed.py      SLUGS       or the post never enters feed.xml
  .build/gen-llms.py      ARTICLES    or gate check 21 fails
  translation-status.json _slugs      or gate check 1 (bidirectional parity) fails
                          translated  per language, or the page counts as not shipped

The card on blog.html is gen-blog-index.py's job: "articles" in its GROUPS lists the slug.

holdback stays {} on purpose: the client's standing instruction is that all four languages go
live together.

Idempotent.

    python .build/register-riccione-office.py
"""
import io
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.dirname(_HERE)
SLUG = "blog-riccione-office"
BEFORE = "article-1"
LANGS = ["it", "es", "sq"]     # 'translated' has no 'en' key: English is the source tree


def patch_py_list(path, label):
    """Insert before BEFORE inside a python list literal, with its trailing comma: adjacent
    string literals in a python list silently concatenate without one."""
    p = os.path.join(SITE_DIR, path)
    s = io.open(p, encoding="utf-8", newline="").read()
    if f"'{SLUG}'" in s:
        print(f"  {path:26} already lists it")
        return
    marker = f"'{BEFORE}',"
    if s.count(marker) != 1:
        raise SystemExit(f"  ! {path}: found {s.count(marker)} copies of {marker!r}, expected 1")
    s = s.replace(marker, f"'{SLUG}', " + marker, 1)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print(f"  {path:26} + {SLUG} ({label})")


def patch_ps1():
    p = os.path.join(SITE_DIR, ".build", "lib-chrome.ps1")
    s = io.open(p, encoding="utf-8", newline="").read()
    if f"'{SLUG}'" in s:
        print("  .build/lib-chrome.ps1      already lists it")
        return

    pages_marker = f"  '{BEFORE}', "
    if s.count(pages_marker) != 1:
        raise SystemExit("  ! lib-chrome.ps1: $PAGES marker not unique")
    s = s.replace(pages_marker, f"  '{SLUG}', '{BEFORE}', ", 1)

    prio_marker = f"'{BEFORE}' = '0.5'"
    if s.count(prio_marker) != 1:
        raise SystemExit("  ! lib-chrome.ps1: $PRIORITY marker not unique")
    s = s.replace(prio_marker, f"'{SLUG}' = '0.5'; " + prio_marker, 1)

    # the comment states the count; it read 38 while the list held 39
    s = s.replace("# The 38 page slugs,", "# The 40 page slugs,", 1)

    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print(f"  .build/lib-chrome.ps1      + {SLUG} ($PAGES and $PRIORITY, 0.5)")


def patch_status():
    p = os.path.join(SITE_DIR, ".build", "translation-status.json")
    d = json.load(io.open(p, encoding="utf-8"))
    changed = []

    if SLUG not in d["_slugs"]:
        d["_slugs"].insert(d["_slugs"].index(BEFORE), SLUG)
        changed.append("_slugs")

    for lang in LANGS:
        lst = d["translated"].get(lang)
        if lst is None or SLUG in lst:
            continue
        lst.insert(lst.index(BEFORE) if BEFORE in lst else len(lst), SLUG)
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
