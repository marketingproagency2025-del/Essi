#!/usr/bin/env python3
"""DO NOT RUN THIS WITHOUT READING THE DIFF. It is behind the shipped pages.

Run on 2026-08-24 it made four destructive changes to portfolio.html and touched only the
English tree, leaving the other three untouched and therefore divergent:

  - stripped the <picture>/<source> WebP wrappers off nine images, so every one of them would
    have fallen back to the JPEG
  - rewrote the H1 from "Client Work: Fly System, OFYR Italia and Rika" to "Work We Have
    Shipped", undoing an edit made in the page
  - exploded "inLanguage" and "availableLanguage" onto multiple lines, which gate checks 9 and
    10 compare against the single-line literal ["en", "it", "es", "sq"] and would have failed
  - only writes the root tree, so it cannot be used to fix anything in it/, es/ or sq/

The OFYR record in it was already stale once before and would have reverted the client's own
correction; that was fixed in e28d37d. This is the same class of problem in the page body, and
it has not been fixed. Until it is, edit portfolio.html directly and keep this file's data in
step by hand.

Rebuild the Portfolio page around real client work.

What was there: ten stock photographs with alt text about a Cycladic alley, a
grey cat and a watermelon drink, headed "the creative work and campaigns we're
proud of"; two generic "Creative Solutions" panels; and a five-star testimonial
signed "Happy Client", avatar "HC". The third gallery row repeated the first
three images verbatim to fill space. A portfolio with nothing in it.

Three real engagements now replace it, and every claim traces to supplied
evidence: two Instagram grid screenshots and a 31-second company film.

WHAT IS DELIBERATELY NOT CLAIMED. No results, no revenue, no follower counts, no
campaign figures. The seven-campaign Meta table on /services stays where it is
and stays anonymous, because it has not been confirmed that those campaigns
belong to these three clients, and attributing real numbers to a named client on
a guess is the one mistake here that would be worth suing over. The pages claim
the services delivered and show the work; that is what the evidence supports.

Fly System's website is stated as live because flysystem.io was fetched and
checked before the sentence was written, not because the repo next door exists.

Each service in each list links to its own service page, so this page also
repairs an internal-link gap: the eight commercial pages previously had no
inbound links from anywhere except /services and their own guides.

    python .build/gen-portfolio.py
"""
import io
import json
import os
import re

from PIL import Image

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = 'https://www.marketingpro-agency.com'

SERVICE_LINKS = [
    ('services-social-media', 'Social media management'),
    ('services-advertising',  'Meta ad campaigns'),
    ('services-photo-video',  'Photo and video production'),
    ('services-sales-funnel', 'Lead qualification and follow-up'),
]

CASES = [
    {
        'id': 'fly-system',
        'client': 'Fly System',
        'meta': 'Windows, doors and outdoor systems &middot; Italy',
        'img': 'case-flysystem-grid',
        'alt': 'The Fly System Instagram feed, showing window systems, interiors and outdoor pergolas',
        'body': [
            'Fly System supplies doors, windows, floors and outdoor systems across Italy. '
            'We run the social channels and the paid campaigns, and we produce the photography '
            'and video that fills them, from the cutaway that explains a window profile to the '
            'finished pergola on a terrace.',
            'Every lead is called and qualified by us before it reaches their sales team, which '
            'is the same model we run for every client on this page.',
        ],
        'extra_service': ('services-website', 'Website design and build'),
        'live': 'Their website is one of ours, and it is live now at flysystem.io.',
        'ig': ('https://www.instagram.com/flysystem.it/', '@flysystem.it'),
    },
    {
        'id': 'ofyr-italia',
        'client': 'OFYR Italia',
        'meta': 'Outdoor cooking &middot; Milan, Italy',
        'img': 'case-ofyr-grid',
        'alt': 'The OFYR Italia Instagram feed, showing chefs cooking over open fire at outdoor events',
        'body': [
            'OFYR Italia sells outdoor cooking, and it is a product that only makes sense in use. '
            'So the content is built around chefs working over live fire, food coming off the '
            'plate, and the events where people can taste it rather than read about it.',
            'We run the channels and the campaigns, produce the photography and video, and '
            'qualify every enquiry before handing it over.',
        ],
        'extra_service': None,
        'live': None,
        'ig': ('https://www.instagram.com/ofyr_italia/', '@ofyr_italia'),
    },
    {
        'id': 'rika',
        'client': 'Rika',
        'meta': 'Wood and pellet stoves &middot; Italy',
        'img': None,          # this one is the film
        'alt': None,
        'body': [
            'Rika makes wood and pellet stoves. We produced the company film for its Premium '
            'Store: the drone approach over the building, then the showroom itself, the range '
            'along the floor, and the details that actually sell a stove in person, which are '
            'the fire behind the glass, the weight of the stone and the controls.',
            'Alongside the film we run the same stack as the others, from the channels and the '
            'campaigns through to the follow-up.',
        ],
        'extra_service': None,
        'live': None,
        'ig': None,
    },
]

# Stills pulled from the 4K master by make-video.py. A 4K source gives sharper
# gallery tiles than any stock photograph the page used to carry.
STILLS = [
    ('rika-fire',     'A wood fire burning behind the glass door of a stone-clad Rika stove'),
    ('rika-facade',   'The Rika store building, dark cladding with the illuminated Rika sign'),
    ('rika-range',    'A row of Rika pellet stoves lined up along the showroom wall'),
    ('rika-store',    'The Rika Premium Store sign on the showroom wall'),
    ('rika-stove',    'A black cylindrical Rika stove on display against a curtained wall'),
    ('rika-showroom', 'The showroom seating area beneath the wall quote from Karl Riener'),
]

TITLE = 'Client Work: Fly System, OFYR Italia and Rika | MarketingPro'
DESC = ('Real work for three clients: social channels, Meta campaigns, photo and video, '
        'and every lead qualified before it reaches their sales team.')
H1 = 'Work We Have Shipped'
LEAD = ('Three businesses in three markets, running the same model. We look after the '
        'channels, produce what goes on them, and call and qualify every lead before it '
        'reaches the people who sell.')


def dims(stem, ext='jpg'):
    with Image.open(f'assets/img/{stem}.{ext}') as im:
        return im.size


def build_main():
    L = []
    A = L.append
    A('  <main id="main" class="portfolio-main">')
    A('')
    A('    <nav class="breadcrumb" aria-label="Breadcrumb">')
    A('      <ol>')
    A('        <li><a href="/">Home</a></li>')
    A('        <li><span aria-current="page">Portfolio</span></li>')
    A('      </ol>')
    A('    </nav>')
    A('')
    # One section, not a head section stacked on a cases section: two .section
    # paddings plus the first row's own margin left a ~350px void under the lead.
    A('    <section class="section portfolio-cases">')
    A('      <div class="container">')
    A('        <header class="section__head reveal" data-reveal>')
    A(f'          <h1 class="section__title section__title--center">{H1}</h1>')
    A(f'          <p class="section__lead section__lead--center">{LEAD}</p>')
    A('        </header>')
    A('')

    for n, c in enumerate(CASES):
        rev = ' split--reverse' if n % 2 else ''
        A(f'        <div class="split__grid feature-row{rev} reveal" id="{c["id"]}" data-reveal>')
        A('          <div class="split__media">')
        if c['img']:
            w, h = dims(c['img'])
            eager = ' fetchpriority="high"' if n == 0 else ' loading="lazy"'
            A('            <div class="case-frame">')
            A(f'              <img{eager} src="assets/img/{c["img"]}.jpg" width="{w}" height="{h}"'
              f' alt="{c["alt"]}" decoding="async" />')
            A('            </div>')
        else:
            pw, ph = dims('rika-poster')
            A('            <div class="case-frame" data-case-video>')
            A(f'              <img class="case-frame__poster" src="assets/img/rika-poster.jpg"'
              f' width="{pw}" height="{ph}"'
              f' alt="A stone-clad Rika stove with a wood fire burning behind its glass door"'
              f' loading="lazy" decoding="async" />')
            # No <source> and no autoplay: main.js decides whether this is ever
            # fetched. muted+playsinline are required for autoplay to be allowed
            # at all; loop keeps a 31-second clip from ending on a frozen frame.
            A(f'              <video muted loop playsinline preload="none" width="{pw}" height="{ph}"')
            A('                     data-src="assets/video/rika.mp4"></video>')
            A('              <button class="case-frame__sound" type="button" data-case-sound'
              ' data-state="play" aria-label="Play video">')
            A('                <svg class="ico-play" viewBox="0 0 24 24" width="20" height="20"'
              ' aria-hidden="true"><path fill="currentColor" d="M8 5v14l11-7z"/></svg>')
            A('                <svg class="ico-muted" viewBox="0 0 24 24" width="20" height="20"'
              ' aria-hidden="true"><path fill="currentColor" d="M3 9v6h4l5 5V4L7 9H3zm13.5 3'
              'l2.5 2.5-1.4 1.4L15 13.4 12.6 15.9l-1.4-1.4L13.6 12l-2.4-2.5 1.4-1.4L15 10.6'
              'l2.6-2.5 1.4 1.4L16.5 12z"/></svg>')
            A('                <svg class="ico-sound" viewBox="0 0 24 24" width="20" height="20"'
              ' aria-hidden="true"><path fill="currentColor" d="M3 9v6h4l5 5V4L7 9H3zm13 3'
              'a4 4 0 00-2-3.5v7A4 4 0 0016 12zm-2-7.7v2.1a6 6 0 010 11.2v2.1a8 8 0 000-15.4z"/>'
              '</svg>')
            A('              </button>')
            A('            </div>')
        A('          </div>')
        A('          <div class="split__text">')
        A(f'            <h2 class="case__client feature-row__title">{c["client"]}</h2>')
        A(f'            <span class="case__meta">{c["meta"]}</span>')
        for p in c['body']:
            A(f'            <p>{p}</p>')
        if c['live']:
            A(f'            <p class="case__live">{c["live"]}</p>')
        A('            <ul class="service__list">')
        links = list(SERVICE_LINKS)
        if c['extra_service']:
            links.append(c['extra_service'])
        for slug, label in links:
            A(f'              <li><a href="/{slug}">{label}</a></li>')
        A('            </ul>')
        if c['ig']:
            href, handle = c['ig']
            A(f'            <p><a href="{href}" target="_blank" rel="noopener">'
              f'See the feed on Instagram, {handle}</a></p>')
        A('          </div>')
        A('        </div>')
        A('')

    A('      </div>')
    A('    </section>')
    A('')
    A('    <section class="section">')
    A('      <div class="container">')
    A('        <header class="section__head reveal" data-reveal>')
    A('          <h2 class="section__title section__title--center">Stills from the Rika film</h2>')
    A('          <p class="section__lead section__lead--center">Frames from the piece above, '
      'shot and graded by us.</p>')
    A('        </header>')
    A('')
    A('        <div class="gallery" data-gallery>')
    for row in (STILLS[:3], STILLS[3:]):
        A('          <div class="gallery__row gallery__row--3 reveal" data-reveal>')
        for stem, alt in row:
            w, h = dims(stem)
            A('            <button class="gallery__item" type="button" aria-label="Enlarge image">'
              f'<img src="assets/img/{stem}.jpg" width="{w}" height="{h}" alt="{alt}"'
              ' loading="lazy" decoding="async" /></button>')
        A('          </div>')
    A('        </div>')
    A('      </div>')
    A('    </section>')
    A('')
    A('    <section class="section">')
    A('      <div class="container">')
    A('        <header class="section__head reveal" data-reveal>')
    A('          <h2 class="section__title section__title--center">Want the same run at your '
      'market?</h2>')
    A('          <p class="section__lead section__lead--center">Tell us the goal. We will come '
      'back with a plan and a price, usually within one business day.</p>')
    A('          <p class="section__cta"><a class="btn btn--green" href="/contact">Tell us your goal</a></p>')
    A('        </header>')
    A('      </div>')
    A('    </section>')
    A('  </main>')
    return '\n'.join(L)


def build_graph(graph):
    keep = [n for n in graph['@graph'] if n.get('@type') not in ('ItemList', 'VideoObject')]
    for node in keep:
        if 'CollectionPage' in str(node.get('@type', '')):
            node['name'] = TITLE
            node['description'] = DESC
    url = f'{SITE}/portfolio'
    items = []
    for i, c in enumerate(CASES, 1):
        about = {'@type': 'Organization', 'name': c['client']}
        if c['ig']:
            about['sameAs'] = c['ig'][0]
        work = {
            '@type': 'CreativeWork',
            'name': f'{c["client"]} - marketing by MarketingPro',
            'creator': {'@id': f'{SITE}/#organization'},
            'about': about,
            'url': f'{url}#{c["id"]}',
        }
        items.append({'@type': 'ListItem', 'position': i, 'item': work})
    keep.append({'@type': 'ItemList', '@id': f'{url}#work', 'itemListElement': items})
    keep.append({
        '@type': 'VideoObject',
        '@id': f'{url}#rika-film',
        'name': 'Rika Premium Store, company film',
        'description': ('A film produced for Rika: the store from the air, the showroom, and '
                        'the stove range on display.'),
        'thumbnailUrl': f'{SITE}/assets/img/rika-poster.jpg',
        'contentUrl': f'{SITE}/assets/video/rika.mp4',
        # Google Search Console flagged this twice on 2026-08-16: "missing a timezone"
        # and "invalid datetime value". A bare date is not an ISO 8601 datetime, which is
        # what VideoObject.uploadDate has to be. Albania is CEST, UTC+2, in August. Midday
        # local because the real upload time is not recorded anywhere and any hour on the
        # right day is equally true, but with an explicit offset it cannot slide a day.
        'uploadDate': '2026-08-12T12:00:00+02:00',
        'duration': 'PT32S',
        'creator': {'@id': f'{SITE}/#organization'},
        'inLanguage': 'en',
    })
    graph['@graph'] = keep
    return graph


def main():
    p = 'portfolio.html'
    s = io.open(p, encoding='utf-8', newline='').read()

    s = re.sub(r'<title>.*?</title>', f'<title>{TITLE}</title>', s, count=1, flags=re.S)
    for attr, prop in (('name', 'description'), ('property', 'og:description'),
                       ('name', 'twitter:description')):
        s = re.sub(rf'(<meta {attr}="{prop}" content=")[^"]*(")',
                   lambda m: m.group(1) + DESC + m.group(2), s, count=1)
    for attr, prop in (('property', 'og:title'), ('name', 'twitter:title')):
        s = re.sub(rf'(<meta {attr}="{prop}" content=")[^"]*(")',
                   lambda m: m.group(1) + TITLE + m.group(2), s, count=1)

    # The first <picture> in <main> is now the Fly System frame, so it is the LCP
    # candidate. The page carried no preload at all before.
    fw, fh = dims('case-flysystem-grid')
    preload = ('  <link rel="preload" as="image" href="assets/img/case-flysystem-grid.webp"'
               ' type="image/webp" fetchpriority="high" />\n')
    s = re.sub(r'[ \t]*<link rel="preload"[^>]*as="image"[^>]*>\n', '', s)
    s = s.replace('  <link rel="canonical"', preload + '  <link rel="canonical"', 1)

    TAG = '<script type="application/ld+json">'
    i = s.index(TAG) + len(TAG)
    j = s.index('</script>', i)
    graph = build_graph(json.loads(s[i:j]))
    s = (s[:i] + '\n  ' + json.dumps(graph, ensure_ascii=False, indent=2).replace('\n', '\n  ')
         + '\n  ' + s[j:])

    mi = s.index('  <main id="main"')
    mj = s.index('</main>') + len('</main>')
    s = s[:mi] + build_main() + s[mj:]

    io.open(p, 'w', encoding='utf-8', newline='').write(s)
    words = len(re.sub(r'<[^>]+>', ' ', s[s.index('<main'):s.index('</main>')]).split())
    print(f'  portfolio.html rebuilt: {len(CASES)} case studies, {len(STILLS)} stills, '
          f'{words} words')
    print(f'  title {len(TITLE)} chars, description {len(DESC)} chars')


if __name__ == '__main__':
    main()
