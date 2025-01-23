# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['client.py', 'src\client\packet_handler.py'],
    pathex=[
        'D:\data\code\python\project_mount_christ\src\client\dialogs',
        'D:\data\code\python\project_mount_christ\src\client\languages',
        'D:\data\code\python\project_mount_christ\src\server\models',
        'D:\data\code\python\project_mount_christ\src\shared',
        'D:\data\code\python\project_mount_christ\src\shared\packets',

    ],
    binaries=[],
    datas=[],
    hiddenimports=['graphics', 'PIL.ImageEnhance', 'google.protobuf.descriptor', 'google.protobuf.internal.main', 'google.protobuf.internal.decoder', 'google.protobuf.internal.encoder', 'sqlalchemy'],
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
    name='client',
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
    icon='D:\data\code\python\project_mount_christ\data\imgs\game_icon\ship.ico',
)
