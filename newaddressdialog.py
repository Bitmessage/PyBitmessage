# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newaddressdialog.ui'
#
# Created: Wed Dec 19 15:55:07 2012
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_NewAddressDialog(object):
    def setupUi(self, NewAddressDialog):
        NewAddressDialog.setObjectName(_fromUtf8("NewAddressDialog"))
        NewAddressDialog.resize(383, 258)
        self.buttonBox = QtGui.QDialogButtonBox(NewAddressDialog)
        self.buttonBox.setGeometry(QtCore.QRect(160, 220, 201, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label = QtGui.QLabel(NewAddressDialog)
        self.label.setGeometry(QtCore.QRect(10, 0, 361, 41))
        self.label.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(NewAddressDialog)
        self.label_2.setGeometry(QtCore.QRect(20, 50, 301, 20))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.newaddresslabel = QtGui.QLineEdit(NewAddressDialog)
        self.newaddresslabel.setGeometry(QtCore.QRect(20, 70, 351, 20))
        self.newaddresslabel.setObjectName(_fromUtf8("newaddresslabel"))
        self.radioButtonMostAvailable = QtGui.QRadioButton(NewAddressDialog)
        self.radioButtonMostAvailable.setGeometry(QtCore.QRect(20, 110, 401, 16))
        self.radioButtonMostAvailable.setChecked(True)
        self.radioButtonMostAvailable.setObjectName(_fromUtf8("radioButtonMostAvailable"))
        self.radioButtonExisting = QtGui.QRadioButton(NewAddressDialog)
        self.radioButtonExisting.setGeometry(QtCore.QRect(20, 150, 351, 18))
        self.radioButtonExisting.setChecked(False)
        self.radioButtonExisting.setObjectName(_fromUtf8("radioButtonExisting"))
        self.label_3 = QtGui.QLabel(NewAddressDialog)
        self.label_3.setGeometry(QtCore.QRect(35, 127, 351, 20))
        self.label_3.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_4 = QtGui.QLabel(NewAddressDialog)
        self.label_4.setGeometry(QtCore.QRect(37, 167, 351, 21))
        self.label_4.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.comboBoxExisting = QtGui.QComboBox(NewAddressDialog)
        self.comboBoxExisting.setEnabled(False)
        self.comboBoxExisting.setGeometry(QtCore.QRect(40, 190, 331, 22))
        self.comboBoxExisting.setEditable(True)
        self.comboBoxExisting.setObjectName(_fromUtf8("comboBoxExisting"))

        self.retranslateUi(NewAddressDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), NewAddressDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), NewAddressDialog.reject)
        QtCore.QObject.connect(self.radioButtonExisting, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.comboBoxExisting.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(NewAddressDialog)

    def retranslateUi(self, NewAddressDialog):
        NewAddressDialog.setWindowTitle(QtGui.QApplication.translate("NewAddressDialog", "Create new Address", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("NewAddressDialog", "Here you may generate as many addresses as you like. Indeed, creating and abandoning addresses is encouraged.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("NewAddressDialog", "Label (not shown to anyone except you)", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButtonMostAvailable.setText(QtGui.QApplication.translate("NewAddressDialog", "Use the most available stream", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButtonExisting.setText(QtGui.QApplication.translate("NewAddressDialog", "Use the same stream as an existing address", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("NewAddressDialog", " (best if this is the first of many addresses you will create)", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("NewAddressDialog", "(saves you some bandwidth and processing power)", None, QtGui.QApplication.UnicodeUTF8))

