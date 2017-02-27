import ctypes
import os
import time

srcPath = "C:\\src\\PyBitmessage\\src\\"
qtPath = "C:\\Qt-4.8.7\\"
openSSLPath = "C:\\OpenSSL-1.0.2j\\bin\\"
outPath = "C:\\src\\PyInstaller-3.2.1\\bitmessagemain"
today = time.strftime("%Y%m%d")
snapshot = False

os.rename(os.path.join(srcPath, '__init__.py'), os.path.join(srcPath, '__init__.py.backup'))

# -*- mode: python -*-
a = Analysis([srcPath + 'bitmessagemain.py'],
             pathex=[outPath],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)

os.rename(os.path.join(srcPath, '__init__.py.backup'), os.path.join(srcPath, '__init__.py'))

def addTranslations():
    import os
    extraDatas = []
    for file in os.listdir(srcPath + 'translations'):
        if file[-3:] != ".qm":
            continue
        extraDatas.append((os.path.join('translations', file), os.path.join(srcPath, 'translations', file), 'DATA'))
    for file in os.listdir(qtPath + 'translations'):
        if file[0:3] != "qt_" or file[5:8] != ".qm":
            continue
        extraDatas.append((os.path.join('translations', file), os.path.join(qtPath, 'translations', file), 'DATA'))
    return extraDatas

def addUIs():
    import os
    extraDatas = []
    for file in os.listdir(srcPath + 'bitmessageqt'):
        if file[-3:] != ".ui":
            continue
        extraDatas.append((os.path.join('ui', file), os.path.join(srcPath, 'bitmessageqt', file), 'DATA'))
    return extraDatas

# append the translations directory
a.datas += addTranslations()
a.datas += addUIs()

if ctypes.sizeof(ctypes.c_voidp) == 4:
	arch=32
else:
	arch=64

a.binaries += [('libeay32.dll', openSSLPath + 'libeay32.dll', 'BINARY'),
	(os.path.join('bitmsghash', 'bitmsghash%i.dll' % (arch)), os.path.join(srcPath, 'bitmsghash', 'bitmsghash%i.dll' % (arch)), 'BINARY'),
	(os.path.join('bitmsghash', 'bitmsghash.cl'), os.path.join(srcPath, 'bitmsghash', 'bitmsghash.cl'), 'BINARY'),
	(os.path.join('sslkeys', 'cert.pem'), os.path.join(srcPath, 'sslkeys', 'cert.pem'), 'BINARY'),
	(os.path.join('sslkeys', 'key.pem'), os.path.join(srcPath, 'sslkeys', 'key.pem'), 'BINARY')
	]

with open(os.path.join(srcPath, 'version.py'), 'rt') as f:
    softwareVersion = f.readline().split('\'')[1]
    
fname = 'Bitmessage_%s_%s.exe' % ("x86" if arch == 32 else "x64", softwareVersion)
if snapshot:
    fname = 'Bitmessagedev_%s_%s.exe' % ("x86" if arch == 32 else "x64", today)
    
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          a.binaries,
          name=fname,
          debug=False,
          strip=None,
          upx=False,
          console=False, icon= os.path.join(srcPath, 'images', 'can-icon.ico'))
