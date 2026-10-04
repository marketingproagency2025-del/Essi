#!/usr/bin/env python3
"""Register services-lead-generation with every hardcoded slug list.

Same job and same reasoning as register-ai-search.py: discovery on this site is explicit, not by
glob, and a page missing from any one of these lists is broken in a different way, only some of
which fail the gate.

A SERVICE page joins four lists, not the five an answer post joins:

  .build/lib-chrome.ps1        $PAGES         drives BOTH verify-langs.ps1 and the sitemap
                               $PRIORITY      0.8, to match the other eight service pages
  .build/gen-llms.py           SERVICES       or the page never appears in llms.txt
                               SERVICE_GUIDE  which guide explains it, stated explicitly
  .build/translation-status.json _slugs       or gate check 1 (parity) fails
                               translated     per language, or the page counts as not shipped

NOT gen-feed.py. That file carries blog guides only; feed.xml is the blog's feed and a service
page has no business in it.

SERVICE_GUIDE pairs this page with blog-lead-quality. That mapping is written out rather than
derived, for the reason gen-llms.py records in its own comment: a positional zip once paired the
funnel service with the Milan city guide and dropped another entry entirely, and it shipped.

Idempotent.

    python .build/register-lead-generation.py
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
SLUG = "services-lead-generation"
GUIDE = "blog-lead-quality"
AFTER = "services-sales-funnel"   # keeps it beside its nearest sibling in every list
LANGS = ["it", "es", "sq"]        # 'translated' has no 'en' key: English is the source tree


def patch_lib_chrome():
    p = os.path.join(HERE, "lib-chrome.ps1")
    s = io.open(p, encoding="utf-8", newline="").read()
    if f"'{SLUG}'" in s:
        print("  lib-chrome.ps1            already lists it")
        return
    pages = f"'{AFTER}',"
    if s.count(pages) != 1:
        raise SystemExit(f"  ! lib-chrome.ps1: {pages!r} appears {s.count(pages)} times, expected 1")
    s = s.replace(pages, f"'{AFTER}', '{SLUG}',", 1)

    prio = f"'{AFTER}' = '0.8'"
    if s.count(prio) != 1:
        raise SystemExit(f"  ! lib-chrome.ps1: {prio!r} appears {s.count(prio)} times, expected 1")
    s = s.replace(prio, prio + f"; '{SLUG}' = '0.8'", 1)

    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print(f"  lib-chrome.ps1            + {SLUG} ($PAGES, $PRIORITY 0.8)")


def patch_gen_llms():
    p = os.path.join(HERE, "gen-llms.py")
    s = io.open(p, encoding="utf-8", newline="").read()
    if f"'{SLUG}'" in s:
        print("  gen-llms.py               already lists it")
        return

    # SERVICES: the trailing comma matters. Adjacent string literals in a python list
    # concatenate silently without one, which is how a doubled slug shipped once.
    marker = f"'{AFTER}',"
    if s.count(marker) != 1:
        raise SystemExit(f"  ! gen-llms.py: {marker!r} appears {s.count(marker)} times, expected 1")
    s = s.replace(marker, f"{marker} '{SLUG}',", 1)

    guide_marker = f"'{AFTER}': 'blog-sales-funnel',"
    if s.count(guide_marker) != 1:
        raise SystemExit("  ! gen-llms.py: SERVICE_GUIDE marker not unique")
    s = s.replace(guide_marker, guide_marker + f"\n    '{SLUG}': '{GUIDE}',", 1)

    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print(f"  gen-llms.py               + {SLUG} (SERVICES, SERVICE_GUIDE -> {GUIDE})")


def patch_status():
    p = os.path.join(HERE, "translation-status.json")
    s = io.open(p, encoding="utf-8", newline="").read()
    d = json.loads(s)
    changed = False

    if SLUG not in d["_slugs"]:
        i = d["_slugs"].index(AFTER)
        d["_slugs"].insert(i + 1, SLUG)
        changed = True
    for lang in LANGS:
        lst = d["translated"][lang]
        if SLUG not in lst:
            if AFTER in lst:
                lst.insert(lst.index(AFTER) + 1, SLUG)
            else:
                lst.append(SLUG)
            changed = True

    if not changed:
        print("  translation-status.json   already lists it")
        return
    io.open(p, "w", encoding="utf-8", newline="\n").write(
        json.dumps(d, ensure_ascii=False, indent=2) + "\n")
    print(f"  translation-status.json   + {SLUG} (_slugs, translated x{len(LANGS)})")


def main():
    patch_lib_chrome()
    patch_gen_llms()
    patch_status()
    print("done. now: gen-llms.py, then the gate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
