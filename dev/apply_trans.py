# -*- coding: utf-8 -*-
"""将翻译回填到 conv txt，生成中文版文件。
用法: python apply_trans.py <texts.json> <trans.py> <srcdir> <outdir>
校验：每条对白必须有译文；生成文件保持原结构（仅替换对白行）。"""
import json, os, sys, importlib.util

texts_path, trans_path, srcdir, outdir = sys.argv[1:5]
spec = importlib.util.spec_from_file_location('trans', trans_path)
trans = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trans)
T = trans.T

data = json.load(open(texts_path, encoding='utf-8'))

# 校验完整性
missing = []
for fn, es in data.items():
    for e in es:
        if e['text'] not in T:
            missing.append((fn, e['text']))
if missing:
    print('MISSING %d:' % len(missing))
    for fn, t in missing:
        print(' ', fn, repr(t))
    sys.exit(1)

os.makedirs(outdir, exist_ok=True)
for fn in sorted(data):
    raw = open(os.path.join(srcdir, fn), 'rb').read()
    text = raw.decode('utf-16')
    # 按行回填（同文件内重复文本一次替换即可，按行号精准替换）
    lines = text.split('\n')
    for e in data[fn]:
        lines[e['line']] = T[e['text']]
    out = '\n'.join(lines)
    # 保持 UTF-16LE BOM
    with open(os.path.join(outdir, fn), 'wb') as f:
        f.write(out.encode('utf-16'))
    print('ok', fn)
print('ALL DONE')
