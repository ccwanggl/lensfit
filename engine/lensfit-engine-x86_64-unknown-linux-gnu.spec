# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['/home/guoliang/WorkSpace/lensfit/engine/lensfit/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['lensfit.api.server', 'lensfit.core.thin_lens', 'lensfit.core.sensor', 'lensfit.core.utils', 'lensfit.db.models', 'lensfit.db.catalog', 'lensfit.domains.base', 'lensfit.domains.industrial', 'lensfit.matching.engine', 'lensfit.matching.scoring', 'lensfit.visualization.coverage', 'uvicorn', 'fastapi', 'sqlalchemy.ext.baked'],
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
    name='lensfit-engine-x86_64-unknown-linux-gnu',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
