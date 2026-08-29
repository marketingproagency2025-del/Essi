#!/usr/bin/env python3
"""Generate feed.xml from the ten English blog pieces.

A feed is a crawl path that does not depend on the sitemap. Aggregators, readers
and several AI crawlers discover posts through it, and it is one more route into
a site that Google has so far declined to fetch at all. It costs one file.

English only, deliberately. RSS has no hreflang: a single feed carrying four
languages would be four duplicates to any consumer, and per-language feeds would
need per-language discovery links to be worth anything. The English tree is
x-default and the one every alternate points back to, so it is the feed.

Dates come from each post's own <time datetime> - the publication date the page
already states - not from git, which records when the file was last edited. A
reader cares when the piece was published.

    python .build/gen-feed.py
"""
import html
import io
import os
import re
from email.utils import format_datetime
from datetime import datetime, timezone

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SITE = 'https://www.marketingpro-agency.com'
SLUGS = ['blog-social-media', 'blog-advertising', 'blog-website', 'blog-seo', 'blog-milano', 'blog-roma', 'blog-lugano', 'blog-ticino', 'blog-boost-or-campaign', 'blog-lead-quality', 'blog-in-house-or-agency', 'blog-showrooms',
         'blog-sales-funnel', 'blog-photo-video', 'blog-renders', 'blog-catalogues',
         'article-1', 'article-2']


def text(s):
    return html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s)).strip())


items = []
for slug in SLUGS:
    s = io.open(f'{slug}.html', encoding='utf-8', newline='').read()
    main = s[s.index('<main'):s.index('</main>')]
    title = text(re.search(r'<h1[^>]*>(.*?)</h1>', main, re.S).group(1))
    desc = text(re.search(r'<meta name="description" content="(.*?)"', s, re.S).group(1))
    d = re.search(r'<time datetime="(\d{4}-\d{2}-\d{2})"', main)
    when = datetime.fromisoformat(d.group(1)).replace(tzinfo=timezone.utc) if d else None
    items.append((slug, title, desc, when))

# newest first, which is what every reader expects
items.sort(key=lambda it: (it[3] is not None, it[3]), reverse=True)

L = ['<?xml version="1.0" encoding="UTF-8"?>',
     '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
     '  <channel>',
     '    <title>MarketingPro Marketing Blog</title>',
     f'    <link>{SITE}/blog</link>',
     '    <description>Practical marketing guides from MarketingPro, a digital '
     'marketing agency based in Durres, Albania.</description>',
     '    <language>en</language>',
     f'    <atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>']
if items[0][3]:
    L.append(f'    <lastBuildDate>{format_datetime(items[0][3])}</lastBuildDate>')
for slug, title, desc, when in items:
    L.append('    <item>')
    L.append(f'      <title>{html.escape(title)}</title>')
    L.append(f'      <link>{SITE}/{slug}</link>')
    L.append(f'      <guid isPermaLink="true">{SITE}/{slug}</guid>')
    L.append(f'      <description>{html.escape(desc)}</description>')
    if when:
        L.append(f'      <pubDate>{format_datetime(when)}</pubDate>')
    L.append('    </item>')
L += ['  </channel>', '</rss>', '']

io.open('feed.xml', 'w', encoding='utf-8', newline='').write('\n'.join(L))
print(f'  feed.xml: {len(items)} items, newest {items[0][3].date()}')
