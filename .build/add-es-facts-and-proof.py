#!/usr/bin/env python3
"""Close two gaps where Spanish, or three languages, were simply missing content.

1. es/about.html has no <section id="facts"> at all. English, Italian and Albanian
   all carry one; Spanish carries none, so the Spanish about page states no
   founding date, no client list and no results. That is the section an assistant
   quotes when asked about the agency, and in Spanish there was nothing to quote.

   It is inserted in the ENGLISH position, after the intro section that holds the
   h1 and before OUR STORY. Italian and Albanian put theirs ABOVE the h1, which
   puts an h2 section before the page heading. That is a real defect in those two
   files and it is reported rather than fixed here, because moving live sections
   is not what this change is for.

2. The homepage proof sentence exists only in English. The other three trees carry
   the same lead-generation card and stop one sentence earlier, so three of four
   homepages omit the strongest number the agency has.

    python .build/add-es-facts-and-proof.py
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)

# Anchored on the closing tag of the Spanish intro section, which is immediately
# followed by the OUR STORY comment.
ES_ANCHOR = """    </section>

    <!-- OUR STORY -->
    <section class="section split" id="story">"""

ES_FACTS = """    </section>

    <section class="section" id="facts">
      <div class="container">
        <header class="section__head reveal" data-reveal>
          <h2 class="section__title section__title--center">MarketingPro en datos</h2>
        </header>
        <div class="article reveal" data-reveal>
          <ul class="service__list">
            <li>MarketingPro es una agencia de marketing digital con sede en Durrës, Albania.</li>
            <li>Fundada en 2024.</li>
            <li>MarketingPro trabaja con empresas de Italia, de toda Europa, de Estados Unidos y de Albania.</li>
            <li>MarketingPro trabaja en cuatro idiomas: inglés, italiano, español y albanés.</li>
            <li>El equipo de MarketingPro tiene más de 10 años de experiencia en marketing digital.</li>
            <li>Entre los clientes de MarketingPro están Fly System, OF Outdoorkitchen, OFYR Italia y Rika.</li>
            <li>En un mes, para un solo cliente, MarketingPro generó 6.150 leads en siete campañas de Meta, a una media de 1,87 euros por lead.</li>
            <li>MarketingPro responde a las nuevas consultas en un día laborable.</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- OUR STORY -->
    <section class="section split" id="story">"""

# Each tree writes the figure in its own separator convention, matching the
# service pages: English 6,150 / 1.87, the others 6.150 / 1,87.
HOME = {
    "it": ("o persone già pronte per un preventivo.</p>",
           "o persone già pronte per un preventivo. In un mese, per un solo cliente, "
           "abbiamo generato 6.150 contatti a una media di 1,87 euro l'uno.</p>"),
    "es": ("llegan contactos ya calificados o personas listas para recibir una propuesta.</p>",
           "llegan contactos ya calificados o personas listas para recibir una propuesta. "
           "En un mes, para un solo cliente, generamos 6.150 leads a una media de 1,87 euros "
           "por lead.</p>"),
    "sq": ("të kualifikuara ose njerëz tashmë gati për një ofertë.</p>",
           "të kualifikuara ose njerëz tashmë gati për një ofertë. "
           "Në një muaj, për një klient të vetëm, gjeneruam "
           "6.150 lead-e me një mesatare prej 1,87 euro secili.</p>"),
}


def main():
    jobs = {"es/about.html": [(ES_ANCHOR, ES_FACTS, 1)]}
    for lang, (old, new) in HOME.items():
        jobs["%s/index.html" % lang] = [(old, new, 1)]

    plan, bad = [], []
    for rel, edits in jobs.items():
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
