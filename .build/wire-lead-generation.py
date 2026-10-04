#!/usr/bin/env python3
"""Wire services-lead-generation into the site so it is not born orphaned.

    python .build/wire-lead-generation.py
    python .build/gen-answer-post.py lead-quality

Three edits, all four trees. Same reasoning as wire-services.py, which states the rule this
follows: a guide and its service page link to each other, and that is what stops the commercial
and the informational page competing for the same query.

1. blog-lead-quality's "Related service" line pointed at the advertising page, because when it was
   written there was nothing better to point at. It now points at the lead generation page, which
   is the service it actually explains. The line lives in the JSON content spec, not the HTML, so
   it is edited there and the page regenerated. gen-llms.py now carries the same pairing.

2. The home page card for this service gains a sentence linking the new page. The card already
   links the advertising guide and that stays: the existing sentence is about campaigns and is
   still true. Adding rather than repointing keeps the sentence honest and still gives the new page
   an editorial inbound link, which is what gate checks 16 and 17 want.

3. The services hub gains a link from the sales funnel block, which is the service immediately
   after this one in the same journey.

WHAT THIS DELIBERATELY DOES NOT DO. The hub has a full section per service, with two photographs
and its own call to action. Lead generation has no section of its own yet because it has no
photography of its own yet, and inventing one by reusing another service's images would put the
wrong picture on a client's page. A dedicated hub section is a follow-up, not part of this.
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
SLUG = "services-lead-generation"
TREES = {"en": "", "it": "it", "es": "es", "sq": "sq"}

# The guide's "Related service" label, per language.
SERVICE_NAME = {
    "en": "Lead generation",
    "it": "Lead Generation",
    "es": "Lead Generation",
    "sq": "Lead Generation",
}

# The card title. English already uses the term the market searches; the other three did not.
CARD_TITLE = {
    "en": ("Lead Generation &amp; Outreach", "Lead Generation &amp; Outreach"),
    "it": ("Soluzioni Marketing Commerciale", "Lead Generation e Contatti Qualificati"),
    "es": ("Generación de Leads y Prospección", "Lead Generation y Contactos Cualificados"),
    "sq": ("Gjenerim dhe Kontaktim Lead-esh", "Lead Generation dhe Kontakte të Kualifikuara"),
}

# The sentence appended to the card, and the end of the card paragraph it attaches to.
CARD_TAIL = {
    "en": ("lead.</p>",
           ' See how our <a href="/services-lead-generation">lead generation service</a> works.</p>'),
    "it": ("l'uno.</p>",
           ' Scopri come funziona il nostro servizio di <a href="/it/services-lead-generation">lead generation</a>.</p>'),
    "es": ("lead.</p>",
           ' Descubre cómo funciona nuestro servicio de <a href="/es/services-lead-generation">lead generation</a>.</p>'),
    "sq": ("secili.</p>",
           ' Shihni si funksionon shërbimi ynë i <a href="/sq/services-lead-generation">lead generation</a>.</p>'),
}

# The hub sentence, appended inside the sales funnel block's description.
HUB = {
    "en": ("sales funnel design</a> service.",
           ' Before it, our <a href="/services-lead-generation">lead generation</a> service brings the enquiries in.'),
    "it": ("</a> service.", None),   # resolved below from the shipped Italian wording
}


def patch_specs():
    """The guide's related-service line, in the content spec that builds it."""
    changed = []
    for lang in TREES:
        rel = "answer-content/lead-quality-%s.json" % lang
        fp = os.path.join(HERE, "answer-content", "lead-quality-%s.json" % lang)
        s = io.open(fp, encoding="utf-8", newline="").read()
        d = json.loads(s)
        if d["service_slug"] == SLUG:
            print("  %-34s already points at the new page" % rel)
            continue
        old_slug = '"service_slug": %s' % json.dumps(d["service_slug"], ensure_ascii=False)
        new_slug = '"service_slug": %s' % json.dumps(SLUG, ensure_ascii=False)
        old_name = '"service_name": %s' % json.dumps(d["service_name"], ensure_ascii=False)
        new_name = '"service_name": %s' % json.dumps(SERVICE_NAME[lang], ensure_ascii=False)
        for old, new in ((old_slug, new_slug), (old_name, new_name)):
            if s.count(old) != 1:
                raise SystemExit("  ! %s: %r appears %d times" % (rel, old[:40], s.count(old)))
            s = s.replace(old, new)
        json.loads(s)
        io.open(fp, "w", encoding="utf-8", newline="").write(s)
        changed.append(rel)
        print("  %-34s -> %s" % (rel, SLUG))
    return changed


def patch_home():
    for lang, tree in TREES.items():
        fp = os.path.join(SITE, tree, "index.html") if tree else os.path.join(SITE, "index.html")
        rel = ("%s/index.html" % tree) if tree else "index.html"
        s = io.open(fp, encoding="utf-8", newline="").read()
        if SLUG in s:
            print("  %-34s already links it" % rel)
            continue

        old_t, new_t = CARD_TITLE[lang]
        if old_t != new_t:
            marker = '<h3 class="client-card__title">%s</h3>' % old_t
            if s.count(marker) != 1:
                raise SystemExit("  ! %s: card title %r appears %d times"
                                 % (rel, old_t, s.count(marker)))
            s = s.replace(marker, '<h3 class="client-card__title">%s</h3>' % new_t)

        end, add = CARD_TAIL[lang]
        if s.count(end) != 1:
            raise SystemExit("  ! %s: card paragraph ending %r appears %d times"
                             % (rel, end, s.count(end)))
        s = s.replace(end, add)
        io.open(fp, "w", encoding="utf-8", newline="").write(s)
        print("  %-34s card renamed and linked" % rel)


def patch_hub():
    """One sentence in the sales funnel block, anchored on that block's own service link."""
    for lang, tree in TREES.items():
        fp = os.path.join(SITE, tree, "services.html") if tree \
            else os.path.join(SITE, "services.html")
        rel = ("%s/services.html" % tree) if tree else "services.html"
        s = io.open(fp, encoding="utf-8", newline="").read()
        if SLUG in s:
            print("  %-34s already links it" % rel)
            continue
        anchor = '<a href="/%sservices-sales-funnel">' % ((tree + "/") if tree else "")
        i = s.find(anchor)
        if i < 0:
            raise SystemExit("  ! %s: no link to the sales funnel service page" % rel)
        j = s.find("</a>", i)
        k = s.find("</p>", j)
        if k < 0:
            raise SystemExit("  ! %s: cannot find the end of that description" % rel)
        add = HUB_SENTENCE[lang] % ((tree + "/") if tree else "")
        s = s[:k] + add + s[k:]
        io.open(fp, "w", encoding="utf-8", newline="").write(s)
        print("  %-34s hub link added" % rel)


HUB_SENTENCE = {
    "en": ' Before any of it, our <a href="/%sservices-lead-generation">lead generation</a> service brings the enquiries in.',
    "it": ' Prima ancora, il nostro servizio di <a href="/%sservices-lead-generation">lead generation</a> porta le richieste.',
    "es": ' Antes de todo eso, nuestro servicio de <a href="/%sservices-lead-generation">lead generation</a> trae las consultas.',
    "sq": ' Para të gjithës, shërbimi ynë i <a href="/%sservices-lead-generation">lead generation</a> sjell kërkesat.',
}


def main():
    patch_specs()
    patch_home()
    patch_hub()
    print("done. now: python .build/gen-answer-post.py lead-quality, then the sitemap and the gate.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
