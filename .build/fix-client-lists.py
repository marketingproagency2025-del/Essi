#!/usr/bin/env python3
"""Add OF Outdoorkitchen to the client lists, and correct the English service pages.

OF Outdoorkitchen went live on the portfolio a week ago and was never added to any
of the sentences that say who the agency works with. Those are exactly the lines an
assistant quotes when asked, so a missing client is a missing citation.

The four English service-page paragraphs are corrected in the same pass because
they are client lists too, and because they carried the OFYR "outdoor cooking"
error and the location-less Premium Store. Each now states all four clients and
their real trades. Their verbs stay deliberately varied (sells / builds / makes)
so the eight service pages are not duplicate content, and services-sales-funnel
keeps its unnamed phrasing.

The IT, ES and SQ service pages have no client-proof paragraph at all. That gap is
real and is being closed separately; this file only touches what already exists.

    python .build/fix-client-lists.py
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)

LINK_EN = '<a href="/portfolio">Fly System, OFYR Italia and Rika</a>'
LINK_EN_NEW = '<a href="/portfolio">Fly System, OF Outdoorkitchen, OFYR Italia and Rika</a>'

FILES = {
    # --- client lists, all trees that have one ---
    "about.html": [
        ("MarketingPro clients include Fly System, OFYR Italia and Rika.",
         "MarketingPro clients include Fly System, OF Outdoorkitchen, OFYR Italia and Rika.", 1),
    ],
    "it/about.html": [
        ("Tra i clienti di MarketingPro ci sono Fly System, OFYR Italia e Rika.",
         "Tra i clienti di MarketingPro ci sono Fly System, OF Outdoorkitchen, OFYR Italia e Rika.", 1),
    ],
    "sq/about.html": [
        ("Ndër klientët e MarketingPro janë Fly System, OFYR Italia dhe Rika.",
         "Ndër klientët e MarketingPro janë Fly System, OF Outdoorkitchen, OFYR Italia dhe Rika.", 1),
    ],
    "index.html": [
        (LINK_EN, LINK_EN_NEW, 1),
    ],

    # --- English service pages: client list + OFYR trade + Verona ---
    "services-advertising.html": [
        (LINK_EN, LINK_EN_NEW, 1),
        ("Fly System sells windows and outdoor products in Italy, OFYR Italia sells outdoor "
         "cooking equipment, and Rika sells wood and pellet stoves in the Italian market.",
         "Fly System sells windows and outdoor products in Italy, OF Outdoorkitchen builds "
         "outdoor kitchens, OFYR Italia sells wood-fired barbecues, and Rika sells wood and "
         "pellet stoves through its Premium Store in Verona.", 1),
    ],
    "services-photo-video.html": [
        (LINK_EN, LINK_EN_NEW, 1),
        ("Fly System builds windows and outdoor products in Italy, OFYR Italia sells outdoor "
         "cooking gear, and Rika makes wood and pellet stoves for the Italian market.",
         "Fly System builds windows and outdoor products in Italy, OF Outdoorkitchen fits "
         "outdoor kitchens, OFYR Italia sells wood-fired barbecues, and Rika makes wood and "
         "pellet stoves for the Italian market.", 1),
    ],
    "services-social-media.html": [
        (LINK_EN, LINK_EN_NEW, 1),
        ("Fly System makes windows and outdoor products in Italy, OFYR Italia sells outdoor "
         "cooking gear, and Rika makes wood and pellet stoves for the Italian market.",
         "Fly System makes windows and outdoor products in Italy, OF Outdoorkitchen builds "
         "outdoor kitchens, OFYR Italia sells wood-fired barbecues, and Rika makes wood and "
         "pellet stoves for the Italian market.", 1),
    ],
    "services-sales-funnel.html": [
        (LINK_EN, LINK_EN_NEW, 1),
        ("One of them makes windows and outdoor products in Italy, one sells outdoor cooking "
         "gear, and one makes wood and pellet stoves for the Italian market.",
         "One of them makes windows and outdoor products in Italy, one builds outdoor kitchens, "
         "one sells wood-fired barbecues, and one makes wood and pellet stoves for the Italian "
         "market.", 1),
    ],

    # --- the citation crib an assistant is pointed at ---
    ".build/citations.md": [
        ("Fly System, OFYR Italia and Rika are three you can ask today.",
         "Fly System, OF Outdoorkitchen, OFYR Italia and Rika are four you can ask today.", 1),
    ],

    # --- the quarantined spec, kept honest so it cannot revert this later ---
    ".build/gen-portfolio.py": [
        ("'meta': 'Outdoor cooking &middot; Milan, Italy',",
         "'meta': 'Wood-fired barbecues &middot; Milan, Italy',", 1),
        ("'OFYR Italia sells outdoor cooking, and it is a product that only makes sense in use. '",
         "'OFYR Italia sells wood-fired barbecues, and it is a product that only makes sense in use. '", 1),
        ("'Store: the drone approach over the building, then the showroom itself, the range '",
         "'Store in Verona: the drone approach over the building, then the showroom itself, the range '", 1),
        ("TITLE = 'Client Work: Fly System, OFYR Italia and Rika | MarketingPro'",
         "TITLE = 'Our Work: Outdoor Kitchens, Windows, Stoves | MarketingPro'", 1),
    ],
}


def main():
    plan, bad = [], []
    for rel, edits in FILES.items():
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
