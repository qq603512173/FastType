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
    excludes=[
        # 排除不需要的 PyQt5 模块
        'PyQt5.QtWebEngine',
        'PyQt5.QtWebEngineWidgets',
        'PyQt5.QtWebSockets',
        'PyQt5.QtQuick',
        'PyQt5.QtQml',
        'PyQt5.QtMultimedia',
        'PyQt5.QtMultimediaWidgets',
        'PyQt5.QtBluetooth',
        'PyQt5.QtNfc',
        'PyQt5.QtPositioning',
        'PyQt5.QtLocation',
        'PyQt5.QtSensors',
        'PyQt5.QtSerialPort',
        'PyQt5.QtSql',
        'PyQt5.QtTest',
        'PyQt5.QtXml',
        'PyQt5.QtXmlPatterns',
        'PyQt5.QtDesigner',
        'PyQt5.QtHelp',
        'PyQt5.QtOpenGL',
        'PyQt5.QtPrintSupport',
        # 排除不需要的 Python 模块
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'Pillow',  # 已有 icon.ico，不需要运行时转换
        # 排除更多不需要的模块
        'tkinter',
        'unittest',
        'email',
        'http',
        'urllib',
        'xml',
        'xmlrpc',
        'pydoc',
        'doctest',
        'pdb',
        'bdb',
        'pydoc_data',
        'distutils',
        'setuptools',
        'pkg_resources',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 过滤掉不需要的文件以减小体积
# 排除 Qt 翻译文件（如果不需要多语言支持，可节省几 MB）
a.datas = [x for x in a.datas if not any(exclude in str(x[0]).lower() for exclude in [
    'translations',  # Qt 翻译文件
])]

# 排除不需要的 Qt 平台插件
a.binaries = [x for x in a.binaries if not any(exclude in x[0].lower() for exclude in [
    'qwebgl',      # WebGL 平台插件
    'qoffscreen',  # 离屏渲染插件
    'qminimal',    # 最小化平台插件（通常不需要）
])]

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
    upx_exclude=[
        # 排除一些 UPX 压缩可能出问题的文件
        'vcruntime140.dll',
        'vcruntime140_1.dll',
        'msvcp140.dll',
    ],
    runtime_tmpdir=None,
    console=False,  # 无黑窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon,
)
