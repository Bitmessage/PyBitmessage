# -*- mode: python -*-
import ctypes
import os
import sys
import time


if ctypes.sizeof(ctypes.c_voidp) == 4:
  arch = 32
else:
  arch = 64

sslName = 'OpenSSL-Win%i' % arch
site_root = os.path.abspath(HOMEPATH)
spec_root = os.path.abspath(SPECPATH)
cdrivePath = site_root[0:3]
srcPath = os.path.join(spec_root[:-20], "src")
qtBase = "PyQt4"
openSSLPath = os.path.join(cdrivePath, sslName)
msvcrDllPath = os.path.join(cdrivePath, "windows", "system32")
outPath = os.path.join(spec_root, "bitmessagemain")

importPath = srcPath 
sys.path.insert(0, importPath)
os.chdir(importPath)

snapshot = False

os.rename(
    os.path.join(srcPath, '__init__.py'),
    os.path.join(srcPath, '__init__.py.backup'))

a = Analysis(
    [os.path.join(srcPath, 'bitmessagemain.py')],
    pathex=[outPath],
    hiddenimports=[
        'bitmessageqt.languagebox', 'pyopencl', 'numpy', 'win32com',
        'setuptools.msvc', '_cffi_backend'
    ],
    hookspath=None,
    runtime_hooks=None,
    excludes=['bsddb', 'bz2', 'tcl', 'tk', 'Tkinter']
)

os.rename(
    os.path.join(srcPath, '__init__.py.backup'),
    os.path.join(srcPath, '__init__.py'))


def addTranslations():
    extraDatas = []
    for file_ in os.listdir(os.path.join(srcPath, 'translations')):
        if file_[-3:] != ".qm":
            continue
        extraDatas.append((
            os.path.join('translations', file_),
            os.path.join(srcPath, 'translations', file_), 'DATA'))
    for libdir in sys.path:
        qtdir = os.path.join(libdir, qtBase, 'translations')
        if os.path.isdir(qtdir):
            break
    if not os.path.isdir(qtdir):
        return extraDatas
    for file_ in os.listdir(qtdir):
        if file_[0:3] != "qt_" or file_[5:8] != ".qm":
            continue
        extraDatas.append((
            os.path.join('translations', file_),
            os.path.join(qtdir, file_), 'DATA'))
    return extraDatas


dir_append = os.path.join(srcPath, 'bitmessageqt')

a.datas += [
    (os.path.join('ui', file_), os.path.join(dir_append, file_), 'DATA')
    for file_ in os.listdir(dir_append) if file_.endswith('.ui')
]

# append the translations directory
a.datas += addTranslations()


excluded_binaries = [
    'QtOpenGL4.dll',
    'QtSvg4.dll',
    'QtXml4.dll',
]
a.binaries = TOC([x for x in a.binaries if x[0] not in excluded_binaries])

a.binaries += [
    # No effect: libeay32.dll will be taken from PyQt if installed
    ('libeay32.dll', os.path.join(openSSLPath, 'libeay32.dll'), 'BINARY'),
    (os.path.join('bitmsghash', 'bitmsghash%i.dll' % arch),
        os.path.join(srcPath, 'bitmsghash', 'bitmsghash%i.dll' % arch),
    'BINARY'),
    (os.path.join('bitmsghash', 'bitmsghash.cl'),
         os.path.join(srcPath, 'bitmsghash', 'bitmsghash.cl'), 'BINARY'),
    (os.path.join('sslkeys', 'cert.pem'),
         os.path.join(srcPath, 'sslkeys', 'cert.pem'), 'BINARY'),
    (os.path.join('sslkeys', 'key.pem'),
         os.path.join(srcPath, 'sslkeys', 'key.pem'), 'BINARY')
]


from version import softwareVersion

today = time.strftime("%Y%m%d")

fname = 'Bitmessage_%s_%s.exe' % (
    "x86" if arch == 32 else "x64",
    today if snapshot else softwareVersion
)

pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name=fname,
    debug=False,
    strip=None,
    upx=False,
    console=False, icon=os.path.join(srcPath, 'images', 'can-icon.ico')
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='main'
)
