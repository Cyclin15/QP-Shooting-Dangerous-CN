# -*- coding: utf-8 -*-
"""提取 conv txt 中的对白行 -> texts.json。
<text> 块内：属性行含 '='，第一个不含 '=' 的非空行 = 对白正文。
"""
import json, os, sys

srcdir = sys.argv[1]
out = sys.argv[2]

data = {}
for fn in sorted(os.listdir(srcdir)):
    if not fn.endswith('.txt'):
        continue
    raw = open(os.path.join(srcdir, fn), 'rb').read()
    text = raw.decode('utf-16')
    lines = text.split('\n')
    entries = []
    in_text = False
    found = False
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s == '<text>':
            in_text = True; found = False
            continue
        if not in_text:
            continue
        if s == '</act>' or s.startswith('---'):
            in_text = False
            continue
        if found:
            continue
        if s and '=' not in ln:
            entries.append({'line': i, 'text': ln})
            found = True
    data[fn] = entries
    print(fn, len(entries))

json.dump(data, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
total = sum(len(v) for v in data.values())
print('TOTAL', total)
