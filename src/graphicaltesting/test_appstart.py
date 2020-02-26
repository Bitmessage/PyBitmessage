from PyQt4 import QtCore, QtGui
from PyQt4.QtTest import QTest


def connectme(dialog):
    """Automate the connect dialog, when run for first time"""
    dialog.show()
    QTest.qWait(1200)
    QtCore.QTimer.singleShot(0, dialog.buttonBox.button(QtGui.QDialogButtonBox.Ok).clicked)
