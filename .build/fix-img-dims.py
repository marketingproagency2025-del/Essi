#!/usr/bin/env python3
"""Give every <img> the width and height its file actually has.

Two defects, both CLS exposure:
  - 180 tags carried no width/height at all
  - 40 declared width="1200" height="500" against portrait sources such as
    1080x1258, so the browser reserved a box of the wrong shape AND was told to
    upscale a 1080px file to 1200px

Rendered size is controlled by CSS everywhere on this site, so writing intrinsic
dimensions changes no visible pixel; it only fixes the aspect box the browser
reserves before CSS arrives.

    python .build/fix-img-dims.py            # all four trees
    python .build/fix-img-dims.py en         # one tree
"""
import glob
import io
import os
import re
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit('Pillow is required: python -m pip install Pillow')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

TREES = {'en': '', 'it': 'it/', 'es': 'es/', 'sq': 'sq/'}
want = sys.argv[1:] or list(TREES)

IMG_RX = re.compile(r'<img\b[^>]*>')
ATTR_RX = re.compile(r'(\w+)="([^"]*)"')

_dims = {}


def size_of(path):
    if path not in _dims:
        try:
            with Image.open(path) as im:
                _dims[path] = im.size
        except Exception:
            _dims[path] = None
    return _dims[path]


def fix_tag(tag, base_dir):
    attrs = dict(ATTR_RX.findall(tag))
    src = attrs.get('src', '').split('#')[0].split('?')[0]
    if not src or re.match(r'^(https?:|//|data:)', src):
        return tag, False
    target = os.path.normpath(os.path.join(base_dir, src))
    size = size_of(target)
    if size is None:
        return tag, False
    w, h = size

    out = tag
    for name, value in (('width', w), ('height', h)):
        if f'{name}="' in out:
            out = re.sub(rf'{name}="[^"]*"', f'{name}="{value}"', out, count=1)
        else:
            # insert right after src so the attribute order stays readable
            out = out.replace(f'src="{attrs["src"]}"',
                              f'src="{attrs["src"]}" {name}="{value}"', 1)
    return out, out != tag


total_files = total_tags = 0
for tree in want:
    pre = TREES[tree]
    for path in sorted(glob.glob(f'{pre}*.html')):
        s = io.open(path, encoding='utf-8', newline='').read()
        base = os.path.dirname(os.path.abspath(path))
        changed = 0

        def repl(m):
            global changed
            new, did = fix_tag(m.group(0), base)
            if did:
                changed += 1
            return new

        out = IMG_RX.sub(repl, s)
        if changed:
            io.open(path, 'w', encoding='utf-8', newline='').write(out)
            total_files += 1
            total_tags += changed
            print(f'  {path:34} {changed} img tags')

print(f'\n  {total_tags} <img> tags corrected across {total_files} files')
