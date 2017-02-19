import ctypes
import os

srcPath = "C:\\src\\PyBitmessage\\src\\"
qtPath = "C:\\Qt-4.8.7\\"
openSSLPath = "C:\\OpenSSL-1.0.2j\\"
outPath = "C:\\src\\PyInstaller-3.2.1\\bitmessagemain"

# -*- mode: python -*-
a = Analysis([srcPath + 'bitmessagemain.py'],
             pathex=[outPath],
             hiddenimports=['messagetypes'],
             hookspath=None,
             runtime_hooks=None)

# manually add messagetypes directory and its listing
with open(os.path.join(srcPath, 'messagetypes.txt'), 'wt') as f:
	for mt in os.listdir(os.path.join(srcPath, 'messagetypes')):
		if mt == "__init__.py":
			continue
		splitted = os.path.splitext(mt)
		if splitted[1] != ".py":
			continue
		f.write(mt + "\n")
		a.scripts.append((os.path.join('messagetypes', mt), os.path.join(srcPath, 'messagetypes', mt), 'PYMODULE'))
a.datas.append(('messagetypes.txt', os.path.join(srcPath, 'messagetypes.txt'), 'DATA'))

# fix duplicates
for d in a.datas:
    if 'pyconfig' in d[0]: 
        a.datas.remove(d)
        break
		
def addTranslations():
    import os
    extraDatas = []
    for file in os.listdir(srcPath + 'translations'):
        if file[-3:] != ".qm":
            continue
        extraDatas.append((os.path.join('translations', file), os.path.join(srcPath, 'translations', file) 'DATA'))
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

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          a.binaries,
          name='Bitmessage.exe',
          debug=False,
          strip=None,
          upx=False,
          console=False, icon= os.path.join(srcPath, 'images', 'can-icon.ico')
