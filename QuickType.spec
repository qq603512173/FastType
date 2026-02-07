# -*- mode: python ; coding: utf-8 -*-
# QuickType 第一版打包配置
# 使用：pyinstaller QuickType.spec

import os

block_cipher = None

# 若有 build 目录则打包进去（图标等）
build_dir = os.path.join(SPECPATH, 'build')
datas = [(build_dir, 'build')] if os.path.isdir(build_dir) else []
# exe 图标：若有 build/icon.ico 则使用
icon_path = os.path.join(SPECPATH, 'build', 'icon.ico')
icon = icon_path if os.path.isfile(icon_path) else None

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
    name='QuickType',
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
