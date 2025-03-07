# -*- mode: python ; coding: utf-8 -*-


block_cipher = pyi_crypto.PyiBlockCipher(key='6150645367566B59703273357638792F423F4528482B4D6251655468576D5A71')


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[
    (r"C:\Users\User\PycharmProjects\LKMshik\.venv2\Lib\site-packages\pywin32_system32\pywintypes38.dll", "."),
    (r"C:\Users\User\PycharmProjects\LKMshik\.venv2\Lib\site-packages\pywin32_system32\pythoncom38.dll", ".")
    ],
    datas=[('images', 'images' ), ('files', 'files')],
    hiddenimports=['skimage.io', 'skimage.transform', 'skimage.filter.rank.core_cy', 'packaging', 'packaging.version',
    'pywin32', 'pywin32-ctypes', 'pypiwin32'],
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
    a.zipfiles,
    a.datas,
    [],
    name='ЛКМщик',
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
    icon=r"C:\Users\User\PycharmProjects\LKMshik\images\icon.ico"
)
