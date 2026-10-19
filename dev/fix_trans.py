# -*- coding: utf-8 -*-
"""修复 qp_trans.py 被 heredoc 转义破坏的部分。"""
data = open('qp_trans.py', 'rb').read()

# 1. 双真实CR的键 -> \r 转义
data = data.replace(b'"!?\r\r"', b'"!?\\r"')
data = data.replace(b'"...!?\r\r"', b'"...!?\\r"')
data = data.replace(b'"Thank you...\r\r"', b'"Thank you...\\r"')

# 2. usa_form_obit 键：字面 \n 保留，字面 \r 结尾 -> 转义 \r
data = data.replace(
    b'"Moves around QP\\\\nand attacks in\\\\nall directions.\\\\r"',
    b'"Moves around QP\\\\nand attacks in\\\\nall directions.\\r"')
data = data.replace(
    b'"While it may appear versatile,\\\\nits power is limited,\\\\nso you must not get cocky.\\\\r"',
    b'"While it may appear versatile,\\\\nits power is limited,\\\\nso you must not get cocky.\\r"')
data = data.replace(b'"Recommended degree, C.\\\\r"', b'"Recommended degree, C.\\r"')
data = data.replace(b'"Try it out for yourself.\\\\r"', b'"Try it out for yourself.\\r"')

# 3. 译文侧结尾真实 CR+引号 -> \r 转义
data = data.replace(b'\r"', b'\\r"')

# 4. 行尾真实 CR（CRLF）清除为 LF
data = data.replace(b'\r\n', b'\n')

open('qp_trans.py', 'wb').write(data)

# 校验语法
import ast
ast.parse(open('qp_trans.py', encoding='utf-8').read())
print('syntax OK')
