# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'emailgateway.ui'
#
# Created: Fri Apr 26 17:43:31 2013
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_EmailGatewayDialog(object):
    def setupUi(self, EmailGatewayDialog):
        EmailGatewayDialog.setObjectName(_fromUtf8("EmailGatewayDialog"))
        EmailGatewayDialog.resize(386, 172)
        self.gridLayout = QtGui.QGridLayout(EmailGatewayDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.radioButtonRegister = QtGui.QRadioButton(EmailGatewayDialog)
        self.radioButtonRegister.setChecked(True)
        self.radioButtonRegister.setObjectName(_fromUtf8("radioButtonRegister"))
        self.gridLayout.addWidget(self.radioButtonRegister, 1, 0, 1, 1)
        self.radioButtonStatus = QtGui.QRadioButton(EmailGatewayDialog)
        self.radioButtonStatus.setObjectName(_fromUtf8("radioButtonStatus"))
        self.gridLayout.addWidget(self.radioButtonStatus, 4, 0, 1, 1)
        self.radioButtonUnregister = QtGui.QRadioButton(EmailGatewayDialog)
        self.radioButtonUnregister.setObjectName(_fromUtf8("radioButtonUnregister"))
        self.gridLayout.addWidget(self.radioButtonUnregister, 5, 0, 1, 1)
        self.label = QtGui.QLabel(EmailGatewayDialog)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(EmailGatewayDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.lineEditEmail = QtGui.QLineEdit(EmailGatewayDialog)
        self.lineEditEmail.setEnabled(True)
        self.lineEditEmail.setObjectName(_fromUtf8("lineEditEmail"))
        self.gridLayout.addWidget(self.lineEditEmail, 3, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(EmailGatewayDialog)
        self.buttonBox.setMinimumSize(QtCore.QSize(368, 0))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 1)

        self.retranslateUi(EmailGatewayDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), EmailGatewayDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), EmailGatewayDialog.reject)
        QtCore.QObject.connect(self.radioButtonRegister, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.lineEditEmail.setEnabled)
        QtCore.QObject.connect(self.radioButtonStatus, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.lineEditEmail.setDisabled)
        QtCore.QObject.connect(self.radioButtonUnregister, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.lineEditEmail.setDisabled)
        QtCore.QMetaObject.connectSlotsByName(EmailGatewayDialog)
        EmailGatewayDialog.setTabOrder(self.radioButtonRegister, self.lineEditEmail)
        EmailGatewayDialog.setTabOrder(self.lineEditEmail, self.radioButtonUnregister)
        EmailGatewayDialog.setTabOrder(self.radioButtonUnregister, self.buttonBox)

    def retranslateUi(self, EmailGatewayDialog):
        EmailGatewayDialog.setWindowTitle(QtGui.QApplication.translate("EmailGatewayDialog", "Email gateway", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButtonRegister.setText(QtGui.QApplication.translate("EmailGatewayDialog", "Register on email gateway", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButtonStatus.setText(QtGui.QApplication.translate("EmailGatewayDialog", "Account status at email gateway", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButtonUnregister.setText(QtGui.QApplication.translate("EmailGatewayDialog", "Unregister from email gateway", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("EmailGatewayDialog", "Email gateway allows you to communicate with email users. Currently, only the Mailchuck email gateway (@mailchuck.com) is available.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("EmailGatewayDialog", "Desired email address (including @mailchuck.com):", None, QtGui.QApplication.UnicodeUTF8))

