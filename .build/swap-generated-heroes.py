#!/usr/bin/env python3
"""Move four city guides and three answer posts onto photographs of their subject.

What they were carrying, and why it had to change:

  blog-roma    White CYCLADIC architecture. Greek, for a post about Rome.
  blog-lugano  fishing boats at sunset. Lugano is a Swiss lakeside city.
  blog-ticino  a generic sea sunset. Ticino is a landlocked Swiss canton.
  blog-milano  a search analytics dashboard, SHARED with blog-ai-search.
  blog-builders            a whitewashed Greek villa, against a headline about a
                           finished kitchen nobody photographed.
  blog-windows-and-doors   a pergola terrace. Real Fly System work, chosen
                           deliberately once for their outdoor range, but a
                           glazing post should show glazing. Reversible.
  blog-ai-search           the dashboard blog-milano also used.

gen-city-guide.py:27 had IMG_W/IMG_H as MODULE CONSTANTS, true only while all four
city heroes happened to be 1080x1258. They are now per city, rebound in __main__
before the language loop, exactly as gen-answer-post.py:142 already does after the
flat-constant version wrote wrong dimensions into three pages.

ORDER IS THE ONLY PROTECTION ON THE ALT TEXT. verify-answer-content.py check 9
compares hero_alt against the alt the site already uses for that image, found by
scanning the tree. For a post-* name used on one page, that page is the post's
own, written from this spec, so the check is a tautology: it catches a missing
image, never a wrong description. Edit the specs FIRST, generate, then verify.
Every string below was written after rendering the actual visible crop band, not
the full frame, because only the middle band is ever shown.

    python .build/swap-generated-heroes.py
    python .build/gen-city-guide.py
    python .build/gen-answer-post.py builders windows-and-doors ai-search
    python .build/verify-city-content.py ; python .build/verify-answer-content.py
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LANGS = ["en", "it", "es", "sq"]

ALTS = {
    "milano": {
        "en": "The glass and iron vault of the Galleria Vittorio Emanuele II in Milan",
        "it": "La volta in ferro e vetro della Galleria Vittorio Emanuele II a Milano",
        "es": "La bóveda de hierro y cristal de la Galleria Vittorio Emanuele II de Milán",
        "sq": "Kupola prej hekuri dhe xhami e Galleria Vittorio Emanuele II në Milano",
    },
    "roma": {
        "en": "The Pantheon portico in Rome, its columns and inscription above the piazza",
        "it": "Il portico del Pantheon a Roma, con le colonne e l'iscrizione sopra la piazza",
        "es": "El pórtico del Panteón de Roma, con sus columnas y la inscripción sobre la plaza",
        "sq": "Portiku i Panteonit në Romë, me kolonat dhe mbishkrimin mbi sheshin",
    },
    "lugano": {
        "en": "A lakefront palazzo in Lugano, with the wooded slope of Monte Brè behind it",
        "it": "Un palazzo sul lungolago di Lugano, con il pendio boscoso del Monte Brè alle spalle",
        "es": "Un palacio junto al lago en Lugano, con la ladera boscosa del Monte Brè detrás",
        "sq": "Një pallat buzë liqenit në Lugano, me shpatin e pyllëzuar të Monte Brè-së pas",
    },
    "ticino": {
        "en": "The double stone arch of the Ponte dei Salti over the Verzasca river in Ticino",
        "it": "La doppia arcata in pietra del Ponte dei Salti sul fiume Verzasca, in Ticino",
        "es": "El doble arco de piedra del Ponte dei Salti sobre el río Verzasca, en el Tesino",
        "sq": "Harku i dyfishtë prej guri i Ponte dei Salti mbi lumin Verzasca, në Tiçino",
    },
    "builders": {
        "en": "A finished fitted kitchen in a house, daylight from the window over the worktop",
        "it": "Una cucina su misura finita in una casa, con la luce della finestra sul piano di lavoro",
        "es": "Una cocina a medida terminada en una vivienda, con luz natural sobre la encimera",
        "sq": "Një kuzhinë e montuar e përfunduar në një shtëpi, me dritë natyrale mbi banak",
    },
    "windows-and-doors": {
        "en": "A large glazed unit fitted into a concrete opening on a building site",
        "it": "Una grande vetrata montata in un'apertura in cemento in un cantiere",
        "es": "Un gran acristalamiento instalado en un hueco de hormigón en una obra",
        "sq": "Një xhamllëk i madh i montuar në një hapje betoni në një kantier",
    },
    "ai-search": {
        "en": "An AI assistant screen listing example questions a user can ask",
        "it": "La schermata di un assistente AI con alcune domande di esempio",
        "es": "La pantalla de un asistente de IA con ejemplos de preguntas",
        "sq": "Ekrani i një asistenti AI me shembuj pyetjesh",
    },
}

CITIES = ["milano", "roma", "lugano", "ticino"]
POSTS = ["builders", "windows-and-doors", "ai-search"]

# gen-city-guide.py CITIES is already updated in place; these are the other tables.
TABLE_EDITS = [
    ("gen-answer-post.py",
     '"builders":           {"slug": "blog-builders",           "img": "solutions-4",  "w": 768, "h": 761},',
     '"builders":           {"slug": "blog-builders",           "img": "post-builders", "w": 1080, "h": 760},'),
    ("gen-answer-post.py",
     '"windows-and-doors":  {"slug": "blog-windows-and-doors",  "img": "solutions-3",  "w": 768, "h": 698},',
     '"windows-and-doors":  {"slug": "blog-windows-and-doors",  "img": "post-windows-and-doors", "w": 1080, "h": 760},'),
    ("gen-answer-post.py",
     '"img": "svc-seo-2",    "w": 1080, "h": 1258,',
     '"img": "post-ai-search", "w": 1080, "h": 760,'),
    ("verify-answer-content.py", '"builders": "solutions-4"', '"builders": "post-builders"'),
    ("verify-answer-content.py", '"windows-and-doors": "solutions-3"',
     '"windows-and-doors": "post-windows-and-doors"'),
    ("verify-answer-content.py", '"ai-search": "svc-seo-2"', '"ai-search": "post-ai-search"'),
]


def spec_path(name):
    d = "city-content" if name in CITIES else "answer-content"
    return lambda lang: os.path.join(HERE, d, "%s-%s.json" % (name, lang))


def main():
    plan, bad = [], []

    for name in CITIES + POSTS:
        path = spec_path(name)
        for lang in LANGS:
            fp = path(lang)
            rel = os.path.relpath(fp, HERE).replace("\\", "/")
            s = io.open(fp, encoding="utf-8", newline="").read()
            cur = json.loads(s)["hero_alt"]
            old = '"hero_alt": %s' % json.dumps(cur, ensure_ascii=False)
            new = '"hero_alt": %s' % json.dumps(ALTS[name][lang], ensure_ascii=False)
            if s.count(old) != 1:
                bad.append("%s: hero_alt anchor found %d times" % (rel, s.count(old)))
                continue
            s = s.replace(old, new)
            try:
                json.loads(s)
            except Exception as e:
                bad.append("%s: invalid JSON: %s" % (rel, e))
                continue
            plan.append((fp, rel, s))

    # verify-city-content.py keeps its own hardcoded per-city per-language alt table,
    # compared directly at :163. It covers roma, lugano and ticino in en, es and sq only:
    # milano is its structural REFERENCE and Italian is its reference tree, so neither is
    # validated by anything and both were proofread by hand.
    vfp = os.path.join(HERE, "verify-city-content.py")
    vs = io.open(vfp, encoding="utf-8", newline="").read()
    # Rebuilt wholesale rather than patched entry by entry: the table is small and fully
    # determined by ALTS above, so regenerating it cannot drift from what the specs now say.
    block = ["HERO = {"]
    for city in ("roma", "lugano", "ticino"):
        lines = []
        for lang in ("en", "es", "sq"):
            lines.append('"%s": %s' % (lang, json.dumps(ALTS[city][lang], ensure_ascii=False)))
        block.append('    "%s":%s {%s},' % (city, " " * (6 - len(city)), ",\n               ".join(lines)))
    block.append("}")
    new_table = "\n".join(block)
    start = vs.index("HERO = {")
    end = vs.index("\n}", start) + 2
    plan.append((vfp, "verify-city-content.py", vs[:start] + new_table + vs[end:]))

    for fname, old, new in TABLE_EDITS:
        fp = os.path.join(HERE, fname)
        s = next((p[2] for p in plan if p[0] == fp), None)
        if s is None:
            s = io.open(fp, encoding="utf-8", newline="").read()
        if s.count(old) != 1:
            bad.append("%s: expected 1, found %d: %s" % (fname, s.count(old), old[:55]))
            continue
        s = s.replace(old, new)
        plan = [p for p in plan if p[0] != fp] + [(fp, fname, s)]

    if bad:
        print("ABORTED, nothing written:")
        for b in bad:
            print("  " + b)
        return 1

    for fp, rel, s in plan:
        io.open(fp, "w", encoding="utf-8", newline="").write(s)
    print("  wrote %d files (%d specs, 3 tables)" % (len(plan), len(plan) - 3))
    return 0


if __name__ == "__main__":
    sys.exit(main())
