#!/usr/bin/env python3
"""The same scope correction, in the 32 answer-post specs.

Eight posts cite the figure and every one of them opened with a bare "Across
seven Meta campaigns", which says nothing about when or for whom. The scope
clause goes in immediately after that phrase, which reads correctly against all
four verbs the posts use after it (we generated / we reached / we have produced /
that has meant).

Two sentences needed rewriting rather than renumbering, because they asserted the
opposite of what is true:

  boost-or-campaign sections[5].p[1] said the leads reached "the sales TEAMS they
  belonged to" - plural, i.e. several clients.

  restaurants sections[6].p[1] said hospitality is "a different shape of CLIENT
  from most of that work", which now reads as comparing hospitality to the one
  client the figure describes. It is comparing it to the agency's wider book, so
  it becomes a different shape of business from what we run.

"One month" and "one client" are spelled as words in all four trees on purpose.
verify-answer-content.py collects every digit group and requires the four trees
to carry an identical set, so writing "1 mese" in Italian would introduce a figure
English does not have and fail the check.

Edited as text, so the files keep their formatting; re-parsed as JSON afterwards.

    python .build/fix-figure-scope-specs.py
    python .build/gen-answer-post.py
    python .build/verify-answer-content.py
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(HERE, "answer-content")

POSTS = ["boost-or-campaign", "lead-quality", "in-house-or-agency", "showrooms",
         "windows-and-doors", "stoves-and-heating", "builders", "restaurants"]
LANGS = ["en", "it", "es", "sq"]

OPENER = {
    "en": ("Across seven Meta campaigns",
           "Across seven Meta campaigns in one month, for one client,"),
    "it": ("Su sette campagne Meta",
           "Su sette campagne Meta in un mese, per un solo cliente,"),
    "es": ("En siete campañas de Meta",
           "En siete campañas de Meta en un mes, para un solo cliente,"),
    "sq": ("Në shtatë fushata Meta",
           "Në shtatë fushata Meta brenda një muaji, "
           "për një klient të vetëm,"),
}

# boost-or-campaign only: the takeaway line, which drops the word Meta.
SUMMARY = {
    "en": ("Across seven campaigns we produced 6,150 leads at a blended 1.87 euro.",
           "In one month, for one client, seven campaigns produced 6,150 leads at a "
           "blended 1.87 euro."),
    "it": ("Su sette campagne abbiamo prodotto 6.150 contatti a 1,87 euro medi.",
           "In un mese, per un solo cliente, sette campagne hanno prodotto 6.150 contatti "
           "a 1,87 euro medi."),
    "es": ("En siete campañas produjimos 6.150 leads a 1,87 euros de media.",
           "En un mes, para un solo cliente, siete campañas produjeron 6.150 leads "
           "a 1,87 euros de media."),
    "sq": ("Në shtatë fushata prodhuam 6.150 lead-e me 1,87 euro mesatare.",
           "Në një muaj, për një klient të vetëm, shtatë "
           "fushata prodhuan 6.150 lead-e me 1,87 euro mesatare."),
}

# boost-or-campaign only: plural sales teams implied several clients.
TEAMS = {
    "en": ("before they reached the sales teams they belonged to",
           "before they reached the sales team they belonged to"),
    "it": ("prima di arrivare ai commerciali a cui erano destinati",
           "prima di arrivare al team commerciale a cui erano destinati"),
    "es": ("antes de llegar a los comerciales a los que correspondían",
           "antes de llegar al equipo comercial al que correspondía"),
    "sq": ("para se të mbërrinin te shitësit të cilëve u përkisnin",
           "para se të mbërrinin te ekipi i shitjeve të cilit i përkiste"),
}

# restaurants only: "a different shape of client" now reads as a comparison with
# the single client the figure belongs to.
HOSPITALITY = {
    "en": ("Hospitality is a different shape of client from most of that work,",
           "Hospitality is a different shape of business from most of what we run,"),
    "it": ("L'ospitalità è un tipo di cliente diverso da gran parte di quel lavoro,",
           "L'ospitalità è un tipo di attività diverso da gran parte di quello "
           "che gestiamo,"),
    "es": ("La hostelería es un tipo de cliente distinto de buena parte de ese trabajo,",
           "La hostelería es un tipo de negocio distinto de buena parte de lo que "
           "gestionamos,"),
    "sq": ("Mikpritja është një lloj klienti i ndryshëm nga pjesa më "
           "e madhe e asaj pune,",
           "Mikpritja është një lloj biznesi i ndryshëm nga pjesa më "
           "e madhe e asaj që drejtojmë,"),
}


def edits_for(post, lang):
    out = [OPENER[lang]]
    if post == "boost-or-campaign":
        out += [SUMMARY[lang], TEAMS[lang]]
    if post == "restaurants":
        out.append(HOSPITALITY[lang])
    return out


def main():
    plan, bad = [], []
    for post in POSTS:
        for lang in LANGS:
            rel = "%s-%s.json" % (post, lang)
            fp = os.path.join(CONTENT, rel)
            s = io.open(fp, encoding="utf-8", newline="").read()
            for old, new in edits_for(post, lang):
                got = s.count(old)
                if got != 1:
                    bad.append("%s: expected 1, found %d: %s" % (rel, got, old[:55]))
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
    print("  wrote %d specs across %d posts" % (len(plan), len(POSTS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
