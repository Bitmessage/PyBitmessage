# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'help.ui'
#
# Created: Wed Jan 14 22:42:39 2015
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_helpDialog(object):
    def setupUi(self, helpDialog):
        helpDialog.setObjectName(_fromUtf8("helpDialog"))
        helpDialog.resize(335, 96)
        self.formLayout = QtGui.QFormLayout(helpDialog)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.labelHelpURI = QtGui.QLabel(helpDialog)
        self.labelHelpURI.setOpenExternalLinks(True)
        self.labelHelpURI.setObjectName(_fromUtf8("labelHelpURI"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.labelHelpURI)
        self.label = QtGui.QLabel(helpDialog)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.SpanningRole, self.label)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.formLayout.setItem(2, QtGui.QFormLayout.LabelRole, spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(helpDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.buttonBox)

        self.retranslateUi(helpDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), helpDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), helpDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(helpDialog)

    def retranslateUi(self, helpDialog):
        helpDialog.setWindowTitle(QtGui.QApplication.translate("helpDialog", "Help", None, QtGui.QApplication.UnicodeUTF8))
        self.labelHelpURI.setText(QtGui.QApplication.translate("helpDialog", "<a href=\"https://bitmessage.org/wiki/PyBitmessage_Help\">https://bitmessage.org/wiki/PyBitmessage_Help</a>", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("helpDialog", "As Bitmessage is a collaborative project, help can be found online in the Bitmessage Wiki:", None, QtGui.QApplication.UnicodeUTF8))

