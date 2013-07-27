# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'connect.ui'
#
# Created: Wed Jul 24 12:42:01 2013
#      by: PyQt4 UI code generator 4.10
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

class Ui_connectDialog(object):
    def setupUi(self, connectDialog):
        connectDialog.setObjectName(_fromUtf8("connectDialog"))
        connectDialog.resize(400, 124)
        self.gridLayout = QtGui.QGridLayout(connectDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(connectDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)
        self.radioButtonConnectNow = QtGui.QRadioButton(connectDialog)
        self.radioButtonConnectNow.setChecked(True)
        self.radioButtonConnectNow.setObjectName(_fromUtf8("radioButtonConnectNow"))
        self.gridLayout.addWidget(self.radioButtonConnectNow, 1, 0, 1, 2)
        self.radioButtonConfigureNetwork = QtGui.QRadioButton(connectDialog)
        self.radioButtonConfigureNetwork.setObjectName(_fromUtf8("radioButtonConfigureNetwork"))
        self.gridLayout.addWidget(self.radioButtonConfigureNetwork, 2, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(185, 24, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(connectDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 1, 1, 1)

        self.retranslateUi(connectDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), connectDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), connectDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(connectDialog)

    def retranslateUi(self, connectDialog):
        connectDialog.setWindowTitle(_translate("connectDialog", "Bitmessage", None))
        self.label.setText(_translate("connectDialog", "Bitmessage won\'t connect to anyone until you let it. ", None))
        self.radioButtonConnectNow.setText(_translate("connectDialog", "Connect now", None))
        self.radioButtonConfigureNetwork.setText(_translate("connectDialog", "Let me configure special network settings first", None))

