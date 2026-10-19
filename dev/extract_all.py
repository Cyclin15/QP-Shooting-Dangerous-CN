# -*- coding: utf-8 -*-
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dxa import Dxa, compress, decompress

random.seed(1)
tests = [b'', b'A', b'\xfa'*10, bytes(random.randrange(256) for _ in range(1000)),
         b'\x00'*5000, (b'BM\x00\x00\x00\x00hello world '*300),
         bytes(random.choice(b'ABCD') for _ in range(50000))]
for t in tests:
    r = decompress(compress(t))
    assert r == t, 'roundtrip fail len=%d' % len(t)
print('roundtrip OK')

KEY = sys.argv[2] if len(sys.argv) > 2 else 'qppass'
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for fn in sys.argv[1].split(','):
    a = Dxa(open(os.path.join(BASE, fn), 'rb').read(), KEY)
    outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'extract', fn.replace('.dat', ''))
    n = 0; exts = {}
    for name, data, k in a.files():
        parts = name.replace('/', '\\').split('\\')
        p = os.path.join(outdir, *parts)
        d = os.path.dirname(p)
        if d: os.makedirs(d, exist_ok=True)
        open(p, 'wb').write(data)
        n += 1
        e = name.rsplit('.', 1)[-1].lower() if '.' in name else '(none)'
        exts[e] = exts.get(e, 0) + 1
    print(fn, 'files=%d' % n, exts)
