# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newchandialog.ui'
#
# Created: Tue Jun 25 17:03:01 2013
#      by: PyQt4 UI code generator 4.10.2
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

class Ui_NewChanDialog(object):
    def setupUi(self, NewChanDialog):
        NewChanDialog.setObjectName(_fromUtf8("NewChanDialog"))
        NewChanDialog.resize(447, 441)
        self.formLayout = QtGui.QFormLayout(NewChanDialog)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.radioButtonCreateChan = QtGui.QRadioButton(NewChanDialog)
        self.radioButtonCreateChan.setObjectName(_fromUtf8("radioButtonCreateChan"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.radioButtonCreateChan)
        self.radioButtonJoinChan = QtGui.QRadioButton(NewChanDialog)
        self.radioButtonJoinChan.setChecked(True)
        self.radioButtonJoinChan.setObjectName(_fromUtf8("radioButtonJoinChan"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.radioButtonJoinChan)
        self.groupBoxJoinChan = QtGui.QGroupBox(NewChanDialog)
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
        self.groupBoxCreateChan = QtGui.QGroupBox(NewChanDialog)
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
        self.buttonBox = QtGui.QDialogButtonBox(NewChanDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.buttonBox)

        self.retranslateUi(NewChanDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), NewChanDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), NewChanDialog.reject)
        QtCore.QObject.connect(self.radioButtonJoinChan, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.groupBoxJoinChan.setShown)
        QtCore.QObject.connect(self.radioButtonCreateChan, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.groupBoxCreateChan.setShown)
        QtCore.QMetaObject.connectSlotsByName(NewChanDialog)

    def retranslateUi(self, NewChanDialog):
        NewChanDialog.setWindowTitle(_translate("NewChanDialog", "Dialog", None))
        self.radioButtonCreateChan.setText(_translate("NewChanDialog", "Create a new chan", None))
        self.radioButtonJoinChan.setText(_translate("NewChanDialog", "Join a chan", None))
        self.groupBoxJoinChan.setTitle(_translate("NewChanDialog", "Join a chan", None))
        self.label.setText(_translate("NewChanDialog", "<html><head/><body><p>A chan is a set of encryption keys that is shared by a group of people. The keys and bitmessage address used by a chan is generated from a human-friendly word or phrase (the chan name).</p><p>Chans are experimental and are unmoderatable.</p></body></html>", None))
        self.label_2.setText(_translate("NewChanDialog", "Chan name:", None))
        self.label_3.setText(_translate("NewChanDialog", "Chan bitmessage address:", None))
        self.groupBoxCreateChan.setTitle(_translate("NewChanDialog", "Create a chan", None))
        self.label_4.setText(_translate("NewChanDialog", "Enter a name for your chan. If you choose a sufficiently complex chan name (like a strong and unique passphrase) and none of your friends share it publicly then the chan will be secure and private.", None))
        self.label_5.setText(_translate("NewChanDialog", "Chan name:", None))

