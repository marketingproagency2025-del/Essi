#!/usr/bin/env python3
"""Register the four answer posts with every hardcoded slug list.

Same job as register-city-guide.py and the same five lists, because discovery on this site is
explicit rather than by glob. What differs is the insertion strategy, and that is why this is a
sibling rather than an import.

register-city-guide.py inserts AFTER a named slug. That worked for the city guides because
'blog-milano' happened to sit alone on its own line in $PAGES. It does not generalise: the
obvious anchor here, 'blog-ticino', appears mid-line as
    'blog-roma', 'blog-lugano', 'blog-ticino',
so a marker of "  'blog-ticino',\\n" matches nothing and patch_ps1 would abort. Rather than
loosen that script's assertions, which are the only thing stopping a silent half-registration,
this one appends to the END of each list against its own explicitly asserted markers.

The five lists, and how each one fails if missed:

  .build/lib-chrome.ps1   $PAGES      drives BOTH verify-langs.ps1 parity and the sitemap
                          $PRIORITY   sitemap priority; 0.7, matching every other guide
  .build/gen-feed.py      SLUGS       or the post never enters feed.xml
  .build/gen-llms.py      GUIDES      or gate check 21 fails
  translation-status.json _slugs      or gate check 1 (bidirectional parity) fails
                          translated  per language, or the page counts as not shipped

holdback stays as it is: the client's standing instruction is that all four languages go live
together, so a post is either finished in all of them or not registered yet.

Idempotent.

    python .build/register-answer-post.py
"""
import io
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.dirname(_HERE)

SLUGS = ["blog-boost-or-campaign", "blog-lead-quality",
         "blog-in-house-or-agency", "blog-showrooms"]
LANGS = ["it", "es", "sq"]      # 'translated' has no 'en' key: English is the source tree
PRIORITY = "0.7"                # same weight as every other guide


def already(text):
    return all(f"'{s}'" in text for s in SLUGS)


def partial(text):
    have = [s for s in SLUGS if f"'{s}'" in text]
    return have if 0 < len(have) < len(SLUGS) else None


def anchored_insert(text, marker, addition, label):
    """Insert immediately after a marker that must occur exactly once.

    The count assertion is the whole value of this helper. A marker that silently matches zero
    times leaves the list unchanged and the script still prints success, which is how a page
    ends up in $PAGES but not in feed.xml.
    """
    if text.count(marker) != 1:
        raise SystemExit(f"  ! {label}: found {text.count(marker)} copies of {marker!r}, "
                         f"expected exactly 1")
    return text.replace(marker, marker + addition, 1)


def patch_py_list(path, marker, label):
    """Append to a python list literal. The trailing comma after each entry is not optional:
    adjacent string literals in a python list silently concatenate without one, which is how
    'blog-milanoblog-sales-funnel' got shipped once."""
    p = os.path.join(SITE_DIR, path)
    s = io.open(p, encoding="utf-8", newline="").read()
    if already(s):
        print(f"  {path:26} already lists all four")
        return
    if partial(s):
        raise SystemExit(f"  ! {path}: partially registered ({partial(s)}); fix by hand")
    s = anchored_insert(s, marker, " " + " ".join(f"'{g}'," for g in SLUGS), path)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print(f"  {path:26} + {len(SLUGS)} slugs ({label})")


def patch_ps1():
    path = ".build/lib-chrome.ps1"
    p = os.path.join(SITE_DIR, path)
    s = io.open(p, encoding="utf-8", newline="").read()
    if already(s):
        print(f"  {path:26} already lists all four")
        return
    if partial(s):
        raise SystemExit(f"  ! {path}: partially registered ({partial(s)}); fix by hand")

    s = anchored_insert(
        s, "  'blog-roma', 'blog-lugano', 'blog-ticino',\n",
        "  " + " ".join(f"'{g}'," for g in SLUGS) + "\n", "$PAGES")
    s = anchored_insert(
        s, "  'blog-roma' = '0.7'; 'blog-lugano' = '0.7'; 'blog-ticino' = '0.7'\n",
        "  " + "; ".join(f"'{g}' = '{PRIORITY}'" for g in SLUGS) + "\n", "$PRIORITY")

    # the comment states the count; it is load-bearing for the next person, not for the code,
    # so it is asserted rather than best-effort replaced
    old, new = "# The 28 page slugs,", "# The 32 page slugs,"
    if s.count(old) != 1:
        raise SystemExit(f"  ! {path}: expected 1 copy of {old!r}, found {s.count(old)}")
    s = s.replace(old, new, 1)

    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print(f"  {path:26} + {len(SLUGS)} slugs ($PAGES and $PRIORITY, {PRIORITY})")


def patch_status():
    path = ".build/translation-status.json"
    p = os.path.join(SITE_DIR, path)
    d = json.load(io.open(p, encoding="utf-8"))
    changed = []

    for g in SLUGS:
        if g not in d["_slugs"]:
            d["_slugs"].append(g)
            changed.append(f"_slugs/{g}")

    for lang in LANGS:
        lst = d["translated"].get(lang)
        if lst is None:
            continue
        for g in SLUGS:
            if g not in lst:
                lst.append(g)
                changed.append(f"{lang}/{g}")

    if not changed:
        print(f"  {path:26} already current")
        return
    io.open(p, "w", encoding="utf-8", newline="\n").write(
        json.dumps(d, ensure_ascii=False, indent=2) + "\n")
    print(f"  {path:26} {len(changed)} insertions "
          f"({len(d['_slugs'])} slugs x 4 trees = {len(d['_slugs']) * 4} pages)")
    print(f"  holdback stays {d['holdback']} (client asked for all languages live)")


if __name__ == "__main__":
    patch_ps1()
    patch_py_list(".build/gen-feed.py", "'blog-ticino',", "feed.xml")
    patch_py_list(".build/gen-llms.py", "'blog-ticino',", "llms.txt")
    patch_status()
    print("done")
