#!/usr/bin/env python3
"""gen_catalog_images.py — generate every catalog item's static product shot.

Data-driven: pulls the deployed API's full catalog (catalog_all), and for every item
carrying img + imgPrompt, generates the image through api/meridian_image.php (same
pipeline as the live hero — cached server-side by prompt hash), downloads it, and
saves it as api/img/<img>. Existing files are skipped unless --force.

Run AFTER deploy_api.py (the endpoint + key must be live), then run deploy_api.py
again to upload the new img/ files.
"""
import json
import os
import ssl
import sys
import urllib.request

BASE = os.environ.get('MERIDIAN_API_BASE', '').rstrip('/')
if not BASE:
    sys.exit('MERIDIAN_API_BASE is not set — point it at your own deployed api/ '
             '(same value you pass to package/build_meridian.py).')
BASE += '/'
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(HERE, 'api', 'img')
FORCE = '--force' in sys.argv

ctx = ssl.create_default_context()

def get(url, body=None):
    req = urllib.request.Request(url, data=(json.dumps(body).encode() if body else None),
                                 headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=90, context=ctx) as r:
        return r.read()

os.makedirs(IMG_DIR, exist_ok=True)
cat = json.loads(get(BASE + 'meridian_api.php?action=catalog_all'))
items = cat.get('items', {})
todo = [(sku, it) for sku, it in items.items() if it.get('img') and it.get('imgPrompt')]
print('%d catalog items, %d with img+imgPrompt' % (len(items), len(todo)))

ok = skip = fail = 0
for sku, it in todo:
    dest = os.path.join(IMG_DIR, it['img'])
    if os.path.exists(dest) and not FORCE:
        print('  - %-16s %s (exists)' % (sku, it['img'])); skip += 1; continue
    try:
        r = json.loads(get(BASE + 'meridian_image.php', {'prompt': it['imgPrompt']}))
        if not r.get('ok'):
            print('  X %-16s ERROR: %s' % (sku, str(r)[:160])); fail += 1; continue
        png = get(r['url'])
        with open(dest, 'wb') as f:
            f.write(png)
        print('  + %-16s %s  (%.0f KB, %s ms%s)' % (sku, it['img'], len(png) / 1024.0,
              r.get('ms'), ', cached' if r.get('cached') else ''))
        ok += 1
    except Exception as e:
        print('  X %-16s FAILED: %s' % (sku, e)); fail += 1

print('generated: %d  skipped: %d  failed: %d' % (ok, skip, fail))
print('Now run: python tools/deploy_api.py  (uploads api/img/ to the live folder)')
sys.exit(1 if fail else 0)
