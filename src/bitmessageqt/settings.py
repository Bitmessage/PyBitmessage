# -*- coding: utf-8 -*-
# pylint: disable=too-many-instance-attributes,too-many-locals,too-many-statements,attribute-defined-outside-init
"""
Form implementation generated from reading ui file 'settings.ui'

Created: Thu Dec 25 23:21:20 2014
     by: PyQt4 UI code generator 4.10.3

WARNING! All changes made in this file will be lost!
"""

from __future__ import absolute_import

from sys import platform

from PyQt4 import QtCore, QtGui

from . import bitmessage_icons_rc  # pylint: disable=unused-import
from .languagebox import LanguageBox


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


class Ui_settingsDialog(object):
    """Encapsulate a UI settings dialog object"""

    def setupUi(self, settingsDialog):
        """Set up the UI"""

        settingsDialog.setObjectName(_fromUtf8("settingsDialog"))
        settingsDialog.resize(521, 413)
        self.gridLayout = QtGui.QGridLayout(settingsDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(settingsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.tabWidgetSettings = QtGui.QTabWidget(settingsDialog)
        self.tabWidgetSettings.setObjectName(_fromUtf8("tabWidgetSettings"))
        self.tabUserInterface = QtGui.QWidget()
        self.tabUserInterface.setEnabled(True)
        self.tabUserInterface.setObjectName(_fromUtf8("tabUserInterface"))
        self.formLayout = QtGui.QFormLayout(self.tabUserInterface)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.checkBoxStartOnLogon = QtGui.QCheckBox(self.tabUserInterface)
        self.checkBoxStartOnLogon.setObjectName(_fromUtf8("checkBoxStartOnLogon"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.checkBoxStartOnLogon)
        self.groupBoxTray = QtGui.QGroupBox(self.tabUserInterface)
        self.groupBoxTray.setObjectName(_fromUtf8("groupBoxTray"))
        self.formLayoutTray = QtGui.QFormLayout(self.groupBoxTray)
        self.formLayoutTray.setObjectName(_fromUtf8("formLayoutTray"))
        self.checkBoxStartInTray = QtGui.QCheckBox(self.groupBoxTray)
        self.checkBoxStartInTray.setObjectName(_fromUtf8("checkBoxStartInTray"))
        self.formLayoutTray.setWidget(0, QtGui.QFormLayout.SpanningRole, self.checkBoxStartInTray)
        self.checkBoxMinimizeToTray = QtGui.QCheckBox(self.groupBoxTray)
        self.checkBoxMinimizeToTray.setChecked(True)
        self.checkBoxMinimizeToTray.setObjectName(_fromUtf8("checkBoxMinimizeToTray"))
        self.formLayoutTray.setWidget(1, QtGui.QFormLayout.LabelRole, self.checkBoxMinimizeToTray)
        self.checkBoxTrayOnClose = QtGui.QCheckBox(self.groupBoxTray)
        self.checkBoxTrayOnClose.setChecked(True)
        self.checkBoxTrayOnClose.setObjectName(_fromUtf8("checkBoxTrayOnClose"))
        self.formLayoutTray.setWidget(2, QtGui.QFormLayout.LabelRole, self.checkBoxTrayOnClose)
        self.formLayout.setWidget(1, QtGui.QFormLayout.SpanningRole, self.groupBoxTray)
        self.checkBoxHideTrayConnectionNotifications = QtGui.QCheckBox(self.tabUserInterface)
        self.checkBoxHideTrayConnectionNotifications.setChecked(False)
        self.checkBoxHideTrayConnectionNotifications.setObjectName(
            _fromUtf8("checkBoxHideTrayConnectionNotifications"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.checkBoxHideTrayConnectionNotifications)
        self.checkBoxShowTrayNotifications = QtGui.QCheckBox(self.tabUserInterface)
        self.checkBoxShowTrayNotifications.setObjectName(_fromUtf8("checkBoxShowTrayNotifications"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.checkBoxShowTrayNotifications)
        self.checkBoxPortableMode = QtGui.QCheckBox(self.tabUserInterface)
        self.checkBoxPortableMode.setObjectName(_fromUtf8("checkBoxPortableMode"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.checkBoxPortableMode)
        self.PortableModeDescription = QtGui.QLabel(self.tabUserInterface)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.PortableModeDescription.sizePolicy().hasHeightForWidth())
        self.PortableModeDescription.setSizePolicy(sizePolicy)
        self.PortableModeDescription.setWordWrap(True)
        self.PortableModeDescription.setObjectName(_fromUtf8("PortableModeDescription"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.SpanningRole, self.PortableModeDescription)
        self.checkBoxWillinglySendToMobile = QtGui.QCheckBox(self.tabUserInterface)
        self.checkBoxWillinglySendToMobile.setObjectName(_fromUtf8("checkBoxWillinglySendToMobile"))
        self.formLayout.setWidget(6, QtGui.QFormLayout.SpanningRole, self.checkBoxWillinglySendToMobile)
        self.checkBoxUseIdenticons = QtGui.QCheckBox(self.tabUserInterface)
        self.checkBoxUseIdenticons.setObjectName(_fromUtf8("checkBoxUseIdenticons"))
        self.formLayout.setWidget(7, QtGui.QFormLayout.LabelRole, self.checkBoxUseIdenticons)
        self.checkBoxReplyBelow = QtGui.QCheckBox(self.tabUserInterface)
        self.checkBoxReplyBelow.setObjectName(_fromUtf8("checkBoxReplyBelow"))
        self.formLayout.setWidget(8, QtGui.QFormLayout.LabelRole, self.checkBoxReplyBelow)
        self.groupBox = QtGui.QGroupBox(self.tabUserInterface)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.formLayout_2 = QtGui.QFormLayout(self.groupBox)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.languageComboBox = LanguageBox(self.groupBox)
        self.languageComboBox.setMinimumSize(QtCore.QSize(100, 0))
        self.languageComboBox.setObjectName(_fromUtf8("languageComboBox"))  # pylint: disable=not-callable
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.languageComboBox)
        self.formLayout.setWidget(9, QtGui.QFormLayout.FieldRole, self.groupBox)
        self.tabWidgetSettings.addTab(self.tabUserInterface, _fromUtf8(""))
        self.tabNetworkSettings = QtGui.QWidget()
        self.tabNetworkSettings.setObjectName(_fromUtf8("tabNetworkSettings"))
        self.gridLayout_4 = QtGui.QGridLayout(self.tabNetworkSettings)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.groupBox1 = QtGui.QGroupBox(self.tabNetworkSettings)
        self.groupBox1.setObjectName(_fromUtf8("groupBox1"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox1)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.label = QtGui.QLabel(self.groupBox1)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1, QtCore.Qt.AlignRight)
        self.lineEditTCPPort = QtGui.QLineEdit(self.groupBox1)
        self.lineEditTCPPort.setMaximumSize(QtCore.QSize(70, 16777215))
        self.lineEditTCPPort.setObjectName(_fromUtf8("lineEditTCPPort"))
        self.gridLayout_3.addWidget(self.lineEditTCPPort, 0, 1, 1, 1, QtCore.Qt.AlignLeft)
        self.labelUPnP = QtGui.QLabel(self.groupBox1)
        self.labelUPnP.setObjectName(_fromUtf8("labelUPnP"))
        self.gridLayout_3.addWidget(self.labelUPnP, 0, 2, 1, 1, QtCore.Qt.AlignRight)
        self.checkBoxUPnP = QtGui.QCheckBox(self.groupBox1)
        self.checkBoxUPnP.setObjectName(_fromUtf8("checkBoxUPnP"))
        self.gridLayout_3.addWidget(self.checkBoxUPnP, 0, 3, 1, 1, QtCore.Qt.AlignLeft)
        self.gridLayout_4.addWidget(self.groupBox1, 0, 0, 1, 1)
        self.groupBox_3 = QtGui.QGroupBox(self.tabNetworkSettings)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.gridLayout_9 = QtGui.QGridLayout(self.groupBox_3)
        self.gridLayout_9.setObjectName(_fromUtf8("gridLayout_9"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_9.addItem(spacerItem1, 0, 0, 2, 1)
        self.label_24 = QtGui.QLabel(self.groupBox_3)
        self.label_24.setObjectName(_fromUtf8("label_24"))
        self.gridLayout_9.addWidget(self.label_24, 0, 1, 1, 1)
        self.lineEditMaxDownloadRate = QtGui.QLineEdit(self.groupBox_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditMaxDownloadRate.sizePolicy().hasHeightForWidth())
        self.lineEditMaxDownloadRate.setSizePolicy(sizePolicy)
        self.lineEditMaxDownloadRate.setMaximumSize(QtCore.QSize(60, 16777215))
        self.lineEditMaxDownloadRate.setObjectName(_fromUtf8("lineEditMaxDownloadRate"))
        self.gridLayout_9.addWidget(self.lineEditMaxDownloadRate, 0, 2, 1, 1)
        self.label_25 = QtGui.QLabel(self.groupBox_3)
        self.label_25.setObjectName(_fromUtf8("label_25"))
        self.gridLayout_9.addWidget(self.label_25, 1, 1, 1, 1)
        self.lineEditMaxUploadRate = QtGui.QLineEdit(self.groupBox_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditMaxUploadRate.sizePolicy().hasHeightForWidth())
        self.lineEditMaxUploadRate.setSizePolicy(sizePolicy)
        self.lineEditMaxUploadRate.setMaximumSize(QtCore.QSize(60, 16777215))
        self.lineEditMaxUploadRate.setObjectName(_fromUtf8("lineEditMaxUploadRate"))
        self.gridLayout_9.addWidget(self.lineEditMaxUploadRate, 1, 2, 1, 1)
        self.label_26 = QtGui.QLabel(self.groupBox_3)
        self.label_26.setObjectName(_fromUtf8("label_26"))
        self.gridLayout_9.addWidget(self.label_26, 2, 1, 1, 1)
        self.lineEditMaxOutboundConnections = QtGui.QLineEdit(self.groupBox_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditMaxOutboundConnections.sizePolicy().hasHeightForWidth())
        self.lineEditMaxOutboundConnections.setSizePolicy(sizePolicy)
        self.lineEditMaxOutboundConnections.setMaximumSize(QtCore.QSize(60, 16777215))
        self.lineEditMaxOutboundConnections.setObjectName(_fromUtf8("lineEditMaxOutboundConnections"))
        self.lineEditMaxOutboundConnections.setValidator(
            QtGui.QIntValidator(0, 8, self.lineEditMaxOutboundConnections))
        self.gridLayout_9.addWidget(self.lineEditMaxOutboundConnections, 2, 2, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_3, 2, 0, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(self.tabNetworkSettings)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_2 = QtGui.QLabel(self.groupBox_2)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)
        self.label_3 = QtGui.QLabel(self.groupBox_2)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 1, 1, 1, 1)
        self.lineEditSocksHostname = QtGui.QLineEdit(self.groupBox_2)
        self.lineEditSocksHostname.setObjectName(_fromUtf8("lineEditSocksHostname"))
        self.lineEditSocksHostname.setPlaceholderText(_fromUtf8("127.0.0.1"))
        self.gridLayout_2.addWidget(self.lineEditSocksHostname, 1, 2, 1, 2)
        self.label_4 = QtGui.QLabel(self.groupBox_2)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_2.addWidget(self.label_4, 1, 4, 1, 1)
        self.lineEditSocksPort = QtGui.QLineEdit(self.groupBox_2)
        self.lineEditSocksPort.setObjectName(_fromUtf8("lineEditSocksPort"))
        if platform in ['darwin', 'win32', 'win64']:
            self.lineEditSocksPort.setPlaceholderText(_fromUtf8("9150"))
        else:
            self.lineEditSocksPort.setPlaceholderText(_fromUtf8("9050"))
        self.gridLayout_2.addWidget(self.lineEditSocksPort, 1, 5, 1, 1)
        self.checkBoxAuthentication = QtGui.QCheckBox(self.groupBox_2)
        self.checkBoxAuthentication.setObjectName(_fromUtf8("checkBoxAuthentication"))
        self.gridLayout_2.addWidget(self.checkBoxAuthentication, 2, 1, 1, 1)
        self.label_5 = QtGui.QLabel(self.groupBox_2)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_2.addWidget(self.label_5, 2, 2, 1, 1)
        self.lineEditSocksUsername = QtGui.QLineEdit(self.groupBox_2)
        self.lineEditSocksUsername.setEnabled(False)
        self.lineEditSocksUsername.setObjectName(_fromUtf8("lineEditSocksUsername"))
        self.gridLayout_2.addWidget(self.lineEditSocksUsername, 2, 3, 1, 1)
        self.label_6 = QtGui.QLabel(self.groupBox_2)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_2.addWidget(self.label_6, 2, 4, 1, 1)
        self.lineEditSocksPassword = QtGui.QLineEdit(self.groupBox_2)
        self.lineEditSocksPassword.setEnabled(False)
        self.lineEditSocksPassword.setInputMethodHints(
            QtCore.Qt.ImhHiddenText | QtCore.Qt.ImhNoAutoUppercase | QtCore.Qt.ImhNoPredictiveText)
        self.lineEditSocksPassword.setEchoMode(QtGui.QLineEdit.Password)
        self.lineEditSocksPassword.setObjectName(_fromUtf8("lineEditSocksPassword"))
        self.gridLayout_2.addWidget(self.lineEditSocksPassword, 2, 5, 1, 1)
        self.checkBoxSocksListen = QtGui.QCheckBox(self.groupBox_2)
        self.checkBoxSocksListen.setObjectName(_fromUtf8("checkBoxSocksListen"))
        self.gridLayout_2.addWidget(self.checkBoxSocksListen, 3, 1, 1, 4)
        self.comboBoxProxyType = QtGui.QComboBox(self.groupBox_2)
        self.comboBoxProxyType.setObjectName(_fromUtf8("comboBoxProxyType"))  # pylint: disable=not-callable
        self.comboBoxProxyType.addItem(_fromUtf8(""))
        self.comboBoxProxyType.addItem(_fromUtf8(""))
        self.comboBoxProxyType.addItem(_fromUtf8(""))
        self.gridLayout_2.addWidget(self.comboBoxProxyType, 0, 1, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_2, 1, 0, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_4.addItem(spacerItem2, 3, 0, 1, 1)
        self.tabWidgetSettings.addTab(self.tabNetworkSettings, _fromUtf8(""))
        self.tabDemandedDifficulty = QtGui.QWidget()
        self.tabDemandedDifficulty.setObjectName(_fromUtf8("tabDemandedDifficulty"))
        self.gridLayout_6 = QtGui.QGridLayout(self.tabDemandedDifficulty)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.label_9 = QtGui.QLabel(self.tabDemandedDifficulty)
        self.label_9.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout_6.addWidget(self.label_9, 1, 1, 1, 1)
        self.label_10 = QtGui.QLabel(self.tabDemandedDifficulty)
        self.label_10.setWordWrap(True)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.gridLayout_6.addWidget(self.label_10, 2, 0, 1, 3)
        self.label_11 = QtGui.QLabel(self.tabDemandedDifficulty)
        self.label_11.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.gridLayout_6.addWidget(self.label_11, 3, 1, 1, 1)
        self.label_8 = QtGui.QLabel(self.tabDemandedDifficulty)
        self.label_8.setWordWrap(True)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout_6.addWidget(self.label_8, 0, 0, 1, 3)
        spacerItem3 = QtGui.QSpacerItem(203, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_6.addItem(spacerItem3, 1, 0, 1, 1)
        self.label_12 = QtGui.QLabel(self.tabDemandedDifficulty)
        self.label_12.setWordWrap(True)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.gridLayout_6.addWidget(self.label_12, 4, 0, 1, 3)
        self.lineEditSmallMessageDifficulty = QtGui.QLineEdit(self.tabDemandedDifficulty)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditSmallMessageDifficulty.sizePolicy().hasHeightForWidth())
        self.lineEditSmallMessageDifficulty.setSizePolicy(sizePolicy)
        self.lineEditSmallMessageDifficulty.setMaximumSize(QtCore.QSize(70, 16777215))
        self.lineEditSmallMessageDifficulty.setObjectName(_fromUtf8("lineEditSmallMessageDifficulty"))
        self.gridLayout_6.addWidget(self.lineEditSmallMessageDifficulty, 3, 2, 1, 1)
        self.lineEditTotalDifficulty = QtGui.QLineEdit(self.tabDemandedDifficulty)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditTotalDifficulty.sizePolicy().hasHeightForWidth())
        self.lineEditTotalDifficulty.setSizePolicy(sizePolicy)
        self.lineEditTotalDifficulty.setMaximumSize(QtCore.QSize(70, 16777215))
        self.lineEditTotalDifficulty.setObjectName(_fromUtf8("lineEditTotalDifficulty"))
        self.gridLayout_6.addWidget(self.lineEditTotalDifficulty, 1, 2, 1, 1)
        spacerItem4 = QtGui.QSpacerItem(203, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_6.addItem(spacerItem4, 3, 0, 1, 1)
        spacerItem5 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_6.addItem(spacerItem5, 5, 0, 1, 1)
        self.tabWidgetSettings.addTab(self.tabDemandedDifficulty, _fromUtf8(""))
        self.tabMaxAcceptableDifficulty = QtGui.QWidget()
        self.tabMaxAcceptableDifficulty.setObjectName(_fromUtf8("tabMaxAcceptableDifficulty"))
        self.gridLayout_7 = QtGui.QGridLayout(self.tabMaxAcceptableDifficulty)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.label_15 = QtGui.QLabel(self.tabMaxAcceptableDifficulty)
        self.label_15.setWordWrap(True)
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.gridLayout_7.addWidget(self.label_15, 0, 0, 1, 3)
        spacerItem6 = QtGui.QSpacerItem(102, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_7.addItem(spacerItem6, 1, 0, 1, 1)
        self.label_13 = QtGui.QLabel(self.tabMaxAcceptableDifficulty)
        self.label_13.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_13.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.gridLayout_7.addWidget(self.label_13, 1, 1, 1, 1)
        self.lineEditMaxAcceptableTotalDifficulty = QtGui.QLineEdit(self.tabMaxAcceptableDifficulty)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditMaxAcceptableTotalDifficulty.sizePolicy().hasHeightForWidth())
        self.lineEditMaxAcceptableTotalDifficulty.setSizePolicy(sizePolicy)
        self.lineEditMaxAcceptableTotalDifficulty.setMaximumSize(QtCore.QSize(70, 16777215))
        self.lineEditMaxAcceptableTotalDifficulty.setObjectName(_fromUtf8("lineEditMaxAcceptableTotalDifficulty"))
        self.gridLayout_7.addWidget(self.lineEditMaxAcceptableTotalDifficulty, 1, 2, 1, 1)
        spacerItem7 = QtGui.QSpacerItem(102, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_7.addItem(spacerItem7, 2, 0, 1, 1)
        self.label_14 = QtGui.QLabel(self.tabMaxAcceptableDifficulty)
        self.label_14.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.gridLayout_7.addWidget(self.label_14, 2, 1, 1, 1)
        self.lineEditMaxAcceptableSmallMessageDifficulty = QtGui.QLineEdit(self.tabMaxAcceptableDifficulty)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditMaxAcceptableSmallMessageDifficulty.sizePolicy().hasHeightForWidth())
        self.lineEditMaxAcceptableSmallMessageDifficulty.setSizePolicy(sizePolicy)
        self.lineEditMaxAcceptableSmallMessageDifficulty.setMaximumSize(QtCore.QSize(70, 16777215))
        self.lineEditMaxAcceptableSmallMessageDifficulty.setObjectName(
            _fromUtf8("lineEditMaxAcceptableSmallMessageDifficulty"))
        self.gridLayout_7.addWidget(self.lineEditMaxAcceptableSmallMessageDifficulty, 2, 2, 1, 1)
        spacerItem8 = QtGui.QSpacerItem(20, 147, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_7.addItem(spacerItem8, 3, 1, 1, 1)
        self.labelOpenCL = QtGui.QLabel(self.tabMaxAcceptableDifficulty)
        self.labelOpenCL.setObjectName(_fromUtf8("labelOpenCL"))
        self.gridLayout_7.addWidget(self.labelOpenCL, 4, 0, 1, 1)
        self.comboBoxOpenCL = QtGui.QComboBox(self.tabMaxAcceptableDifficulty)
        self.comboBoxOpenCL.setObjectName = (_fromUtf8("comboBoxOpenCL"))
        self.gridLayout_7.addWidget(self.comboBoxOpenCL, 4, 1, 1, 1)
        self.tabWidgetSettings.addTab(self.tabMaxAcceptableDifficulty, _fromUtf8(""))
        self.tabNamecoin = QtGui.QWidget()
        self.tabNamecoin.setObjectName(_fromUtf8("tabNamecoin"))
        self.gridLayout_8 = QtGui.QGridLayout(self.tabNamecoin)
        self.gridLayout_8.setObjectName(_fromUtf8("gridLayout_8"))
        spacerItem9 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_8.addItem(spacerItem9, 2, 0, 1, 1)
        self.label_16 = QtGui.QLabel(self.tabNamecoin)
        self.label_16.setWordWrap(True)
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.gridLayout_8.addWidget(self.label_16, 0, 0, 1, 3)
        self.label_17 = QtGui.QLabel(self.tabNamecoin)
        self.label_17.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_17.setObjectName(_fromUtf8("label_17"))
        self.gridLayout_8.addWidget(self.label_17, 2, 1, 1, 1)
        self.lineEditNamecoinHost = QtGui.QLineEdit(self.tabNamecoin)
        self.lineEditNamecoinHost.setObjectName(_fromUtf8("lineEditNamecoinHost"))
        self.gridLayout_8.addWidget(self.lineEditNamecoinHost, 2, 2, 1, 1)
        spacerItem10 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_8.addItem(spacerItem10, 3, 0, 1, 1)
        spacerItem11 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_8.addItem(spacerItem11, 4, 0, 1, 1)
        self.label_18 = QtGui.QLabel(self.tabNamecoin)
        self.label_18.setEnabled(True)
        self.label_18.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_18.setObjectName(_fromUtf8("label_18"))
        self.gridLayout_8.addWidget(self.label_18, 3, 1, 1, 1)
        self.lineEditNamecoinPort = QtGui.QLineEdit(self.tabNamecoin)
        self.lineEditNamecoinPort.setObjectName(_fromUtf8("lineEditNamecoinPort"))
        self.gridLayout_8.addWidget(self.lineEditNamecoinPort, 3, 2, 1, 1)
        spacerItem12 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_8.addItem(spacerItem12, 8, 1, 1, 1)
        self.labelNamecoinUser = QtGui.QLabel(self.tabNamecoin)
        self.labelNamecoinUser.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.labelNamecoinUser.setObjectName(_fromUtf8("labelNamecoinUser"))
        self.gridLayout_8.addWidget(self.labelNamecoinUser, 4, 1, 1, 1)
        self.lineEditNamecoinUser = QtGui.QLineEdit(self.tabNamecoin)
        self.lineEditNamecoinUser.setObjectName(_fromUtf8("lineEditNamecoinUser"))
        self.gridLayout_8.addWidget(self.lineEditNamecoinUser, 4, 2, 1, 1)
        spacerItem13 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_8.addItem(spacerItem13, 5, 0, 1, 1)
        self.labelNamecoinPassword = QtGui.QLabel(self.tabNamecoin)
        self.labelNamecoinPassword.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.labelNamecoinPassword.setObjectName(_fromUtf8("labelNamecoinPassword"))
        self.gridLayout_8.addWidget(self.labelNamecoinPassword, 5, 1, 1, 1)
        self.lineEditNamecoinPassword = QtGui.QLineEdit(self.tabNamecoin)
        self.lineEditNamecoinPassword.setInputMethodHints(
            QtCore.Qt.ImhHiddenText | QtCore.Qt.ImhNoAutoUppercase | QtCore.Qt.ImhNoPredictiveText)
        self.lineEditNamecoinPassword.setEchoMode(QtGui.QLineEdit.Password)
        self.lineEditNamecoinPassword.setObjectName(_fromUtf8("lineEditNamecoinPassword"))
        self.gridLayout_8.addWidget(self.lineEditNamecoinPassword, 5, 2, 1, 1)
        self.labelNamecoinTestResult = QtGui.QLabel(self.tabNamecoin)
        self.labelNamecoinTestResult.setText(_fromUtf8(""))
        self.labelNamecoinTestResult.setObjectName(_fromUtf8("labelNamecoinTestResult"))
        self.gridLayout_8.addWidget(self.labelNamecoinTestResult, 7, 0, 1, 2)
        self.pushButtonNamecoinTest = QtGui.QPushButton(self.tabNamecoin)
        self.pushButtonNamecoinTest.setObjectName(_fromUtf8("pushButtonNamecoinTest"))
        self.gridLayout_8.addWidget(self.pushButtonNamecoinTest, 7, 2, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_21 = QtGui.QLabel(self.tabNamecoin)
        self.label_21.setObjectName(_fromUtf8("label_21"))
        self.horizontalLayout.addWidget(self.label_21)
        self.radioButtonNamecoinNamecoind = QtGui.QRadioButton(self.tabNamecoin)
        self.radioButtonNamecoinNamecoind.setObjectName(_fromUtf8("radioButtonNamecoinNamecoind"))
        self.horizontalLayout.addWidget(self.radioButtonNamecoinNamecoind)
        self.radioButtonNamecoinNmcontrol = QtGui.QRadioButton(self.tabNamecoin)
        self.radioButtonNamecoinNmcontrol.setObjectName(_fromUtf8("radioButtonNamecoinNmcontrol"))
        self.horizontalLayout.addWidget(self.radioButtonNamecoinNmcontrol)
        self.gridLayout_8.addLayout(self.horizontalLayout, 1, 0, 1, 3)
        self.tabWidgetSettings.addTab(self.tabNamecoin, _fromUtf8(""))
        self.tabResendsExpire = QtGui.QWidget()
        self.tabResendsExpire.setObjectName(_fromUtf8("tabResendsExpire"))
        self.gridLayout_5 = QtGui.QGridLayout(self.tabResendsExpire)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.label_7 = QtGui.QLabel(self.tabResendsExpire)
        self.label_7.setWordWrap(True)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_5.addWidget(self.label_7, 0, 0, 1, 3)
        spacerItem14 = QtGui.QSpacerItem(212, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_5.addItem(spacerItem14, 1, 0, 1, 1)
        self.widget = QtGui.QWidget(self.tabResendsExpire)
        self.widget.setMinimumSize(QtCore.QSize(231, 75))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.label_19 = QtGui.QLabel(self.widget)
        self.label_19.setGeometry(QtCore.QRect(10, 20, 101, 20))
        self.label_19.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_19.setObjectName(_fromUtf8("label_19"))
        self.label_20 = QtGui.QLabel(self.widget)
        self.label_20.setGeometry(QtCore.QRect(30, 40, 80, 16))
        self.label_20.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_20.setObjectName(_fromUtf8("label_20"))
        self.lineEditDays = QtGui.QLineEdit(self.widget)
        self.lineEditDays.setGeometry(QtCore.QRect(113, 20, 51, 20))
        self.lineEditDays.setObjectName(_fromUtf8("lineEditDays"))
        self.lineEditMonths = QtGui.QLineEdit(self.widget)
        self.lineEditMonths.setGeometry(QtCore.QRect(113, 40, 51, 20))
        self.lineEditMonths.setObjectName(_fromUtf8("lineEditMonths"))
        self.label_22 = QtGui.QLabel(self.widget)
        self.label_22.setGeometry(QtCore.QRect(169, 23, 61, 16))
        self.label_22.setObjectName(_fromUtf8("label_22"))
        self.label_23 = QtGui.QLabel(self.widget)
        self.label_23.setGeometry(QtCore.QRect(170, 41, 71, 16))
        self.label_23.setObjectName(_fromUtf8("label_23"))
        self.gridLayout_5.addWidget(self.widget, 1, 2, 1, 1)
        spacerItem15 = QtGui.QSpacerItem(20, 129, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_5.addItem(spacerItem15, 2, 1, 1, 1)
        self.tabWidgetSettings.addTab(self.tabResendsExpire, _fromUtf8(""))
        self.gridLayout.addWidget(self.tabWidgetSettings, 0, 0, 1, 1)

        self.retranslateUi(settingsDialog)
        self.tabWidgetSettings.setCurrentIndex(0)
        QtCore.QObject.connect(  # pylint: disable=no-member
            self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), settingsDialog.accept)
        QtCore.QObject.connect(  # pylint: disable=no-member
            self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), settingsDialog.reject)
        QtCore.QObject.connect(  # pylint: disable=no-member
            self.checkBoxAuthentication,
            QtCore.SIGNAL(
                _fromUtf8("toggled(bool)")),
            self.lineEditSocksUsername.setEnabled)
        QtCore.QObject.connect(  # pylint: disable=no-member
            self.checkBoxAuthentication,
            QtCore.SIGNAL(
                _fromUtf8("toggled(bool)")),
            self.lineEditSocksPassword.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(settingsDialog)
        settingsDialog.setTabOrder(self.tabWidgetSettings, self.checkBoxStartOnLogon)
        settingsDialog.setTabOrder(self.checkBoxStartOnLogon, self.checkBoxStartInTray)
        settingsDialog.setTabOrder(self.checkBoxStartInTray, self.checkBoxMinimizeToTray)
        settingsDialog.setTabOrder(self.checkBoxMinimizeToTray, self.lineEditTCPPort)
        settingsDialog.setTabOrder(self.lineEditTCPPort, self.comboBoxProxyType)
        settingsDialog.setTabOrder(self.comboBoxProxyType, self.lineEditSocksHostname)
        settingsDialog.setTabOrder(self.lineEditSocksHostname, self.lineEditSocksPort)
        settingsDialog.setTabOrder(self.lineEditSocksPort, self.checkBoxAuthentication)
        settingsDialog.setTabOrder(self.checkBoxAuthentication, self.lineEditSocksUsername)
        settingsDialog.setTabOrder(self.lineEditSocksUsername, self.lineEditSocksPassword)
        settingsDialog.setTabOrder(self.lineEditSocksPassword, self.checkBoxSocksListen)
        settingsDialog.setTabOrder(self.checkBoxSocksListen, self.buttonBox)

    def retranslateUi(self, settingsDialog):
        """Re-translate the UI into the supported languages"""

        settingsDialog.setWindowTitle(_translate("settingsDialog", "Settings", None))
        self.checkBoxStartOnLogon.setText(_translate("settingsDialog", "Start Bitmessage on user login", None))
        self.groupBoxTray.setTitle(_translate("settingsDialog", "Tray", None))
        self.checkBoxStartInTray.setText(
            _translate(
                "settingsDialog",
                "Start Bitmessage in the tray (don\'t show main window)",
                None))
        self.checkBoxMinimizeToTray.setText(_translate("settingsDialog", "Minimize to tray", None))
        self.checkBoxTrayOnClose.setText(_translate("settingsDialog", "Close to tray", None))
        self.checkBoxHideTrayConnectionNotifications.setText(
            _translate("settingsDialog", "Hide connection notifications", None))
        self.checkBoxShowTrayNotifications.setText(
            _translate(
                "settingsDialog",
                "Show notification when message received",
                None))
        self.checkBoxPortableMode.setText(_translate("settingsDialog", "Run in Portable Mode", None))
        self.PortableModeDescription.setText(
            _translate(
                "settingsDialog",
                "In Portable Mode, messages and config files are stored in the same directory as the"
                " program rather than the normal application-data folder. This makes it convenient to"
                " run Bitmessage from a USB thumb drive.",
                None))
        self.checkBoxWillinglySendToMobile.setText(
            _translate(
                "settingsDialog",
                "Willingly include unencrypted destination address when sending to a mobile device",
                None))
        self.checkBoxUseIdenticons.setText(_translate("settingsDialog", "Use Identicons", None))
        self.checkBoxReplyBelow.setText(_translate("settingsDialog", "Reply below Quote", None))
        self.groupBox.setTitle(_translate("settingsDialog", "Interface Language", None))
        self.languageComboBox.setItemText(0, _translate("settingsDialog", "System Settings", "system"))
        self.tabWidgetSettings.setTabText(
            self.tabWidgetSettings.indexOf(
                self.tabUserInterface),
            _translate(
                "settingsDialog", "User Interface", None))
        self.groupBox1.setTitle(_translate("settingsDialog", "Listening port", None))
        self.label.setText(_translate("settingsDialog", "Listen for connections on port:", None))
        self.labelUPnP.setText(_translate("settingsDialog", "UPnP:", None))
        self.groupBox_3.setTitle(_translate("settingsDialog", "Bandwidth limit", None))
        self.label_24.setText(_translate("settingsDialog", "Maximum download rate (kB/s): [0: unlimited]", None))
        self.label_25.setText(_translate("settingsDialog", "Maximum upload rate (kB/s): [0: unlimited]", None))
        self.label_26.setText(_translate("settingsDialog", "Maximum outbound connections: [0: none]", None))
        self.groupBox_2.setTitle(_translate("settingsDialog", "Proxy server / Tor", None))
        self.label_2.setText(_translate("settingsDialog", "Type:", None))
        self.label_3.setText(_translate("settingsDialog", "Server hostname:", None))
        self.label_4.setText(_translate("settingsDialog", "Port:", None))
        self.checkBoxAuthentication.setText(_translate("settingsDialog", "Authentication", None))
        self.label_5.setText(_translate("settingsDialog", "Username:", None))
        self.label_6.setText(_translate("settingsDialog", "Pass:", None))
        self.checkBoxSocksListen.setText(
            _translate(
                "settingsDialog",
                "Listen for incoming connections when using proxy",
                None))
        self.comboBoxProxyType.setItemText(0, _translate("settingsDialog", "none", None))
        self.comboBoxProxyType.setItemText(1, _translate("settingsDialog", "SOCKS4a", None))
        self.comboBoxProxyType.setItemText(2, _translate("settingsDialog", "SOCKS5", None))
        self.tabWidgetSettings.setTabText(
            self.tabWidgetSettings.indexOf(
                self.tabNetworkSettings),
            _translate(
                "settingsDialog", "Network Settings", None))
        self.label_9.setText(_translate("settingsDialog", "Total difficulty:", None))
        self.label_10.setText(
            _translate(
                "settingsDialog",
                "The \'Total difficulty\' affects the absolute amount of work the sender must complete."
                " Doubling this value doubles the amount of work.",
                None))
        self.label_11.setText(_translate("settingsDialog", "Small message difficulty:", None))
        self.label_8.setText(_translate(
            "settingsDialog",
            "When someone sends you a message, their computer must first complete some work. The difficulty of this"
            " work, by default, is 1. You may raise this default for new addresses you create by changing the values"
            " here. Any new addresses you create will require senders to meet the higher difficulty. There is one"
            " exception: if you add a friend or acquaintance to your address book, Bitmessage will automatically"
            " notify them when you next send a message that they need only complete the minimum amount of"
            " work: difficulty 1. ",
            None))
        self.label_12.setText(
            _translate(
                "settingsDialog",
                "The \'Small message difficulty\' mostly only affects the difficulty of sending small messages."
                " Doubling this value makes it almost twice as difficult to send a small message but doesn\'t really"
                " affect large messages.",
                None))
        self.tabWidgetSettings.setTabText(
            self.tabWidgetSettings.indexOf(
                self.tabDemandedDifficulty),
            _translate(
                "settingsDialog", "Demanded difficulty", None))
        self.label_15.setText(
            _translate(
                "settingsDialog",
                "Here you may set the maximum amount of work you are willing to do to send a message to another"
                " person. Setting these values to 0 means that any value is acceptable.",
                None))
        self.label_13.setText(_translate("settingsDialog", "Maximum acceptable total difficulty:", None))
        self.label_14.setText(_translate("settingsDialog", "Maximum acceptable small message difficulty:", None))
        self.tabWidgetSettings.setTabText(
            self.tabWidgetSettings.indexOf(
                self.tabMaxAcceptableDifficulty),
            _translate(
                "settingsDialog", "Max acceptable difficulty", None))
        self.labelOpenCL.setText(_translate("settingsDialog", "Hardware GPU acceleration (OpenCL):", None))
        self.label_16.setText(_translate(
            "settingsDialog",
            "<html><head/><body><p>Bitmessage can utilize a different Bitcoin-based program called Namecoin to make"
            " addresses human-friendly. For example, instead of having to tell your friend your long Bitmessage"
            " address, you can simply tell him to send a message to <span style=\" font-style:italic;\">test."
            " </span></p><p>(Getting your own Bitmessage address into Namecoin is still rather difficult).</p>"
            "<p>Bitmessage can use either namecoind directly or a running nmcontrol instance.</p></body></html>",
            None))
        self.label_17.setText(_translate("settingsDialog", "Host:", None))
        self.label_18.setText(_translate("settingsDialog", "Port:", None))
        self.labelNamecoinUser.setText(_translate("settingsDialog", "Username:", None))
        self.labelNamecoinPassword.setText(_translate("settingsDialog", "Password:", None))
        self.pushButtonNamecoinTest.setText(_translate("settingsDialog", "Test", None))
        self.label_21.setText(_translate("settingsDialog", "Connect to:", None))
        self.radioButtonNamecoinNamecoind.setText(_translate("settingsDialog", "Namecoind", None))
        self.radioButtonNamecoinNmcontrol.setText(_translate("settingsDialog", "NMControl", None))
        self.tabWidgetSettings.setTabText(
            self.tabWidgetSettings.indexOf(
                self.tabNamecoin),
            _translate(
                "settingsDialog", "Namecoin integration", None))
        self.label_7.setText(_translate(
            "settingsDialog",
            "<html><head/><body><p>By default, if you send a message to someone and he is offline for more than two"
            " days, Bitmessage will send the message again after an additional two days. This will be continued with"
            " exponential backoff forever; messages will be resent after 5, 10, 20 days ect. until the receiver"
            " acknowledges them. Here you may change that behavior by having Bitmessage give up after a certain"
            " number of days or months.</p><p>Leave these input fields blank for the default behavior."
            " </p></body></html>",
            None))
        self.label_19.setText(_translate("settingsDialog", "Give up after", None))
        self.label_20.setText(_translate("settingsDialog", "and", None))
        self.label_22.setText(_translate("settingsDialog", "days", None))
        self.label_23.setText(_translate("settingsDialog", "months.", None))
        self.tabWidgetSettings.setTabText(
            self.tabWidgetSettings.indexOf(
                self.tabResendsExpire),
            _translate(
                "settingsDialog", "Resends Expire", None))
