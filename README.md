# QP Shooting - Dangerous!! 简体中文补丁

[QP Shooting - Dangerous!!](https://store.steampowered.com/app/316600/) 的民间简体中文补丁。

## 汉化内容

- 主界面与全部菜单的说明文字（exe 内 ANNOUNCE 资源，78 条）
- exe 区域设置 `jpn` → `chs`（让游戏正确使用中文字体渲染）
- 全部剧情对白脚本（conv.dat 内 23 个脚本）
- 游戏内说明书（Manual）全部 5 页图形汉化（含标题下划线重画）

## 使用方法

1. 安装 [Python 3.8+](https://www.python.org/downloads/)（安装时勾选 *Add python.exe to PATH*）
2. 安装依赖：
   ```
   pip install pillow numpy
   ```
3. 在 Steam 中正常安装游戏，保持文件为原版（改过的话先做一次"验证游戏文件完整性"）
4. 下载本仓库（绿色 **Code** → **Download ZIP**，解压；或 `git clone`）
5. 在仓库目录运行：
   ```
   python apply_cn.py
   ```
   补丁器会自动通过 Steam 注册表定位游戏目录；定位失败就手动指定：
   ```
   python apply_cn.py "D:\Steam\steamapps\common\QP Shooting - Dangerous"
   ```
6. 每个文件显示"补丁完成 … 校验一致"即成功，正常启动游戏即可。

## 还原

- 把游戏目录 `cn_backup\` 里的三个文件拷回游戏目录覆盖；或
- Steam：右键游戏 → 属性 → 已安装文件 → **验证游戏文件完整性**

## 说明

- 补丁器逐文件校验 sha256：原版 → 打补丁；已是汉化版 → 自动跳过；其他情况会提示先走 Steam 校验（确信无误时可用 `--force` 强制）。
- 打补丁前会自动把原版备份到游戏目录的 `cn_backup\`。
- 本仓库不含任何游戏本体资源：所有修改都由 `apply_cn.py` 在你本地的游戏文件上现场完成，Steam 校验还原后可随时重新打上。

## 工程文件（dev/）

开发期使用的原始脚本（内含当时开发机上的绝对路径，仅作参考，勿直接运行）：

| 文件 | 用途 |
| --- | --- |
| `dxa.py` | DX Archive (DxLib) v4 打包格式逆向 + 解包/重打包库（apply_cn.py 直接依赖根目录这份） |
| `qp_announce_cn.py` | exe 界面文案 + 区域设置补丁 |
| `extract_all.py` / `extract_texts.py` | 资源与对白文本提取 |
| `qp_trans.py` / `qp_texts.json` / `apply_trans.py` / `fix_trans.py` | 对白翻译映射与回填 |
| `repack_conv.py` | conv.dat 重打包 |
| `qp_manual_patch.py` | 说明书 5 页图形汉化（alpha 蒙版保护 + 下划线检测重画） |

想修改译文：`apply_cn.py` 里的 `ANNOUNCE`（界面文案）、`L`（说明书排版）和 `data/conv_zh/` 下的对白脚本，改完重新运行即可。

---

仅供学习交流，请支持正版。
