from glob import glob
import os
from PyQt4 import QtCore
from setuptools import setup

name = "Bitmessage"
version = os.getenv("PYBITMESSAGEVERSION", "custom")
mainscript = ["bitmessagemain.py"]

DATA_FILES = [
    ('', ['sslkeys', 'images']),
    ('bitmsghash', ['bitmsghash/bitmsghash.cl', 'bitmsghash/bitmsghash.so']),
    ('translations', glob('translations/*.qm')),
    ('ui', glob('bitmessageqt/*.ui')),
    ('translations', glob(str(QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath)) + '/qt_??.qm')),
    ('translations', glob(str(QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath)) + '/qt_??_??.qm')),
]

setup(
    name = name,
    version = version,
    app = mainscript,
    data_files = DATA_FILES,
    setup_requires = ["py2app"],
    options = dict(
        py2app = dict(
            includes = ['sip', 'PyQt4._qt'],
            iconfile = "images/bitmessage.icns"
        )
    )
)
