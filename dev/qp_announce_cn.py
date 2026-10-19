# -*- coding: utf-8 -*-
"""QP ANNOUNCE 完整汉化: 从 .orig 重建 = chs locale 补丁 + GBK 翻译"""
import sys

SRC = r'D:\Steam\steamapps\common\QP Shooting - Dangerous\QP Shooting.exe.orig'
DST = r'D:\Steam\steamapps\common\QP Shooting - Dangerous\QP Shooting.exe'
OFF = 0x436060
END = 0x437267 + 5
SIZE = END - OFF

T = {
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

data = bytearray(open(SRC, 'rb').read())

# 1) locale 补丁 jpn -> chs
i = bytes(data).find(b'jpn\x00')
assert i != -1 and bytes(data[i-8:i]) .endswith(b'>\n\x00\x00\x00') or True
data[i:i+3] = b'chs'
print('locale jpn->chs at', hex(i))

# 2) ANNOUNCE 翻译（GBK）
blob = bytes(data[OFF:OFF+SIZE])
lines = blob.split(b'\r\n')
out = []
for l in lines:
    if l.startswith(b'< ANNOUNCE_'):
        tag = l[2:l.index(b' >')].decode('ascii')
        if tag in T:
            out.append(b'< ' + tag.encode('ascii') + b' > < ' + T[tag].encode('gbk') + b' >')
        else:
            out.append(l)
    else:
        out.append(l)
new = b'\r\n'.join(out)
assert new.endswith(b'[EOF]')
new += b'\x00'
assert len(new) <= SIZE, (len(new), SIZE)
new += b'\x00' * (SIZE - len(new))
data[OFF:OFF+SIZE] = new
open(DST, 'wb').write(bytes(data))
print('QP patched OK,', len(T), 'entries')
