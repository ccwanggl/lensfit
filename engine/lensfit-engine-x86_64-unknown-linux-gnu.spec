# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['/home/guoliang/WorkSpace/optibench/engine/optibench/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['optibench.api.server', 'optibench.api.routers.lab', 'optibench.core.thin_lens', 'optibench.core.sensor', 'optibench.core.utils', 'optibench.db.models', 'optibench.db.catalog', 'optibench.domains.base', 'optibench.domains.industrial', 'optibench.matching.engine', 'optibench.matching.scoring', 'optibench.visualization.coverage', 'optibench.lab', 'optibench.lab.base', 'optibench.lab.registry', 'optibench.lab.schemas', 'optibench.lab.renderer', 'optibench.lab.experiments.thin_lens', 'optibench.lab.experiments.diffraction', 'optibench.lab.experiments.color_mixing', 'optibench.lab.experiments.sensor_coverage', 'uvicorn', 'fastapi', 'sqlalchemy.ext.baked'],
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
    name='optibench-engine-x86_64-unknown-linux-gnu',
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
