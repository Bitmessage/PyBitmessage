# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'iconglossary.ui'
#
# Created: Thu Jun 13 20:15:48 2013
#      by: PyQt4 UI code generator 4.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_iconGlossaryDialog(object):
    def setupUi(self, iconGlossaryDialog):
        iconGlossaryDialog.setObjectName(_fromUtf8("iconGlossaryDialog"))
        iconGlossaryDialog.resize(424, 282)
        self.gridLayout = QtGui.QGridLayout(iconGlossaryDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupBox = QtGui.QGroupBox(iconGlossaryDialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setText(_fromUtf8(""))
        self.label.setPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/redicon.png")))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 0, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setText(_fromUtf8(""))
        self.label_3.setPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/yellowicon.png")))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 1, 0, 1, 1)
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_2.addWidget(self.label_4, 1, 1, 2, 1)
        spacerItem = QtGui.QSpacerItem(20, 73, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 2, 0, 2, 1)
        self.labelPortNumber = QtGui.QLabel(self.groupBox)
        self.labelPortNumber.setObjectName(_fromUtf8("labelPortNumber"))
        self.gridLayout_2.addWidget(self.labelPortNumber, 3, 1, 1, 1)
        self.label_5 = QtGui.QLabel(self.groupBox)
        self.label_5.setText(_fromUtf8(""))
        self.label_5.setPixmap(QtGui.QPixmap(_fromUtf8(":/newPrefix/images/greenicon.png")))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_2.addWidget(self.label_5, 4, 0, 1, 1)
        self.label_6 = QtGui.QLabel(self.groupBox)
        self.label_6.setWordWrap(True)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_2.addWidget(self.label_6, 4, 1, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(iconGlossaryDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(iconGlossaryDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), iconGlossaryDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), iconGlossaryDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(iconGlossaryDialog)

    def retranslateUi(self, iconGlossaryDialog):
        iconGlossaryDialog.setWindowTitle(_translate("iconGlossaryDialog", "Icon Glossary", None))
        self.groupBox.setTitle(_translate("iconGlossaryDialog", "Icon Glossary", None))
        self.label_2.setText(_translate("iconGlossaryDialog", "You have no connections with other peers. ", None))
        self.label_4.setText(_translate("iconGlossaryDialog", "You have made at least one connection to a peer using an outgoing connection but you have not yet received any incoming connections. Your firewall or home router probably isn\'t configured to forward incoming TCP connections to your computer. Bitmessage will work just fine but it would help the Bitmessage network if you allowed for incoming connections and will help you be a better-connected node.", None))
        self.labelPortNumber.setText(_translate("iconGlossaryDialog", "You are using TCP port ?. (This can be changed in the settings).", None))
        self.label_6.setText(_translate("iconGlossaryDialog", "You do have connections with other peers and your firewall is correctly configured.", None))

import bitmessage_icons_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    iconGlossaryDialog = QtGui.QDialog()
    ui = Ui_iconGlossaryDialog()
    ui.setupUi(iconGlossaryDialog)
    iconGlossaryDialog.show()
    sys.exit(app.exec_())

