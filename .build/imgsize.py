#!/usr/bin/env python3
"""Emit the real pixel dimensions of every image under assets/, as TSV.

Called by verify-langs.ps1. A first attempt parsed PNG IHDR and JPEG SOF markers
in PowerShell directly and got them wrong - logo.png read as 119x77 against a
real 375x77, and the article heroes as 176x208 against 1200x720. Rather than
debug byte-walking in a shell language, this defers to Pillow, which is already
installed and is the thing that is actually correct.

This still re-derives from the files themselves rather than trusting any
manifest, which is the property the gate needs.

    python .build/imgsize.py
    assets/img/logo.png<TAB>375<TAB>77
"""
import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.stderr.write('Pillow is required: python -m pip install Pillow\n')
    sys.exit(2)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, 'assets')

count = 0
for dirpath, _dirnames, filenames in os.walk(ASSETS):
    for name in sorted(filenames):
        full = os.path.join(dirpath, name)
        try:
            with Image.open(full) as im:
                w, h = im.size
        except Exception:
            continue  # not an image, or a format Pillow will not open
        rel = os.path.relpath(full, ROOT).replace(os.sep, '/')
        print(f'{rel}\t{w}\t{h}')
        count += 1

if count == 0:
    sys.stderr.write('no images found under assets/\n')
    sys.exit(1)
