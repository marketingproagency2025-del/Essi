#!/usr/bin/env python3
"""Move blog-in-house-or-agency onto a photograph of an agency.

The post asks "The Question Is Not Who Posts. It Is Who Answers." It was
illustrated with the Rika Premium Store sign, which is a shop sign for a stove
retailer: real client photography, correctly described, and about a different
subject. It stays in use on portfolio.html, so nothing is lost.

ORDER MATTERS AND IS THE ONLY PROTECTION HERE. verify-answer-content.py check 9
compares each spec's hero_alt against the alt the site already uses for that
image in that tree, via site_alt() at :110, which returns the alt of the first
page containing the file. A post-* name is used on exactly one page, so after
regeneration that page is the post's own, written from the spec. The check
therefore becomes a tautology: it can catch a MISSING image, never a wrong alt.

So: edit hero_alt FIRST, then the generator tables, then generate, then verify.
Skip the first step and the page ships the old photo's description against the
new photo with the whole suite green. The four new alt strings below were written
against the actual picture, which was opened and looked at.

    python .build/swap-in-house-hero.py
    python .build/gen-answer-post.py in-house-or-agency
    python .build/verify-answer-content.py
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(HERE, "answer-content")

NEW_ALT = {
    "en": "The glass frontage of a creative studio at street level, with a lit sign and "
          "people working at desks inside",
    "it": "La vetrata di uno studio creativo al piano strada, con l'insegna illuminata e le "
          "persone che lavorano alle scrivanie all'interno",
    "es": "El escaparate acristalado de un estudio creativo a pie de calle, con un rótulo "
          "iluminado y gente trabajando en escritorios dentro",
    "sq": "Fasada prej xhami e një studioje kreative në nivel rruge, me një "
          "tabelë të ndriçuar dhe njerëz që punojnë në "
          "tavolina brenda",
}

OLD_ALT = {
    "en": "The Rika Premium Store sign on the showroom wall",
    "it": "L'insegna Rika Premium Store sulla parete dello showroom",
    "es": "El rótulo de Rika Premium Store en la pared del showroom",
    "sq": "Tabela Rika Premium Store në murin e showroom-it",
}

GEN = os.path.join(HERE, "gen-answer-post.py")
VERIFY = os.path.join(HERE, "verify-answer-content.py")

TABLE_EDITS = [
    (GEN,
     '"in-house-or-agency": {"slug": "blog-in-house-or-agency", "img": "rika-store",   "w": 750, "h": 1000},',
     '"in-house-or-agency": {"slug": "blog-in-house-or-agency", "img": "post-in-house-or-agency", "w": 1080, "h": 650},'),
    (VERIFY,
     '"in-house-or-agency": "rika-store"',
     '"in-house-or-agency": "post-in-house-or-agency"'),
]


def main():
    plan, bad = [], []

    for lang in ("en", "it", "es", "sq"):
        rel = "in-house-or-agency-%s.json" % lang
        fp = os.path.join(CONTENT, rel)
        s = io.open(fp, encoding="utf-8", newline="").read()
        old = json.dumps(OLD_ALT[lang], ensure_ascii=False)
        new = json.dumps(NEW_ALT[lang], ensure_ascii=False)
        # Only the hero_alt occurrence, which is the one preceded by the key.
        key_old = '"hero_alt": %s' % old
        if s.count(key_old) != 1:
            bad.append("%s: hero_alt anchor found %d times" % (rel, s.count(key_old)))
            continue
        s = s.replace(key_old, '"hero_alt": %s' % new)
        try:
            json.loads(s)
        except Exception as e:
            bad.append("%s: invalid JSON: %s" % (rel, e))
            continue
        plan.append((fp, rel, s))

    for fp, old, new in TABLE_EDITS:
        s = io.open(fp, encoding="utf-8", newline="").read()
        if s.count(old) != 1:
            bad.append("%s: expected 1, found %d: %s"
                       % (os.path.basename(fp), s.count(old), old[:60]))
            continue
        plan.append((fp, os.path.basename(fp), s.replace(old, new)))

    if bad:
        print("ABORTED, nothing written:")
        for b in bad:
            print("  " + b)
        return 1

    for fp, rel, s in plan:
        io.open(fp, "w", encoding="utf-8", newline="").write(s)
        print("  wrote %s" % rel)
    print("done. now: gen-answer-post.py in-house-or-agency, then verify-answer-content.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
