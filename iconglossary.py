# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'iconglossary.ui'
#
# Created: Tue Dec 18 14:31:18 2012
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_iconGlossaryDialog(object):
    def setupUi(self, iconGlossaryDialog):
        iconGlossaryDialog.setObjectName(_fromUtf8("iconGlossaryDialog"))
        iconGlossaryDialog.resize(400, 300)
        self.buttonBox = QtGui.QDialogButtonBox(iconGlossaryDialog)
        self.buttonBox.setGeometry(QtCore.QRect(50, 260, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.groupBox = QtGui.QGroupBox(iconGlossaryDialog)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 381, 241))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(20, 30, 21, 21))
        self.label.setText(_fromUtf8(""))
        self.label.setPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/redicon.png")))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(50, 30, 281, 20))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(20, 70, 16, 21))
        self.label_3.setText(_fromUtf8(""))
        self.label_3.setPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/yellowicon.png")))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setGeometry(QtCore.QRect(50, 60, 321, 101))
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_5 = QtGui.QLabel(self.groupBox)
        self.label_5.setGeometry(QtCore.QRect(20, 200, 21, 21))
        self.label_5.setText(_fromUtf8(""))
        self.label_5.setPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/greenicon.png")))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.label_6 = QtGui.QLabel(self.groupBox)
        self.label_6.setGeometry(QtCore.QRect(50, 200, 301, 31))
        self.label_6.setWordWrap(True)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.labelPortNumber = QtGui.QLabel(self.groupBox)
        self.labelPortNumber.setGeometry(QtCore.QRect(50, 160, 321, 16))
        self.labelPortNumber.setObjectName(_fromUtf8("labelPortNumber"))

        self.retranslateUi(iconGlossaryDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), iconGlossaryDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), iconGlossaryDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(iconGlossaryDialog)

    def retranslateUi(self, iconGlossaryDialog):
        iconGlossaryDialog.setWindowTitle(QtGui.QApplication.translate("iconGlossaryDialog", "Icon Glossary", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("iconGlossaryDialog", "Icon Glossary", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("iconGlossaryDialog", "You have no connections with other peers. ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("iconGlossaryDialog", "You have made at least one connection to a peer using an outgoing connection but you have not yet received any incoming connections. Your firewall or home router probably isn\'t configured to foward incoming TCP connections to your computer. Bitmessage will work just fine but it would help the Bitmessage network if you allowed for incoming connections and will help you be a better-connected node.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("iconGlossaryDialog", "You do have connections with other peers and your firewall is correctly configured.", None, QtGui.QApplication.UnicodeUTF8))
        self.labelPortNumber.setText(QtGui.QApplication.translate("iconGlossaryDialog", "You are using TCP port ?. (This can be changed in the settings).", None, QtGui.QApplication.UnicodeUTF8))

import bitmessage_icons_rc
