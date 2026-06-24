# -*- mode: python ; coding: utf-8 -*-

import re

# Read version from version.py
with open('version.py', 'r') as f:
    _version_content = f.read()
_version_match = re.search(r'VERSION:\s*str\s*=\s*"(\d+\.\d+)"', _version_content)
_version = _version_match.group(1) if _version_match else '0.0'

a = Analysis(
    ['cipher_ui_modern.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('message_cipher.py', '.'),
        ('version.py', '.'),
        ('input_validation.py', '.'),
        ('theme_engine.py', '.'),
        ('placeholder_manager.py', '.'),
        ('status_banner.py', '.'),
        ('status_banner_ui.py', '.'),
        ('keyboard_shortcuts.py', '.'),
        ('card_panel.py', '.'),
        ('header_bar.py', '.'),
        ('key_input_row.py', '.'),
        ('action_bar.py', '.'),
    ],
    hiddenimports=['customtkinter'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=f'MessageCipher_v{_version}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
