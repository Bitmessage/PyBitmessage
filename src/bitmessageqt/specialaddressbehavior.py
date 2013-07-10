# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'specialaddressbehavior.ui'
#
# Created: Wed Jul 10 15:20:02 2013
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

class Ui_SpecialAddressBehaviorDialog(object):
    def setupUi(self, SpecialAddressBehaviorDialog):
        SpecialAddressBehaviorDialog.setObjectName(_fromUtf8("SpecialAddressBehaviorDialog"))
        SpecialAddressBehaviorDialog.resize(386, 186)
        self.gridLayout = QtGui.QGridLayout(SpecialAddressBehaviorDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.radioButtonBehaveNormalAddress = QtGui.QRadioButton(SpecialAddressBehaviorDialog)
        self.radioButtonBehaveNormalAddress.setChecked(True)
        self.radioButtonBehaveNormalAddress.setObjectName(_fromUtf8("radioButtonBehaveNormalAddress"))
        self.gridLayout.addWidget(self.radioButtonBehaveNormalAddress, 0, 0, 1, 1)
        self.radioButtonBehaviorMailingList = QtGui.QRadioButton(SpecialAddressBehaviorDialog)
        self.radioButtonBehaviorMailingList.setObjectName(_fromUtf8("radioButtonBehaviorMailingList"))
        self.gridLayout.addWidget(self.radioButtonBehaviorMailingList, 1, 0, 1, 1)
        self.label = QtGui.QLabel(SpecialAddressBehaviorDialog)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 3, 0, 1, 1)
        self.label_2 = QtGui.QLabel(SpecialAddressBehaviorDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 4, 0, 1, 1)
        self.lineEditMailingListName = QtGui.QLineEdit(SpecialAddressBehaviorDialog)
        self.lineEditMailingListName.setEnabled(False)
        self.lineEditMailingListName.setObjectName(_fromUtf8("lineEditMailingListName"))
        self.gridLayout.addWidget(self.lineEditMailingListName, 5, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(SpecialAddressBehaviorDialog)
        self.buttonBox.setMinimumSize(QtCore.QSize(368, 0))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 1)
        self.checkBoxWrapMessagesWithEmailHeaders = QtGui.QCheckBox(SpecialAddressBehaviorDialog)
        self.checkBoxWrapMessagesWithEmailHeaders.setObjectName(_fromUtf8("checkBoxWrapMessagesWithEmailHeaders"))
        self.gridLayout.addWidget(self.checkBoxWrapMessagesWithEmailHeaders, 2, 0, 1, 1)

        self.retranslateUi(SpecialAddressBehaviorDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SpecialAddressBehaviorDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SpecialAddressBehaviorDialog.reject)
        QtCore.QObject.connect(self.radioButtonBehaviorMailingList, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.lineEditMailingListName.setEnabled)
        QtCore.QObject.connect(self.radioButtonBehaveNormalAddress, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.lineEditMailingListName.setDisabled)
        QtCore.QMetaObject.connectSlotsByName(SpecialAddressBehaviorDialog)
        SpecialAddressBehaviorDialog.setTabOrder(self.radioButtonBehaveNormalAddress, self.radioButtonBehaviorMailingList)
        SpecialAddressBehaviorDialog.setTabOrder(self.radioButtonBehaviorMailingList, self.lineEditMailingListName)
        SpecialAddressBehaviorDialog.setTabOrder(self.lineEditMailingListName, self.buttonBox)

    def retranslateUi(self, SpecialAddressBehaviorDialog):
        SpecialAddressBehaviorDialog.setWindowTitle(_translate("SpecialAddressBehaviorDialog", "Special Address Behavior", None))
        self.radioButtonBehaveNormalAddress.setText(_translate("SpecialAddressBehaviorDialog", "Behave as a normal address", None))
        self.radioButtonBehaviorMailingList.setText(_translate("SpecialAddressBehaviorDialog", "Behave as a pseudo-mailing-list address", None))
        self.label.setText(_translate("SpecialAddressBehaviorDialog", "Mail received to a pseudo-mailing-list address will be automatically broadcast to subscribers (and thus will be public).", None))
        self.label_2.setText(_translate("SpecialAddressBehaviorDialog", "Name of the pseudo-mailing-list:", None))
        self.checkBoxWrapMessagesWithEmailHeaders.setText(_translate("SpecialAddressBehaviorDialog", "Ensure all incoming messages have standard E-mail headers", None))

