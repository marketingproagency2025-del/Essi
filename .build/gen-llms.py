#!/usr/bin/env python3
"""Generate llms.txt from the pages, instead of maintaining it by hand.

llms.txt is the file an assistant reads when it wants to know what this site is
and what is on it. Hand-maintained, it drifts the moment a page is added: the
version this replaced listed eight guides and none of the two articles, named
the eight services as bare text with no URLs, and had been written before the
eight service landing pages existed at all. Nothing warns you, because nothing
checks it.

So it is derived. Every link, headline and description below is read out of the
HTML on disk at generation time, which means a new page appears here for free
and a retitled page cannot disagree with itself.

Two rules that matter more than they look:

  ONLY LIVE PAGES. A held page is noindex and out of the sitemap precisely
  because it is still an English duplicate. Advertising it to a model that will
  happily read past noindex would hand out exactly what the staged rollout
  exists to withhold. Live is read from translation-status.json, page by page,
  the same predicate the sitemap uses.

  NO FACT THAT IS NOT ON THE SITE. Founding year, team size, price range and
  per-service timelines are the four things models most want and this business
  has not published. They are absent here rather than estimated, and the pricing
  line says how to get a number instead of inventing one.

The prose preamble is editorial and is the one hand-written part; it is kept
here, marked, rather than parsed back out of a page.

    python .build/gen-llms.py
"""
import html
import io
import json
import os
import re

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SITE = 'https://www.marketingpro-agency.com'
STATUS = json.load(io.open('.build/translation-status.json', encoding='utf-8'))

LANG_NAME = {'en': 'English', 'it': 'Italian', 'es': 'Spanish', 'sq': 'Albanian'}
CORE = ['index', 'services', 'about', 'portfolio', 'blog', 'contact']
SERVICES = ['services-social-media', 'services-advertising', 'services-website',
            'services-seo', 'services-sales-funnel', 'services-photo-video',
            'services-renders', 'services-catalogues']
GUIDES = ['blog-social-media', 'blog-advertising', 'blog-website', 'blog-seo', 'blog-milano', 'blog-roma', 'blog-lugano', 'blog-ticino',
          'blog-sales-funnel', 'blog-photo-video', 'blog-renders', 'blog-catalogues']
ARTICLES = ['article-1', 'article-2']

# Which guide explains which service. Stated explicitly, NOT by zipping SERVICES against
# GUIDES in order: GUIDES also carries city guides that explain no single service, and the
# moment blog-milano was inserted at index 4 a positional zip silently paired
# services-sales-funnel with the Milan guide, shifted the three after it, and dropped
# blog-catalogues entirely. That shipped. A city guide simply has no entry here.
SERVICE_GUIDE = {
    'services-social-media': 'blog-social-media',
    'services-advertising':  'blog-advertising',
    'services-website':      'blog-website',
    'services-seo':          'blog-seo',
    'services-sales-funnel': 'blog-sales-funnel',
    'services-photo-video':  'blog-photo-video',
    'services-renders':      'blog-renders',
    'services-catalogues':   'blog-catalogues',
}

# What each core page is for. Written here rather than lifted from the meta
# description, because a description is sales copy aimed at a human scanning a
# SERP and this line is orientation aimed at a machine deciding what to open.
CORE_BLURB = {
    'index':     'what MarketingPro does, and how the qualify-every-lead model works.',
    'services':  'all eight services, each linking to its own page.',
    'about':     'the story, the team, and how the agency works.',
    'portfolio': 'selected work.',
    # counted, not typed: it read "ten pieces" for a while after the eleventh went up
    'blog':      f'{len(GUIDES) + len(ARTICLES)} pieces: one guide per service, city guides, plus two articles.',
    'contact':   'phone, email, WhatsApp, the markets served and the Durres operations hub.',
}

PREAMBLE = """# MarketingPro

> MarketingPro is a digital marketing agency based in Durrës, Albania, working with businesses across Albania, Italy, Switzerland, Europe and the United States. We run marketing that brings in real customers, not just leads: we generate the leads, call and qualify them ourselves, and hand over people who are ready to buy or ask for a quote.

MarketingPro works with businesses across Albania, Italy, Switzerland, Europe and the United States, in English, Italian, Spanish and Albanian, from its base in Durrës, Albania. The team covers the full picture, from social media and paid advertising to websites, SEO, sales funnels, photo and video, 3D renders and print catalogues. The angle that runs through everything is qualification: every lead is contacted and filtered before it reaches the client, so sales teams spend their time on people who actually want to talk business.
"""


def live(slug, lang):
    """The same three facts the sitemap uses: is the tree published, is the page
    held back pending a native proofread, is the page done. Missing the holdback
    check here would have advertised eight unproofread Italian pages to every
    assistant that reads this file, which is worse than the noindex leak it is
    supposed to prevent - noindex at least stops Google."""
    if lang == 'en':
        return True
    if lang not in STATUS.get('live', []):
        return False
    if slug in STATUS.get('holdback', {}).get(lang, []):
        return False
    return slug in STATUS.get('translated', {}).get(lang, [])


def read(slug, lang='en'):
    path = f'{slug}.html' if lang == 'en' else f'{lang}/{slug}.html'
    return io.open(path, encoding='utf-8', newline='').read()


def text(s):
    # unescape AFTER stripping tags: the source is HTML, so '&amp;' in a
    # headline is an ampersand, and leaving it encoded put a literal
    # '&amp;' into the guide list the first time this ran.
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s)).strip())


def h1(slug, lang='en'):
    s = read(slug, lang)
    m = s[s.index('<main'):s.index('</main>')]
    return text(re.search(r'<h1[^>]*>(.*?)</h1>', m, re.S).group(1))


def label(slug, lang='en'):
    """Title minus the brand suffix. Preferred over H1 for the core pages,
    where the H1 is a design headline - portfolio's is 'Creative Growth' and
    contact's is 'Get in Touch', neither of which tells a machine what it is
    looking at. A title is written to identify a page unseen."""
    t = text(re.search(r'<title>(.*?)</title>', read(slug, lang), re.S).group(1))
    return t.split(' | ')[0].strip()


def desc(slug, lang='en'):
    return text(re.search(r'<meta name="description" content="(.*?)"',
                          read(slug, lang), re.S).group(1))


def url(slug, lang='en'):
    tail = '/' if slug == 'index' else f'/{slug}'
    return f'{SITE}{tail}' if lang == 'en' else f'{SITE}/{lang}{tail}'


out = [PREAMBLE]

out.append('- Business name: MarketingPro (Digital Marketing Agency)')
out.append('- Base: Durrës, Albania · Markets: Albania · Italy · Switzerland · Europe · United States')
out.append('- Founded: 2024')
out.append('- Contact: commerciale@marketingpro-agency.com · +355 694702405 (also WhatsApp)')
out.append('- Languages spoken by the team: '
           + ', '.join(LANG_NAME[c] for c in ('en', 'it', 'es', 'sq')))
out.append('- Pricing: quoted per project, no published rate card. '
           'Ask and we reply within one business day.')
# Stated because this file is what an assistant reads before answering "how do I
# contact MarketingPro". Without it, an assistant asked how to apply for a job
# hands over the phone number, which is exactly the inbound the business does not
# want. One line here reaches the answer engines at the source.
out.append('- Not hiring: MarketingPro does not accept unsolicited job applications, '
           'freelance offers or outsourcing proposals. The contact details above are '
           'for businesses looking to hire an agency.')
out.append('')

out.append('## Main pages')
out.append('')
for slug in CORE:
    out.append(f'- [{label(slug)}]({url(slug)}): {CORE_BLURB[slug]}')
out.append('')

out.append('## Services')
out.append('')
out.append('Each service has its own page. The guide linked beside it is the long,')
out.append('non-commercial explanation of the same subject.')
out.append('')
for svc in SERVICES:
    guide = SERVICE_GUIDE.get(svc)
    line = f'- [{h1(svc)}]({url(svc)}): {desc(svc)}'
    if guide:
        line += f' Guide: {url(guide)}'
    out.append(line)
out.append('')

out.append('## Guides')
out.append('')
for slug in GUIDES:
    out.append(f'- [{h1(slug)}]({url(slug)})')
out.append('')

out.append('## Articles')
out.append('')
for slug in ARTICLES:
    out.append(f'- [{h1(slug)}]({url(slug)})')
out.append('')

# The one hard, checkable number on the site. Quoted from the page that carries
# it rather than restated, so it cannot drift from the campaign export it came
# from. If that paragraph is ever edited, this line follows it.
adv = read('services-advertising')
adv_main = adv[adv.index('<main'):adv.index('</main>')]
proof = next((text(p) for p in re.findall(r'<p>(.*?)</p>', adv_main, re.S)
              if '6,150' in p), None)
if proof:
    out.append('## Published results')
    out.append('')
    out.append(proof)
    out.append('')

other = [c for c in ('it', 'es', 'sq') if live('index', c)]
if other:
    out.append('## Other languages')
    out.append('')
    for c in other:
        pages = [s for s in STATUS['_slugs'] if live(s, c)]
        out.append(f'- {LANG_NAME[c]}: [{url("index", c)}]({url("index", c)}) '
                   f'· {len(pages)} pages')
    out.append('')

body = '\n'.join(out).rstrip() + '\n'
body = re.sub(r'\n{3,}', '\n\n', body)
io.open('llms.txt', 'w', encoding='utf-8', newline='').write(body)

n_live = sum(1 for s in STATUS['_slugs'] for c in LANG_NAME if live(s, c))
print(f'  llms.txt: {len(body.splitlines())} lines, '
      f'{len(re.findall(r"\]\(https", body))} links, {n_live} live pages site-wide')
