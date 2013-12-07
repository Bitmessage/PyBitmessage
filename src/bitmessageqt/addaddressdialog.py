# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'addaddressdialog.ui'
#
# Created: Sat Nov 30 20:35:38 2013
#      by: PyQt4 UI code generator 4.10.3
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

class Ui_AddAddressDialog(object):
    def setupUi(self, AddAddressDialog):
        AddAddressDialog.setObjectName(_fromUtf8("AddAddressDialog"))
        AddAddressDialog.resize(368, 162)
        self.formLayout = QtGui.QFormLayout(AddAddressDialog)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label_2 = QtGui.QLabel(AddAddressDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.SpanningRole, self.label_2)
        self.newAddressLabel = QtGui.QLineEdit(AddAddressDialog)
        self.newAddressLabel.setObjectName(_fromUtf8("newAddressLabel"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.SpanningRole, self.newAddressLabel)
        self.label = QtGui.QLabel(AddAddressDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.label)
        self.lineEditAddress = QtGui.QLineEdit(AddAddressDialog)
        self.lineEditAddress.setObjectName(_fromUtf8("lineEditAddress"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.SpanningRole, self.lineEditAddress)
        self.labelAddressCheck = QtGui.QLabel(AddAddressDialog)
        self.labelAddressCheck.setText(_fromUtf8(""))
        self.labelAddressCheck.setWordWrap(True)
        self.labelAddressCheck.setObjectName(_fromUtf8("labelAddressCheck"))
        self.formLayout.setWidget(6, QtGui.QFormLayout.SpanningRole, self.labelAddressCheck)
        self.buttonBox = QtGui.QDialogButtonBox(AddAddressDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(7, QtGui.QFormLayout.FieldRole, self.buttonBox)

        self.retranslateUi(AddAddressDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), AddAddressDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), AddAddressDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AddAddressDialog)

    def retranslateUi(self, AddAddressDialog):
        AddAddressDialog.setWindowTitle(_translate("AddAddressDialog", "Add new entry", None))
        self.label_2.setText(_translate("AddAddressDialog", "Label", None))
        self.label.setText(_translate("AddAddressDialog", "Address", None))

