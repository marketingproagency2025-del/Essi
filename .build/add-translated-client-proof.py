#!/usr/bin/env python3
"""Give the Italian, Spanish and Albanian service pages the client proof they lack.

Four English service pages each carry a "Who we X for" section naming real
clients. None of the twelve translated pages has one, so the three trees that
serve the agency's actual markets showed no named client on the pages that sell
the work. Italy is the primary market and OFYR, Fly System and Rika are Italian
operations, which makes the Italian pages the worst place for that gap to be.

Each new paragraph carries the corrections from this batch already, so it is never
wrong in any tree: OFYR sells wood-fired barbecues, the Rika Premium Store is in
Verona, and OF Outdoorkitchen is named.

Two things preserved from the English:
  - the verbs vary per page (sells / builds / makes) so the eight service pages
    are not duplicate content. The translations vary in the same places.
  - services-sales-funnel leaves the clients unnamed in the second sentence
    ("One of them makes..."). That stays.

Placement is load-bearing. The new h2 goes immediately BEFORE the "who this suits"
heading, which keeps it out of the four positions check 23 compares across the
eight service pages: verify-langs.ps1:761-766 reads $h2s[0] and the last three,
and inserting at -4 leaves all four untouched.

Albanian says "stufa" here, matching what sq/portfolio.html says today. The
stufa/soba split is real and is being standardised in its own pass; writing the
minority form here would just move the inconsistency.

    python .build/add-translated-client-proof.py
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)

SLUGS = ["services-advertising", "services-photo-video",
         "services-social-media", "services-sales-funnel"]

# The heading that currently follows where the new section belongs.
ANCHOR = {
    "it": "          <h2>A chi è adatto</h2>",
    "es": "          <h2>Para quién es</h2>",
    "sq": "          <h2>Për kë është</h2>",
}

LEAD = {
    "it": "Questo servizio lo gestiamo oggi per "
          '<a href="/it/portfolio">Fly System, OF Outdoorkitchen, OFYR Italia e Rika</a>.',
    "es": "Hoy prestamos este servicio a "
          '<a href="/es/portfolio">Fly System, OF Outdoorkitchen, OFYR Italia y Rika</a>.',
    "sq": "Këtë shërbim e ofrojmë sot për "
          '<a href="/sq/portfolio">Fly System, OF Outdoorkitchen, OFYR Italia dhe Rika</a>.',
}

H2 = {
    ("it", "services-advertising"): "Per chi gestiamo le campagne",
    ("it", "services-photo-video"): "Per chi produciamo foto e video",
    ("it", "services-social-media"): "Per chi gestiamo i social",
    ("it", "services-sales-funnel"): "Per chi costruiamo funnel di vendita",
    ("es", "services-advertising"): "Para quién gestionamos campañas",
    ("es", "services-photo-video"): "Para quién producimos foto y vídeo",
    ("es", "services-social-media"): "Para quién gestionamos redes sociales",
    ("es", "services-sales-funnel"): "Para quién construimos embudos de venta",
    ("sq", "services-advertising"): "Për kë i drejtojmë fushatat",
    ("sq", "services-photo-video"): "Për kë prodhojmë foto dhe video",
    ("sq", "services-social-media"): "Për kë i menaxhojmë rrjetet sociale",
    ("sq", "services-sales-funnel"): "Për kë ndërtojmë funnel-e shitjeje",
}

# Second sentence, mirroring the English verb variation per page.
BODY = {
    ("it", "services-advertising"):
        "Fly System vende serramenti e prodotti da esterno in Italia, OF Outdoorkitchen "
        "realizza cucine da esterno, OFYR Italia vende barbecue a legna, e Rika vende stufe "
        "a legna e a pellet attraverso il suo Premium Store di Verona.",
    ("it", "services-photo-video"):
        "Fly System costruisce serramenti e prodotti da esterno in Italia, OF Outdoorkitchen "
        "installa cucine da esterno, OFYR Italia vende barbecue a legna, e Rika produce stufe "
        "a legna e a pellet per il mercato italiano.",
    ("it", "services-social-media"):
        "Fly System produce serramenti e prodotti da esterno in Italia, OF Outdoorkitchen "
        "realizza cucine da esterno, OFYR Italia vende barbecue a legna, e Rika produce stufe "
        "a legna e a pellet per il mercato italiano.",
    ("it", "services-sales-funnel"):
        "Una di queste produce serramenti e prodotti da esterno in Italia, una realizza cucine "
        "da esterno, una vende barbecue a legna, e una produce stufe a legna e a pellet per il "
        "mercato italiano.",
    ("es", "services-advertising"):
        "Fly System vende ventanas y productos de exterior en Italia, OF Outdoorkitchen "
        "construye cocinas de exterior, OFYR Italia vende barbacoas de leña, y Rika vende "
        "estufas de leña y de pellets a través de su Premium Store de Verona.",
    ("es", "services-photo-video"):
        "Fly System fabrica ventanas y productos de exterior en Italia, OF Outdoorkitchen "
        "instala cocinas de exterior, OFYR Italia vende barbacoas de leña, y Rika fabrica "
        "estufas de leña y de pellets para el mercado italiano.",
    ("es", "services-social-media"):
        "Fly System hace ventanas y productos de exterior en Italia, OF Outdoorkitchen "
        "construye cocinas de exterior, OFYR Italia vende barbacoas de leña, y Rika "
        "fabrica estufas de leña y de pellets para el mercado italiano.",
    ("es", "services-sales-funnel"):
        "Una de ellas hace ventanas y productos de exterior en Italia, una construye cocinas "
        "de exterior, una vende barbacoas de leña, y una fabrica estufas de leña y "
        "de pellets para el mercado italiano.",
    ("sq", "services-advertising"):
        "Fly System shet dritare dhe produkte të jashtme në Itali, OF Outdoorkitchen "
        "ndërton kuzhina të jashtme, OFYR Italia shet barbekju me dru, dhe Rika shet "
        "stufa me dru dhe me pelet përmes Premium Store-it të saj në Verona.",
    ("sq", "services-photo-video"):
        "Fly System ndërton dritare dhe produkte të jashtme në Itali, "
        "OF Outdoorkitchen instalon kuzhina të jashtme, OFYR Italia shet barbekju me dru, "
        "dhe Rika prodhon stufa me dru dhe me pelet për tregun italian.",
    ("sq", "services-social-media"):
        "Fly System prodhon dritare dhe produkte të jashtme në Itali, "
        "OF Outdoorkitchen ndërton kuzhina të jashtme, OFYR Italia shet barbekju me "
        "dru, dhe Rika prodhon stufa me dru dhe me pelet për tregun italian.",
    ("sq", "services-sales-funnel"):
        "Njëra prej tyre prodhon dritare dhe produkte të jashtme në Itali, "
        "njëra ndërton kuzhina të jashtme, njëra shet barbekju me dru, dhe "
        "njëra prodhon stufa me dru dhe me pelet për tregun italian.",
}


def main():
    plan, bad = [], []
    for lang in ("it", "es", "sq"):
        for slug in SLUGS:
            rel = "%s/%s.html" % (lang, slug)
            fp = os.path.join(SITE, lang, slug + ".html")
            s = io.open(fp, encoding="utf-8", newline="").read()
            anchor = ANCHOR[lang]
            if s.count(anchor) != 1:
                bad.append("%s: anchor found %d times" % (rel, s.count(anchor)))
                continue
            block = ("          <h2>%s</h2>\n          <p>%s %s</p>\n%s"
                     % (H2[(lang, slug)], LEAD[lang], BODY[(lang, slug)], anchor))
            plan.append((fp, rel, s.replace(anchor, block)))

    if bad:
        print("ABORTED, nothing written:")
        for b in bad:
            print("  " + b)
        return 1

    for fp, rel, s in plan:
        io.open(fp, "w", encoding="utf-8", newline="").write(s)
        print("  wrote %s" % rel)
    print("done, %d pages" % len(plan))
    return 0


if __name__ == "__main__":
    sys.exit(main())
