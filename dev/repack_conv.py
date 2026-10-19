# -*- coding: utf-8 -*-
"""用翻译后的 txt 重打包 conv.dat。
用法: python repack_conv.py <orig_dat> <zh_dir> <out_dat> <key>
原版 conv.dat 中 conv/*.txt 用 zh_dir 里的同名文件替换，其余文件原样保留。"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dxa import Dxa

orig, zhdir, out, key = sys.argv[1:5]
raw = open(orig, 'rb').read()
a = Dxa(raw, key)
repl = {}
n = 0
for name, data, k in a.files():
    base = name.replace('/', '\\').split('\\')[-1]
    p = os.path.join(zhdir, base)
    if os.path.exists(p):
        new = open(p, 'rb').read()
        repl[name] = new
        n += 1
print('replace', n, 'files')
assert n >= 13, 'too few replaced'
a.repack(repl, out)
print('repacked ->', out, os.path.getsize(out), 'bytes')

# 验证: 重新解析并逐文件比对
b = Dxa(open(out, 'rb').read(), key)
cnt = 0
for name, data, k in b.files():
    base = name.replace('/', '\\').split('\\')[-1]
    p = os.path.join(zhdir, base)
    if name in repl:
        assert data == repl[name], 'mismatch ' + name
        cnt += 1
    else:
        orig_data = dict((nm, d) for nm, d, _ in a.files())
        assert data == orig_data[name], 'orig changed ' + name
print('verify OK: %d replaced + others intact' % cnt)
