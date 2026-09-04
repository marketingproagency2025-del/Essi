#!/usr/bin/env python3
"""Put OF Outdoorkitchen first on the portfolio, in all four trees.

NOT gen-portfolio.py. That script is quarantined: its own docstring records that it is behind
the shipped pages and made four destructive changes on 2026-08-24, including stripping the
<picture>/WebP wrappers and touching only the English tree. This one edits the shipped HTML in
place, identically across the four trees, and asserts every anchor it depends on.

Four things move together, and a half-done version of any of them fails the gate:

  order        the new case goes FIRST, so the run becomes
               OF Outdoorkitchen / OFYR Italia / Fly System / Rika
  alternation  four cases alternate normal / reverse / normal / reverse, so Rika gains
               split--reverse. OFYR and Fly System keep the classes they already have.
  the LCP      exactly one fetchpriority="high" per page, on the first case, and that image
               alone omits loading. Fly System hands both over to the new case, and the
               <link rel=preload> in the head has to name the same file, which is gate check 22.
  structured   a fourth ListItem at position 1, the rest renumbered.

The Instagram link is deliberately absent. Every other case carries one, but the handle was not
supplied, and guessing it would put a dead link on a client page and a wrong sameAs in the
structured data. One line each to add when it arrives.

    python .build/add-of-outdoorkitchen.py
"""
import io
import json
import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(_HERE)
URL = "https://www.marketingpro-agency.com"

TREES = {"en": "", "it": "it", "es": "es", "sq": "sq"}

CLIENT = "OF Outdoorkitchen"
SLUG = "of-outdoorkitchen"
IMG = "case-of-grid"

# Title candidates per tree, longest first. The cap is 60 (gate check 14) and the English title
# was already sitting at exactly 60, so a fourth brand name could not be added: these name the
# trades instead, which is also the half that does not need editing when a client list changes.
TITLES = {
    "en": ["Our Work: Outdoor Kitchens, Windows, Stoves | MarketingPro",
           "Client Work: Outdoor Kitchens and Windows | MarketingPro"],
    "it": ["Portfolio: Cucine da Esterno, Infissi, Stufe | MarketingPro",
           "Portfolio: Cucine da Esterno e Infissi | MarketingPro"],
    "es": ["Cocinas de Exterior, Ventanas y Estufas | MarketingPro",
           "Portfolio: Cocinas de Exterior, Ventanas | MarketingPro"],
    "sq": ["Portfolio: Kuzhina të Jashtme, Dritare, Stufa | MarketingPro",
           "Portfolio: Kuzhina të Jashtme dhe Dritare | MarketingPro"],
}

# Only the English H1 names the clients; it/es/sq already use a generic heading, so they are
# left alone rather than given a new one they never had.
H1 = {"en": "Client Work: Outdoor Kitchens, Windows and Stoves"}

DESC = {
    "en": "Outdoor kitchens, windows and stoves: social channels, Meta campaigns, photo and "
          "video, and every lead qualified before it reaches the sales team.",
    "it": "Cucine da esterno, infissi e stufe: social, campagne Meta, foto e video, e ogni lead "
          "lo chiamiamo e lo qualifichiamo prima di passarlo.",
    "es": "Cocinas de exterior, ventanas y estufas: redes sociales, campañas en Meta, foto y "
          "vídeo, y cada lead calificado antes de llegar a quien vende.",
    "sq": "Kuzhina të jashtme, dritare dhe stufa: social media, fushata në Meta, foto dhe video, "
          "dhe çdo lead i kualifikuar para se t'ua dorëzojmë.",
}

ALT = {
    "en": "The OF Outdoorkitchen Instagram feed, showing built-in outdoor kitchens in gardens, "
          "on terraces and beside pools",
    "it": "Il feed Instagram di OF Outdoorkitchen, con cucine da esterno in giardini, su terrazze "
          "e a bordo piscina",
    "es": "El feed de Instagram de OF Outdoorkitchen, con cocinas de exterior en jardines, "
          "terrazas y bordes de piscina",
    "sq": "Feed-i i Instagram-it i OF Outdoorkitchen, me kuzhina të jashtme në kopshte, tarraca "
          "dhe buzë pishinave",
}

META = {
    "en": "Outdoor kitchens &middot; Italy",
    "it": "Cucine da esterno &middot; Italia",
    "es": "Cocinas de exterior &middot; Italia",
    "sq": "Kuzhina të jashtme &middot; Itali",
}

BODY = {
    "en": [
        "OF Outdoorkitchen builds modular outdoor kitchens: powder-coated and stainless units "
        "with built-in grills, sinks and refrigeration, configured to a plan and then installed "
        "in gardens, on terraces and beside pools across Italy.",
        "A kitchen like this is chosen from a configuration and judged finished, in somebody "
        "else's garden, which is exactly what the feed is for. We run the channels and the paid "
        "campaigns, produce the photography and video, and call and qualify every enquiry before "
        "it reaches the people who sell.",
    ],
    "it": [
        "OF Outdoorkitchen realizza cucine da esterno modulari: elementi in acciaio e verniciati "
        "con barbecue, lavelli e refrigerazione integrati, configurati su progetto e installati "
        "in giardini, su terrazze e a bordo piscina in tutta Italia.",
        "Una cucina così si sceglie da una configurazione e si giudica finita, nel giardino di "
        "qualcun altro, ed è esattamente a questo che serve il feed. Gestiamo noi i canali e le "
        "campagne, produciamo le foto e i video, e chiamiamo e qualifichiamo ogni richiesta "
        "prima che arrivi a chi vende.",
    ],
    "es": [
        "OF Outdoorkitchen fabrica cocinas de exterior modulares: módulos de acero y lacados con "
        "barbacoa, fregadero y refrigeración integrados, configurados sobre plano e instalados "
        "en jardines, terrazas y bordes de piscina por toda Italia.",
        "Una cocina así se elige desde una configuración y se juzga terminada, en el jardín de "
        "otra persona, que es justo para lo que sirve el feed. Llevamos los canales y las "
        "campañas, producimos la fotografía y el vídeo, y llamamos y calificamos cada consulta "
        "antes de que llegue a quien vende.",
    ],
    "sq": [
        "OF Outdoorkitchen prodhon kuzhina të jashtme modulare: module prej çeliku dhe të lyera "
        "me skarë, lavaman dhe ftohje të integruar, të konfiguruara sipas projektit dhe të "
        "montuara në kopshte, tarraca dhe buzë pishinave në gjithë Italinë.",
        "Një kuzhinë e tillë zgjidhet nga një konfigurim dhe gjykohet e përfunduar, në kopshtin e "
        "dikujt tjetër, dhe pikërisht për këtë shërben feed-i. Ne i drejtojmë kanalet dhe "
        "fushatat, prodhojmë fotot dhe videot, dhe telefonojmë e kualifikojmë çdo kërkesë "
        "përpara se të mbërrijë te ata që shesin.",
    ],
}

# Reused verbatim from each tree's own OFYR block rather than retranslated, so the four cases
# cannot drift into four different names for one service.
SERVICES = {
    "en": [("/services-social-media", "Social media management"),
           ("/services-advertising", "Meta ad campaigns"),
           ("/services-photo-video", "Photo and video production"),
           ("/services-sales-funnel", "Lead qualification and follow-up")],
    "it": [("/it/services-social-media", "Gestione Social Media"),
           ("/it/services-advertising", "Gestione Sponsorizzate Meta"),
           ("/it/services-photo-video", "Produzione Foto e Video"),
           ("/it/services-sales-funnel", "Funnel di Vendita e Qualifica dei Lead")],
    "es": [("/es/services-social-media", "Gestión de redes sociales"),
           ("/es/services-advertising", "Campañas publicitarias en Meta"),
           ("/es/services-photo-video", "Producción de foto y vídeo"),
           ("/es/services-sales-funnel", "Calificación y seguimiento de leads")],
    "sq": [("/sq/services-social-media", "Menaxhim i social media"),
           ("/sq/services-advertising", "Fushata reklamuese në Meta"),
           ("/sq/services-photo-video", "Prodhim fotosh dhe videosh"),
           ("/sq/services-sales-funnel", "Kualifikim i lead-eve dhe ndjekje e kontakteve")],
}


def img_prefix(tree):
    return "assets/img" if not tree else "../assets/img"


def case_block(lang, tree):
    a = img_prefix(tree)
    lines = [
        '        <div class="split__grid feature-row reveal" id="%s" data-reveal>' % SLUG,
        '          <div class="split__media">',
        '            <div class="case-frame case-frame--grid">',
        "              <picture>",
        '                <source srcset="%s/%s.webp" type="image/webp" />' % (a, IMG),
        '                <img fetchpriority="high" src="%s/%s.jpg" width="738" height="984" '
        'alt="%s" decoding="async" />' % (a, IMG, ALT[lang]),
        "              </picture>",
        "            </div>",
        "          </div>",
        '          <div class="split__text">',
        '            <h2 class="case__client feature-row__title">%s</h2>' % CLIENT,
        '            <span class="case__meta">%s</span>' % META[lang],
    ]
    for p in BODY[lang]:
        lines.append("            <p>%s</p>" % p)
    lines.append('            <ul class="service__list">')
    for href, label in SERVICES[lang]:
        lines.append('              <li><a href="%s">%s</a></li>' % (href, label))
    lines.append("            </ul>")
    lines.append("          </div>")
    lines.append("        </div>")
    lines.append("")
    return "\n".join(lines)


def sub1(s, pattern, repl, label, flags=0):
    out, n = re.subn(pattern, lambda _m: repl, s, count=1, flags=flags)
    if n != 1:
        raise SystemExit("  ! %s: expected 1 replacement, made %d" % (label, n))
    return out


def pick_title(lang):
    for t in TITLES[lang]:
        if len(t) <= 60:
            return t
    raise SystemExit("  ! %s: no title candidate fits 60 chars" % lang)


def rewrite_jsonld(s, tree):
    """A fourth ListItem at position 1, the rest renumbered. Parsed rather than regexed: the
    graph carries @id references that are textually identical to definitions."""
    tag = '<script type="application/ld+json">'
    i = s.index(tag) + len(tag)
    j = s.index("</script>", i)
    graph = json.loads(s[i:j])
    page = "%s/%s" % (URL, ("%s/portfolio" % tree) if tree else "portfolio")
    for node in graph["@graph"]:
        if node.get("@type") != "ItemList":
            continue
        items = node["itemListElement"]
        if any(CLIENT in json.dumps(it, ensure_ascii=False) for it in items):
            return s  # already present
        new = {
            "@type": "ListItem",
            "position": 1,
            "item": {
                "@type": "CreativeWork",
                "name": "%s - marketing by MarketingPro" % CLIENT,
                "creator": {"@id": "%s/#organization" % URL},
                # no sameAs: the Instagram handle was not supplied, and a guessed one would be
                # a false claim about the client's identity in structured data
                "about": {"@type": "Organization", "name": CLIENT},
                "url": "%s#%s" % (page, SLUG),
            },
        }
        items.insert(0, new)
        for n, it in enumerate(items, start=1):
            it["position"] = n
        if "numberOfItems" in node:
            node["numberOfItems"] = len(items)
    body = json.dumps(graph, ensure_ascii=False, indent=2).replace("\n", "\n  ")
    return s[:i] + "\n  " + body + "\n  " + s[j:]


for lang, tree in TREES.items():
    path = os.path.join(SITE, tree, "portfolio.html") if tree else os.path.join(SITE, "portfolio.html")
    s = io.open(path, encoding="utf-8", newline="").read()
    if SLUG in s:
        print("  %-22s already has the case" % (tree or "en"))
        continue

    a = img_prefix(tree)

    # 1. the LCP hands over. Fly System loses fetchpriority and becomes lazy like its neighbours.
    old_fly = '<img fetchpriority="high" src="%s/case-flysystem-grid.jpg"' % a
    new_fly = '<img loading="lazy" src="%s/case-flysystem-grid.jpg"' % a
    s = sub1(s, re.escape(old_fly), new_fly, "%s fly-system LCP" % lang)

    # 2. the head preload has to name what the first <picture> actually fetches (gate check 22)
    s = sub1(s, re.escape("%s/case-flysystem-grid.webp" % a),
             "%s/%s.webp" % (a, IMG), "%s preload" % lang)

    # 3. Rika becomes the fourth case, so it flips side
    s = sub1(s, r'<div class="split__grid feature-row reveal" id="rika"',
             '<div class="split__grid feature-row split--reverse reveal" id="rika"',
             "%s rika alternation" % lang)

    # 4. the new case goes in front of Fly System
    anchor = '        <div class="split__grid feature-row reveal" id="fly-system" data-reveal>'
    if s.count(anchor) != 1:
        raise SystemExit("  ! %s: fly-system anchor found %d times" % (lang, s.count(anchor)))
    s = s.replace(anchor, case_block(lang, tree) + anchor, 1)

    # 5. head and headings
    title = pick_title(lang)
    s = sub1(s, r"<title>.*?</title>", "<title>%s</title>" % title, "%s title" % lang, re.S)
    s = sub1(s, r'<meta property="og:title" content="[^"]*" />',
             '<meta property="og:title" content="%s" />' % title, "%s og:title" % lang)
    s = sub1(s, r'<meta name="twitter:title" content="[^"]*" />',
             '<meta name="twitter:title" content="%s" />' % title, "%s twitter:title" % lang)
    # all three description variants carry the same text on this page
    for attr, key in (("name", "description"), ("property", "og:description"),
                      ("name", "twitter:description")):
        s = sub1(s, r'<meta %s="%s" content="[^"]*" />' % (attr, re.escape(key)),
                 '<meta %s="%s" content="%s" />' % (attr, key, DESC[lang]),
                 "%s %s" % (lang, key))
    if lang in H1:
        # the open tag is preserved by matching it and rebuilding, because sub1 replaces with a
        # literal and a backreference would arrive as text
        m = re.search(r'(<h1[^>]*>)([^<]*)(</h1>)', s)
        if not m:
            raise SystemExit("  ! %s: no h1 found" % lang)
        s = s.replace(m.group(0), m.group(1) + H1[lang] + m.group(3), 1)

    # 6. structured data
    s = rewrite_jsonld(s, tree)

    io.open(path, "w", encoding="utf-8", newline="").write(s)
    rel = os.path.relpath(path, SITE).replace("\\", "/")
    print("  %-22s title %2d  %s" % (rel, len(title), title))

print("done")
