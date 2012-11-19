# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'help.ui'
#
# Created: Mon Nov 19 12:25:18 2012
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_helpDialog(object):
    def setupUi(self, helpDialog):
        helpDialog.setObjectName(_fromUtf8("helpDialog"))
        helpDialog.resize(335, 170)
        self.buttonBox = QtGui.QDialogButtonBox(helpDialog)
        self.buttonBox.setGeometry(QtCore.QRect(30, 120, 281, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label = QtGui.QLabel(helpDialog)
        self.label.setGeometry(QtCore.QRect(30, 20, 291, 51))
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.labelHelpURI = QtGui.QLabel(helpDialog)
        self.labelHelpURI.setGeometry(QtCore.QRect(30, 70, 301, 21))
        self.labelHelpURI.setObjectName(_fromUtf8("labelHelpURI"))

        self.retranslateUi(helpDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), helpDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), helpDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(helpDialog)

    def retranslateUi(self, helpDialog):
        helpDialog.setWindowTitle(QtGui.QApplication.translate("helpDialog", "Help", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("helpDialog", "As Bitmessage is a collaborative project, help can be found online in the Bitmessage Wiki:", None, QtGui.QApplication.UnicodeUTF8))
        self.labelHelpURI.setText(QtGui.QApplication.translate("helpDialog", "<a href=\"http://Bitmessage.org/wiki/PyBitmessage_Help\">http://Bitmessage.org/wiki/PyBitmessage_Help</a>", None, QtGui.QApplication.UnicodeUTF8))

