"""
SEV Tech Tree — image asset preparation
Copies/converts game images into src/public/images/ for bundling with Vite.

Usage:
    python3 scripts/copy_images.py
"""

import json
import os
import re
import shutil
from pathlib import Path

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print('WARNING: Pillow not installed, BMP conversion will be skipped')

ROOT      = Path(__file__).parent.parent
GAME      = ROOT / '__game'
OUT       = ROOT / 'src' / 'public' / 'images'
RESOURCES = ROOT / 'resources'

def ensure(path: Path):
    path.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Tech icons sprite sheet  (Bmp_TechIcons.bmp → tech_icons.png)
# ---------------------------------------------------------------------------

def copy_tech_icons():
    src = GAME / 'pictures' / 'ui' / 'Bmp_TechIcons.bmp'
    dst = OUT / 'tech_icons.png'
    if not HAS_PIL:
        print('  skipped tech_icons (no Pillow)')
        return
    img = Image.open(src)
    img.save(dst)
    print(f'  tech_icons.png  ({img.size[0]}×{img.size[1]})')

# ---------------------------------------------------------------------------
# Component large portraits  (LargePortrait_Comp_NNN.jpg)
# ---------------------------------------------------------------------------

def copy_components():
    src_dir = GAME / 'pictures' / 'components'
    dst_dir = OUT / 'components'
    ensure(dst_dir)

    # Collect used image numbers from resources JSON
    used = set()
    for fname in ('components_uk.json', 'components_en.json'):
        with open(RESOURCES / fname) as f:
            for item in json.load(f):
                if item.get('imageNum'):
                    used.add(item['imageNum'])

    copied = 0
    for num in sorted(used):
        src = src_dir / f'LargePortrait_Comp_{num:03d}.jpg'
        dst = dst_dir / f'{num:03d}.jpg'
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
            copied += 1
    print(f'  components: {copied} new images copied ({len(used)} used)')

# ---------------------------------------------------------------------------
# Facility large portraits  (LargePortrait_Building_NNN.jpg)
# ---------------------------------------------------------------------------

def copy_facilities():
    src_dir = GAME / 'pictures' / 'facilities'
    dst_dir = OUT / 'facilities'
    ensure(dst_dir)

    used = set()
    for fname in ('facilities_uk.json', 'facilities_en.json'):
        with open(RESOURCES / fname) as f:
            for item in json.load(f):
                if item.get('imageNum'):
                    used.add(item['imageNum'])

    copied = 0
    for num in sorted(used):
        dst_jpg = dst_dir / f'{num:03d}.jpg'
        dst_png = dst_dir / f'{num:03d}.png'
        if dst_jpg.exists() or dst_png.exists():
            continue
        large = src_dir / f'LargePortrait_Building_{num:03d}.jpg'
        if large.exists():
            shutil.copy2(large, dst_jpg)
            copied += 1
        elif HAS_PIL:
            small = src_dir / f'Building_{num:03d}.bmp'
            if small.exists():
                Image.open(small).save(dst_png)
                copied += 1
    print(f'  facilities: {copied} new images copied ({len(used)} used)')

# ---------------------------------------------------------------------------
# Ship inventory portraits  (Default_InvPortrait_*.jpg)
# ---------------------------------------------------------------------------

def copy_ships():
    src_dir = GAME / 'empires' / 'default'
    dst_dir = OUT / 'ships'
    ensure(dst_dir)

    # Collect used portrait filenames from resources JSON
    used = set()
    for fname in ('vehicle_sizes_uk.json', 'vehicle_sizes_en.json'):
        with open(RESOURCES / fname) as f:
            for item in json.load(f):
                if item.get('portrait'):
                    used.add(item['portrait'])

    copied = 0
    for name in sorted(used):
        src = src_dir / name
        dst = dst_dir / name
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)
            copied += 1
    skipped = len([n for n in used if not (src_dir / n).exists()])
    print(f'  ships: {copied} copied, {skipped} not found (organic/crystalline)')

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    ensure(OUT)
    print(f'Copying images → {OUT.relative_to(ROOT)}')
    copy_tech_icons()
    copy_components()
    copy_facilities()
    copy_ships()
    print('Done.')
