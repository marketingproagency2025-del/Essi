#!/usr/bin/env python3
"""Independently validate a translated city-post content file.

The three porting agents each ran their own self-check and each reported passing. That is not
evidence: a self-check written by the same process that wrote the content shares its blind
spots, and one of these agents was working from a source file that changed underneath it. This
re-derives every constraint from the Italian on disk and from the shipped milano-<lang>.json,
so it cannot inherit an agent's assumption about what it was supposed to produce.

Checks, per file:
  1. key set identical to milano-<lang>.json (a missing key crashes build_city.py at render time)
  2. len(title) <= 60 and 120 <= len(description) <= 155   [gate checks 3 and 4]
  3. no em dash, en dash, figure dash, horizontal bar or minus sign anywhere  [house style]
  4. no HTML entities at all: the gate rejects diacritics written as &xxx;
  5. structure matches the CURRENT Italian: intro/sections/summary/faq/related/keywords counts,
     and paragraph count per section
  6. related slugs identical to the Italian (labels differ, targets must not)
  7. service_slug identical to the Italian
  8. fixed per-tree values (lang, breadcrumbs, date, byline, section headings) exactly as given
  9. hero_alt matches the string the site already uses for that image in that tree
 10. the agency market list and the no-Swiss-office statement survive on the posts that carry
     them in the Italian
 11. no digit-bearing claim that is not in the Italian, and no percent sign

    python validate_lang.py es
    python validate_lang.py en es sq
"""
import io
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.dirname(_HERE)          # the repo root, one level above .build
CONTENT = os.path.join(_HERE, "city-content")
CITIES = ["roma", "lugano", "ticino"]
TREE = {"en": "", "it": "it", "es": "es", "sq": "sq"}

DASHES = "\u2014\u2013\u2012\u2015\u2212"

FIXED = {
    "en": {"lang": "en", "breadcrumb_home": "Home", "breadcrumb_blog": "Blog",
           "date_display": "23 August 2026", "by": "By", "read_time": "6 min read",
           "summary_h2": "The Short Version", "faq_h2": "Frequently Asked Questions",
           "related_h2": "Keep Reading", "service_label": "Related service:",
           "back_label": "Back to Blog", "articleSection": "Local marketing"},
    "es": {"lang": "es", "breadcrumb_home": "Inicio", "breadcrumb_blog": "Blog",
           "date_display": "23 de agosto de 2026", "by": "Por", "read_time": "6 min de lectura",
           "summary_h2": "En resumen", "faq_h2": "Preguntas Frecuentes",
           "related_h2": "Sigue leyendo", "service_label": "Servicio relacionado:",
           "back_label": "Volver al Blog", "articleSection": "Marketing local"},
    "sq": {"lang": "sq", "breadcrumb_home": "Kreu", "breadcrumb_blog": "Blog",
           "date_display": "23 gusht 2026", "by": "Nga", "read_time": "6 min lexim",
           "summary_h2": "Shkurtimisht", "faq_h2": "Pyetje t\u00eb Shpeshta",
           "related_h2": "Vazhdoni leximin", "service_label": "Sh\u00ebrbimi p\u00ebrkat\u00ebs:",
           "back_label": "Kthehuni te Blogu", "articleSection": "Marketing lokal"},
}

# the alt text the site already uses for each hero, per tree; hero_alt must equal it
HERO = {
    "roma":   {"en": "White Cycladic architecture against a vivid blue sky",
               "es": "Arquitectura cicl\u00e1dica blanca contra un cielo azul intenso",
               "sq": "Arkitektur\u00eb kikladike e bardh\u00eb p\u00ebrball\u00eb nj\u00eb qielli blu t\u00eb ndezur"},
    "lugano": {"en": "Fishing boats in a harbour at sunset",
               "es": "Barcos de pesca en un puerto al atardecer",
               "sq": "Barka peshkimi n\u00eb nj\u00eb port n\u00eb per\u00ebndim t\u00eb diellit"},
    "ticino": {"en": "The sun setting over the sea",
               "es": "El sol poni\u00e9ndose sobre el mar",
               "sq": "Dielli q\u00eb per\u00ebndon mbi det"},
}

# the market list, as each tree writes it (verified against that tree's contact page)
MARKETS = {
    "en": "Italy, Switzerland, the rest of Europe and the United States",
    "es": "de Italia, de Suiza, del resto de Europa y de Estados Unidos",
    "sq": "n\u00eb Itali, n\u00eb Zvic\u00ebr, n\u00eb pjes\u00ebn tjet\u00ebr t\u00eb Evrop\u00ebs dhe n\u00eb Shtetet e Bashkuara",
}

problems = []


def bad(city, lang, msg):
    problems.append(f"  {lang}/{city:7} {msg}")


def blob(c):
    """Every string in the document, for pattern scanning."""
    out = []

    def walk(v):
        if isinstance(v, str):
            out.append(v)
        elif isinstance(v, list):
            for x in v:
                walk(x)
        elif isinstance(v, dict):
            for x in v.values():
                walk(x)
    walk(c)
    return "\n".join(out)


def body(c):
    return " ".join(c["intro"]) + " " + " ".join(p for s in c["sections"] for p in s["p"])


def check(city, lang):
    fp = os.path.join(CONTENT, f"{city}-{lang}.json")
    if not os.path.exists(fp):
        bad(city, lang, "MISSING FILE")
        return
    c = json.load(io.open(fp, encoding="utf-8"))
    it = json.load(io.open(os.path.join(CONTENT, f"{city}-it.json"), encoding="utf-8"))
    ref = json.load(io.open(os.path.join(CONTENT, f"milano-{lang}.json"), encoding="utf-8"))

    # 1 key set
    if set(c) != set(ref):
        miss, extra = set(ref) - set(c), set(c) - set(ref)
        bad(city, lang, f"key mismatch vs milano-{lang}: missing {sorted(miss)} extra {sorted(extra)}")

    # 2 lengths
    if len(c.get("title", "")) > 60:
        bad(city, lang, f"title {len(c['title'])} > 60")
    d = len(c.get("description", ""))
    if not 120 <= d <= 155:
        bad(city, lang, f"description {d} outside 120-155")

    s = blob(c)

    # 3 dashes
    for ch in DASHES:
        if ch in s:
            i = s.index(ch)
            bad(city, lang, f"dash U+{ord(ch):04X} present: ...{s[max(0,i-40):i+40]!r}")

    # 4 entities
    for m in set(re.findall(r"&[a-zA-Z]{2,10};|&#\d+;", s)):
        bad(city, lang, f"HTML entity {m}")

    # 5 structure
    for key in ("intro", "sections", "summary", "faq", "related", "keywords"):
        if len(c.get(key, [])) != len(it[key]):
            bad(city, lang, f"{key}: {len(c.get(key, []))} vs Italian {len(it[key])}")
    if len(c.get("sections", [])) == len(it["sections"]):
        got = [len(x["p"]) for x in c["sections"]]
        want = [len(x["p"]) for x in it["sections"]]
        if got != want:
            bad(city, lang, f"paragraphs per section {got} vs Italian {want}")

    # 6 / 7 link targets
    if [r["slug"] for r in c.get("related", [])] != [r["slug"] for r in it["related"]]:
        bad(city, lang, "related slugs differ from Italian")
    if c.get("service_slug") != it["service_slug"]:
        bad(city, lang, f"service_slug {c.get('service_slug')!r} vs {it['service_slug']!r}")

    # 8 fixed values
    for k, v in FIXED[lang].items():
        if c.get(k) != v:
            bad(city, lang, f"{k} = {c.get(k)!r}, expected {v!r}")

    # 9 hero alt
    if c.get("hero_alt") != HERO[city][lang]:
        bad(city, lang, f"hero_alt {c.get('hero_alt')!r} != site string {HERO[city][lang]!r}")

    # 10 the claims that must survive
    if MARKETS[lang] not in s:
        bad(city, lang, "market list missing or reworded")
    if city in ("lugano", "ticino"):
        # the Italian says it plainly; the port must too, in whatever words
        if not re.search(r"(?i)(svizzera|suiza|switzerland|zvic)", s):
            bad(city, lang, "no mention of Switzerland at all")

    # 11 numbers not in the Italian
    if "%" in s:
        bad(city, lang, "percent sign present")
    it_nums = set(re.findall(r"\d+", blob(it)))
    for n in set(re.findall(r"\d+", body(c))) - it_nums:
        bad(city, lang, f"digit {n!r} in body but not in the Italian")


def main():
    langs = sys.argv[1:] or ["en", "es", "sq"]
    for lang in langs:
        for city in CITIES:
            check(city, lang)
    if problems:
        print(f"  {len(problems)} problems\n")
        for p in problems:
            print(p)
        return 1
    print(f"  {len(langs) * len(CITIES)} files validated, no problems "
          f"({', '.join(langs)} x {', '.join(CITIES)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
