#!/usr/bin/env python3
"""Name Switzerland in the prose that states which markets the agency serves.

add-swiss-market.py put Switzerland into areaServed. That is the machine-readable half. This
is the human half, and without it a reader in Lugano lands on a page titled for their city and
reads a market list that does not contain their country.

SCOPE IS DELIBERATELY NARROW. Three surfaces, not every sentence that names a country:

  1. The contact page FAQ "Which markets do you work with?" - the one place on the site that
     directly answers the question a Swiss prospect is asking. Both copies: the visible answer
     and the FAQPage JSON-LD, which gate check 10 requires to be character-identical.
  2. The contact page lead sentence, same list, same page.
  3. llms.txt, via gen-llms.py: the PREAMBLE and the Markets line. No length gate, read by
     machines, cheap to keep true.

DELIBERATELY NOT TOUCHED:

  - Meta, og: and twitter: descriptions. Gate check 4 holds descriptions to 120-155 characters
    and the Spanish tree already runs at 153. "Europe" is not false, so the cost of a rewrite
    across 4 trees x 3 tags buys nothing.
  - about.html. Its market sentences are narrative ("we help businesses in Italy, across
    Europe, in the United States and in Albania"), they already disagree with contact.html's
    list by including Albania, and the site plainly does not treat these as one canonical
    enumeration. Editing four languages of biography prose is a bigger, more opinionated
    change than this decision authorises.

Switzerland goes next to Italy, not at the end after the United States: that is the geography,
and it is the pairing the Lugano and Ticino guides depend on.

Idempotent.

    python name_switzerland.py
"""
import io
import os

SITE = r"c:\Users\aceto\OneDrive\Desktop\web and apps\Essi"

EDITS = {
    "contact.html": [
        ("We work with businesses across Italy, the rest of Europe and the United States.",
         "We work with businesses across Italy, Switzerland, the rest of Europe and the United States."),
        ("MarketingPro is a digital marketing agency for businesses across Italy, the rest of Europe and the United States.",
         "MarketingPro is a digital marketing agency for businesses across Italy, Switzerland, the rest of Europe and the United States."),
    ],
    "it/contact.html": [
        ("Lavoriamo con aziende in Italia, nel resto d'Europa e negli Stati Uniti.",
         "Lavoriamo con aziende in Italia, in Svizzera, nel resto d'Europa e negli Stati Uniti."),
        ("MarketingPro \u00e8 un'agenzia di marketing digitale per aziende in Italia, nel resto d'Europa e negli Stati Uniti.",
         "MarketingPro \u00e8 un'agenzia di marketing digitale per aziende in Italia, in Svizzera, nel resto d'Europa e negli Stati Uniti."),
    ],
    "es/contact.html": [
        ("Trabajamos con empresas de Italia, del resto de Europa y de Estados Unidos.",
         "Trabajamos con empresas de Italia, de Suiza, del resto de Europa y de Estados Unidos."),
        ("MarketingPro es una agencia de marketing digital para empresas de Italia, del resto de Europa y de Estados Unidos.",
         "MarketingPro es una agencia de marketing digital para empresas de Italia, de Suiza, del resto de Europa y de Estados Unidos."),
    ],
    "sq/contact.html": [
        ("Punojm\u00eb me biznese n\u00eb Itali, n\u00eb pjes\u00ebn tjet\u00ebr t\u00eb Evrop\u00ebs dhe n\u00eb Shtetet e Bashkuara.",
         "Punojm\u00eb me biznese n\u00eb Itali, n\u00eb Zvic\u00ebr, n\u00eb pjes\u00ebn tjet\u00ebr t\u00eb Evrop\u00ebs dhe n\u00eb Shtetet e Bashkuara."),
        ("MarketingPro \u00ebsht\u00eb agjenci marketingu dixhital p\u00ebr biznese n\u00eb Itali, n\u00eb pjes\u00ebn tjet\u00ebr t\u00eb Evrop\u00ebs dhe n\u00eb Shtetet e Bashkuara.",
         "MarketingPro \u00ebsht\u00eb agjenci marketingu dixhital p\u00ebr biznese n\u00eb Itali, n\u00eb Zvic\u00ebr, n\u00eb pjes\u00ebn tjet\u00ebr t\u00eb Evrop\u00ebs dhe n\u00eb Shtetet e Bashkuara."),
    ],
    ".build/gen-llms.py": [
        ("working with businesses across Albania, Italy, Europe and the United States",
         "working with businesses across Albania, Italy, Switzerland, Europe and the United States"),
        ("MarketingPro works with businesses across Albania, Italy, Europe and the United States,",
         "MarketingPro works with businesses across Albania, Italy, Switzerland, Europe and the United States,"),
        ("Markets: Albania \u00b7 Italy \u00b7 Europe \u00b7 United States",
         "Markets: Albania \u00b7 Italy \u00b7 Switzerland \u00b7 Europe \u00b7 United States"),
    ],
}

for path, subs in EDITS.items():
    p = os.path.join(SITE, path)
    s = io.open(p, encoding="utf-8", newline="").read()
    done = skipped = 0
    for old, new in subs:
        if old not in s:
            if new in s:
                skipped += 1
                continue
            raise SystemExit("  ! %s: not found: %s..." % (path, old[:70]))
        n = s.count(old)
        s = s.replace(old, new)
        done += n
    io.open(p, "w", encoding="utf-8", newline="").write(s)
    print("  %-20s %d replaced, %d already done" % (path, done, skipped))
print("done")
