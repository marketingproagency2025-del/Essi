#!/usr/bin/env python3
"""Push every live URL to Bing, Yandex and Seznam the moment a deploy lands.

WHY THIS EXISTS. Search Console reported "Discovered - currently not indexed"
with Last crawled: N/A across the English tree - Google had found the URLs and
never fetched one of them. That is the normal fate of a new domain with no
inbound links: Google rations crawl budget by authority, and a two-week-old site
has none to spend.

IndexNow is the way around waiting. It is a push protocol rather than a pull one:
you submit the URLs, the engine fetches them, and no crawl-priority auction
happens. Bing, Yandex and Seznam share one endpoint, so a single POST reaches
all three.

The reason that matters here more than it looks: **Bing's index is what ChatGPT
Search and Copilot read.** For a site whose stated goal is AI visibility, getting
into Bing in days beats getting into Google in months, and it does not have to
wait for Google at all.

Google has no IndexNow equivalent and does not accept one. Its Indexing API is
restricted to JobPosting and BroadcastEvent pages; using it for anything else is
against its terms and is not attempted here. For Google the levers are inbound
links, honest lastmod, and manual requests in Search Console.

THE KEY. IndexNow authenticates by asking the site to prove it controls the
domain: a file named <key>.txt at the root, containing exactly that key. If the
file is missing, misnamed, or its contents differ by a single character, every
submission fails - usually with a 403 and no other explanation. Gate check 24
compares the file's name and contents against KEY below so that cannot rot.

    python .build/indexnow.py --dry-run    # print what would be sent
    python .build/indexnow.py              # submit
"""
import io
import json
import os
import re
import sys
import urllib.request

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

KEY = '981f9bdd7802d1b669b6288dfa5e2ce5d2210d0a121c7322e78ca51d7e2ec8f4'
HOST = 'www.marketingpro-agency.com'
ENDPOINT = 'https://api.indexnow.org/indexnow'


def urls():
    """Read the sitemap rather than the filesystem: the sitemap already encodes
    the live/held predicate, so a held page can never be submitted by accident."""
    s = io.open('sitemap.xml', encoding='utf-8').read()
    return re.findall(r'<loc>([^<]+)</loc>', s)


def main():
    key_file = f'{KEY}.txt'
    if not os.path.isfile(key_file):
        sys.exit(f'  missing {key_file} at the repo root - submissions would 403')
    if io.open(key_file, encoding='utf-8').read().strip() != KEY:
        sys.exit(f'  {key_file} does not contain the key - submissions would 403')

    batch = urls()
    if not batch:
        sys.exit('  sitemap.xml yielded no URLs')

    payload = {
        'host': HOST,
        'key': KEY,
        'keyLocation': f'https://{HOST}/{key_file}',
        'urlList': batch,
    }

    if '--dry-run' in sys.argv:
        print(f'  would submit {len(batch)} urls to {ENDPOINT}')
        print(f'  key file: https://{HOST}/{key_file}')
        for u in batch[:5]:
            print(f'    {u}')
        print(f'    ... and {len(batch) - 5} more')
        return

    body = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        ENDPOINT, data=body,
        headers={'Content-Type': 'application/json; charset=utf-8'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            # 200 accepted, 202 accepted but key still being validated. Both fine.
            print(f'  {r.status} {r.reason} - {len(batch)} urls submitted to '
                  f'Bing, Yandex and Seznam')
    except urllib.error.HTTPError as e:
        # 403 is nearly always the key file; 422 is a url that is not on HOST.
        print(f'  FAILED {e.code} {e.reason}')
        print(f'  {e.read().decode("utf-8", "replace")[:300]}')
        sys.exit(1)


if __name__ == '__main__':
    main()
