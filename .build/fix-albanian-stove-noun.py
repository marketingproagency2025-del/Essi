#!/usr/bin/env python3
"""One Albanian noun for one product, instead of two.

The site called the same client's product both "stufa" and "soba", sometimes in
the same file: stoves-and-heating-sq.json used "soba" in its body while its own
hero_alt said "stufe". Eleven files used the stufa family and one used soba, so
the outlier moves to the majority rather than the other way round. Both words are
real Albanian; "stufe" is the Italianism and "soba" the native form, and Albanian
retailers selling wood and pellet stoves mostly file them under soba. That is an
argument for a future sweep, not for rewriting eleven files and roughly thirty
image alt strings today. Flipping direction later is one pass over this same list.

The keywords field is deliberately NOT changed. "marketing per instalues sobash"
is a search term, not body copy, and what people type into a search box is allowed
to differ from what the page calls the product. Changing it would be a targeting
decision dressed up as a consistency fix.

    python .build/fix-albanian-stove-noun.py
    python .build/gen-answer-post.py stoves-and-heating ai-search restaurants
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(HERE, "answer-content")

EDITS = {
    "stoves-and-heating-sq.json": [
        ("Shitja e sobave,", "Shitja e stufave,"),
        ("donin një sobë për tri javë",
         "donin një stufë për tri javë"),
        ("një Film për një Sobë", "një Film për një Stufë"),
        ("Rika prodhon soba me dru", "Rika prodhon stufa me dru"),
        ("e shesin një sobë personalisht", "e shesin një stufë personalisht"),
    ],
    "ai-search-sq.json": [
        ("Në soba, ose në pergola", "Në stufa, ose në pergola"),
    ],
    "restaurants-sq.json": [
        ("një sobë dimrin tjetër", "një stufë dimrin tjetër"),
    ],
}


def main():
    plan, bad = [], []
    for rel, edits in EDITS.items():
        fp = os.path.join(CONTENT, rel)
        s = io.open(fp, encoding="utf-8", newline="").read()
        for old, new in edits:
            got = s.count(old)
            if got != 1:
                bad.append("%s: expected 1, found %d: %s" % (rel, got, old[:50]))
                continue
            s = s.replace(old, new)
        try:
            json.loads(s)
        except Exception as e:
            bad.append("%s: no longer valid JSON: %s" % (rel, e))
            continue
        plan.append((fp, rel, s))

    if bad:
        print("ABORTED, nothing written:")
        for b in bad:
            print("  " + b)
        return 1

    for fp, rel, s in plan:
        io.open(fp, "w", encoding="utf-8", newline="").write(s)
        print("  wrote %s" % rel)

    left = 0
    for rel in EDITS:
        s = io.open(os.path.join(CONTENT, rel), encoding="utf-8", newline="").read()
        left += s.lower().count("sob")
    print("done. %d 'sob' occurrences remain, which should be the keywords field only" % left)
    return 0


if __name__ == "__main__":
    sys.exit(main())
