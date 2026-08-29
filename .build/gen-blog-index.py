#!/usr/bin/env python3
"""Lay out the blog index as five named groups, in all four trees.

REPLACES gen-city-cards.py, which assumed the page had exactly one card grid. It found that
grid with html.index(GRID) and stopped, so with three grids it would have renumbered the first
group's reveal delays, enforced the LCP rule inside the first group only, and silently ignored
the other two. Rather than patch three functions to loop, this script owns the whole index.

WHY GROUPS AT ALL. The page was one flat wall: a single section, fourteen identical cards, and
no <h2> anywhere, so the <h1> dropped straight to the cards' <h3>s. Since the city guides
shipped it mixed three genuinely different kinds of post with nothing to separate them.

The reference was MINARANK's blog, which gets its order from grouping, counts, heading rules
and spacing ratios ALONE: every row is the same size and there is no featured card. That is the
part borrowed. The visual language stays this site's own, so the group headings reuse
.section__head and .section__title--center and inherit the animated underline for free.

THREE THINGS THAT MUST HOLD, and the reason each is re-asserted here rather than trusted:

  reveal delays   cycle 0,1,2 and RESTART IN EACH GROUP, because each group starts a new visual
                  row on the 3-column desktop grid. A continuous cycle across groups would
                  stagger the second group's first row from the middle.
  the LCP image   exactly ONE fetchpriority="high" on the page, on the first card in DOM order,
                  and that card alone omits loading. It broke silently once before, when a
                  prepended card took fetchpriority and the demoted one never got lazy back.
                  Services now lead, so the LCP is the social-media card, not Milan's.
  the ItemList    positions 1..N in DOM order with numberOfItems matching. Nothing in
                  verify-langs.ps1 counts cards or checks numberOfItems, so this is the only
                  thing keeping them honest.

THE ITEMLIST KEY ORDER IS LOAD-BEARING. Gate check 14 parses it with a literal regex,
'"@type":\\s*"BlogPosting",\\s*"headline":\\s*"([^"]+)",\\s*"url":\\s*"([^"]+)"', and then
compares each headline against the target page's real <h1>. Serialise those three keys in any
other order and the check matches zero items and passes vacuously, which is worse than failing.
Cards are therefore the source of truth here: headline, url, image and date are all read back
out of the emitted card, so the JSON cannot drift from what a reader sees.

    python .build/gen-blog-index.py
"""
import html as htmllib
import io
import json
import os
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
SITE_DIR = os.path.dirname(_HERE)
SITE = "https://www.marketingpro-agency.com"

TREES = {"en": "", "it": "it", "es": "es", "sq": "sq"}

# Order on the page. The eight service guides already sit in the order $PAGES and services.html
# use, so only the four city cards actually move when this first runs.
GROUPS = [
    ("by-service", ["blog-social-media", "blog-advertising", "blog-website", "blog-seo",
                    "blog-sales-funnel", "blog-photo-video", "blog-renders", "blog-catalogues"]),
    # Decision posts: each one answers a question somebody types before they hire anybody.
    # Second rather than first on purpose, so the LCP card stays the social-media guide and
    # the single fetchpriority="high" does not move to a different image on every reorder.
    ("answers",    ["blog-boost-or-campaign", "blog-lead-quality",
                    "blog-in-house-or-agency", "blog-showrooms"]),
    # Trade guides. A group of their own rather than folded into "answers": these answer
    # "marketing for MY industry" rather than a decision question, and they carry
    # articleSection "Industry guides" in their own JSON-LD.
    ("verticals",  ["blog-windows-and-doors", "blog-stoves-and-heating",
                    "blog-builders", "blog-restaurants"]),
    ("by-city",    ["blog-milano", "blog-roma", "blog-lugano", "blog-ticino"]),
    ("articles",   ["article-1", "article-2"]),
]

# Everything the page says, per tree. Nothing here may contain an em dash (check 12), and
# nothing in es/ or sq/ may reuse an English stock string from check 13's list.
COPY = {
    "en": {
        "title": "Marketing Blog: Guides by Service and by City | MarketingPro",
        "desc": "Practical guides on social media, ads, websites, SEO, funnels, video, renders "
                "and catalogues, plus city guides for Milan, Rome, Lugano and Ticino.",
        "lead": "One deep dive per service, the questions we get asked most, and guides for the cities we work in.",
        "aria": "Jump to a section",
        "all": "All",
        "groups": {"by-service": "One guide per service", "answers": "The questions we get asked", "verticals": "Guides by trade",
                   "by-city": "Marketing by city",
                   "articles": "Articles"},
        "chips": {"by-service": "By service", "answers": "Answers", "verticals": "By trade", "by-city": "By city", "articles": "Articles"},
    },
    "it": {
        "title": "Blog di Marketing: Guide per Servizio e Città | MarketingPro",
        "desc": "Guide pratiche su social, sponsorizzate, siti web, SEO, funnel, video, render e "
                "cataloghi, più le guide per Milano, Roma, Lugano e il Ticino.",
        "lead": "Un approfondimento per ogni servizio, le domande che ci fanno più spesso "
                "e le guide per le città in cui lavoriamo.",
        "aria": "Vai a una sezione",
        "all": "Tutte",
        "groups": {"by-service": "Una guida per ogni servizio", "answers": "Le domande che ci fanno", "verticals": "Guide per settore",
                   "by-city": "Marketing per città",
                   "articles": "Articoli"},
        "chips": {"by-service": "Per servizio", "answers": "Risposte", "verticals": "Per settore", "by-city": "Per città", "articles": "Articoli"},
    },
    "es": {
        # "Blog de marketing: guías por servicio y ciudad" came to 61, one over check 16's cap.
        # Dropping the "Blog de marketing:" frame rather than mangling the useful half.
        "title": "Guías de marketing por servicio y ciudad | MarketingPro",
        "desc": "Guías prácticas sobre redes sociales, anuncios, sitios web, SEO, embudos, "
                "vídeo, renders y catálogos, más las guías de Milán, Roma, Lugano y el Tesino.",
        "lead": "Un análisis a fondo de cada servicio, las preguntas que más nos hacen "
                "y las guías de las ciudades donde trabajamos.",
        "aria": "Ir a una sección",
        "all": "Todas",
        "groups": {"by-service": "Una guía por servicio", "answers": "Las preguntas que nos hacen", "verticals": "Guías por sector",
                   "by-city": "Marketing por ciudad",
                   "articles": "Artículos"},
        "chips": {"by-service": "Por servicio", "answers": "Respuestas", "verticals": "Por sector", "by-city": "Por ciudad", "articles": "Artículos"},
    },
    "sq": {
        "title": "Blog Marketingu: Udhëzues Shërbimi dhe Qyteti | MarketingPro",
        "desc": "Udhëzues praktikë për social media, reklama, faqe interneti, SEO, funnel, video, "
                "render dhe katalogë, si dhe udhëzues për Milano, Romë, Lugano dhe Tiçino.",
        "lead": "Një analizë e thelluar për çdo shërbim, pyetjet që na bëhen më shpesh "
                "dhe udhëzues për qytetet ku punojmë.",
        "aria": "Kaloni te një seksion",
        "all": "Të gjitha",
        "groups": {"by-service": "Një udhëzues për çdo shërbim", "answers": "Pyetjet që na bëhen", "verticals": "Udhëzues sipas sektorit",
                   "by-city": "Marketing sipas qytetit",
                   "articles": "Artikuj"},
        "chips": {"by-service": "Sipas shërbimit", "answers": "Përgjigje", "verticals": "Sipas sektorit", "by-city": "Sipas qytetit",
                  "articles": "Artikuj"},
    },
}

CARD_RX = re.compile(
    r'<article class="article-card reveal" data-reveal(?: data-reveal-delay="\d+")?>.*?</article>',
    re.S)
HREF_RX = re.compile(r'<a class="article-card__link" href="([^"]*)"')


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def attr(s):
    return esc(s).replace('"', "&quot;")


def txt(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


def page(tree, slug):
    return os.path.join(SITE_DIR, tree, slug + ".html") if tree \
        else os.path.join(SITE_DIR, slug + ".html")


def read(tree, slug):
    return io.open(page(tree, slug), encoding="utf-8", newline="").read()


# --------------------------------------------------------------------------- building a card

def build_card(tree, slug):
    """A card for a page that has none yet, built from the TARGET PAGE, never translated from
    the English card. Check 14 compares the card headline against the target's <h1>, so reading
    the h1 straight off the page it points at is the only way that cannot drift."""
    s = read(tree, slug)
    m = s[s.index("<main"):s.index("</main>")]
    h1 = txt(re.search(r"<h1[^>]*>(.*?)</h1>", m, re.S).group(1))
    desc = re.search(r'<meta name="description" content="(.*?)"', s, re.S).group(1)
    pic = re.search(r"<picture>(.*?)</picture>", m, re.S).group(1)
    img_src = re.search(r'<img[^>]*src="([^"]*)"', pic).group(1)
    w = re.search(r'width="(\d+)"', pic).group(1)
    h = re.search(r'height="(\d+)"', pic).group(1)
    alt = re.search(r'alt="([^"]*)"', pic).group(1)
    hero = re.search(r'class="article-hero__meta">(.*?)</p>', m, re.S).group(1)
    dt = re.search(r'<time datetime="([^"]*)"', hero).group(1)
    date_disp = txt(re.search(r"<time[^>]*>(.*?)</time>", hero, re.S).group(1))
    # the hero meta reads: <time>date</time> SEP read-time SEP by-line
    parts = [p.strip() for p in re.split(r"·|&middot;", txt(hero))]
    read_time = parts[1] if len(parts) > 1 else ""

    base = img_src.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    imgdir = "../assets/img" if tree else "assets/img"
    root = f"/{tree}" if tree else ""
    return (
        f'<article class="article-card reveal" data-reveal>\n'
        f'            <a class="article-card__link" href="{root}/{slug}">\n'
        f'              <figure class="article-card__media"><picture>\n'
        f'  <source srcset="{imgdir}/{base}.webp" type="image/webp" />\n'
        f'  <img src="{imgdir}/{base}.jpg" height="{h}" width="{w}" alt="{attr(alt)}" '
        f'loading="lazy" decoding="async" />\n'
        f'</picture></figure>\n'
        f'              <div class="article-card__body">\n'
        f'                <h3 class="article-card__title">{esc(h1)}</h3>\n'
        f'                <p class="article-card__excerpt">{desc}</p>\n'
        f'                <p class="article-card__meta"><time datetime="{dt}">{esc(date_disp)}</time>'
        f' &middot; {esc(read_time)}</p>\n'
        f'              </div>\n'
        f'            </a>\n'
        f'          </article>'
    )


def reindent(card, extra):
    """Shift a card block right, leaving the <picture> block alone.

    wrap-picture.py deliberately dedents <source>/<img>/</picture> to column 0. Preserving that
    keeps this script's output stable if wrap-picture.py is ever run again."""
    out = []
    for line in card.split("\n"):
        lead = len(line) - len(line.lstrip())
        out.append(" " * extra + line if lead >= 10 else line)
    return "\n".join(out)


# --------------------------------------------------------------------------- the invariants

def set_delay(card, i):
    """0,1,2 cycling. The literal <article ...> string is what the old script matched on, so it
    is rebuilt here rather than regex-patched, and stays byte-identical in shape."""
    open_tag = '<article class="article-card reveal" data-reveal>' if i % 3 == 0 else \
        f'<article class="article-card reveal" data-reveal data-reveal-delay="{i % 3}">'
    return re.sub(r'<article class="article-card reveal" data-reveal(?: data-reveal-delay="\d+")?>',
                  lambda _m: open_tag, card, count=1)


def set_loading(card, is_lcp):
    tag = re.search(r"<img\b[^>]*>", card).group(0)
    new = re.sub(r'\s+(?:fetchpriority|loading)="[^"]*"', "", tag)
    if is_lcp:
        new = new.replace("<img ", '<img fetchpriority="high" ', 1)
    elif ' decoding="async"' in new:
        new = new.replace(' decoding="async"', ' loading="lazy" decoding="async"', 1)
    else:
        new = new.replace("<img ", '<img loading="lazy" ', 1)
    return card.replace(tag, new, 1)


def collapse_lang_arrays(s):
    def fix(m):
        items = re.findall(r'"([^"]*)"', m.group(2))
        return '"%s": [%s]' % (m.group(1), ", ".join('"%s"' % i for i in items))
    return re.sub(r'"(inLanguage|availableLanguage)":\s*\[([^\]]*)\]', fix, s)


def rewrite_itemlist(page_html, cards_in_order, lang):
    """Rebuilt FROM THE CARDS, so the JSON cannot disagree with the page. Key order
    @type -> headline -> url is required by check 14's literal regex."""
    tag = '<script type="application/ld+json">'
    i = page_html.index(tag) + len(tag)
    j = page_html.index("</script>", i)
    graph = json.loads(page_html[i:j])

    items = []
    for pos, card in enumerate(cards_in_order, 1):
        href = HREF_RX.search(card).group(1)
        headline = htmllib.unescape(
            txt(re.search(r'class="article-card__title">(.*?)</h3>', card, re.S).group(1)))
        img = re.search(r'<img[^>]*src="([^"]*)"', card).group(1).rsplit("/", 1)[-1]
        dt = re.search(r'<time datetime="([^"]*)"', card).group(1)
        items.append({
            "@type": "ListItem",
            "position": pos,
            "item": {
                "@type": "BlogPosting",
                "headline": headline,
                "url": f"{SITE}{href}",
                "image": f"{SITE}/assets/img/{img}",
                "datePublished": dt,
                "inLanguage": lang,
                "author": {"@id": f"{SITE}/about#author"},
                "publisher": {"@id": f"{SITE}/#organization"},
            },
        })

    for node in graph["@graph"]:
        if node.get("@type") == "ItemList":
            node["itemListElement"] = items
            node["numberOfItems"] = len(items)

    body = collapse_lang_arrays(
        json.dumps(graph, ensure_ascii=False, indent=2)).replace("\n", "\n  ")
    return page_html[:i] + "\n  " + body + "\n  " + page_html[j:]


# --------------------------------------------------------------------------- the page

def chips(c, counts, total):
    L = [f'        <nav class="topics" aria-label="{attr(c["aria"])}">']
    L.append(f'          <a class="topic topic--all" href="#posts">{esc(c["all"])} '
             f'<span class="topic__n">{total}</span></a>')
    for gid, _slugs in GROUPS:
        L.append(f'          <a class="topic" href="#{gid}">{esc(c["chips"][gid])} '
                 f'<span class="topic__n">{counts[gid]}</span></a>')
    L.append("        </nav>")
    return "\n".join(L)


def build_main_body(c, by_group):
    """Everything between </header> and </div></section>: the chips, then the three groups."""
    counts = {gid: len(by_group[gid]) for gid, _ in GROUPS}
    total = sum(counts.values())

    L = ["", chips(c, counts, total), "", '        <div id="posts">']
    for gid, _slugs in GROUPS:
        L.append(f'          <div class="post-group" id="{gid}">')
        L.append('            <header class="section__head reveal" data-reveal>')
        L.append(f'              <h2 class="section__title section__title--center">'
                 f'{esc(c["groups"][gid])} <span class="post-group__n">{counts[gid]}</span></h2>')
        L.append("            </header>")
        L.append('            <div class="articles articles--blog">')
        for card in by_group[gid]:
            L.append("              " + reindent(card, 4).lstrip())
        L.append("            </div>")
        L.append("          </div>")
    L.append("        </div>")
    return "\n".join(L)


def run(lang, tree):
    p = page(tree, "blog")
    s = io.open(p, encoding="utf-8", newline="").read()
    c = COPY[lang]

    # collect the cards that already exist, keyed by slug
    have = {}
    for m in CARD_RX.finditer(s):
        have[HREF_RX.search(m.group(0)).group(1).rsplit("/", 1)[-1]] = m.group(0)

    built = []
    by_group, ordered = {}, []
    for gid, slugs in GROUPS:
        by_group[gid] = []
        for slug in slugs:
            card = have.get(slug)
            if card is None:
                card = build_card(tree, slug)
                built.append(slug)
            by_group[gid].append(card)

    # delays restart per group; the LCP is the very first card on the page
    n = 0
    for gid, _slugs in GROUPS:
        for i, card in enumerate(by_group[gid]):
            card = set_delay(card, i)
            card = set_loading(card, n == 0)
            by_group[gid][i] = card
            ordered.append(card)
            n += 1

    # splice: replace everything from the first card grid to the end of the container
    head_end = s.index("</header>", s.index('class="section__head')) + len("</header>")
    grid_start = s.index('<div class="articles articles--blog">')
    tail_start = s.index("</div>", s.rindex("</article>", grid_start)) + len("</div>")
    body = build_main_body(c, by_group)
    s = s[:head_end] + "\n" + body + s[tail_start:]

    # copy
    s = re.sub(r"<title>.*?</title>", lambda _m: f"<title>{esc(c['title'])}</title>", s, count=1)
    s = re.sub(r'<meta name="description" content="[^"]*" />',
               lambda _m: f'<meta name="description" content="{attr(c["desc"])}" />', s, count=1)
    s = re.sub(r'(<p class="section__lead section__lead--center">).*?(</p>)',
               lambda m: m.group(1) + esc(c["lead"]) + m.group(2), s, count=1, flags=re.S)

    s = rewrite_itemlist(s, ordered, lang)
    io.open(p, "w", encoding="utf-8", newline="").write(s)

    rel = os.path.relpath(p, SITE_DIR).replace("\\", "/")
    print(f"  {rel:16} {len(ordered)} cards in {len(GROUPS)} groups"
          f"  title {len(c['title']):>2}  desc {len(c['desc']):>3}"
          + (f"  built {', '.join(built)}" if built else ""))


if __name__ == "__main__":
    bad = [(l, k, len(COPY[l][k])) for l in COPY for k in ("title", "desc")
           if (k == "title" and len(COPY[l][k]) > 60)
           or (k == "desc" and not 120 <= len(COPY[l][k]) <= 155)]
    if bad:
        raise SystemExit("  ! copy outside the gate limits: %s" % bad)
    for lang, tree in TREES.items():
        run(lang, tree)
    print("done")
