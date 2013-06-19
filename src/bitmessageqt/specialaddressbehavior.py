# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'specialaddressbehavior.ui'
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

class Ui_SpecialAddressBehaviorDialog(object):
    def setupUi(self, SpecialAddressBehaviorDialog):
        SpecialAddressBehaviorDialog.setObjectName(_fromUtf8("SpecialAddressBehaviorDialog"))
        SpecialAddressBehaviorDialog.resize(386, 172)
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
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.label_2 = QtGui.QLabel(SpecialAddressBehaviorDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        self.lineEditMailingListName = QtGui.QLineEdit(SpecialAddressBehaviorDialog)
        self.lineEditMailingListName.setEnabled(False)
        self.lineEditMailingListName.setObjectName(_fromUtf8("lineEditMailingListName"))
        self.gridLayout.addWidget(self.lineEditMailingListName, 4, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(SpecialAddressBehaviorDialog)
        self.buttonBox.setMinimumSize(QtCore.QSize(368, 0))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 1)

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
        SpecialAddressBehaviorDialog.setWindowTitle(QtGui.QApplication.translate("SpecialAddressBehaviorDialog", "Special Address Behavior", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButtonBehaveNormalAddress.setText(QtGui.QApplication.translate("SpecialAddressBehaviorDialog", "Behave as a normal address", None, QtGui.QApplication.UnicodeUTF8))
        self.radioButtonBehaviorMailingList.setText(QtGui.QApplication.translate("SpecialAddressBehaviorDialog", "Behave as a pseudo-mailing-list address", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("SpecialAddressBehaviorDialog", "Mail received to a pseudo-mailing-list address will be automatically broadcast to subscribers (and thus will be public).", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("SpecialAddressBehaviorDialog", "Name of the pseudo-mailing-list:", None, QtGui.QApplication.UnicodeUTF8))

