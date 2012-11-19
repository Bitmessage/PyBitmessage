# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'about.ui'
#
# Created: Mon Nov 19 13:33:47 2012
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_aboutDialog(object):
    def setupUi(self, aboutDialog):
        aboutDialog.setObjectName(_fromUtf8("aboutDialog"))
        aboutDialog.resize(360, 402)
        self.buttonBox = QtGui.QDialogButtonBox(aboutDialog)
        self.buttonBox.setGeometry(QtCore.QRect(20, 360, 311, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label = QtGui.QLabel(aboutDialog)
        self.label.setGeometry(QtCore.QRect(70, 126, 111, 20))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.labelVersion = QtGui.QLabel(aboutDialog)
        self.labelVersion.setGeometry(QtCore.QRect(190, 126, 161, 20))
        self.labelVersion.setObjectName(_fromUtf8("labelVersion"))
        self.label_2 = QtGui.QLabel(aboutDialog)
        self.label_2.setGeometry(QtCore.QRect(10, 150, 341, 20))
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(aboutDialog)
        self.label_3.setGeometry(QtCore.QRect(30, 210, 321, 51))
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_4 = QtGui.QLabel(aboutDialog)
        self.label_4.setGeometry(QtCore.QRect(30, 260, 321, 101))
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_5 = QtGui.QLabel(aboutDialog)
        self.label_5.setGeometry(QtCore.QRect(10, 180, 341, 20))
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName(_fromUtf8("label_5"))

        self.retranslateUi(aboutDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), aboutDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), aboutDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(aboutDialog)

    def retranslateUi(self, aboutDialog):
        aboutDialog.setWindowTitle(QtGui.QApplication.translate("aboutDialog", "About", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("aboutDialog", "PyBitmessage", None, QtGui.QApplication.UnicodeUTF8))
        self.labelVersion.setText(QtGui.QApplication.translate("aboutDialog", "version ?", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("aboutDialog", "Copyright © 2012 Jonathan Warren", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("aboutDialog", "Distributed under the MIT/X11 software license, see the accompanying file license.txt or http://www.opensource.org/licenses/mit-license.php", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("aboutDialog", "This product includes Python-RSA (http://stuvel.eu/rsa) originally written by Sybren A. Stüvel <sybren@stuvel.eu>. It is licensed under the Apache 2.0 license: http://www.apache.org/licenses/LICENSE-2.0", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("aboutDialog", "This is Beta software.", None, QtGui.QApplication.UnicodeUTF8))

