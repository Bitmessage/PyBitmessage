# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\mjha\Documents\GitHub\PyBitmessage\src\bitmessageqt\backuprestore.ui'
#
# Created: Tue Oct 08 12:25:23 2013
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

class Ui_BackupRestore(object):
    def setupUi(self, BackupRestore):
        BackupRestore.setObjectName(_fromUtf8("BackupRestore"))
        BackupRestore.setEnabled(True)
        BackupRestore.resize(359, 250)
        self.BackupRestorebuttonBox = QtGui.QDialogButtonBox(BackupRestore)
        self.BackupRestorebuttonBox.setGeometry(QtCore.QRect(-90, 210, 341, 32))
        self.BackupRestorebuttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.BackupRestorebuttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.BackupRestorebuttonBox.setObjectName(_fromUtf8("BackupRestorebuttonBox"))
        self.radioButton_Restore = QtGui.QRadioButton(BackupRestore)
        self.radioButton_Restore.setGeometry(QtCore.QRect(30, 20, 82, 17))
        self.radioButton_Restore.setChecked(True)
        self.radioButton_Restore.setObjectName(_fromUtf8("radioButton_Restore"))
        self.radioButton_Backup = QtGui.QRadioButton(BackupRestore)
        self.radioButton_Backup.setGeometry(QtCore.QRect(130, 20, 82, 17))
        self.radioButton_Backup.setChecked(False)
        self.radioButton_Backup.setObjectName(_fromUtf8("radioButton_Backup"))
        self.checkBox_keys = QtGui.QCheckBox(BackupRestore)
        self.checkBox_keys.setEnabled(True)
        self.checkBox_keys.setGeometry(QtCore.QRect(40, 140, 70, 20))
        self.checkBox_keys.setObjectName(_fromUtf8("checkBox_keys"))
        self.checkBox_messages = QtGui.QCheckBox(BackupRestore)
        self.checkBox_messages.setEnabled(True)
        self.checkBox_messages.setGeometry(QtCore.QRect(40, 160, 171, 17))
        self.checkBox_messages.setObjectName(_fromUtf8("checkBox_messages"))
        self.label = QtGui.QLabel(BackupRestore)
        self.label.setEnabled(True)
        self.label.setGeometry(QtCore.QRect(30, 120, 111, 20))
        self.label.setObjectName(_fromUtf8("label"))
        self.checkBox_inbox_only = QtGui.QCheckBox(BackupRestore)
        self.checkBox_inbox_only.setEnabled(True)
        self.checkBox_inbox_only.setGeometry(QtCore.QRect(40, 180, 167, 17))
        self.checkBox_inbox_only.setCheckable(True)
        self.checkBox_inbox_only.setObjectName(_fromUtf8("checkBox_inbox_only"))
        self.radioButton_DeleteBackup = QtGui.QRadioButton(BackupRestore)
        self.radioButton_DeleteBackup.setGeometry(QtCore.QRect(240, 20, 101, 17))
        self.radioButton_DeleteBackup.setObjectName(_fromUtf8("radioButton_DeleteBackup"))
        self.label_2 = QtGui.QLabel(BackupRestore)
        self.label_2.setEnabled(True)
        self.label_2.setGeometry(QtCore.QRect(30, 50, 321, 20))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.lineEdit_directory_name = QtGui.QLineEdit(BackupRestore)
        self.lineEdit_directory_name.setEnabled(True)
        self.lineEdit_directory_name.setGeometry(QtCore.QRect(40, 90, 211, 20))
        self.lineEdit_directory_name.setObjectName(_fromUtf8("lineEdit_directory_name"))
        self.pushButton_browse = QtGui.QPushButton(BackupRestore)
        self.pushButton_browse.setEnabled(True)
        self.pushButton_browse.setGeometry(QtCore.QRect(270, 90, 75, 23))
        self.pushButton_browse.setObjectName(_fromUtf8("pushButton_browse"))
        self.checkBox_Default_directory = QtGui.QCheckBox(BackupRestore)
        self.checkBox_Default_directory.setEnabled(True)
        self.checkBox_Default_directory.setGeometry(QtCore.QRect(40, 70, 221, 17))
        self.checkBox_Default_directory.setObjectName(_fromUtf8("checkBox_Default_directory"))

        self.retranslateUi(BackupRestore)
        QtCore.QObject.connect(self.radioButton_Restore, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.checkBox_keys.setEnabled)
        QtCore.QObject.connect(self.radioButton_Restore, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.checkBox_messages.setEnabled)
        QtCore.QObject.connect(self.radioButton_Backup, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.checkBox_keys.setEnabled)
        QtCore.QObject.connect(self.radioButton_Backup, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.checkBox_messages.setEnabled)
        QtCore.QObject.connect(self.radioButton_Backup, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.checkBox_inbox_only.setEnabled)
        QtCore.QObject.connect(self.radioButton_Restore, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.checkBox_inbox_only.setEnabled)
        QtCore.QObject.connect(self.radioButton_Backup, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.checkBox_inbox_only.setEnabled)
        QtCore.QObject.connect(self.checkBox_messages, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.checkBox_inbox_only.setDisabled)
        QtCore.QObject.connect(self.checkBox_inbox_only, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.checkBox_messages.setDisabled)
        QtCore.QObject.connect(self.radioButton_DeleteBackup, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.checkBox_keys.setDisabled)
        QtCore.QObject.connect(self.radioButton_DeleteBackup, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.checkBox_messages.setDisabled)
        QtCore.QObject.connect(self.radioButton_DeleteBackup, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.checkBox_inbox_only.setDisabled)
        QtCore.QObject.connect(self.radioButton_Backup, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.checkBox_inbox_only.setHidden)
        QtCore.QObject.connect(self.radioButton_Restore, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.checkBox_inbox_only.setVisible)
        QtCore.QObject.connect(self.checkBox_Default_directory, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.lineEdit_directory_name.setDisabled)
        QtCore.QObject.connect(self.BackupRestorebuttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), BackupRestore.accept)
        QtCore.QObject.connect(self.BackupRestorebuttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), BackupRestore.reject)
        QtCore.QObject.connect(self.checkBox_Default_directory, QtCore.SIGNAL(_fromUtf8("clicked(bool)")), self.pushButton_browse.setDisabled)
        QtCore.QMetaObject.connectSlotsByName(BackupRestore)

    def retranslateUi(self, BackupRestore):
        BackupRestore.setWindowTitle(_translate("BackupRestore", "Dialog", None))
        self.radioButton_Restore.setText(_translate("BackupRestore", "Restore Files", None))
        self.radioButton_Backup.setText(_translate("BackupRestore", "Backup Files", None))
        self.checkBox_keys.setText(_translate("BackupRestore", "Keys.dat", None))
        self.checkBox_messages.setText(_translate("BackupRestore", "Complete messages.dat", None))
        self.label.setText(_translate("BackupRestore", "Please select the files", None))
        self.checkBox_inbox_only.setText(_translate("BackupRestore", "Restore Only Inbox Messages", None))
        self.radioButton_DeleteBackup.setText(_translate("BackupRestore", "Delete Backup", None))
        self.label_2.setText(_translate("BackupRestore", "Provide Directory Location to Restore/Backup/Delete ", None))
        self.pushButton_browse.setText(_translate("BackupRestore", "Browse", None))
        self.checkBox_Default_directory.setText(_translate("BackupRestore", "use default directory location \".\\backup\"", None))

