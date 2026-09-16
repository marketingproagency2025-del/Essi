#!/usr/bin/env python3
"""Correct two facts about two clients on the portfolio, in all four trees.

Both came from the client on 16 September 2026, after he read the live site.

1. OFYR Italia sells WOOD-FIRED BARBECUES, not outdoor kitchens. Every tree said
   outdoor kitchen. This mattered more than it looks: OF Outdoorkitchen was added
   directly above OFYR on the same page a week earlier and genuinely does sell
   outdoor kitchens, so in Italian and Spanish the two cases carried word-for-word
   the same trade line and a reader could not tell the businesses apart.

2. The Rika Premium Store is in VERONA. The string did not appear anywhere in the
   repo, while the OFYR case directly above it named Milan.

Also, because these are the same sentences: OF Outdoorkitchen is added to the
client lists it has been missing from since it went live, and the JSON-LD "name"
at :185 is resynced to the page's real <title>. That name still claimed the old
three-client title the page stopped using when OF was added, so structured data
and the page have been contradicting each other.

NOT here, deliberately:
  - the image alt for the OFYR grid. "chefs cooking over open fire at outdoor
    events" is accurate for a wood-fired BBQ.
  - the Rika photo alts. They describe what is visible in the frame, and Verona
    is not visible in a sign on a wall or a building from the air.
  - the page <title>s. Adding a fourth trade breaks the 60-char cap in three of
    four trees, and buying room by dropping the "Our Work:" / "Portfolio:" prefix
    trades an intent keyword for one case out of four. The meta descriptions carry
    it instead; they all had headroom.
  - the Albanian stufa/soba split. Real, but it reaches into gallery alts and
    cross-file alt consistency, so it gets its own pass.

    python .build/fix-ofyr-and-verona.py
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)

# (old, new, expected occurrences). Anything that does not hit its count exactly
# aborts the whole run before a single file is written, following sub1() in
# gen-city-guide.py: a silent no-op here ships a half-corrected page.
EDITS = {
    "en": [
        # trade list -> meta description, og:description, twitter:description
        ("Outdoor kitchens, windows and stoves:",
         "Outdoor kitchens, BBQs, windows and stoves:", 3),
        # JSON-LD name resynced to the real <title>
        ('"name": "Client Work: Fly System, OFYR Italia and Rika | MarketingPro"',
         '"name": "Our Work: Outdoor Kitchens, Windows, Stoves | MarketingPro"', 1),
        ("Client Work: Outdoor Kitchens, Windows and Stoves",
         "Client Work: Outdoor Kitchens, BBQs, Windows and Stoves", 1),
        # OFYR
        ("Outdoor cooking &middot; Milan, Italy",
         "Wood-fired barbecues &middot; Milan, Italy", 1),
        ("OFYR Italia sells outdoor cooking, and it is a product",
         "OFYR Italia sells wood-fired barbecues, and it is a product", 1),
        ('"name": "OFYR Italia",\n                "sameAs"',
         '"name": "OFYR Italia",\n                "description": "OFYR Italia sells wood-fired barbecues in Italy.",\n                "sameAs"', 1),
        # Rika
        ("Wood and pellet stoves &middot; Italy",
         "Wood and pellet stoves &middot; Verona, Italy", 1),
        ("the company film for its Premium Store:",
         "the company film for its Premium Store in Verona:", 1),
        ('"name": "Rika"\n              },',
         '"name": "Rika",\n                "description": "Rika makes wood and pellet stoves. Its Premium Store is in Verona, Italy."\n              },', 1),
        ('"description": "A film produced for Rika: the store from the air, the showroom, and the stove range on display.",',
         '"description": "A film produced for Rika: the store from the air, the showroom, and the stove range on display.",\n        "contentLocation": {\n          "@type": "Place",\n          "name": "Verona, Italy"\n        },', 1),
    ],
    "it": [
        ("Cucine da esterno, infissi e stufe:",
         "Cucine da esterno, BBQ, infissi e stufe:", 3),
        ('"name": "Portfolio: Fly System, OFYR Italia e Rika | MarketingPro"',
         '"name": "Portfolio: Cucine da Esterno, Infissi, Stufe | MarketingPro"', 1),
        ("Cucina all'aperto &middot; Milano, Italia",
         "Barbecue a legna &middot; Milano, Italia", 1),
        ("OFYR Italia vende cucina all'aperto, ed è un prodotto",
         "OFYR Italia vende barbecue a legna, ed è un prodotto", 1),
        ('"name": "OFYR Italia",\n                "sameAs"',
         '"name": "OFYR Italia",\n                "description": "OFYR Italia vende barbecue a legna in Italia.",\n                "sameAs"', 1),
        ("Stufe a legna e a pellet &middot; Italia",
         "Stufe a legna e a pellet &middot; Verona, Italia", 1),
        ("il video aziendale del suo Premium Store:",
         "il video aziendale del suo Premium Store di Verona:", 1),
        ('"name": "Rika"\n              },',
         '"name": "Rika",\n                "description": "Rika produce stufe a legna e a pellet. Il suo Premium Store è a Verona, in Italia."\n              },', 1),
        ('"description": "Un video prodotto per Rika: lo store dall\'alto, lo showroom e la gamma di stufe in esposizione.",',
         '"description": "Un video prodotto per Rika: lo store dall\'alto, lo showroom e la gamma di stufe in esposizione.",\n        "contentLocation": {\n          "@type": "Place",\n          "name": "Verona, Italia"\n        },', 1),
    ],
    "es": [
        ("Cocinas de exterior, ventanas y estufas:",
         "Cocinas de exterior, BBQ, ventanas y estufas:", 3),
        ('"name": "Portfolio: Fly System, OFYR Italia y Rika | MarketingPro"',
         '"name": "Cocinas de Exterior, Ventanas y Estufas | MarketingPro"', 1),
        ("Cocina al aire libre &middot; Milán, Italia",
         "Barbacoas de leña &middot; Milán, Italia", 1),
        ("OFYR Italia vende cocina al aire libre, un producto",
         "OFYR Italia vende barbacoas de leña, un producto", 1),
        ('"name": "OFYR Italia",\n                "sameAs"',
         '"name": "OFYR Italia",\n                "description": "OFYR Italia vende barbacoas de leña en Italia.",\n                "sameAs"', 1),
        ("Estufas de leña y de pellets &middot; Italia",
         "Estufas de leña y de pellets &middot; Verona, Italia", 1),
        ("el vídeo corporativo de su Premium Store:",
         "el vídeo corporativo de su Premium Store de Verona:", 1),
        ('"name": "Rika"\n              },',
         '"name": "Rika",\n                "description": "Rika fabrica estufas de leña y de pellets. Su Premium Store está en Verona, Italia."\n              },', 1),
        ('"description": "Un vídeo producido para Rika: la tienda desde el aire, el showroom y la gama de estufas expuesta.",',
         '"description": "Un vídeo producido para Rika: la tienda desde el aire, el showroom y la gama de estufas expuesta.",\n        "contentLocation": {\n          "@type": "Place",\n          "name": "Verona, Italia"\n        },', 1),
        # Every other Spanish mention keeps the brand term "Rika Premium Store";
        # this alt alone translated it into a common noun.
        ("Vista aérea de la tienda premium de Rika, con el rótulo",
         "Vista aérea del Rika Premium Store, con el rótulo", 1),
    ],
    "sq": [
        ("Kuzhina të jashtme, dritare dhe stufa:",
         "Kuzhina të jashtme, BBQ, dritare dhe stufa:", 3),
        ('"name": "Portfolio: Fly System, OFYR Italia dhe Rika | MarketingPro"',
         '"name": "Portfolio: Kuzhina të Jashtme, Dritare, Stufa | MarketingPro"', 1),
        ("Gatim në natyrë &middot; Milano, Itali",
         "Barbekju me dru &middot; Milano, Itali", 1),
        ("OFYR Italia shet gatim në natyrë, një produkt",
         "OFYR Italia shet barbekju me dru, një produkt", 1),
        ('"name": "OFYR Italia",\n                "sameAs"',
         '"name": "OFYR Italia",\n                "description": "OFYR Italia shet barbekju me dru në Itali.",\n                "sameAs"', 1),
        ("Stufa me dru dhe me pelet &middot; Itali",
         "Stufa me dru dhe me pelet &middot; Verona, Itali", 1),
        ("për Premium Store-in e saj:",
         "për Premium Store-in e saj në Verona:", 1),
        ('"name": "Rika"\n              },',
         '"name": "Rika",\n                "description": "Rika prodhon stufa me dru dhe me pelet. Premium Store-i i saj është në Verona, Itali."\n              },', 1),
        ('"description": "Një film i realizuar për Rika: dyqani nga ajri, showroom-i dhe gama e stufave në ekspozim.",',
         '"description": "Një film i realizuar për Rika: dyqani nga ajri, showroom-i dhe gama e stufave në ekspozim.",\n        "contentLocation": {\n          "@type": "Place",\n          "name": "Verona, Itali"\n        },', 1),
    ],
}

TREE = {"en": "", "it": "it", "es": "es", "sq": "sq"}


def path(lang, slug):
    d = os.path.join(SITE, TREE[lang]) if TREE[lang] else SITE
    return os.path.join(d, slug + ".html")


def apply(fp, edits):
    s = io.open(fp, encoding="utf-8", newline="").read()
    problems = []
    for old, new, want in edits:
        got = s.count(old)
        if got != want:
            problems.append("  expected %d, found %d: %s" % (want, got, old[:70]))
            continue
        s = s.replace(old, new)
    return s, problems


def main():
    plan = []
    allbad = []
    for lang, edits in EDITS.items():
        fp = path(lang, "portfolio")
        s, bad = apply(fp, edits)
        if bad:
            allbad.append("%s:" % os.path.relpath(fp, SITE))
            allbad += bad
        plan.append((fp, s))

    if allbad:
        print("ABORTED, nothing written:")
        for line in allbad:
            print(line)
        return 1

    for fp, s in plan:
        io.open(fp, "w", encoding="utf-8", newline="").write(s)
        print("  wrote %s" % os.path.relpath(fp, SITE))
    print("done, %d files" % len(plan))
    return 0


if __name__ == "__main__":
    sys.exit(main())
