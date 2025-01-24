# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['client.py'],
    pathex=[
        'D:\data\code\python\client_only_encripted\src\client',
        'D:\data\code\python\client_only_encripted\src\client\dialogs',
        'D:\data\code\python\client_only_encripted\src\client\languages',
        'D:\data\code\python\client_only_encripted\src\server\models',
        'D:\data\code\python\client_only_encripted\src\shared',
        'D:\data\code\python\client_only_encripted\src\shared\packets',

    ],
    binaries=[],
    datas=[],
    hiddenimports=[
    'login_pb2', 'opcodes', 'constants', 'helpers', 'map_maker', 'object_mgr', 'shared', 'world_models',
    'chat_dialog', 'create_account_dialog', 'create_role_dialog', 'login_dialog', 'options_dialog', 'packet_params_dialog',
    'chinese', 'game', 'graphics', 'gui', 'model', 'my_ui_console_window', 'my_ui_elements',
    'packet_handler', 'translator', 'dialogs.create_role_dialog', 'dialogs.options_dialog', 'dialogs.login_dialog',
    'dialogs.chat_dialog', 'dialogs.create_account_dialog', 'dialogs.packet_params_dialog',
    'asset_mgr', 'translator',
    'PIL.ImageEnhance', 'pygame_gui', 'PIL',

    'google.protobuf.descriptor', 'google.protobuf.internal.main',
    'google.protobuf.internal.decoder', 'google.protobuf.internal.encoder',
    'sqlalchemy'],
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
