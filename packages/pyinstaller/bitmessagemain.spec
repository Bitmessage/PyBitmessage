srcPath = "C:\\src\\PyBitmessage\\src\\"
qtPath = "C:\\Qt\\4.8.6\\"
openSSLPath = "C:\\OpenSSL-1.0.2e\\"
outPath = "C:\\src\\PyInstaller\\bitmessagemain"

# -*- mode: python -*-
a = Analysis([srcPath + 'bitmessagemain.py'],
             pathex=[outPath],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
			 
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
        extraDatas.append(('translations\\'+file, srcPath + 'translations\\' + file, 'DATA'))
    for file in os.listdir(qtPath + 'translations'):
        if file[0:3] != "qt_" or file[5:8] != ".qm":
            continue
        extraDatas.append(('translations\\'+file, qtPath + 'translations\\' + file, 'DATA'))
    return extraDatas

def addUIs():
    import os
    extraDatas = []
    for file in os.listdir(srcPath + 'bitmessageqt'):
        if file[-3:] != ".ui":
            continue
        extraDatas.append(('ui\\'+file, srcPath + 'bitmessageqt\\' + file, 'DATA'))
    return extraDatas

# append the translations directory
a.datas += addTranslations()
a.datas += addUIs()

a.binaries.append(('msvcr120.dll', 'C:\\WINDOWS\\system32\\msvcr120.dll', 'BINARY'))

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          a.binaries + [('libeay32.dll', openSSLPath + 'libeay32.dll', 'BINARY'), ('bitmsghash\\bitmsghash32.dll', srcPath + 'bitmsghash\\bitmsghash32.dll', 'BINARY'), ('bitmsghash\\bitmsghash.cl', srcPath + 'bitmsghash\\bitmsghash.cl', 'BINARY'), ('sslkeys\\cert.pem', srcPath + 'sslkeys\\cert.pem', 'BINARY'), ('sslkeys\\key.pem', srcPath + 'sslkeys\\key.pem', 'BINARY')],
          name='Bitmessage.exe',
          debug=False,
          strip=None,
          upx=False,
          console=False, icon= srcPath + 'images\\can-icon.ico')
