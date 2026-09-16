#!/usr/bin/env python3
"""Give the 6,150 lead figure its real scope: one month, one client.

The site framed it as "Across seven Meta campaigns" with no period and no client,
which reads as a lifetime total across the whole book of business and badly
understates what it is. The client corrected it on 16 September 2026: seven
campaigns run in a single month for one client. He asked that the client not be
named.

That is consistent with the evidence already on the page. The seven rows in the
table on services.html sum exactly to 6,150 leads, 1,084,529 reach and 11,480.98
euro, and they came from one Ads Manager export.

Honest limit, recorded here and in service-content.py: that screenshot is cropped
above the date selector and left of the campaign names. It proves the numbers and
the seven rows. It does not prove the period or the client count. Those come from
the person who owns the ad account, not from anything on this machine.

This file covers the hand-written HTML only. The JSON specs behind the eight blog
posts are handled by fix-figure-scope-specs.py, and are guarded by the digit-set
check in verify-answer-content.py. Nothing guards the files below, so they were
diffed by hand.

Scope discipline: "one month" and "one client" are written as WORDS in all four
trees. Writing 1 mese or 1 mes would introduce a digit that English does not have
and fail the cross-language figure check in the specs, and inconsistency between
the two families is exactly the kind of drift this site keeps paying for.

    python .build/fix-figure-scope.py
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)

# The five-per-page description: meta, og, twitter, and two JSON-LD nodes. They
# must move together or the structured data contradicts the meta tags. Every
# replacement below was measured against $DESC_MAX = 155 in verify-langs.ps1;
# EN had 1 character of headroom before this, so each one trades something out.
DESC = {
    "en": ("Meta and Google Ads agency for Italy, Europe, the US and Albania. Seven campaigns, "
           "6,150 leads at 1.87 euro each, every lead called and qualified for you.",
           "Meta and Google Ads agency for Italy, Europe, the US and Albania. One client, one "
           "month: 6,150 leads at 1.87 euro each, every lead called and qualified."),
    "it": ("Campagne mirate su Meta e Google, con ogni contatto chiamato e qualificato prima di "
           "passartelo. Sette campagne, 6.150 contatti, in media 1,87 euro l'uno.",
           "Campagne mirate su Meta e Google, con ogni contatto chiamato e qualificato prima di "
           "passartelo. Un cliente, un mese: 6.150 contatti a 1,87 euro l'uno."),
    "es": ("Campañas segmentadas en Meta y Google, con cada lead llamado y calificado antes "
           "de pasártelo. Siete campañas, 6.150 leads, a 1,87 euros de media.",
           "Campañas segmentadas en Meta y Google, con cada lead llamado y calificado antes "
           "de pasártelo. Un cliente, un mes: 6.150 leads a 1,87 euros de media."),
    "sq": ("Fushata të targetuara në Meta dhe Google, me çdo lead të "
           "kontaktuar e të kualifikuar nga ne. Shtatë fushata, 6.150 lead-e, "
           "mesatarisht 1,87 euro secili.",
           "Fushata të targetuara në Meta dhe Google, me çdo lead të "
           "kontaktuar e të kualifikuar nga ne. Një klient, një muaj: 6.150 "
           "lead-e me 1,87 euro secili."),
}

# The proof paragraph. English states it outright; the other three already refer
# back to "those seven campaigns", so the scope is added as a clause there.
PROOF = {
    "en": ("Across seven Meta campaigns we generated 6,150 leads",
           "Across seven Meta campaigns run in one month for a single client, we generated "
           "6,150 leads"),
    "it": ("Su quelle sette campagne: 6.150 contatti",
           "Su quelle sette campagne, tutte per un solo cliente e nell'arco di un mese: "
           "6.150 contatti"),
    "es": ("En esas siete campañas: 6.150 leads",
           "En esas siete campañas, todas para un solo cliente y en un mes: 6.150 leads"),
    "sq": ("Në ato shtatë fushata: 6.150 lead-e",
           "Në ato shtatë fushata, të gjitha për një klient të "
           "vetëm dhe brenda një muaji: 6.150 lead-e"),
}

# The AI-answer fact list on the about pages. Spanish has no such section at all;
# that gap is closed separately.
ABOUT = {
    "en": ("Across seven Meta campaigns, MarketingPro generated 6,150 leads at a blended "
           "€1.87 per lead.",
           "In one month, for a single client, MarketingPro generated 6,150 leads across seven "
           "Meta campaigns at a blended €1.87 per lead."),
    "it": ("Su sette campagne Meta, MarketingPro ha generato 6.150 lead a una media di 1,87 "
           "euro ciascuno.",
           "In un mese, per un solo cliente, MarketingPro ha generato 6.150 lead su sette "
           "campagne Meta, a una media di 1,87 euro ciascuno."),
    "sq": ("Në shtatë fushata Meta, MarketingPro gjeneroi 6.150 lead-e me një "
           "mesatare prej 1,87 euro secili.",
           "Në një muaj, për një klient të vetëm, MarketingPro "
           "gjeneroi 6.150 lead-e në shtatë fushata Meta, me një mesatare prej "
           "1,87 euro secili."),
}

TREE = {"en": "", "it": "it", "es": "es", "sq": "sq"}


def build():
    jobs = {}
    for lang, tree in TREE.items():
        pre = (tree + "/") if tree else ""
        old, new = DESC[lang]
        jobs[pre + "services-advertising.html"] = [(old, new, 5), PROOF[lang] + (1,)]
        if lang in ABOUT:
            jobs[pre + "about.html"] = [ABOUT[lang] + (1,)]

    # English-only surfaces.
    jobs["services-advertising.html"].append((
        "<h2>Meta ads results from seven real campaigns</h2>",
        "<h2>Meta ads results: seven campaigns, one client, one month</h2>", 1))
    jobs["index.html"] = [(
        "Across seven Meta campaigns we generated 6,150 leads",
        "In one month, for a single client, we generated 6,150 leads", 1)]
    jobs["services-social-media.html"] = [(
        "These channels feed real pipelines: across seven Meta campaigns, 6,150 leads have come "
        "through the social systems we run.",
        "These channels feed real pipelines: in one month, for a single client, seven Meta "
        "campaigns produced 6,150 leads through the social systems we run.", 1)]
    jobs["services-sales-funnel.html"] = [(
        "The follow-up systems behind our campaigns have handled 6,150 leads across seven Meta "
        "campaigns, each one called and qualified before handover.",
        "The follow-up systems behind our campaigns handled 6,150 leads from seven Meta "
        "campaigns run in a single month for one client, each one called and qualified before "
        "handover.", 1)]

    # The copy spec. Its own docstring says the shipped pages are the source of
    # truth and it is not to be run against them, but a stale spec is how a client
    # correction got reverted on this site once already.
    jobs[".build/service-content.py"] = [
        ("Seven campaigns, 6,150 leads, an average of 1.87 euro each.",
         "One client, one month: 6,150 leads at an average of 1.87 euro each.", 1),
        ("'Across those seven campaigns: 6,150 leads from 1,084,529 people reached, at a blended cost of '",
         "'Across those seven campaigns, all for one client and inside a single month: 6,150 leads '\n      'from 1,084,529 people reached, at a blended cost of '", 1),
        ("verified against the source Ads Manager screenshot in\noriginals/ (28 May 2025): seven campaigns, 6,150 leads, 11,480.98 EUR spent.\nTotals and the blended average are arithmetic on that table, nothing more.",
         "verified against the source Ads Manager screenshot in\noriginals/ (28 May 2025): seven campaigns, 6,150 leads, 11,480.98 EUR spent.\nTotals and the blended average are arithmetic on that table, nothing more.\n\nThat screenshot is cropped above the date selector and left of the campaign\nnames. It proves the seven rows and the numbers. It does NOT prove the period\nor how many clients they span. \"One month, one client\" comes from the person\nwho owns the ad account, given 16 September 2026, and is published on his word.\nIf an uncropped export ever arrives, say so here.", 1),
    ]
    return jobs


def main():
    plan, bad = [], []
    for rel, edits in build().items():
        fp = os.path.join(SITE, *rel.split("/"))
        s = io.open(fp, encoding="utf-8", newline="").read()
        for old, new, want in edits:
            got = s.count(old)
            if got != want:
                bad.append("%s: expected %d, found %d: %s" % (rel, want, got, old[:60]))
                continue
            s = s.replace(old, new)
        plan.append((fp, rel, s))

    if bad:
        print("ABORTED, nothing written:")
        for b in bad:
            print("  " + b)
        return 1

    for fp, rel, s in plan:
        io.open(fp, "w", encoding="utf-8", newline="").write(s)
        print("  wrote %s" % rel)
    print("done, %d files" % len(plan))
    return 0


if __name__ == "__main__":
    sys.exit(main())
