#!/usr/bin/env python3
"""Independently validate the answer-post content files.

Modelled on verify-city-content.py and for the same reason: a translation self-check written by
whoever produced the translation shares its blind spots. Everything here is re-derived either
from the English on disk or from the site itself, so it cannot inherit an assumption about what
the file was supposed to contain.

The English file is the structural reference. Every constraint that is not about English is
checked against it rather than against a hardcoded expectation, so the reference moving is not
a silent way to weaken the check.

Checks, per file:
  1. key set identical to the English file      (a missing key crashes the generator at render)
  2. len(title) <= 60 and 120 <= len(description) <= 155              [gate checks 3 and 4]
  3. no em dash, en dash, figure dash, horizontal bar or minus sign        [house style]
  4. no HTML entities: the gate rejects diacritics written as &xxx;
  5. structure matches the English: intro / sections / summary / faq / related counts, plus the
     paragraph count inside every section
  6. related slugs identical to the English (labels differ by language, targets must not)
  7. service_slug identical to the English
  8. fixed per-tree values exactly as the city guides already use them
  9. hero_alt equals the string the site ALREADY uses for that image in that tree
 10. every figure in the English body survives into the translation, in that tree's number
     format, and no new figure is invented
 11. related labels equal the target page's real H1 in that tree, once it exists

    python .build/verify-answer-content.py
    python .build/verify-answer-content.py showrooms
"""
import io
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.dirname(_HERE)
CONTENT = os.path.join(_HERE, "answer-content")

POSTS = ["boost-or-campaign", "lead-quality", "in-house-or-agency", "showrooms",
         "windows-and-doors", "stoves-and-heating", "builders", "restaurants"]
TREE = {"en": "", "it": "it", "es": "es", "sq": "sq"}
DASHES = "—–‒―−"

# Lifted verbatim from the shipped city guides so the two families cannot drift apart. Anything
# in here that is wrong is wrong on twenty other pages too, which is the point.
FIXED = {
    "en": {"lang": "en", "breadcrumb_home": "Home", "breadcrumb_blog": "Blog",
           "date_display": "29 August 2026", "by": "By", "read_time": "6 min read",
           "summary_h2": "The Short Version", "faq_h2": "Frequently Asked Questions",
           "related_h2": "Keep Reading", "service_label": "Related service:",
           "back_label": "Back to Blog"},
    "it": {"lang": "it", "breadcrumb_home": "Home", "breadcrumb_blog": "Blog",
           "date_display": "29 agosto 2026", "by": "Di", "read_time": "6 min di lettura",
           "summary_h2": "In Breve", "faq_h2": "Domande Frequenti",
           "related_h2": "Continua a Leggere", "service_label": "Servizio correlato:",
           "back_label": "Torna al Blog"},
    "es": {"lang": "es", "breadcrumb_home": "Inicio", "breadcrumb_blog": "Blog",
           "date_display": "29 de agosto de 2026", "by": "Por", "read_time": "6 min de lectura",
           "summary_h2": "En resumen", "faq_h2": "Preguntas Frecuentes",
           "related_h2": "Sigue leyendo", "service_label": "Servicio relacionado:",
           "back_label": "Volver al Blog"},
    "sq": {"lang": "sq", "breadcrumb_home": "Kreu", "breadcrumb_blog": "Blog",
           "date_display": "29 gusht 2026", "by": "Nga", "read_time": "6 min lexim",
           "summary_h2": "Shkurtimisht", "faq_h2": "Pyetje të Shpeshta",
           "related_h2": "Vazhdoni leximin", "service_label": "Shërbimi përkatës:",
           "back_label": "Kthehuni te Blogu"},
}

# The hero for each post, needed to look its alt text up on the site. Kept here rather than
# imported from gen-answer-post.py so that this file agreeing with that one is evidence.
HERO = {"boost-or-campaign": "rika-stove", "lead-quality": "rika-facade",
        "in-house-or-agency": "rika-store", "showrooms": "rika-range",
        "windows-and-doors": "solutions-3", "stoves-and-heating": "rika-fire",
        "builders": "solutions-4", "restaurants": "solutions-6"}


def load(post, lang):
    return json.load(io.open(os.path.join(CONTENT, f"{post}-{lang}.json"), encoding="utf-8"))


def flat(d):
    """Every string a reader will actually see."""
    out = list(d["intro"]) + list(d["summary"])
    for s in d["sections"]:
        out.append(s["h2"])
        out.extend(p["html"] if isinstance(p, dict) else p for p in s["p"])
    for q in d["faq"]:
        out += [q["q"], q["a"]]
    return out


def site_alt(tree, img):
    """The alt this site already uses for an image in a tree. Read from the pages, not typed."""
    d = os.path.join(SITE_DIR, tree) if tree else SITE_DIR
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".html"):
            continue
        s = io.open(os.path.join(d, fn), encoding="utf-8", newline="").read()
        m = re.search(r"<img[^>]*" + re.escape(img) + r"\.jpg[^>]*>", s)
        if m:
            a = re.search(r'alt="([^"]*)"', m.group(0))
            if a:
                return a.group(1)
    return None


def page_h1(tree, slug):
    p = os.path.join(SITE_DIR, tree, slug + ".html") if tree \
        else os.path.join(SITE_DIR, slug + ".html")
    if not os.path.exists(p):
        return None
    s = io.open(p, encoding="utf-8", newline="").read()
    m = re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S)
    if not m:
        return None
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", m.group(1))).strip().replace("&amp;", "&")


def figures(strings, lang):
    """Digit groups, normalised so 6,150 and 6.150 compare equal.

    English writes 6,150 and 1.87; the other three trees write 6.150 and 1,87, matching the
    service pages. Comparing raw would flag every translated file, so separators are stripped
    and only the digits are compared. That still catches an invented or dropped figure, which
    is the thing worth catching.
    """
    out = set()
    for s in strings:
        for m in re.findall(r"\d[\d.,]*", s):
            out.add(re.sub(r"[.,]", "", m))
    return out


def check(post):
    en = load(post, "en")
    problems = []

    def bad(lang, msg):
        problems.append(f"{post}-{lang}: {msg}")

    en_shape = (len(en["intro"]), [len(s["p"]) for s in en["sections"]],
                len(en["summary"]), len(en["faq"]), len(en["related"]))
    en_figs = figures(flat(en), "en")

    for lang, tree in TREE.items():
        d = load(post, lang)
        blob = json.dumps(d, ensure_ascii=False)

        if set(d) != set(en):
            bad(lang, f"key set differs: missing {set(en) - set(d)}, extra {set(d) - set(en)}")
        if len(d["title"]) > 60:
            bad(lang, f"title is {len(d['title'])} chars, limit 60")
        if not 120 <= len(d["description"]) <= 155:
            bad(lang, f"description is {len(d['description'])} chars, must be 120 to 155")
        found = sorted({c for c in blob if c in DASHES})
        if found:
            bad(lang, f"forbidden dash {found}")
        ents = re.findall(r"&[a-zA-Z]+;|&#\d+;", blob)
        if ents:
            bad(lang, f"HTML entities {sorted(set(ents))}")
        if "%" in blob:
            bad(lang, "percent sign")

        shape = (len(d["intro"]), [len(s["p"]) for s in d["sections"]],
                 len(d["summary"]), len(d["faq"]), len(d["related"]))
        if shape != en_shape:
            bad(lang, f"structure {shape} does not match English {en_shape}")

        if [r["slug"] for r in d["related"]] != [r["slug"] for r in en["related"]]:
            bad(lang, "related slugs differ from English")
        if d["service_slug"] != en["service_slug"]:
            bad(lang, f"service_slug {d['service_slug']} != English {en['service_slug']}")

        for k, v in FIXED[lang].items():
            if d.get(k) != v:
                bad(lang, f"{k} is {d.get(k)!r}, expected {v!r}")

        want = site_alt(tree, HERO[post])
        if want is None:
            bad(lang, f"no existing alt found for {HERO[post]} in tree {tree or 'root'}")
        elif d["hero_alt"] != want:
            bad(lang, f"hero_alt does not match the site\n      file: {d['hero_alt']}\n"
                      f"      site: {want}")

        figs = figures(flat(d), lang)
        if figs - en_figs:
            bad(lang, f"figures not present in English: {sorted(figs - en_figs)}")
        if en_figs - figs:
            bad(lang, f"figures dropped from English: {sorted(en_figs - figs)}")

        for r in d["related"]:
            real = page_h1(tree, r["slug"])
            if real is not None and real != r["label"]:
                bad(lang, f"related label for {r['slug']} is not that page's H1\n"
                          f"      file: {r['label']}\n      page: {real}")

    return problems


if __name__ == "__main__":
    wanted = sys.argv[1:] or POSTS
    allp = []
    for post in wanted:
        if post not in POSTS:
            raise SystemExit(f"unknown post {post!r}; known: {', '.join(POSTS)}")
        missing = [l for l in TREE if not os.path.exists(
            os.path.join(CONTENT, f"{post}-{l}.json"))]
        if missing:
            print(f"  {post:20} SKIPPED, no content for {', '.join(missing)}")
            continue
        p = check(post)
        allp += p
        print(f"  {post:20} {'OK' if not p else str(len(p)) + ' PROBLEMS'}")
        for x in p:
            print(f"    ! {x}")
    print()
    print("ALL CLEAN" if not allp else f"{len(allp)} PROBLEMS")
    sys.exit(1 if allp else 0)
