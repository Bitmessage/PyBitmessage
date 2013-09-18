# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'regenerateaddresses.ui'
#
# Created: Sun Sep 15 23:50:23 2013
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

class Ui_regenerateAddressesDialog(object):
    def setupUi(self, regenerateAddressesDialog):
        regenerateAddressesDialog.setObjectName(_fromUtf8("regenerateAddressesDialog"))
        regenerateAddressesDialog.resize(532, 332)
        self.gridLayout_2 = QtGui.QGridLayout(regenerateAddressesDialog)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.buttonBox = QtGui.QDialogButtonBox(regenerateAddressesDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.groupBox = QtGui.QGroupBox(regenerateAddressesDialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_6 = QtGui.QLabel(self.groupBox)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 1, 0, 1, 1)
        self.lineEditPassphrase = QtGui.QLineEdit(self.groupBox)
        self.lineEditPassphrase.setInputMethodHints(QtCore.Qt.ImhHiddenText|QtCore.Qt.ImhNoAutoUppercase|QtCore.Qt.ImhNoPredictiveText)
        self.lineEditPassphrase.setEchoMode(QtGui.QLineEdit.Password)
        self.lineEditPassphrase.setObjectName(_fromUtf8("lineEditPassphrase"))
        self.gridLayout.addWidget(self.lineEditPassphrase, 2, 0, 1, 5)
        self.label_11 = QtGui.QLabel(self.groupBox)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.gridLayout.addWidget(self.label_11, 3, 0, 1, 3)
        self.spinBoxNumberOfAddressesToMake = QtGui.QSpinBox(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinBoxNumberOfAddressesToMake.sizePolicy().hasHeightForWidth())
        self.spinBoxNumberOfAddressesToMake.setSizePolicy(sizePolicy)
        self.spinBoxNumberOfAddressesToMake.setMinimum(1)
        self.spinBoxNumberOfAddressesToMake.setProperty("value", 8)
        self.spinBoxNumberOfAddressesToMake.setObjectName(_fromUtf8("spinBoxNumberOfAddressesToMake"))
        self.gridLayout.addWidget(self.spinBoxNumberOfAddressesToMake, 3, 3, 1, 1)
        spacerItem = QtGui.QSpacerItem(132, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 3, 4, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 4, 0, 1, 1)
        self.lineEditAddressVersionNumber = QtGui.QLineEdit(self.groupBox)
        self.lineEditAddressVersionNumber.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditAddressVersionNumber.sizePolicy().hasHeightForWidth())
        self.lineEditAddressVersionNumber.setSizePolicy(sizePolicy)
        self.lineEditAddressVersionNumber.setMaximumSize(QtCore.QSize(31, 16777215))
        self.lineEditAddressVersionNumber.setText(_fromUtf8(""))
        self.lineEditAddressVersionNumber.setObjectName(_fromUtf8("lineEditAddressVersionNumber"))
        self.gridLayout.addWidget(self.lineEditAddressVersionNumber, 4, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 4, 2, 1, 1)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 5, 0, 1, 1)
        self.lineEditStreamNumber = QtGui.QLineEdit(self.groupBox)
        self.lineEditStreamNumber.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditStreamNumber.sizePolicy().hasHeightForWidth())
        self.lineEditStreamNumber.setSizePolicy(sizePolicy)
        self.lineEditStreamNumber.setMaximumSize(QtCore.QSize(31, 16777215))
        self.lineEditStreamNumber.setObjectName(_fromUtf8("lineEditStreamNumber"))
        self.gridLayout.addWidget(self.lineEditStreamNumber, 5, 1, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(325, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 5, 2, 1, 3)
        self.checkBoxEighteenByteRipe = QtGui.QCheckBox(self.groupBox)
        self.checkBoxEighteenByteRipe.setObjectName(_fromUtf8("checkBoxEighteenByteRipe"))
        self.gridLayout.addWidget(self.checkBoxEighteenByteRipe, 6, 0, 1, 5)
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 7, 0, 1, 5)
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 5)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)

        self.retranslateUi(regenerateAddressesDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), regenerateAddressesDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), regenerateAddressesDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(regenerateAddressesDialog)

    def retranslateUi(self, regenerateAddressesDialog):
        regenerateAddressesDialog.setWindowTitle(_translate("regenerateAddressesDialog", "Regenerate Existing Addresses", None))
        self.groupBox.setTitle(_translate("regenerateAddressesDialog", "Regenerate existing addresses", None))
        self.label_6.setText(_translate("regenerateAddressesDialog", "Passphrase", None))
        self.label_11.setText(_translate("regenerateAddressesDialog", "Number of addresses to make based on your passphrase:", None))
        self.label_2.setText(_translate("regenerateAddressesDialog", "Address version number:", None))
        self.label_3.setText(_translate("regenerateAddressesDialog", "Stream number:", None))
        self.lineEditStreamNumber.setText(_translate("regenerateAddressesDialog", "1", None))
        self.checkBoxEighteenByteRipe.setText(_translate("regenerateAddressesDialog", "Spend several minutes of extra computing time to make the address(es) 1 or 2 characters shorter", None))
        self.label_4.setText(_translate("regenerateAddressesDialog", "You must check (or not check) this box just like you did (or didn\'t) when you made your addresses the first time.", None))
        self.label.setText(_translate("regenerateAddressesDialog", "If you have previously made deterministic addresses but lost them due to an accident (like hard drive failure), you can regenerate them here. If you used the random number generator to make your addresses then this form will be of no use to you.", None))

