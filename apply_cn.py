# -*- coding: utf-8 -*-
"""QP Shooting - Dangerous!! 简体中文补丁（一键版）

补丁内容：
  1. QP Shooting.exe  — locale jpn→chs + 78 条 ANNOUNCE 界面文案（GBK）
  2. conv.dat         — 全部剧情对白脚本（data/conv_zh/*.txt）
  3. model.dat        — 游戏内说明书 5 页图形汉化

用法：
  python apply_cn.py [游戏目录] [--force]
  不带参数时自动通过 Steam 注册表定位游戏目录。

依赖：Python 3.8+，Pillow，numpy
  pip install pillow numpy

还原：把 cn_backup 目录里的文件拷回游戏目录，或在 Steam 中
右键游戏 → 属性 → 已安装文件 → 验证游戏文件完整性。
"""
import sys, os, io, re, hashlib, shutil, struct

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GAME_NAME = 'QP Shooting - Dangerous'
KEY = 'qppass'
FILES = ['QP Shooting.exe', 'conv.dat', 'model.dat']

# 每个文件: (原版 sha256, 汉化后 sha256)
SHA = {
    'QP Shooting.exe': (
        '42519385c2c7ccf811ec9263b9671cdddbb43d77bdfdb558f39c4c388cd994a4',
        '0786b4ab07f1bbf38d1dc206af424e2ec0b896d2ac7ec2f26438c334556f5497'),
    'conv.dat': (
        '86172341501215c07151d1a42b579a035afc06c835173cadd46b61707a0b6f83',
        '43b6e3bc2553ab5eaf7abeed9d0e41f4c9a3ac8a871fcfda0c61b8df5b5a5b1b'),
    'model.dat': (
        '8150e0be1b28b85a5555ae8196a84ac0abd4aa61c9fb959bd93cf00dc1b8e1e2',
        '1cbb72099553c6562e6d67ef6d7ff6b37d0ceefbc2f4bdd37f10e50efb1ae944'),
}

# ================= 1. exe 补丁 =================
EXE_OFF = 0x436060
EXE_END = 0x437267 + 5

ANNOUNCE = {
'ANNOUNCE_MENU_ARCADE': '从头开始依次游玩各个关卡',
'ANNOUNCE_MENU_CONQUEST': '保存进度并逐关征服',
'ANNOUNCE_MENU_USAROOM': '学习新阵型或查看奖杯信息',
'ANNOUNCE_MENU_RECORD': '查看街机模式排行榜',
'ANNOUNCE_MENU_REPLAY': '观看保存的回放',
'ANNOUNCE_MENU_CONFIG': '更改游戏设置',
'ANNOUNCE_MENU_MANUAL': '了解游戏基本操作',
'ANNOUNCE_MENU_EXIT': '退出游戏',
'ANNOUNCE_SMENU_DIFF': '选择难度',
'ANNOUNCE_SMENU_SLOT': '选择设置槽位',
'ANNOUNCE_SMENU_SAVE': '选择文件',
'ANNOUNCE_SMENU_STILE': '选择游玩风格',
'ANNOUNCE_SMENU_AUTOSLOW': '切换自动慢速模式',
'ANNOUNCE_SMENU_CTRLTYPE': '选择操作方式',
'ANNOUNCE_SMENU_FORMATION': '选择你的阵型',
'ANNOUNCE_SMENU_SLOTNAME': '输入设置槽位名称',
'ANNOUNCE_SMENU_SAVENAME': '输入存档名称',
'ANNOUNCE_SMENU_USA': '选择要进入的房间',
'ANNOUNCE_REPLAY_SELECT': '选择要观看的回放',
'ANNOUNCE_REPLAY_STAGE': '选择要观看的关卡',
'ANNOUNCE_REPLAY_ERROR': '没有找到可用的回放',
'ANNOUNCE_USA_FORM': '选择要学习的阵型',
'ANNOUNCE_USA_FORM_BUY': '学习这个阵型？',
'ANNOUNCE_USA_FORM_ERROR0': 'R点数不足，无法学习该阵型',
'ANNOUNCE_USA_FORM_ERROR1': '已经学习过该阵型',
'ANNOUNCE_USA_FORM_ERROR2': '尚未学习该阵型',
'ANNOUNCE_USA_TROPHY': '用 ← → 键切换难度',
'ANNOUNCE_TRANSFER': '你的R点数已转移',
'ANNOUNCE_TRANSFER_ERROR': '读取 QP Shooting 1 数据失败',
'ANNOUNCE_TRANSFER_ERROR2': '点数已经转移过了',
'ANNOUNCE_RECORD': '用 ← → 键切换记录难度',
'ANNOUNCE_INQUIRY': '打开问卷页面？',
'ANNOUNCE_DELETE_SLOT': '确定要删除这些设置吗？',
'ANNOUNCE_DELETE_SAVE': '确定要删除这个存档吗？',
'ANNOUNCE_CONFIG_SCREEN': '更改显示模式',
'ANNOUNCE_CONFIG_WINDOW': '更改窗口大小',
'ANNOUNCE_CONFIG_ASPECT': '更改画面放大方式',
'ANNOUNCE_CONFIG_COLOR': '更改画面色彩深度',
'ANNOUNCE_CONFIG_FPS': '切换每秒帧数显示',
'ANNOUNCE_CONFIG_DARK': '切换背景加深以便看清弹幕',
'ANNOUNCE_CONFIG_BLUR': '切换动态模糊效果',
'ANNOUNCE_CONFIG_SKIP': '跳过全部剧情对话',
'ANNOUNCE_CONFIG_SE': '更改音效音量',
'ANNOUNCE_CONFIG_BGM': '更改背景音乐音量',
'ANNOUNCE_CONFIG_CONTROLLER': '更改手柄/键盘按键设置',
'ANNOUNCE_CONFIG_MENU': '返回主菜单',
'ANNOUNCE_CONFIG_BUTTON_DEFAULT': '按确认键更改该动作的按键',
'ANNOUNCE_CONFIG_BUTTON_BIND': '按下想要绑定的按键（ESC取消）',
'ANNOUNCE_CONFIG_BUTTON_OK': '更改设置以使用该按键布局',
'ANNOUNCE_CONFIG_BUTTON_RESET': '将操作恢复为默认设置',
'ANNOUNCE_CONFIG_BUTTON_CANCEL': '放弃按键布局并返回菜单',
'ANNOUNCE_SETTING_STYLE': '选择游玩风格',
'ANNOUNCE_SETTING_SLOW': '切换射击时自动慢速移动',
'ANNOUNCE_SETTING_CONTROL': '选择阵型切换模式',
'ANNOUNCE_SETTING_FORM_A': '选择Rbit阵型A',
'ANNOUNCE_SETTING_FORM_B': '选择Rbit阵型B',
'ANNOUNCE_SETTING_FORM_C': '选择Rbit阵型C',
'ANNOUNCE_SETTING_OK': '以当前设置开始游戏',
'ANNOUNCE_SETTING_CANCEL': '取消并返回菜单',
'ANNOUNCE_SETTING_DELETE_SAVE': '删除该存档',
'ANNOUNCE_SETTING_DELETE_SLOT': '删除这些设置',
'ANNOUNCE_SETTING_ERROR': '现在无法更改这些设置',
'ANNOUNCE_SLOT_SELECT': '选择要使用的槽位',
'ANNOUNCE_SAVE_SELECT': '选择要使用的存档',
'ANNOUNCE_FORM_SELECT': '选择要设置的阵型',
'ANNOUNCE_STYLE_SELECT': '选择游玩风格',
'ANNOUNCE_STAGE_SELECT': '选择要继续的关卡',
'ANNOUNCE_PAUSE_RETURN': '返回游戏',
'ANNOUNCE_PAUSE_RETRY': '从头开始重新挑战',
'ANNOUNCE_PAUSE_RESTART': '从头开始重新观看',
'ANNOUNCE_PAUSE_EXIT': '退出到主菜单',
'ANNOUNCE_RESULT_SAVE': '警告：将覆盖该征服模式关卡的数据',
'ANNOUNCE_RESULT_REPLAY': '已保存回放 "hqp2＊＊＊.rpl"',
'ANNOUNCE_MANUAL_1': '第1/5页',
'ANNOUNCE_MANUAL_2': '第2/5页',
'ANNOUNCE_MANUAL_3': '第3/5页',
'ANNOUNCE_MANUAL_4': '第4/5页',
'ANNOUNCE_MANUAL_5': '第5/5页',
}

def patch_exe(path):
    data = bytearray(open(path, 'rb').read())
    # 1) locale jpn -> chs（让游戏加载中文字体/代码页）
    i = bytes(data).find(b'jpn\x00')
    assert i != -1, '未找到 locale 字符串 jpn，文件可能不是原版'
    data[i:i+3] = b'chs'
    # 2) ANNOUNCE 资源块翻译（GBK 编码，保持资源总大小不变）
    size = EXE_END - EXE_OFF
    blob = bytes(data[EXE_OFF:EXE_OFF+size])
    lines = blob.split(b'\r\n')
    out, hit = [], 0
    for l in lines:
        if l.startswith(b'< ANNOUNCE_'):
            tag = l[2:l.index(b' >')].decode('ascii')
            if tag in ANNOUNCE:
                out.append(b'< ' + tag.encode('ascii') + b' > < ' + ANNOUNCE[tag].encode('gbk') + b' >')
                hit += 1
            else:
                out.append(l)
        else:
            out.append(l)
    assert hit == len(ANNOUNCE), 'ANNOUNCE 命中 %d/%d，资源块位置可能不对' % (hit, len(ANNOUNCE))
    new = b'\r\n'.join(out)
    assert new.endswith(b'[EOF]'), '资源块结尾异常'
    new += b'\x00'
    assert len(new) <= size, (len(new), size)
    new += b'\x00' * (size - len(new))
    data[EXE_OFF:EXE_OFF+size] = new
    return bytes(data)

# ================= 2. conv.dat 补丁 =================
def patch_conv(path):
    from dxa import Dxa
    a = Dxa(open(path, 'rb').read(), KEY)
    zhdir = os.path.join(SCRIPT_DIR, 'data', 'conv_zh')
    repl, n = {}, 0
    for name, data, k in a.files():
        base = name.replace('/', '\\').split('\\')[-1]
        p = os.path.join(zhdir, base)
        if os.path.exists(p):
            repl[name] = open(p, 'rb').read()
            n += 1
    assert n >= 20, '翻译脚本只匹配到 %d 个，原版结构可能不同' % n
    tmp = os.path.join(SCRIPT_DIR, '_conv_tmp.dat')
    a.repack(repl, tmp)
    out = open(tmp, 'rb').read()
    os.remove(tmp)
    # 回读验证
    b = Dxa(out, KEY)
    cnt = 0
    for name, data, k in b.files():
        if name in repl:
            assert data == repl[name], 'repack 校验失败: ' + name
            cnt += 1
    assert cnt == n
    return out, n

# ================= 3. model.dat 补丁（说明书 5 页） =================
GOLD = (247, 192, 99)
BLACK = (0, 0, 0)

def _font(size, bold):
    from PIL import ImageFont
    return ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc' if bold else 'C:/Windows/Fonts/msyh.ttc', size)

# (page, y0, y1, x0, x1, kind, text[, maxw])
# kind: T=页标题 H=节标题 B=正文 b=要点/标签  text空=只擦除
# 擦除区: x0-5 ~ x1+5, y0-3 ~ y1+3 (仅alpha>128像素); 绘制宽默认x1-x0
L = [
# ---- Page 1: 游戏设置 ----
(1, 5, 15, 6, 126, 'T', '游戏设置'),
(1, 5, 15, 396, 541, 'H', '—自动慢速移动'),
(1, 23, 33, 397, 770, 'B', '开启后，射击时'),
(1, 42, 44, 396, 469, 'B', ''),  # "when firing." 升部残影补擦
(1, 45, 51, 397, 469, 'B', '会自动进入慢速移动。', 250),
(1, 59, 69, 397, 759, 'B', '关闭后，需要按专用按键'),
(1, 78, 87, 397, 518, 'B', '手动进入慢速移动。', 250),
(1, 113, 123, 396, 512, 'H', '—阵型切换模式'),
(1, 131, 141, 397, 769, 'B', '设为“顺序切换”时，阵型切换键'),
(1, 149, 160, 397, 647, 'B', '会按 A→B→C→A 循环切换。'),
(1, 168, 177, 397, 730, 'B', '设为“单独切换”时，每种阵型都有专属按键。'),
(1, 185, 195, 397, 770, 'B', '设为“两者皆可”时，阵型切换键和'),
(1, 205, 213, 397, 552, 'B', '专属按键都可以自由使用。', 250),
(1, 239, 249, 396, 518, 'H', '—阵型 A-B-C'),
(1, 257, 267, 398, 748, 'B', '在此选择 3 种要在游戏中使用的阵型。'),
(1, 278, 288, 396, 425, 'B', ''),
(1, 293, 303, 6, 75, 'H', '→游玩风格', 100),
(1, 293, 303, 399, 765, 'B', '※详情参见本说明书的“阵型”一节。'),
(1, 312, 321, 6, 236, 'B', '在此选择你的游玩风格。'),
(1, 329, 339, 8, 364, 'B', '※详情参见本说明书的“游玩风格”一节。'),
(1, 329, 339, 397, 762, 'B', '各项设置可以保存到槽位中，'),
(1, 350, 357, 397, 442, 'B', '方便下次快速调用。', 250),
# ---- Page 2: 游玩风格/阵型 ----
(2, 5, 15, 6, 68, 'T', '游玩风格'),
(2, 8, 15, 397, 469, 'H', '阵型'),
(2, 36, 48, 611, 771, 'B', 'QP 在战斗中会得到'),
(2, 49, 67, 611, 771, 'B', '“Rbit”的协助，'),
(2, 71, 82, 611, 654, 'B', '它们会以编队形式发起攻击。', 160),
(2, 108, 118, 610, 771, 'B', '最多可以选择三种 Rbit，'),
(2, 123, 137, 611, 771, 'B', '熟练运用它们是取胜的关键。', 160),
(2, 147, 154, 611, 741, 'B', ''),
(2, 185, 195, 397, 771, 'B', '每种编队不仅站位不同，'),
(2, 204, 213, 397, 560, 'B', '性能也各有差异，如下所示。'),
(2, 222, 231, 397, 535, 'b', '・弹速与威力'),
(2, 240, 249, 397, 543, 'b', '・自机移动速度'),
(2, 258, 267, 397, 600, 'b', '・击杀敌人时的奖励'),
(2, 276, 286, 399, 686, 'B', '※这些会以“★+x”的形式显示在名称旁。'),
(2, 311, 321, 399, 720, 'B', '※部分编队有自己独特的操作方式。'),
(2, 330, 339, 397, 450, 'B', ''),
(2, 347, 357, 397, 741, 'B', '各编队的具体用法，请参阅游戏内的编队说明。'),
(2, 293, 305, 6, 373, 'B', '更换游玩风格会稍微改变 QP 的行动特性。'),
(2, 311, 321, 5, 303, 'B', '都试试看，找到最适合自己的风格吧。'),
(2, 329, 341, 6, 369, 'B', '根据游玩风格与阵型的组合，'),
(2, 347, 357, 6, 287, 'B', '说不定还能发现意想不到的效果。'),
# ---- Page 3: 游戏界面说明 (左上插图x10-233 y27-194不动, 正文在x244-394列) ----
(3, 5, 15, 6, 174, 'T', '游戏界面说明'),
(3, 5, 15, 397, 512, 'H', '5) 敌人血条'),
(3, 23, 33, 397, 769, 'B', '显示敌人的剩余血量。部分敌人会一直显示，'),
(3, 41, 51, 397, 770, 'B', '其余敌人只会在受到攻击时显示。'),
(3, 62, 69, 397, 502, 'B', ''),
(3, 27, 36, 245, 296, 'H', '1) 得分'),
(3, 45, 54, 245, 364, 'B', '显示当前得分。'),
(3, 67, 72, 245, 279, 'B', ''),
(3, 99, 108, 245, 296, 'H', '2) 生命数'),
(3, 117, 126, 245, 381, 'B', '显示剩余生命数。'),
(3, 135, 144, 245, 376, 'B', '生命数归零时，游戏结束。'),
(3, 153, 164, 244, 365, 'B', ''),
(3, 203, 215, 6, 210, 'H', '3) 链数计数/链量表'),
(3, 221, 231, 6, 378, 'B', '显示快速连续获取的星星数量，会影响得分。'),
(3, 240, 249, 6, 373, 'B', '链数增长时指针会随之转动，'),
(3, 260, 269, 6, 200, 'B', '链数归零时指针回到原位。'),
(3, 293, 306, 6, 108, 'H', '4) 超载槽'),
(3, 311, 321, 6, 380, 'B', '显示收集的超载能量。变绿后即可'),
(3, 330, 341, 6, 389, 'B', '发动超载模式。超载模式可用后，'),
(3, 347, 359, 6, 366, 'B', '能量会显示在自机周围，最高可累积至 150%。'),
(3, 186, 195, 397, 751, 'B', '敌人处于防御状态、难以造成伤害时，'),
(3, 204, 213, 397, 521, 'B', '血条会变成蓝色。'),
# ---- Page 4: 游戏规则 (正文行前有彩色图标, 起点见各行x0) ----
(4, 5, 15, 6, 83, 'T', '游戏规则'),
(4, 23, 35, 5, 348, 'B', '本作是较为正统的纵向卷轴射击游戏，'),
(4, 42, 51, 6, 174, 'B', '需要按顺序通关各个关卡。'),
(4, 59, 69, 5, 383, 'B', '要通关关卡，必须抵达关底的最终 Boss，'),
(4, 80, 87, 6, 64, 'B', '并将其击败。', 150),
(4, 95, 105, 5, 233, 'B', '本作没有接关（Continue）机制。'),
(4, 131, 141, 6, 108, 'H', '—敌方攻击'),
(4, 149, 159, 6, 327, 'B', '敌方攻击大致分为以下几类。'),
(4, 169, 180, 65, 107, 'b', '・子弹'),
(4, 187, 198, 60, 343, 'B', '击坠发射子弹的敌人后，'),
(4, 205, 218, 60, 183, 'B', '子弹会变成道具。'),
(4, 242, 251, 67, 114, 'b', '・导弹'),
(4, 260, 269, 60, 286, 'B', '导弹可以被攻击破坏。'),
(4, 299, 305, 67, 104, 'b', '・激光'),
(4, 314, 324, 61, 386, 'B', '击坠发射激光的敌人后，激光会变成绿色星星。'),
(4, 332, 342, 61, 373, 'B', '超载模式无法消除激光，但发动期间'),
(4, 350, 360, 62, 351, 'B', '可以短时间免疫激光伤害。'),
(4, 5, 15, 396, 513, 'H', '—敌方障碍物'),
(4, 27, 37, 450, 769, 'B', '有些敌方能力并不算攻击，'),
(4, 45, 55, 451, 649, 'B', '但会与你发生碰撞。'),
(4, 78, 92, 449, 763, 'B', '它们周围有明显的光环，'),
(4, 100, 112, 449, 587, 'B', '提示玩家注意躲避。'),
(4, 149, 159, 396, 492, 'H', '—自机判定点'),
(4, 171, 183, 449, 752, 'B', 'QP 的中弹判定只有她正中央的一个小点，'),
(4, 189, 201, 449, 735, 'B', '慢速移动时可以看到。'),
(4, 239, 249, 396, 435, 'H', '—星星'),
(4, 293, 303, 397, 762, 'B', '破坏导弹或击坠敌人时会出现星星道具。'),
(4, 311, 321, 397, 765, 'B', '收集星星可以增加得分。有时还能获得'),
(4, 329, 339, 397, 769, 'B', '更多 Rbit，绿色道具则能积攒超载槽。'),
(4, 347, 357, 397, 675, 'B', '得分多少取决于当时的链数。'),
# ---- Page 5: 超载模式 (右上截图框x644-771 y8-103不动) ----
(5, 5, 18, 6, 93, 'H', '—超载模式'),
(5, 23, 35, 6, 394, 'B', '超载槽变绿后即可发动超载模式。'),
(5, 41, 53, 6, 368, 'B', '超载模式期间，QP 会笼罩在绿色光环中，'),
(5, 59, 69, 6, 130, 'B', '获得以下效果：'),
(5, 78, 87, 227, 368, 'b', '・攻击力提升。'),
(5, 95, 105, 228, 371, 'b', '・中弹时，画面上的子弹会全部', 150),
(5, 112, 123, 222, 379, 'B', '消失，且不会损失生命。'),
(5, 131, 142, 222, 356, 'B', ''),
(5, 149, 161, 223, 383, 'b', '・链量表固定在最大值。'),
(5, 167, 176, 223, 355, 'b', ''),
(5, 186, 197, 223, 365, 'b', '・出现更多星星。'),
(5, 203, 212, 223, 373, 'b', '・绿色星星变成黄色星星。', 155),
(5, 219, 233, 218, 299, 'b', ''),
(5, 257, 267, 6, 376, 'B', '此外，周围的子弹也会变成黄色星星，'),
(5, 276, 285, 6, 225, 'B', '是很实用的回避手段。'),
(5, 311, 323, 6, 352, 'B', '陷入危机时，果断发动超载模式吧。'),
(5, 329, 341, 6, 394, 'B', '简单难度下，超载槽会自动回复，'),
(5, 348, 357, 6, 225, 'B', '直到可以发动超载模式为止。'),
(5, 5, 19, 396, 487, 'H', '—超载终结'),
(5, 23, 33, 401, 638, 'B', '在超载模式中击坠敌人的话，'),
(5, 41, 54, 402, 638, 'B', '即可获得超载终结（Hyper Finish）'),
(5, 58, 71, 401, 638, 'B', '的奖励分。'),
(5, 95, 105, 396, 453, 'H', '—奖励生命', 100),
(5, 114, 123, 397, 746, 'B', '得分超过特定值时可以获得 1UP。'),
(5, 132, 143, 399, 703, 'B', '生命数上限为 9 条。'),
(5, 167, 177, 396, 451, 'H', '奖杯'),
(5, 186, 195, 397, 771, 'B', '在游戏中达成各种条件即可获得“奖杯”。'),
(5, 204, 213, 397, 462, 'B', ''),
(5, 239, 249, 400, 770, 'B', '部分条件无法在征服模式中达成，'),
(5, 257, 268, 397, 769, 'B', '想全收集的话请挑战街机模式。'),
(5, 275, 285, 397, 761, 'B', '另外，每个难度各自计算奖杯，'),
(5, 293, 305, 397, 742, 'B', '正好作为挑战自我的理由。'),
(5, 330, 339, 398, 766, 'B', '已获得的奖杯可以在 Rbit 房间的'),
(5, 348, 357, 397, 492, 'B', '“奖杯”页面查看。'),
]

def find_underline(arr, x0, x1, y1):
    """在 y1-1..y1+4 找水平连续深色线(下划线), 返回 (y, xa, xb, color) 或 None"""
    for y in range(y1 - 1, min(y1 + 5, 512)):
        s, e = max(0, x0 - 5), min(1023, x1 + 5)
        row = arr[y, s:e + 1].astype(int)
        dark = row.sum(axis=1) < 420          # 金色sum=538, 棕=207, 黑=0
        best = cur = 0; bs = 0
        for i, v in enumerate(dark):
            if v:
                if cur == 0: st = i
                cur += 1
                if cur > best: best, bs = cur, st
            else:
                cur = 0
        if best >= 30:
            seg = arr[y, s + bs:s + bs + best]
            cols = [tuple(p) for p in seg]
            col = max(set(cols), key=cols.count)
            return y, s + bs, s + bs + best - 1, tuple(int(c) for c in col)
    return None

def patch_model(path):
    from dxa import Dxa
    from PIL import Image, ImageDraw
    import numpy as np
    d = Dxa(open(path, 'rb').read(), KEY)
    imgs, masks = {}, {}
    for name, data, k in d.files():
        if name.startswith('manual_0') and name.endswith('.bmp') and '_a' not in name:
            imgs[name] = data
        elif name.startswith('manual_0') and name.endswith('_a.bmp'):
            m = np.array(Image.open(io.BytesIO(data)).convert('L'))
            masks[name[:-6] + '.bmp'] = m > 128   # manual_01_a.bmp -> manual_01.bmp
    # 说明只用到 1-5 页；包内可能还有更多 manual 页，全部原样保留
    need = ['manual_%02d.bmp' % i for i in range(1, 6)]
    assert all(n in imgs and n in masks for n in need), 'manual 1-5 页不齐全'

    pages = {}
    for row in L:
        pages.setdefault(row[0], []).append(row)

    out = {}
    for pg, rows in pages.items():
        name = 'manual_%02d.bmp' % pg
        arr = np.array(Image.open(io.BytesIO(imgs[name])).convert('RGB'))
        mask = masks[name]
        # 第一遍: 检测标题下划线
        ulines = {}
        for row in rows:
            _, y0, y1, x0, x1, kind, txt = row[:7]
            if kind in 'THb' and txt:
                u = find_underline(arr, x0, x1, y1)
                if u:
                    ulines[(y0, y1, x0)] = u
        # 第二遍: 擦除(alpha蒙版保护面板外像素)
        for row in rows:
            _, y0, y1, x0, x1, kind, txt = row[:7]
            ey0, ey1 = max(0, y0 - 3), min(511, y1 + 3)
            ex0, ex1 = max(0, x0 - 5), min(1023, x1 + 5)
            sel = mask[ey0:ey1 + 1, ex0:ex1 + 1]
            arr[ey0:ey1 + 1, ex0:ex1 + 1][sel] = GOLD
        # 第三遍: 中文绘制 + 下划线重画
        im = Image.fromarray(arr)
        d2 = ImageDraw.Draw(im)
        for row in rows:
            _, y0, y1, x0, x1, kind, txt = row[:7]
            maxw = row[7] if len(row) > 7 else (x1 - x0)
            if not txt:
                continue
            h = y1 - y0
            if kind == 'T':
                size = min(16, h + 3)
            elif kind == 'H':
                size = min(15, h + 3)
            else:
                size = min(13, h + 2)
            while size > 9:
                f = _font(size, kind in 'THb')
                if d2.textlength(txt, font=f) <= maxw:
                    break
                size -= 1
            yc = (y0 + y1) / 2
            d2.text((x0, yc), txt, font=f, fill=BLACK, anchor='lm')
            u = ulines.get((y0, y1, x0))
            if u:
                uy, _, _, col = u
                tw = int(d2.textlength(txt, font=f))
                d2.line((x0 - 2, uy, x0 + tw + 2, uy), fill=col, width=1)
        buf = io.BytesIO()
        im.save(buf, format='BMP')
        out[name] = buf.getvalue()

    tmp = os.path.join(SCRIPT_DIR, '_model_tmp.dat')
    d.repack(out, tmp)
    res = open(tmp, 'rb').read()
    os.remove(tmp)
    return res

# ================= 主流程 =================
def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def autodetect():
    # 当前目录就是游戏目录?
    if os.path.exists(os.path.join(os.getcwd(), FILES[0])):
        return os.getcwd()
    cands = []
    try:
        import winreg
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Valve\Steam')
        sp, _ = winreg.QueryValueEx(k, 'SteamPath')
        sp = sp.replace('/', os.sep)
        cands.append(os.path.join(sp, 'steamapps', 'common', GAME_NAME))
        vdf = os.path.join(sp, 'steamapps', 'libraryfolders.vdf')
        if os.path.exists(vdf):
            txt = open(vdf, encoding='utf-8', errors='replace').read()
            for m in re.finditer(r'"path"\s*"([^"]+)"', txt):
                cands.append(os.path.join(m.group(1).replace('\\\\', os.sep), 'steamapps', 'common', GAME_NAME))
    except OSError:
        pass
    for c in cands:
        if os.path.exists(os.path.join(c, FILES[0])):
            return c
    return None

def main():
    force = '--force' in sys.argv
    args = [a for a in sys.argv[1:] if a != '--force']
    gamedir = args[0] if args else autodetect()
    if not gamedir or not os.path.exists(os.path.join(gamedir, FILES[0])):
        print('未找到游戏目录，请手动指定: python apply_cn.py "游戏目录"')
        sys.exit(1)
    print('游戏目录:', gamedir)
    sys.path.insert(0, SCRIPT_DIR)

    todo = []
    for f in FILES:
        p = os.path.join(gamedir, f)
        if not os.path.exists(p):
            print('[%s] 缺失！' % f); sys.exit(1)
        s = sha256(p)
        if s == SHA[f][1]:
            print('[%s] 已是汉化版，跳过' % f)
        elif s == SHA[f][0]:
            todo.append(f)
            print('[%s] 原版，待打补丁' % f)
        elif force:
            todo.append(f)
            print('[%s] 哈希不认识（--force 强制打补丁）' % f)
        else:
            print('[%s] 不是已知的原版或汉化版文件。' % f)
            print('    请先在 Steam 中“验证游戏文件完整性”还原成原版再运行；')
            print('    或用 --force 强制打补丁。')
            sys.exit(1)

    if not todo:
        print('\n全部文件都已是汉化版，无需处理。')
        return

    bakdir = os.path.join(gamedir, 'cn_backup')
    os.makedirs(bakdir, exist_ok=True)
    for f in todo:
        p = os.path.join(gamedir, f)
        bp = os.path.join(bakdir, f)
        if not os.path.exists(bp):
            shutil.copy2(p, bp)
            print('[%s] 已备份原版 -> cn_backup/' % f)

    ok = True
    for f in todo:
        p = os.path.join(gamedir, f)
        try:
            if f == FILES[0]:
                res = patch_exe(p)
                msg = 'locale+78 条界面文案'
            elif f == 'conv.dat':
                res, n = patch_conv(p)
                msg = '对白脚本 %d 个' % n
            else:
                res = patch_model(p)
                msg = '说明书 5 页'
            with open(p, 'wb') as fh:
                fh.write(res)
            s = sha256(p)
            mark = '一致' if s == SHA[f][1] else '不一致(%s)' % s[:12]
            print('[%s] 补丁完成（%s），校验%s' % (f, msg, mark))
        except Exception as e:
            ok = False
            print('[%s] 失败: %r' % (f, e))
    print('\n完成！如需还原，用 cn_backup 里的文件覆盖回去，或走 Steam 校验。' if ok else '\n有失败项，未完全应用。')

if __name__ == '__main__':
    main()
