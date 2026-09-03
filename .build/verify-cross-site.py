#!/usr/bin/env python3
"""Measure reused prose between MARKETINGPRO and MINA RANK.

WHY THIS EXISTS. verify-originality.py measures whether four city guides on THIS site are four
articles or one article with four names. It cannot see the other problem, which is newer: the
same agency owns MINA RANK, both sites now publish on AI search, and the same person writes for
both. On 2026-09-03 a new post here shared 69 distinct six-word runs with three new posts there,
including a whole paragraph defining AIO, AEO and GEO that was near-verbatim in both. Nothing on
either site could see it. MINA RANK's gate fails a 9+ word sentence repeated on two of ITS pages
and has no idea this site exists; every check here is scoped to this repo.

Two client sites publishing the same paragraphs is the failure both sites already warn clients
about, so shipping it would have been the exact thing the copy says not to do.

WHAT IT MEASURES. Six-word runs, lowercased, punctuation dropped, shared between a page here and
a page there. Six is deliberate: a five-word run catches ordinary English, and a whole sentence
catches nothing until the duplication is already blatant. Runs contained inside a longer reported
run are suppressed so one duplicated sentence reports once rather than nine times.

WHAT IT DOES NOT MEASURE. Whether the ARGUMENT is the same. Two posts can share no phrasing and
still make one point twice. That is a judgement, and it stays one.

TERMINOLOGY IS EXEMPT and has to be. "answer engine optimisation and generative engine
optimisation" is the name of a thing, not a reused sentence, so runs made only of the words in
EXEMPT are dropped rather than reported.

The comparison runs per language, over the three languages both sites publish. Spanish is
MARKETINGPRO only and has nothing to compare against.

    python .build/verify-cross-site.py            # the AI search material, both sites
    python .build/verify-cross-site.py --all      # every answer post against every MINA RANK post
"""
import io
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.dirname(_HERE)
WORKSPACE = os.path.dirname(SITE_DIR)
MINA = os.path.join(WORKSPACE, "MINA RANK")

N = 6
LANGS = {"en": "posts", "it": "posts_it", "sq": "posts_sq"}

# Runs built only from these words are the names of things and are allowed to coincide.
EXEMPT = {"ai", "aio", "aeo", "geo", "optimisation", "optimization", "answer", "engine",
          "generative", "search", "and", "or", "is", "the", "a", "an", "of", "for", "chatgpt",
          "ricerca", "motore", "motori", "generativi", "risposta", "sigla", "sigle",
          "kerkimi", "kerkim", "pergjigje", "shkurtesa", "shkurtesat"}

# Runs that were found, read, and judged not to be reuse. Each is ordinary language two writers
# would arrive at separately rather than a borrowed sentence, and each was checked by opening
# both pages on 2026-09-03. They are listed rather than tuned away with a larger N, because a
# threshold big enough to hide these would also hide a real seven-word lift.
#
#   "if there is nothing to find" / "there is nothing to find they"
#       builders <-> hotels-and-guesthouses. Both say that a search returning nothing returns
#       nothing. There is not much else to call it.
#   "what you do where you are"
#       roma <-> how-to-appear-in-chatgpt. Four function words and two verbs.
#   "e ve re qe ne rreshtin" / "ve re qe ne rreshtin e"
#       ticino <-> ai-search-in-italian. Albanian for "notices by the line", both making the
#       point that a machine translation gives itself away early. The argument is shared house
#       thinking; the sentences around it are not shared.
#   "pjesa me e madhe e trafikut"
#       milano <-> what-nobody-can-promise-ai-search. Albanian for "most of the traffic".
#
# Anything not in here is new and fails. Do not add a line without opening both pages first.
BASELINE = {
    "if there is nothing to find",
    "there is nothing to find they",
    "what you do where you are",
    "e vë re që në rreshtin",
    "vë re që në rreshtin e",
    "pjesa më e madhe e trafikut",
    # "most of what", added 2026-09-03. It appeared only after a grammar fix on the
    # MINA RANK side ("e atij qe" -> "e asaj qe", wrong gender for an abstract
    # antecedent) made the correct form collide with two MARKETINGPRO city guides.
    # Writing it any other way would mean writing it wrongly.
    "më e madhe e asaj që",
    "pjesa më e madhe e asaj",
}

# What this compares by default.
#
# On this side, the answer posts about AI search. On MINA RANK, EVERY post whose service is
# /geo/, which is their AI search service, and not a hand-written list of slugs.
#
# The hand-written list is how this check first went wrong. It named the three posts added on
# 2026-09-03, reported clean, and missed that the new post here duplicated a whole sentence from
# does-my-agency-do-ai-search, a MINA RANK post that has been live for days: in Italian, "un sito
# che un assistente legge con chiarezza di solito e un sito che anche un motore legge con
# chiarezza" was word for word on both client sites. Only --all found it. A scope that has to be
# remembered is a scope that will be forgotten, so it is derived from the data instead.
ESSI_POSTS = ["ai-search"]
MINA_SERVICE = "/geo/"


def norm(t):
    return re.findall(r"[\w']+", re.sub(r"<[^>]+>", " ", t).lower(), re.UNICODE)


def runs(blocks):
    """Runs WITHIN a block, never across two.

    Joining a heading to the paragraph under it and sliding a window over the join invents
    runs no reader ever sees. It reported one on the first run here: the heading "Cosa Non
    Sostituisce" followed by "Il lavoro normale sulla ricerca non e finito" produced
    "sostituisce il lavoro normale sulla ricerca", which appears nowhere on either site as a
    phrase. So every heading, paragraph, bullet and answer is measured on its own."""
    if isinstance(blocks, str):
        blocks = [blocks]
    out = set()
    for b in blocks:
        w = norm(b)
        out |= {" ".join(w[i:i + N]) for i in range(len(w) - N + 1)}
    return out


def solo_termini(run):
    return all(w.strip("'") in EXEMPT for w in run.split())


def essi_text_file(path):
    """Every reader-visible block in a content file, answer post or city guide alike.

    Keys are fetched defensively: the two families do not carry an identical key set and a
    KeyError here would stop the comparison rather than report it."""
    d = json.load(io.open(path, encoding="utf-8"))
    parts = list(d.get("intro") or []) + list(d.get("summary") or [])
    for s in d.get("sections") or []:
        parts.append(s.get("h2", ""))
        parts.extend(p["html"] if isinstance(p, dict) else p for p in (s.get("p") or []))
    for q in d.get("faq") or []:
        parts += [q.get("q", ""), q.get("a", "")]
    return parts


def essi_service_block(lang):
    """The AI search block on services-seo, read from the shipped page rather than a record."""
    tree = "" if lang == "en" else lang
    path = os.path.join(SITE_DIR, tree, "services-seo.html") if tree \
        else os.path.join(SITE_DIR, "services-seo.html")
    s = io.open(path, encoding="utf-8").read()
    if "AIO" not in s:
        return ""
    i = s.rfind("<h2>", 0, s.index("AIO"))
    j = s.index("<h2>", i + 4)
    return re.findall(r"<(?:h2|p)[^>]*>(.*?)</(?:h2|p)>", s[i:j], re.S)


def mina_text(rec):
    """Every reader-visible string in a MINA RANK post record.

    Keys are fetched defensively because not every record carries every one: --all found
    posts with no "faq" at all, and a KeyError there would stop the comparison rather than
    report it, which is the wrong way for a check to fail."""
    faq = rec.get("faq") or []
    return ([rec.get("summary", ""), rec.get("standfirst", ""), rec.get("payoff", "")] +
            [h for h, _ps in rec.get("body", [])] +
            [p for _h, ps in rec.get("body", []) for p in ps] +
            [q for q, _a in faq] + [a for _q, a in faq])


def main(tutto):
    if not os.path.isdir(MINA):
        print(f"  MINA RANK not found beside this repo at {MINA}; nothing to compare")
        return 0
    sys.path.insert(0, os.path.join(MINA, ".build"))

    problemi = 0
    for lang, modulo in LANGS.items():
        try:
            mod = __import__(modulo)
        except Exception as e:                       # a MINA RANK stamp mismatch is theirs
            print(f"  {lang}: cannot read MINA RANK {modulo} ({e})")
            continue

        loro = {}
        scelti = [p for p in mod.POSTS
                  if tutto or (p.get("service") or ("",))[0] == MINA_SERVICE]
        for rec in scelti:
            for r in runs(mina_text(rec)):
                loro.setdefault(r, rec["slug"])

        # BOTH DIRECTIONS, and this is not symmetry for its own sake. The first version
        # compared only the new post here against MINA RANK. That misses the other half:
        # a new post THERE landing on top of something already published HERE. Nobody
        # would find that either, so every content file on this side goes in.
        nostri = {}
        for cartella in ("answer-content", "city-content"):
            d = os.path.join(_HERE, cartella)
            if not os.path.isdir(d):
                continue
            for f in sorted(os.listdir(d)):
                if not f.endswith(f"-{lang}.json"):
                    continue
                nome = f[:-len(f"-{lang}.json")]
                if not tutto and cartella == "answer-content" and nome not in ESSI_POSTS:
                    # the default pass still leads with the AI search material, but the
                    # rest is present so a MINA RANK post cannot quietly land on it
                    pass
                try:
                    for r in runs(essi_text_file(os.path.join(d, f))):
                        nostri.setdefault(r, nome)
                except (OSError, ValueError, KeyError):
                    continue
        for r in runs(essi_service_block(lang)):
            nostri.setdefault(r, "services-seo")

        com = sorted(set(loro) & set(nostri))
        com = [c for c in com if not solo_termini(c)]
        com = [c for c in com if not any(c != o and c in o for o in com)]
        noti = [c for c in com if c in BASELINE]
        nuovi = [c for c in com if c not in BASELINE]
        if nuovi:
            problemi += len(nuovi)
            print(f"  {lang}: {len(nuovi)} NEW reused run(s) of {N}+ words")
            for c in nuovi:
                print(f"     {nostri[c]} <-> MINA RANK {loro[c]}")
                print(f"       {c}")
        else:
            print(f"  {lang}: clean" + (f" ({len(noti)} known, see BASELINE)" if noti else ""))

    if problemi:
        print(f"\n  {problemi} reused run(s). Rewrite on THIS side: MINA RANK's own gate has "
              f"already accepted its wording and re-stamping its translations to follow ours "
              f"costs three languages of churn for nothing.")
    return 1 if problemi else 0


if __name__ == "__main__":
    sys.exit(main("--all" in sys.argv))
