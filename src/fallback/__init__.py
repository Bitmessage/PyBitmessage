"""
Fallback expressions help PyBitmessage modules to run without some external
dependencies.


RIPEMD160Hash
-------------

We need to check :mod:`hashlib` for RIPEMD-160, as it won't be available
if OpenSSL is not linked against or the linked OpenSSL has RIPEMD disabled.
Try to use `pycryptodome <https://pypi.org/project/pycryptodome/>`_
in that case.
"""

import hashlib

try:
    hashlib.new('ripemd160')
except ValueError:
    try:
        from Crypto.Hash import RIPEMD
    except ImportError:
        RIPEMD160Hash = None
    else:
        RIPEMD160Hash = RIPEMD.RIPEMD160Hash
else:
    def RIPEMD160Hash(data=None):
        """hashlib based RIPEMD160Hash"""
        hasher = hashlib.new('ripemd160')
        if data:
            hasher.update(data)
        return hasher

try:
    import qtpy
except ImportError:
    try:
        from PyQt5 import QtCore, QtGui, QtWidgets, QtNetwork, uic
    except ImportError:
        qtpy = None
    else:
        import sys
        import types

        QtCore.Signal = QtCore.pyqtSignal
        context = {
            'API': 'pyqt5',  # for tr
            'PYQT_VERSION': QtCore.PYQT_VERSION_STR,
            'QT_VERSION': QtCore.QT_VERSION_STR,
            'QtCore': QtCore,
            'QtGui': QtGui,
            'QtWidgets': QtWidgets,
            'QtNetwork': QtNetwork,
            'uic': uic
        }
        try:
            from PyQt5 import QtTest
        except ImportError:
            pass
        else:
            context['QtTest'] = QtTest
        qtpy = types.ModuleType(
            'qtpy', 'PyQt5 based dynamic fallback for qtpy')
        qtpy.__dict__.update(context)
        sys.modules['qtpy'] = qtpy
