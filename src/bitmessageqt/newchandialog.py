# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newchandialog.ui'
#
# Created: Wed Aug  7 16:51:29 2013
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

class Ui_newChanDialog(object):
    def setupUi(self, newChanDialog):
        newChanDialog.setObjectName(_fromUtf8("newChanDialog"))
        newChanDialog.resize(553, 422)
        newChanDialog.setMinimumSize(QtCore.QSize(0, 0))
        self.formLayout = QtGui.QFormLayout(newChanDialog)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.radioButtonCreateChan = QtGui.QRadioButton(newChanDialog)
        self.radioButtonCreateChan.setObjectName(_fromUtf8("radioButtonCreateChan"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.radioButtonCreateChan)
        self.radioButtonJoinChan = QtGui.QRadioButton(newChanDialog)
        self.radioButtonJoinChan.setChecked(True)
        self.radioButtonJoinChan.setObjectName(_fromUtf8("radioButtonJoinChan"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.radioButtonJoinChan)
        self.groupBoxCreateChan = QtGui.QGroupBox(newChanDialog)
        self.groupBoxCreateChan.setObjectName(_fromUtf8("groupBoxCreateChan"))
        self.gridLayout = QtGui.QGridLayout(self.groupBoxCreateChan)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_4 = QtGui.QLabel(self.groupBoxCreateChan)
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)
        self.label_5 = QtGui.QLabel(self.groupBoxCreateChan)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 1, 0, 1, 1)
        self.lineEditChanNameCreate = QtGui.QLineEdit(self.groupBoxCreateChan)
        self.lineEditChanNameCreate.setObjectName(_fromUtf8("lineEditChanNameCreate"))
        self.gridLayout.addWidget(self.lineEditChanNameCreate, 2, 0, 1, 1)
        self.formLayout.setWidget(2, QtGui.QFormLayout.SpanningRole, self.groupBoxCreateChan)
        self.groupBoxJoinChan = QtGui.QGroupBox(newChanDialog)
        self.groupBoxJoinChan.setObjectName(_fromUtf8("groupBoxJoinChan"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBoxJoinChan)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label = QtGui.QLabel(self.groupBoxJoinChan)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBoxJoinChan)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.lineEditChanNameJoin = QtGui.QLineEdit(self.groupBoxJoinChan)
        self.lineEditChanNameJoin.setObjectName(_fromUtf8("lineEditChanNameJoin"))
        self.gridLayout_2.addWidget(self.lineEditChanNameJoin, 2, 0, 1, 1)
        self.label_3 = QtGui.QLabel(self.groupBoxJoinChan)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 3, 0, 1, 1)
        self.lineEditChanBitmessageAddress = QtGui.QLineEdit(self.groupBoxJoinChan)
        self.lineEditChanBitmessageAddress.setObjectName(_fromUtf8("lineEditChanBitmessageAddress"))
        self.gridLayout_2.addWidget(self.lineEditChanBitmessageAddress, 4, 0, 1, 1)
        self.formLayout.setWidget(3, QtGui.QFormLayout.SpanningRole, self.groupBoxJoinChan)
        spacerItem = QtGui.QSpacerItem(389, 2, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.formLayout.setItem(4, QtGui.QFormLayout.FieldRole, spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(newChanDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.FieldRole, self.buttonBox)

        self.retranslateUi(newChanDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), newChanDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), newChanDialog.reject)
        QtCore.QObject.connect(self.radioButtonJoinChan, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.groupBoxJoinChan.setShown)
        QtCore.QObject.connect(self.radioButtonCreateChan, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.groupBoxCreateChan.setShown)
        QtCore.QMetaObject.connectSlotsByName(newChanDialog)
        newChanDialog.setTabOrder(self.radioButtonJoinChan, self.radioButtonCreateChan)
        newChanDialog.setTabOrder(self.radioButtonCreateChan, self.lineEditChanNameCreate)
        newChanDialog.setTabOrder(self.lineEditChanNameCreate, self.lineEditChanNameJoin)
        newChanDialog.setTabOrder(self.lineEditChanNameJoin, self.lineEditChanBitmessageAddress)
        newChanDialog.setTabOrder(self.lineEditChanBitmessageAddress, self.buttonBox)

    def retranslateUi(self, newChanDialog):
        newChanDialog.setWindowTitle(_translate("newChanDialog", "Dialog", None))
        self.radioButtonCreateChan.setText(_translate("newChanDialog", "Create a new chan", None))
        self.radioButtonJoinChan.setText(_translate("newChanDialog", "Join a chan", None))
        self.groupBoxCreateChan.setTitle(_translate("newChanDialog", "Create a chan", None))
        self.label_4.setText(_translate("newChanDialog", "<html><head/><body><p>Enter a name for your chan. If you choose a sufficiently complex chan name (like a strong and unique passphrase) and none of your friends share it publicly then the chan will be secure and private. If you and someone else both create a chan with the same chan name then it is currently very likely that they will be the same chan.</p></body></html>", None))
        self.label_5.setText(_translate("newChanDialog", "Chan name:", None))
        self.groupBoxJoinChan.setTitle(_translate("newChanDialog", "Join a chan", None))
        self.label.setText(_translate("newChanDialog", "<html><head/><body><p>A chan exists when a group of people share the same decryption keys. The keys and bitmessage address used by a chan are generated from a human-friendly word or phrase (the chan name). To send a message to everyone in the chan, send a normal person-to-person message to the chan address.</p><p>Chans are experimental and completely unmoderatable.</p></body></html>", None))
        self.label_2.setText(_translate("newChanDialog", "Chan name:", None))
        self.label_3.setText(_translate("newChanDialog", "Chan bitmessage address:", None))

