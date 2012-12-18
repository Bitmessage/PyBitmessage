# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settings.ui'
#
# Created: Tue Dec 18 14:31:06 2012
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_settingsDialog(object):
    def setupUi(self, settingsDialog):
        settingsDialog.setObjectName(_fromUtf8("settingsDialog"))
        settingsDialog.resize(417, 297)
        self.gridLayout = QtGui.QGridLayout(settingsDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tabWidgetSettings = QtGui.QTabWidget(settingsDialog)
        self.tabWidgetSettings.setObjectName(_fromUtf8("tabWidgetSettings"))
        self.tabUserInterface = QtGui.QWidget()
        self.tabUserInterface.setEnabled(True)
        self.tabUserInterface.setObjectName(_fromUtf8("tabUserInterface"))
        self.formLayout = QtGui.QFormLayout(self.tabUserInterface)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.checkBoxStartOnLogon = QtGui.QCheckBox(self.tabUserInterface)
        self.checkBoxStartOnLogon.setObjectName(_fromUtf8("checkBoxStartOnLogon"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.checkBoxStartOnLogon)
        self.checkBoxStartInTray = QtGui.QCheckBox(self.tabUserInterface)
        self.checkBoxStartInTray.setObjectName(_fromUtf8("checkBoxStartInTray"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.checkBoxStartInTray)
        self.checkBoxMinimizeToTray = QtGui.QCheckBox(self.tabUserInterface)
        self.checkBoxMinimizeToTray.setChecked(True)
        self.checkBoxMinimizeToTray.setObjectName(_fromUtf8("checkBoxMinimizeToTray"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.checkBoxMinimizeToTray)
        self.checkBoxShowTrayNotifications = QtGui.QCheckBox(self.tabUserInterface)
        self.checkBoxShowTrayNotifications.setObjectName(_fromUtf8("checkBoxShowTrayNotifications"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.SpanningRole, self.checkBoxShowTrayNotifications)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.formLayout.setItem(4, QtGui.QFormLayout.LabelRole, spacerItem)
        self.labelSettingsNote = QtGui.QLabel(self.tabUserInterface)
        self.labelSettingsNote.setText(_fromUtf8(""))
        self.labelSettingsNote.setWordWrap(True)
        self.labelSettingsNote.setObjectName(_fromUtf8("labelSettingsNote"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.SpanningRole, self.labelSettingsNote)
        self.tabWidgetSettings.addTab(self.tabUserInterface, _fromUtf8(""))
        self.tabNetworkSettings = QtGui.QWidget()
        self.tabNetworkSettings.setObjectName(_fromUtf8("tabNetworkSettings"))
        self.gridLayout_2 = QtGui.QGridLayout(self.tabNetworkSettings)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        spacerItem1 = QtGui.QSpacerItem(56, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem1, 0, 0, 1, 1)
        self.label = QtGui.QLabel(self.tabNetworkSettings)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 1, 1, 1)
        self.lineEditTCPPort = QtGui.QLineEdit(self.tabNetworkSettings)
        self.lineEditTCPPort.setObjectName(_fromUtf8("lineEditTCPPort"))
        self.gridLayout_2.addWidget(self.lineEditTCPPort, 0, 2, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 169, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem2, 1, 2, 1, 1)
        self.tabWidgetSettings.addTab(self.tabNetworkSettings, _fromUtf8(""))
        self.gridLayout.addWidget(self.tabWidgetSettings, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(settingsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(settingsDialog)
        self.tabWidgetSettings.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), settingsDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), settingsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(settingsDialog)

    def retranslateUi(self, settingsDialog):
        settingsDialog.setWindowTitle(QtGui.QApplication.translate("settingsDialog", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxStartOnLogon.setText(QtGui.QApplication.translate("settingsDialog", "Start Bitmessage on user login", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxStartInTray.setText(QtGui.QApplication.translate("settingsDialog", "Start Bitmessage in the tray (don\'t show main window)", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxMinimizeToTray.setText(QtGui.QApplication.translate("settingsDialog", "Minimize to tray", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBoxShowTrayNotifications.setText(QtGui.QApplication.translate("settingsDialog", "Show notification when message received and minimzed to tray", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidgetSettings.setTabText(self.tabWidgetSettings.indexOf(self.tabUserInterface), QtGui.QApplication.translate("settingsDialog", "User Interface", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("settingsDialog", "Listen for connections on port:", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidgetSettings.setTabText(self.tabWidgetSettings.indexOf(self.tabNetworkSettings), QtGui.QApplication.translate("settingsDialog", "Network Settings", None, QtGui.QApplication.UnicodeUTF8))

