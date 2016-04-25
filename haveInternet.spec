# -*- mode: python -*-

block_cipher = None


a = Analysis(['haveInternet.pyw'],
             pathex=['C:\\Users\\James\\Documents\\Code!\\Projects\\internet_metrics - Copy'],
             binaries=None,
             datas=None,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='haveInternet',
          debug=False,
          strip=None,
          upx=True,
          console=False,
          icon='globeicon.ico')
