#!/usr/bin/env python3
"""Generate the eight English service landing pages.

Uses blog-seo.html purely as a structural shell, so head, nav, footer, chrome and
every generated element stay byte-correct and the existing build scripts keep
working on the result. Only the parts that differ are replaced: metadata,
breadcrumb, hero, body, FAQ and the JSON-LD graph.

The BlogPosting node is replaced by a Service node, which is what these pages
actually are. Organization and WebSite stay untouched, as everywhere else.

    python .build/gen-service-pages.py
"""
import html
import importlib.util
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

spec = importlib.util.spec_from_file_location('sc', '.build/service-content.py')
sc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sc)

SITE = 'https://www.marketingpro-agency.com'
SHELL = io.open('blog-seo.html', encoding='utf-8', newline='').read()

try:
    from PIL import Image
except ImportError:
    sys.exit('Pillow required')


def esc(t):
    return html.escape(t, quote=False).replace('&#x27;', "'")


def build(slug, c):
    s = SHELL

    with Image.open(f"assets/img/{c['img']}.jpg") as im:
        iw, ih = im.size

    url = f'{SITE}/{slug}'

    # ---- head metadata -----------------------------------------------------
    s = re.sub(r'<title>.*?</title>', f"<title>{esc(c['title'])}</title>", s, count=1, flags=re.S)
    s = re.sub(r'(<meta name="description" content=")[^"]*(")',
               lambda m: m.group(1) + esc(c['desc']) + m.group(2), s, count=1)
    s = re.sub(r'(<link rel="canonical" href=")[^"]*(")',
               lambda m: m.group(1) + url + m.group(2), s, count=1)
    for prop, val in (('og:title', c['title']), ('twitter:title', c['title']),
                      ('og:description', c['desc']), ('twitter:description', c['desc'])):
        attr = 'property' if prop.startswith('og:') else 'name'
        s = re.sub(rf'(<meta {attr}="{prop}" content=")[^"]*(")',
                   lambda m: m.group(1) + esc(val) + m.group(2), s, count=1)
    s = re.sub(r'(<meta property="og:url" content=")[^"]*(")',
               lambda m: m.group(1) + url + m.group(2), s, count=1)
    for prop, attr in (('og:image', 'property'), ('twitter:image', 'name')):
        s = re.sub(rf'(<meta {attr}="{prop}" content=")[^"]*(")',
                   lambda m: m.group(1) + f"{SITE}/assets/img/{c['img']}.jpg" + m.group(2), s, count=1)
    for prop, attr in (('og:image:alt', 'property'), ('twitter:image:alt', 'name')):
        s = re.sub(rf'(<meta {attr}="{prop}" content=")[^"]*(")',
                   lambda m: m.group(1) + esc(c['alt']) + m.group(2), s, count=1)
    s = re.sub(r'(<meta property="og:image:width" content=")[^"]*(")',
               lambda m: m.group(1) + str(iw) + m.group(2), s, count=1)
    s = re.sub(r'(<meta property="og:image:height" content=")[^"]*(")',
               lambda m: m.group(1) + str(ih) + m.group(2), s, count=1)
    # The shell is blog-seo.html, so its hero preload names svc-seo-1. Repoint
    # it at this page's own hero, in the format <picture> will actually resolve
    # to. Shipping the shell's value preloaded a wasted JPEG on all eight.
    s = re.sub(r'<link rel="preload"[^>]*as="image"[^>]*>',
               f'<link rel="preload" as="image" href="assets/img/{c["img"]}.webp"'
               ' type="image/webp" fetchpriority="high" />', s, count=1)

    # this page type is a service, not an article
    s = s.replace('<meta property="og:type" content="article" />',
                  '<meta property="og:type" content="website" />')
    s = re.sub(r'\n[ \t]*<meta property="article:[^>]*>', '', s)

    # ---- JSON-LD -----------------------------------------------------------
    i = s.index('<script type="application/ld+json">')
    j = s.index('</script>', i)
    graph = json.loads(s[i + len('<script type="application/ld+json">'):j])
    # @type may be a list (fix-geo-schema.py dual-types the Organization as
    # ["Organization", "ProfessionalService"]); plain membership would then
    # silently drop the node on a future regeneration.
    keep = [n for n in graph['@graph']
            if ({'Organization', 'WebSite'} &
                set(n['@type'] if isinstance(n['@type'], list) else [n['@type']]))]
    keep.append({
        '@type': 'Service', '@id': f'{url}#service',
        'name': c['service_name'], 'serviceType': c['service_type'],
        'description': c['desc'], 'url': url,
        'provider': {'@id': f'{SITE}/#organization'},
        'areaServed': [
            {'@type': 'Country', 'name': 'Italy'},
            {'@type': 'Place', 'name': 'Europe'},
            {'@type': 'Country', 'name': 'United States'},
        ],
        'inLanguage': 'en',
    })
    keep.append({
        '@type': 'WebPage', '@id': f'{url}#webpage', 'url': url,
        'name': c['title'], 'description': c['desc'],
        'isPartOf': {'@id': f'{SITE}/#website'},
        'about': {'@id': f'{url}#service'},
        'primaryImageOfPage': f"{SITE}/assets/img/{c['img']}.jpg",
        'inLanguage': 'en',
    })
    keep.append({
        '@type': 'FAQPage', '@id': f'{url}#faq',
        'mainEntity': [
            {'@type': 'Question', 'name': q,
             'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in c['faq']
        ],
    })
    keep.append({
        '@type': 'BreadcrumbList', '@id': f'{url}#breadcrumb',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': f'{SITE}/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'Services', 'item': f'{SITE}/services'},
            # c['nav'], not c['service_name']: the markup has to say what the
            # visible crumb says, and the visible crumb is the short label.
            {'@type': 'ListItem', 'position': 3, 'name': c['nav']},
        ],
    })
    graph['@graph'] = keep
    s = (s[:i + len('<script type="application/ld+json">')] + '\n  '
         + json.dumps(graph, ensure_ascii=False, indent=2).replace('\n', '\n  ')
         + '\n  ' + s[j:])

    # ---- main -------------------------------------------------------------
    body = []
    A = body.append
    A('  <main id="main" class="article-page">')
    A('    <nav class="breadcrumb" aria-label="Breadcrumb">')
    A('      <ol>')
    A('        <li><a href="/">Home</a></li>')
    A('        <li><a href="/services">Services</a></li>')
    A(f"        <li><span aria-current=\"page\">{esc(c['nav'])}</span></li>")
    A('      </ol>')
    A('    </nav>')
    A('')
    A('    <article>')
    A('      <header class="section article-hero">')
    A('        <div class="container">')
    A(f"          <h1 class=\"article-hero__title\">{esc(c['h1'])}</h1>")
    A('          <div class="article-hero__media">')
    A('            <picture>')
    A(f"              <source srcset=\"assets/img/{c['img']}.webp\" type=\"image/webp\" />")
    A(f"              <img src=\"assets/img/{c['img']}.jpg\" alt=\"{esc(c['alt'])}\""
      f" width=\"{iw}\" height=\"{ih}\" fetchpriority=\"high\" decoding=\"async\" />")
    A('            </picture>')
    A('          </div>')
    A('        </div>')
    A('      </header>')
    A('')
    A('      <div class="article article__body">')
    A('        <div class="container">')
    for p in c['lead']:
        A(f'          <p>{esc(p)}</p>')
    A(f"          <h2>{esc(c['covers_h'])}</h2>")
    A('          <ul>')
    for it in c['covers']:
        A(f'            <li>{esc(it)}</li>')
    A('          </ul>')
    if c.get('proof'):
        A(f"          <h2>{esc(c['proof_h'])}</h2>")
        A(f"          <p>{esc(c['proof'])}</p>")
    A(f"          <h2>{esc(c['how_h'])}</h2>")
    for h, p in c['how']:
        A(f'          <p><strong>{esc(h)}.</strong> {esc(p)}</p>')
    A(f"          <h2>{esc(c['who_h'])}</h2>")
    A(f"          <p>{esc(c['who'])}</p>")
    A('          <h2>Timelines and pricing</h2>')
    A(f'          <p>{esc(sc.TODO_SLOT)}</p>')
    A('          <h2>Frequently Asked Questions</h2>')
    A('          <div class="faq__list">')
    for q, a in c['faq']:
        A('            <details class="faq__item">')
        A(f'              <summary>{esc(q)}</summary>')
        A(f'              <p>{esc(a)}</p>')
        A('            </details>')
    A('          </div>')
    A('')
    A(f"          <p class=\"post-service\"><strong>The long version:</strong> "
      f"<a href=\"/{c['guide']}\">{esc(c['guide_label'])}</a></p>")
    A('          <p><a class="btn btn--green" href="/contact">Tell us your goal</a></p>')
    A('')
    A('          <a class="article__back" href="/services">')
    A('            <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">'
      '<path fill="currentColor" d="M15 6l-6 6 6 6 1.4-1.4L11.8 12l4.6-4.6z"/></svg>')
    A('            All services')
    A('          </a>')
    A('        </div>')
    A('      </div>')
    A('    </article>')
    A('  </main>')

    mi = s.index('  <main id="main"')
    mj = s.index('</main>') + len('</main>')
    return s[:mi] + '\n'.join(body) + s[mj:]


for slug, c in sc.SERVICES.items():
    out = build(slug, c)
    io.open(f'{slug}.html', 'w', encoding='utf-8', newline='').write(out)
    words = len(re.sub(r'<[^>]+>', ' ', out[out.index('<main'):out.index('</main>')]).split())
    print(f'  {slug + ".html":34} {words:4d} words  title {len(c["title"]):2d}  desc {len(c["desc"]):3d}')

print(f'\n  {len(sc.SERVICES)} English service pages generated')
