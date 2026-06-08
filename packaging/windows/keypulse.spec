# -*- mode: python ; coding: utf-8 -*-

import os

from PyInstaller.utils.hooks import collect_submodules

project_root = os.path.abspath(os.path.join(SPECPATH, "../.."))
hiddenimports = collect_submodules("pynput") + collect_submodules("sqlalchemy")

a = Analysis(
    [os.path.join(project_root, "src/game_input_tracker/__main__.py")],
    pathex=[project_root, os.path.join(project_root, "src")],
    binaries=[],
    datas=[
        (
            os.path.join(project_root, "src/game_input_tracker/assets"),
            "game_input_tracker/assets",
        )
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="KeyPulse",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=os.path.join(project_root, "src/game_input_tracker/assets/keypulse.ico"),
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="KeyPulse",
)
