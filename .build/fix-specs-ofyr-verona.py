#!/usr/bin/env python3
"""The same two corrections, in the JSON specs the blog pages are generated from.

Edited as text rather than loaded and re-dumped, so the files keep their existing
formatting and the diff shows only the sentences that actually changed. Every
replacement asserts its count, and the JSON is re-parsed afterwards.

No figure is added or removed by any of these, so the cross-language digit-set
check in verify-answer-content.py stays satisfied.

After this, regenerate:
    python .build/gen-answer-post.py showrooms stoves-and-heating
    python .build/gen-city-guide.py

    python .build/fix-specs-ofyr-verona.py
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# OFYR sells wood-fired barbecues, not outdoor kitchens. The Italian and Spanish
# forms here were the worst of the lot: "cucina da esterno" and "cocina de
# exterior" are word-for-word the OF Outdoorkitchen trade line in the same trees.
OFYR = {
    "en": [("OFYR Italia sells outdoor cooking, a product",
            "OFYR Italia sells wood-fired barbecues, a product"),
           ("for OFYR Italia in outdoor cooking.",
            "for OFYR Italia in wood-fired barbecues.")],
    "it": [("OFYR Italia vende cucina all'aperto, un prodotto",
            "OFYR Italia vende barbecue a legna, un prodotto"),
           ("per OFYR Italia nella cucina da esterno.",
            "per OFYR Italia nei barbecue a legna.")],
    "es": [("OFYR Italia vende cocina al aire libre, un producto",
            "OFYR Italia vende barbacoas de leña, un producto"),
           ("para OFYR Italia en cocina de exterior.",
            "para OFYR Italia en barbacoas de leña.")],
    "sq": [("OFYR Italia shet gatim në natyrë, një produkt",
            "OFYR Italia shet barbekju me dru, një produkt"),
           ("për OFYR Italia në gatimin e jashtëm.",
            "për OFYR Italia në barbekju me dru.")],
}

# The Premium Store is in Verona.
VERONA = {
    "en": ("for its Premium Store:", "for its Premium Store in Verona:"),
    "it": ("per il suo Premium Store:", "per il suo Premium Store di Verona:"),
    "es": ("de su Premium Store:", "de su Premium Store de Verona:"),
    "sq": ("për Premium Store-in e saj:", "për Premium Store-in e saj në Verona:"),
}

LANGS = ["en", "it", "es", "sq"]


def build():
    """Return {relative path: [(old, new), ...]}, one entry per file touched."""
    jobs = {}
    for lang in LANGS:
        jobs["city-content/milano-%s.json" % lang] = [OFYR[lang][0]]
        jobs["answer-content/showrooms-%s.json" % lang] = [VERONA[lang], OFYR[lang][1]]
        jobs["answer-content/stoves-and-heating-%s.json" % lang] = [VERONA[lang]]
    return jobs


def main():
    plan, bad = [], []
    for rel, edits in sorted(build().items()):
        fp = os.path.join(HERE, *rel.split("/"))
        s = io.open(fp, encoding="utf-8", newline="").read()
        for old, new in edits:
            got = s.count(old)
            if got != 1:
                bad.append("%s: expected 1, found %d: %s" % (rel, got, old[:60]))
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
    print("done, %d specs" % len(plan))
    return 0


if __name__ == "__main__":
    sys.exit(main())
