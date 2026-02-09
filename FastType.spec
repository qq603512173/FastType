# -*- mode: python ; coding: utf-8 -*-
# FastType 第一版打包配置
# 使用：pyinstaller FastType.spec

import os

block_cipher = None

# 只打包 build 下的图标文件，不打包整个 build/（避免把 build/FastType 打进包）
build_dir = os.path.join(SPECPATH, 'build')
datas = []
for name in ('icon.ico', 'icon.png'):
    p = os.path.join(build_dir, name)
    if os.path.isfile(p):
        datas.append((p, 'build'))

# exe 图标：优先使用 build/icon.ico，若不存在则尝试从 icon.png 转换
icon_path = os.path.join(build_dir, 'icon.ico')
icon_png_path = os.path.join(build_dir, 'icon.png')

if os.path.isfile(icon_path):
    icon = icon_path
elif os.path.isfile(icon_png_path):
    # 尝试用 Pillow 将 PNG 转换为 ICO
    try:
        from PIL import Image
        img = Image.open(icon_png_path)
        # ICO 格式需要多个尺寸，创建常用尺寸
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        img.save(icon_path, format='ICO', sizes=sizes)
        icon = icon_path
        print(f"已自动将 {icon_png_path} 转换为 {icon_path}")
    except ImportError:
        print("警告: 未安装 Pillow，无法自动转换 PNG 为 ICO。请手动提供 icon.ico 文件。")
        icon = None
    except Exception as e:
        print(f"警告: 转换图标失败: {e}。请手动提供 icon.ico 文件。")
        icon = None
else:
    icon = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'keyboard', 'pyperclip'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='FastType',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 无黑窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon,
)
