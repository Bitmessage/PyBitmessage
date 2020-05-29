# -*- coding: utf-8 -*-
"""
bitmessage qt Ui module.
"""
# Form implementation generated from reading ui file 'bitmessageui.ui'
#
# Created: Mon Mar 23 22:18:07 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!
# pylint: disable=attribute-defined-outside-init,too-few-public-methods
# pylint: disable=relative-import,too-many-lines,unused-argument
# pylint: disable=too-many-instance-attributes,too-many-locals,too-many-statements
from PyQt4 import QtCore, QtGui
from bmconfigparser import BMConfigParser
from foldertree import AddressBookCompleter
from messageview import MessageView
from messagecompose import MessageCompose
import settingsmixin
from networkstatus import NetworkStatus
from blacklist import Blacklist

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:

    def _fromUtf8(s):
        return s


try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(
            context, text, disambig, encoding=QtCore.QCoreApplication.CodecForTr, n=None
    ):
        if n is None:
            return QtGui.QApplication.translate(context, text, disambig, _encoding)
        return QtGui.QApplication.translate(context, text, disambig, _encoding, n)


except AttributeError:

    def _translate(
            context, text, disambig, encoding=QtCore.QCoreApplication.CodecForTr, n=None
    ):
        if n is None:
            return QtGui.QApplication.translate(context, text, disambig)
        return QtGui.QApplication.translate(
            context, text, disambig, QtCore.QCoreApplication.CodecForTr, n)


class Ui_MainWindow(object):
    """Ui for MainWindow QT"""
    # pylint: disable=redefined-outer-name
    def setupUi(self, MainWindow):
        """setting up attributes for UI"""
        # pylint: disable=attribute-defined-outside-init
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(885, 580)
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/newPrefix/images/can-icon-24px.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        MainWindow.setWindowIcon(icon)
        MainWindow.setTabShape(QtGui.QTabWidget.Rounded)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout_10 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_10.setObjectName(_fromUtf8("gridLayout_10"))
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.tabWidget.setBaseSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.tabWidget.setFont(font)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.North)
        self.tabWidget.setTabShape(QtGui.QTabWidget.Rounded)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.inbox = QtGui.QWidget()
        self.inbox.setObjectName(_fromUtf8("inbox"))
        self.gridLayout = QtGui.QGridLayout(self.inbox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalSplitter_3 = settingsmixin.SSplitter()
        self.horizontalSplitter_3.setObjectName(_fromUtf8("horizontalSplitter_3"))
        self.verticalSplitter_12 = settingsmixin.SSplitter()
        self.verticalSplitter_12.setObjectName(_fromUtf8("verticalSplitter_12"))
        self.verticalSplitter_12.setOrientation(QtCore.Qt.Vertical)
        self.treeWidgetYourIdentities = settingsmixin.STreeWidget(self.inbox)
        self.treeWidgetYourIdentities.setObjectName(
            _fromUtf8("treeWidgetYourIdentities")
        )
        self.treeWidgetYourIdentities.resize(
            200, self.treeWidgetYourIdentities.height()
        )
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/newPrefix/images/identities.png")),
            QtGui.QIcon.Selected,
            QtGui.QIcon.Off
        )
        self.treeWidgetYourIdentities.headerItem().setIcon(0, icon1)
        self.verticalSplitter_12.addWidget(self.treeWidgetYourIdentities)
        self.pushButtonNewAddress = QtGui.QPushButton(self.inbox)
        self.pushButtonNewAddress.setObjectName(_fromUtf8("pushButtonNewAddress"))
        self.pushButtonNewAddress.resize(200, self.pushButtonNewAddress.height())
        self.verticalSplitter_12.addWidget(self.pushButtonNewAddress)
        self.verticalSplitter_12.setStretchFactor(0, 1)
        self.verticalSplitter_12.setStretchFactor(1, 0)
        self.verticalSplitter_12.setCollapsible(0, False)
        self.verticalSplitter_12.setCollapsible(1, False)
        self.verticalSplitter_12.handle(1).setEnabled(False)
        self.horizontalSplitter_3.addWidget(self.verticalSplitter_12)
        self.verticalSplitter_7 = settingsmixin.SSplitter()
        self.verticalSplitter_7.setObjectName(_fromUtf8("verticalSplitter_7"))
        self.verticalSplitter_7.setOrientation(QtCore.Qt.Vertical)
        self.horizontalSplitterSearch = QtGui.QSplitter()
        self.horizontalSplitterSearch.setObjectName(
            _fromUtf8("horizontalSplitterSearch")
        )
        self.inboxSearchLineEdit = QtGui.QLineEdit(self.inbox)
        self.inboxSearchLineEdit.setObjectName(_fromUtf8("inboxSearchLineEdit"))
        self.horizontalSplitterSearch.addWidget(self.inboxSearchLineEdit)
        self.inboxSearchOption = QtGui.QComboBox(self.inbox)
        self.inboxSearchOption.setObjectName(_fromUtf8("inboxSearchOption"))
        self.inboxSearchOption.addItem(_fromUtf8(""))
        self.inboxSearchOption.addItem(_fromUtf8(""))
        self.inboxSearchOption.addItem(_fromUtf8(""))
        self.inboxSearchOption.addItem(_fromUtf8(""))
        self.inboxSearchOption.addItem(_fromUtf8(""))
        self.inboxSearchOption.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
        self.inboxSearchOption.setCurrentIndex(3)
        self.horizontalSplitterSearch.addWidget(self.inboxSearchOption)
        self.horizontalSplitterSearch.handle(1).setEnabled(False)
        self.horizontalSplitterSearch.setStretchFactor(0, 1)
        self.horizontalSplitterSearch.setStretchFactor(1, 0)
        self.verticalSplitter_7.addWidget(self.horizontalSplitterSearch)
        self.tableWidgetInbox = settingsmixin.STableWidget(self.inbox)
        self.tableWidgetInbox.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tableWidgetInbox.setAlternatingRowColors(True)
        self.tableWidgetInbox.setSelectionMode(
            QtGui.QAbstractItemView.ExtendedSelection
        )
        self.tableWidgetInbox.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tableWidgetInbox.setWordWrap(False)
        self.tableWidgetInbox.setObjectName(_fromUtf8("tableWidgetInbox"))
        self.tableWidgetInbox.setColumnCount(4)
        self.tableWidgetInbox.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetInbox.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetInbox.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetInbox.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetInbox.setHorizontalHeaderItem(3, item)
        self.tableWidgetInbox.horizontalHeader().setCascadingSectionResizes(True)
        self.tableWidgetInbox.horizontalHeader().setDefaultSectionSize(200)
        self.tableWidgetInbox.horizontalHeader().setHighlightSections(False)
        self.tableWidgetInbox.horizontalHeader().setMinimumSectionSize(27)
        self.tableWidgetInbox.horizontalHeader().setSortIndicatorShown(False)
        self.tableWidgetInbox.horizontalHeader().setStretchLastSection(True)
        self.tableWidgetInbox.verticalHeader().setVisible(False)
        self.tableWidgetInbox.verticalHeader().setDefaultSectionSize(26)
        self.verticalSplitter_7.addWidget(self.tableWidgetInbox)
        self.textEditInboxMessage = MessageView(self.inbox)
        self.textEditInboxMessage.setBaseSize(QtCore.QSize(0, 500))
        self.textEditInboxMessage.setReadOnly(True)
        self.textEditInboxMessage.setObjectName(_fromUtf8("textEditInboxMessage"))
        self.verticalSplitter_7.addWidget(self.textEditInboxMessage)
        self.verticalSplitter_7.setStretchFactor(0, 0)
        self.verticalSplitter_7.setStretchFactor(1, 1)
        self.verticalSplitter_7.setStretchFactor(2, 2)
        self.verticalSplitter_7.setCollapsible(0, False)
        self.verticalSplitter_7.setCollapsible(1, False)
        self.verticalSplitter_7.setCollapsible(2, False)
        self.verticalSplitter_7.handle(1).setEnabled(False)
        self.horizontalSplitter_3.addWidget(self.verticalSplitter_7)
        self.horizontalSplitter_3.setStretchFactor(0, 0)
        self.horizontalSplitter_3.setStretchFactor(1, 1)
        self.horizontalSplitter_3.setCollapsible(0, False)
        self.horizontalSplitter_3.setCollapsible(1, False)
        self.gridLayout.addWidget(self.horizontalSplitter_3)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/newPrefix/images/inbox.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self.tabWidget.addTab(self.inbox, icon2, _fromUtf8(""))
        self.send = QtGui.QWidget()
        self.send.setObjectName(_fromUtf8("send"))
        self.gridLayout_7 = QtGui.QGridLayout(self.send)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.horizontalSplitter = settingsmixin.SSplitter()
        self.horizontalSplitter.setObjectName(_fromUtf8("horizontalSplitter"))
        self.verticalSplitter_2 = settingsmixin.SSplitter()
        self.verticalSplitter_2.setObjectName(_fromUtf8("verticalSplitter_2"))
        self.verticalSplitter_2.setOrientation(QtCore.Qt.Vertical)
        self.tableWidgetAddressBook = settingsmixin.STableWidget(self.send)
        self.tableWidgetAddressBook.setAlternatingRowColors(True)
        self.tableWidgetAddressBook.setSelectionMode(
            QtGui.QAbstractItemView.ExtendedSelection
        )
        self.tableWidgetAddressBook.setSelectionBehavior(
            QtGui.QAbstractItemView.SelectRows
        )
        self.tableWidgetAddressBook.setObjectName(_fromUtf8("tableWidgetAddressBook"))
        self.tableWidgetAddressBook.setColumnCount(2)
        self.tableWidgetAddressBook.setRowCount(0)
        self.tableWidgetAddressBook.resize(200, self.tableWidgetAddressBook.height())
        item = QtGui.QTableWidgetItem()
        icon3 = QtGui.QIcon()
        icon3.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/newPrefix/images/addressbook.png")),
            QtGui.QIcon.Selected,
            QtGui.QIcon.Off
        )
        item.setIcon(icon3)
        self.tableWidgetAddressBook.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetAddressBook.setHorizontalHeaderItem(1, item)
        self.tableWidgetAddressBook.horizontalHeader().setCascadingSectionResizes(True)
        self.tableWidgetAddressBook.horizontalHeader().setDefaultSectionSize(200)
        self.tableWidgetAddressBook.horizontalHeader().setHighlightSections(False)
        self.tableWidgetAddressBook.horizontalHeader().setStretchLastSection(True)
        self.tableWidgetAddressBook.verticalHeader().setVisible(False)
        self.verticalSplitter_2.addWidget(self.tableWidgetAddressBook)
        self.addressBookCompleter = AddressBookCompleter()
        self.addressBookCompleter.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        self.addressBookCompleter.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.addressBookCompleterModel = QtGui.QStringListModel()
        self.addressBookCompleter.setModel(self.addressBookCompleterModel)
        self.pushButtonAddAddressBook = QtGui.QPushButton(self.send)
        self.pushButtonAddAddressBook.setObjectName(
            _fromUtf8("pushButtonAddAddressBook")
        )
        self.pushButtonAddAddressBook.resize(
            200, self.pushButtonAddAddressBook.height()
        )
        self.verticalSplitter_2.addWidget(self.pushButtonAddAddressBook)
        self.pushButtonFetchNamecoinID = QtGui.QPushButton(self.send)
        self.pushButtonFetchNamecoinID.resize(
            200, self.pushButtonFetchNamecoinID.height()
        )
        self.pushButtonFetchNamecoinID.setObjectName(
            _fromUtf8("pushButtonFetchNamecoinID")
        )
        self.verticalSplitter_2.addWidget(self.pushButtonFetchNamecoinID)
        self.verticalSplitter_2.setStretchFactor(0, 1)
        self.verticalSplitter_2.setStretchFactor(1, 0)
        self.verticalSplitter_2.setStretchFactor(2, 0)
        self.verticalSplitter_2.setCollapsible(0, False)
        self.verticalSplitter_2.setCollapsible(1, False)
        self.verticalSplitter_2.setCollapsible(2, False)
        self.verticalSplitter_2.handle(1).setEnabled(False)
        self.verticalSplitter_2.handle(2).setEnabled(False)
        self.horizontalSplitter.addWidget(self.verticalSplitter_2)
        self.verticalSplitter = settingsmixin.SSplitter()
        self.verticalSplitter.setObjectName(_fromUtf8("verticalSplitter"))
        self.verticalSplitter.setOrientation(QtCore.Qt.Vertical)
        self.tabWidgetSend = QtGui.QTabWidget(self.send)
        self.tabWidgetSend.setObjectName(_fromUtf8("tabWidgetSend"))
        self.sendDirect = QtGui.QWidget()
        self.sendDirect.setObjectName(_fromUtf8("sendDirect"))
        self.gridLayout_8 = QtGui.QGridLayout(self.sendDirect)
        self.gridLayout_8.setObjectName(_fromUtf8("gridLayout_8"))
        self.verticalSplitter_5 = settingsmixin.SSplitter()
        self.verticalSplitter_5.setObjectName(_fromUtf8("verticalSplitter_5"))
        self.verticalSplitter_5.setOrientation(QtCore.Qt.Vertical)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_3 = QtGui.QLabel(self.sendDirect)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)
        self.label_2 = QtGui.QLabel(self.sendDirect)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)
        self.lineEditSubject = QtGui.QLineEdit(self.sendDirect)
        self.lineEditSubject.setText(_fromUtf8(""))
        self.lineEditSubject.setObjectName(_fromUtf8("lineEditSubject"))
        self.gridLayout_2.addWidget(self.lineEditSubject, 2, 1, 1, 1)
        self.label = QtGui.QLabel(self.sendDirect)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 1, 0, 1, 1)
        self.comboBoxSendFrom = QtGui.QComboBox(self.sendDirect)
        self.comboBoxSendFrom.setMinimumSize(QtCore.QSize(300, 0))
        self.comboBoxSendFrom.setObjectName(_fromUtf8("comboBoxSendFrom"))
        self.gridLayout_2.addWidget(self.comboBoxSendFrom, 0, 1, 1, 1)
        self.lineEditTo = QtGui.QLineEdit(self.sendDirect)
        self.lineEditTo.setObjectName(_fromUtf8("lineEditTo"))
        self.gridLayout_2.addWidget(self.lineEditTo, 1, 1, 1, 1)
        self.lineEditTo.setCompleter(self.addressBookCompleter)
        self.gridLayout_2_Widget = QtGui.QWidget()
        self.gridLayout_2_Widget.setLayout(self.gridLayout_2)
        self.verticalSplitter_5.addWidget(self.gridLayout_2_Widget)
        self.textEditMessage = MessageCompose(self.sendDirect)
        self.textEditMessage.setObjectName(_fromUtf8("textEditMessage"))
        self.verticalSplitter_5.addWidget(self.textEditMessage)
        self.verticalSplitter_5.setStretchFactor(0, 0)
        self.verticalSplitter_5.setStretchFactor(1, 1)
        self.verticalSplitter_5.setCollapsible(0, False)
        self.verticalSplitter_5.setCollapsible(1, False)
        self.verticalSplitter_5.handle(1).setEnabled(False)
        self.gridLayout_8.addWidget(self.verticalSplitter_5, 0, 0, 1, 1)
        self.tabWidgetSend.addTab(self.sendDirect, _fromUtf8(""))
        self.sendBroadcast = QtGui.QWidget()
        self.sendBroadcast.setObjectName(_fromUtf8("sendBroadcast"))
        self.gridLayout_9 = QtGui.QGridLayout(self.sendBroadcast)
        self.gridLayout_9.setObjectName(_fromUtf8("gridLayout_9"))
        self.verticalSplitter_6 = settingsmixin.SSplitter()
        self.verticalSplitter_6.setObjectName(_fromUtf8("verticalSplitter_6"))
        self.verticalSplitter_6.setOrientation(QtCore.Qt.Vertical)
        self.gridLayout_5 = QtGui.QGridLayout()
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.label_8 = QtGui.QLabel(self.sendBroadcast)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout_5.addWidget(self.label_8, 0, 0, 1, 1)
        self.lineEditSubjectBroadcast = QtGui.QLineEdit(self.sendBroadcast)
        self.lineEditSubjectBroadcast.setText(_fromUtf8(""))
        self.lineEditSubjectBroadcast.setObjectName(
            _fromUtf8("lineEditSubjectBroadcast")
        )
        self.gridLayout_5.addWidget(self.lineEditSubjectBroadcast, 1, 1, 1, 1)
        self.label_7 = QtGui.QLabel(self.sendBroadcast)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_5.addWidget(self.label_7, 1, 0, 1, 1)
        self.comboBoxSendFromBroadcast = QtGui.QComboBox(self.sendBroadcast)
        self.comboBoxSendFromBroadcast.setMinimumSize(QtCore.QSize(300, 0))
        self.comboBoxSendFromBroadcast.setObjectName(
            _fromUtf8("comboBoxSendFromBroadcast")
        )
        self.gridLayout_5.addWidget(self.comboBoxSendFromBroadcast, 0, 1, 1, 1)
        self.gridLayout_5_Widget = QtGui.QWidget()
        self.gridLayout_5_Widget.setLayout(self.gridLayout_5)
        self.verticalSplitter_6.addWidget(self.gridLayout_5_Widget)
        self.textEditMessageBroadcast = MessageCompose(self.sendBroadcast)
        self.textEditMessageBroadcast.setObjectName(
            _fromUtf8("textEditMessageBroadcast")
        )
        self.verticalSplitter_6.addWidget(self.textEditMessageBroadcast)
        self.verticalSplitter_6.setStretchFactor(0, 0)
        self.verticalSplitter_6.setStretchFactor(1, 1)
        self.verticalSplitter_6.setCollapsible(0, False)
        self.verticalSplitter_6.setCollapsible(1, False)
        self.verticalSplitter_6.handle(1).setEnabled(False)
        self.gridLayout_9.addWidget(self.verticalSplitter_6, 0, 0, 1, 1)
        self.tabWidgetSend.addTab(self.sendBroadcast, _fromUtf8(""))
        self.verticalSplitter.addWidget(self.tabWidgetSend)
        self.tTLContainer = QtGui.QWidget()
        self.tTLContainer.setSizePolicy(
            QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed
        )
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.tTLContainer.setLayout(self.horizontalLayout_5)
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.pushButtonTTL = QtGui.QPushButton(self.send)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.pushButtonTTL.sizePolicy().hasHeightForWidth()
        )
        self.pushButtonTTL.setSizePolicy(sizePolicy)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        self.pushButtonTTL.setPalette(palette)
        font = QtGui.QFont()
        font.setUnderline(True)
        self.pushButtonTTL.setFont(font)
        self.pushButtonTTL.setFlat(True)
        self.pushButtonTTL.setObjectName(_fromUtf8("pushButtonTTL"))
        self.horizontalLayout_5.addWidget(self.pushButtonTTL, 0, QtCore.Qt.AlignRight)
        self.horizontalSliderTTL = QtGui.QSlider(self.send)
        self.horizontalSliderTTL.setMinimumSize(QtCore.QSize(70, 0))
        self.horizontalSliderTTL.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSliderTTL.setInvertedAppearance(False)
        self.horizontalSliderTTL.setInvertedControls(False)
        self.horizontalSliderTTL.setObjectName(_fromUtf8("horizontalSliderTTL"))
        self.horizontalLayout_5.addWidget(
            self.horizontalSliderTTL, 0, QtCore.Qt.AlignLeft
        )
        self.labelHumanFriendlyTTLDescription = QtGui.QLabel(self.send)
        sizePolicy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.labelHumanFriendlyTTLDescription.sizePolicy().hasHeightForWidth()
        )
        self.labelHumanFriendlyTTLDescription.setSizePolicy(sizePolicy)
        self.labelHumanFriendlyTTLDescription.setMinimumSize(QtCore.QSize(45, 0))
        self.labelHumanFriendlyTTLDescription.setObjectName(
            _fromUtf8("labelHumanFriendlyTTLDescription")
        )
        self.horizontalLayout_5.addWidget(
            self.labelHumanFriendlyTTLDescription, 1, QtCore.Qt.AlignLeft
        )
        self.pushButtonClear = QtGui.QPushButton(self.send)
        self.pushButtonClear.setObjectName(_fromUtf8("pushButtonClear"))
        self.horizontalLayout_5.addWidget(self.pushButtonClear, 0, QtCore.Qt.AlignRight)
        self.pushButtonSend = QtGui.QPushButton(self.send)
        self.pushButtonSend.setObjectName(_fromUtf8("pushButtonSend"))
        self.horizontalLayout_5.addWidget(self.pushButtonSend, 0, QtCore.Qt.AlignRight)
        self.horizontalSliderTTL.setMaximumSize(
            QtCore.QSize(105, self.pushButtonSend.height())
        )
        self.verticalSplitter.addWidget(self.tTLContainer)
        self.tTLContainer.adjustSize()
        self.verticalSplitter.setStretchFactor(1, 0)
        self.verticalSplitter.setStretchFactor(0, 1)
        self.verticalSplitter.setCollapsible(0, False)
        self.verticalSplitter.setCollapsible(1, False)
        self.verticalSplitter.handle(1).setEnabled(False)
        self.horizontalSplitter.addWidget(self.verticalSplitter)
        self.horizontalSplitter.setStretchFactor(0, 0)
        self.horizontalSplitter.setStretchFactor(1, 1)
        self.horizontalSplitter.setCollapsible(0, False)
        self.horizontalSplitter.setCollapsible(1, False)
        self.gridLayout_7.addWidget(self.horizontalSplitter, 0, 0, 1, 1)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/newPrefix/images/send.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self.tabWidget.addTab(self.send, icon4, _fromUtf8(""))
        self.subscriptions = QtGui.QWidget()
        self.subscriptions.setObjectName(_fromUtf8("subscriptions"))
        self.gridLayout_3 = QtGui.QGridLayout(self.subscriptions)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.horizontalSplitter_4 = settingsmixin.SSplitter()
        self.horizontalSplitter_4.setObjectName(_fromUtf8("horizontalSplitter_4"))
        self.verticalSplitter_3 = settingsmixin.SSplitter()
        self.verticalSplitter_3.setObjectName(_fromUtf8("verticalSplitter_3"))
        self.verticalSplitter_3.setOrientation(QtCore.Qt.Vertical)
        self.treeWidgetSubscriptions = settingsmixin.STreeWidget(self.subscriptions)
        self.treeWidgetSubscriptions.setAlternatingRowColors(True)
        self.treeWidgetSubscriptions.setSelectionMode(
            QtGui.QAbstractItemView.SingleSelection
        )
        self.treeWidgetSubscriptions.setSelectionBehavior(
            QtGui.QAbstractItemView.SelectRows
        )
        self.treeWidgetSubscriptions.setObjectName(_fromUtf8("treeWidgetSubscriptions"))
        self.treeWidgetSubscriptions.resize(200, self.treeWidgetSubscriptions.height())
        icon5 = QtGui.QIcon()
        icon5.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/newPrefix/images/subscriptions.png")),
            QtGui.QIcon.Selected,
            QtGui.QIcon.Off
        )
        self.treeWidgetSubscriptions.headerItem().setIcon(0, icon5)
        self.verticalSplitter_3.addWidget(self.treeWidgetSubscriptions)
        self.pushButtonAddSubscription = QtGui.QPushButton(self.subscriptions)
        self.pushButtonAddSubscription.setObjectName(
            _fromUtf8("pushButtonAddSubscription")
        )
        self.pushButtonAddSubscription.resize(
            200, self.pushButtonAddSubscription.height()
        )
        self.verticalSplitter_3.addWidget(self.pushButtonAddSubscription)
        self.verticalSplitter_3.setStretchFactor(0, 1)
        self.verticalSplitter_3.setStretchFactor(1, 0)
        self.verticalSplitter_3.setCollapsible(0, False)
        self.verticalSplitter_3.setCollapsible(1, False)
        self.verticalSplitter_3.handle(1).setEnabled(False)
        self.horizontalSplitter_4.addWidget(self.verticalSplitter_3)
        self.verticalSplitter_4 = settingsmixin.SSplitter()
        self.verticalSplitter_4.setObjectName(_fromUtf8("verticalSplitter_4"))
        self.verticalSplitter_4.setOrientation(QtCore.Qt.Vertical)
        self.horizontalSplitter_2 = QtGui.QSplitter()
        self.horizontalSplitter_2.setObjectName(_fromUtf8("horizontalSplitter_2"))
        self.inboxSearchLineEditSubscriptions = QtGui.QLineEdit(self.subscriptions)
        self.inboxSearchLineEditSubscriptions.setObjectName(
            _fromUtf8("inboxSearchLineEditSubscriptions")
        )
        self.horizontalSplitter_2.addWidget(self.inboxSearchLineEditSubscriptions)
        self.inboxSearchOptionSubscriptions = QtGui.QComboBox(self.subscriptions)
        self.inboxSearchOptionSubscriptions.setObjectName(
            _fromUtf8("inboxSearchOptionSubscriptions")
        )
        self.inboxSearchOptionSubscriptions.addItem(_fromUtf8(""))
        self.inboxSearchOptionSubscriptions.addItem(_fromUtf8(""))
        self.inboxSearchOptionSubscriptions.addItem(_fromUtf8(""))
        self.inboxSearchOptionSubscriptions.addItem(_fromUtf8(""))
        self.inboxSearchOptionSubscriptions.setSizeAdjustPolicy(
            QtGui.QComboBox.AdjustToContents
        )
        self.inboxSearchOptionSubscriptions.setCurrentIndex(2)
        self.horizontalSplitter_2.addWidget(self.inboxSearchOptionSubscriptions)
        self.horizontalSplitter_2.handle(1).setEnabled(False)
        self.horizontalSplitter_2.setStretchFactor(0, 1)
        self.horizontalSplitter_2.setStretchFactor(1, 0)
        self.verticalSplitter_4.addWidget(self.horizontalSplitter_2)
        self.tableWidgetInboxSubscriptions = settingsmixin.STableWidget(
            self.subscriptions
        )
        self.tableWidgetInboxSubscriptions.setEditTriggers(
            QtGui.QAbstractItemView.NoEditTriggers
        )
        self.tableWidgetInboxSubscriptions.setAlternatingRowColors(True)
        self.tableWidgetInboxSubscriptions.setSelectionMode(
            QtGui.QAbstractItemView.ExtendedSelection
        )
        self.tableWidgetInboxSubscriptions.setSelectionBehavior(
            QtGui.QAbstractItemView.SelectRows
        )
        self.tableWidgetInboxSubscriptions.setWordWrap(False)
        self.tableWidgetInboxSubscriptions.setObjectName(
            _fromUtf8("tableWidgetInboxSubscriptions")
        )
        self.tableWidgetInboxSubscriptions.setColumnCount(4)
        self.tableWidgetInboxSubscriptions.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetInboxSubscriptions.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetInboxSubscriptions.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetInboxSubscriptions.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetInboxSubscriptions.setHorizontalHeaderItem(3, item)
        self.tableWidgetInboxSubscriptions.horizontalHeader().setCascadingSectionResizes(
            True
        )
        self.tableWidgetInboxSubscriptions.horizontalHeader().setDefaultSectionSize(200)
        self.tableWidgetInboxSubscriptions.horizontalHeader().setHighlightSections(
            False
        )
        self.tableWidgetInboxSubscriptions.horizontalHeader().setMinimumSectionSize(27)
        self.tableWidgetInboxSubscriptions.horizontalHeader().setSortIndicatorShown(
            False
        )
        self.tableWidgetInboxSubscriptions.horizontalHeader().setStretchLastSection(
            True
        )
        self.tableWidgetInboxSubscriptions.verticalHeader().setVisible(False)
        self.tableWidgetInboxSubscriptions.verticalHeader().setDefaultSectionSize(26)
        self.verticalSplitter_4.addWidget(self.tableWidgetInboxSubscriptions)
        self.textEditInboxMessageSubscriptions = MessageView(self.subscriptions)
        self.textEditInboxMessageSubscriptions.setBaseSize(QtCore.QSize(0, 500))
        self.textEditInboxMessageSubscriptions.setReadOnly(True)
        self.textEditInboxMessageSubscriptions.setObjectName(
            _fromUtf8("textEditInboxMessageSubscriptions")
        )
        self.verticalSplitter_4.addWidget(self.textEditInboxMessageSubscriptions)
        self.verticalSplitter_4.setStretchFactor(0, 0)
        self.verticalSplitter_4.setStretchFactor(1, 1)
        self.verticalSplitter_4.setStretchFactor(2, 2)
        self.verticalSplitter_4.setCollapsible(0, False)
        self.verticalSplitter_4.setCollapsible(1, False)
        self.verticalSplitter_4.setCollapsible(2, False)
        self.verticalSplitter_4.handle(1).setEnabled(False)
        self.horizontalSplitter_4.addWidget(self.verticalSplitter_4)
        self.horizontalSplitter_4.setStretchFactor(0, 0)
        self.horizontalSplitter_4.setStretchFactor(1, 1)
        self.horizontalSplitter_4.setCollapsible(0, False)
        self.horizontalSplitter_4.setCollapsible(1, False)
        self.gridLayout_3.addWidget(self.horizontalSplitter_4, 0, 0, 1, 1)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/newPrefix/images/subscriptions.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self.tabWidget.addTab(self.subscriptions, icon6, _fromUtf8(""))
        self.chans = QtGui.QWidget()
        self.chans.setObjectName(_fromUtf8("chans"))
        self.gridLayout_4 = QtGui.QGridLayout(self.chans)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.horizontalSplitter_7 = settingsmixin.SSplitter()
        self.horizontalSplitter_7.setObjectName(_fromUtf8("horizontalSplitter_7"))
        self.verticalSplitter_17 = settingsmixin.SSplitter()
        self.verticalSplitter_17.setObjectName(_fromUtf8("verticalSplitter_17"))
        self.verticalSplitter_17.setOrientation(QtCore.Qt.Vertical)
        self.treeWidgetChans = settingsmixin.STreeWidget(self.chans)
        self.treeWidgetChans.setFrameShadow(QtGui.QFrame.Sunken)
        self.treeWidgetChans.setLineWidth(1)
        self.treeWidgetChans.setAlternatingRowColors(True)
        self.treeWidgetChans.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.treeWidgetChans.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.treeWidgetChans.setObjectName(_fromUtf8("treeWidgetChans"))
        self.treeWidgetChans.resize(200, self.treeWidgetChans.height())
        icon7 = QtGui.QIcon()
        icon7.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/newPrefix/images/can-icon-16px.png")),
            QtGui.QIcon.Selected,
            QtGui.QIcon.Off
        )
        self.treeWidgetChans.headerItem().setIcon(0, icon7)
        self.verticalSplitter_17.addWidget(self.treeWidgetChans)
        self.pushButtonAddChan = QtGui.QPushButton(self.chans)
        self.pushButtonAddChan.setObjectName(_fromUtf8("pushButtonAddChan"))
        self.pushButtonAddChan.resize(200, self.pushButtonAddChan.height())
        self.verticalSplitter_17.addWidget(self.pushButtonAddChan)
        self.verticalSplitter_17.setStretchFactor(0, 1)
        self.verticalSplitter_17.setStretchFactor(1, 0)
        self.verticalSplitter_17.setCollapsible(0, False)
        self.verticalSplitter_17.setCollapsible(1, False)
        self.verticalSplitter_17.handle(1).setEnabled(False)
        self.horizontalSplitter_7.addWidget(self.verticalSplitter_17)
        self.verticalSplitter_8 = settingsmixin.SSplitter()
        self.verticalSplitter_8.setObjectName(_fromUtf8("verticalSplitter_8"))
        self.verticalSplitter_8.setOrientation(QtCore.Qt.Vertical)
        self.horizontalSplitter_6 = QtGui.QSplitter()
        self.horizontalSplitter_6.setObjectName(_fromUtf8("horizontalSplitter_6"))
        self.inboxSearchLineEditChans = QtGui.QLineEdit(self.chans)
        self.inboxSearchLineEditChans.setObjectName(
            _fromUtf8("inboxSearchLineEditChans")
        )
        self.horizontalSplitter_6.addWidget(self.inboxSearchLineEditChans)
        self.inboxSearchOptionChans = QtGui.QComboBox(self.chans)
        self.inboxSearchOptionChans.setObjectName(_fromUtf8("inboxSearchOptionChans"))
        self.inboxSearchOptionChans.addItem(_fromUtf8(""))
        self.inboxSearchOptionChans.addItem(_fromUtf8(""))
        self.inboxSearchOptionChans.addItem(_fromUtf8(""))
        self.inboxSearchOptionChans.addItem(_fromUtf8(""))
        self.inboxSearchOptionChans.addItem(_fromUtf8(""))
        self.inboxSearchOptionChans.setSizeAdjustPolicy(
            QtGui.QComboBox.AdjustToContents
        )
        self.inboxSearchOptionChans.setCurrentIndex(3)
        self.horizontalSplitter_6.addWidget(self.inboxSearchOptionChans)
        self.horizontalSplitter_6.handle(1).setEnabled(False)
        self.horizontalSplitter_6.setStretchFactor(0, 1)
        self.horizontalSplitter_6.setStretchFactor(1, 0)
        self.verticalSplitter_8.addWidget(self.horizontalSplitter_6)
        self.tableWidgetInboxChans = settingsmixin.STableWidget(self.chans)
        self.tableWidgetInboxChans.setEditTriggers(
            QtGui.QAbstractItemView.NoEditTriggers
        )
        self.tableWidgetInboxChans.setAlternatingRowColors(True)
        self.tableWidgetInboxChans.setSelectionMode(
            QtGui.QAbstractItemView.ExtendedSelection
        )
        self.tableWidgetInboxChans.setSelectionBehavior(
            QtGui.QAbstractItemView.SelectRows
        )
        self.tableWidgetInboxChans.setWordWrap(False)
        self.tableWidgetInboxChans.setObjectName(_fromUtf8("tableWidgetInboxChans"))
        self.tableWidgetInboxChans.setColumnCount(4)
        self.tableWidgetInboxChans.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetInboxChans.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetInboxChans.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetInboxChans.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetInboxChans.setHorizontalHeaderItem(3, item)
        self.tableWidgetInboxChans.horizontalHeader().setCascadingSectionResizes(True)
        self.tableWidgetInboxChans.horizontalHeader().setDefaultSectionSize(200)
        self.tableWidgetInboxChans.horizontalHeader().setHighlightSections(False)
        self.tableWidgetInboxChans.horizontalHeader().setMinimumSectionSize(27)
        self.tableWidgetInboxChans.horizontalHeader().setSortIndicatorShown(False)
        self.tableWidgetInboxChans.horizontalHeader().setStretchLastSection(True)
        self.tableWidgetInboxChans.verticalHeader().setVisible(False)
        self.tableWidgetInboxChans.verticalHeader().setDefaultSectionSize(26)
        self.verticalSplitter_8.addWidget(self.tableWidgetInboxChans)
        self.textEditInboxMessageChans = MessageView(self.chans)
        self.textEditInboxMessageChans.setBaseSize(QtCore.QSize(0, 500))
        self.textEditInboxMessageChans.setReadOnly(True)
        self.textEditInboxMessageChans.setObjectName(
            _fromUtf8("textEditInboxMessageChans")
        )
        self.verticalSplitter_8.addWidget(self.textEditInboxMessageChans)
        self.verticalSplitter_8.setStretchFactor(0, 0)
        self.verticalSplitter_8.setStretchFactor(1, 1)
        self.verticalSplitter_8.setStretchFactor(2, 2)
        self.verticalSplitter_8.setCollapsible(0, False)
        self.verticalSplitter_8.setCollapsible(1, False)
        self.verticalSplitter_8.setCollapsible(2, False)
        self.verticalSplitter_8.handle(1).setEnabled(False)
        self.horizontalSplitter_7.addWidget(self.verticalSplitter_8)
        self.horizontalSplitter_7.setStretchFactor(0, 0)
        self.horizontalSplitter_7.setStretchFactor(1, 1)
        self.horizontalSplitter_7.setCollapsible(0, False)
        self.horizontalSplitter_7.setCollapsible(1, False)
        self.gridLayout_4.addWidget(self.horizontalSplitter_7, 0, 0, 1, 1)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/newPrefix/images/can-icon-16px.png")),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off
        )
        self.tabWidget.addTab(self.chans, icon8, _fromUtf8(""))
        self.blackwhitelist = Blacklist()
        self.tabWidget.addTab(
            self.blackwhitelist, QtGui.QIcon(":/newPrefix/images/blacklist.png"), ""
        )
        # Initialize the Blacklist or Whitelist
        if BMConfigParser().get("bitmessagesettings", "blackwhitelist") == "white":
            self.blackwhitelist.radioButtonWhitelist.click()
        self.blackwhitelist.rerenderBlackWhiteList()

        self.networkstatus = NetworkStatus()
        self.tabWidget.addTab(
            self.networkstatus, QtGui.QIcon(":/newPrefix/images/networkstatus.png"), ""
        )
        self.gridLayout_10.addWidget(self.tabWidget, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 885, 27))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuSettings = QtGui.QMenu(self.menubar)
        self.menuSettings.setObjectName(_fromUtf8("menuSettings"))
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setMaximumSize(QtCore.QSize(16777215, 22))
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionImport_keys = QtGui.QAction(MainWindow)
        self.actionImport_keys.setObjectName(_fromUtf8("actionImport_keys"))
        self.actionManageKeys = QtGui.QAction(MainWindow)
        self.actionManageKeys.setCheckable(False)
        self.actionManageKeys.setEnabled(True)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("dialog-password"))
        self.actionManageKeys.setIcon(icon)
        self.actionManageKeys.setObjectName(_fromUtf8("actionManageKeys"))
        self.actionNetworkSwitch = QtGui.QAction(MainWindow)
        self.actionNetworkSwitch.setObjectName(_fromUtf8("actionNetworkSwitch"))
        self.actionExit = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("application-exit"))
        self.actionExit.setIcon(icon)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionHelp = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("help-contents"))
        self.actionHelp.setIcon(icon)
        self.actionHelp.setObjectName(_fromUtf8("actionHelp"))
        self.actionSupport = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("help-support"))
        self.actionSupport.setIcon(icon)
        self.actionSupport.setObjectName(_fromUtf8("actionSupport"))
        self.actionAbout = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("help-about"))
        self.actionAbout.setIcon(icon)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.actionSettings = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("document-properties"))
        self.actionSettings.setIcon(icon)
        self.actionSettings.setObjectName(_fromUtf8("actionSettings"))
        self.actionRegenerateDeterministicAddresses = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("view-refresh"))
        self.actionRegenerateDeterministicAddresses.setIcon(icon)
        self.actionRegenerateDeterministicAddresses.setObjectName(
            _fromUtf8("actionRegenerateDeterministicAddresses")
        )
        self.actionDeleteAllTrashedMessages = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("user-trash"))
        self.actionDeleteAllTrashedMessages.setIcon(icon)
        self.actionDeleteAllTrashedMessages.setObjectName(
            _fromUtf8("actionDeleteAllTrashedMessages")
        )
        self.actionJoinChan = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("contact-new"))
        self.actionJoinChan.setIcon(icon)
        self.actionJoinChan.setObjectName(_fromUtf8("actionJoinChan"))
        self.menuFile.addAction(self.actionManageKeys)
        self.menuFile.addAction(self.actionDeleteAllTrashedMessages)
        self.menuFile.addAction(self.actionRegenerateDeterministicAddresses)
        self.menuFile.addAction(self.actionNetworkSwitch)
        self.menuFile.addAction(self.actionExit)
        self.menuSettings.addAction(self.actionSettings)
        self.menuHelp.addAction(self.actionHelp)
        self.menuHelp.addAction(self.actionSupport)
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(self.tabWidget.indexOf(self.inbox))
        self.tabWidgetSend.setCurrentIndex(self.tabWidgetSend.indexOf(self.sendDirect))
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.tableWidgetInbox, self.textEditInboxMessage)
        MainWindow.setTabOrder(self.textEditInboxMessage, self.comboBoxSendFrom)
        MainWindow.setTabOrder(self.comboBoxSendFrom, self.lineEditTo)
        MainWindow.setTabOrder(self.lineEditTo, self.lineEditSubject)
        MainWindow.setTabOrder(self.lineEditSubject, self.textEditMessage)
        MainWindow.setTabOrder(self.textEditMessage, self.pushButtonAddSubscription)

        # Popup menu actions container for the Sent page
        # pylint: disable=attribute-defined-outside-init
        self.sentContextMenuToolbar = QtGui.QToolBar()
        # Popup menu actions container for chans tree
        self.addressContextMenuToolbar = QtGui.QToolBar()
        # Popup menu actions container for subscriptions tree
        self.subscriptionsContextMenuToolbar = QtGui.QToolBar()

    def updateNetworkSwitchMenuLabel(self, dontconnect=None):
        """method to update network switch menu labels"""
        if dontconnect is None:
            dontconnect = BMConfigParser().safeGetBoolean(
                "bitmessagesettings", "dontconnect"
            )
        self.actionNetworkSwitch.setText(
            _translate("MainWindow", "Go online", None)
            if dontconnect
            else _translate("MainWindow", "Go offline", None)
        )

    def retranslateUi(self, MainWindow):
        """ui retransalation"""
        # pylint: disable=redefined-outer-name
        MainWindow.setWindowTitle(_translate("MainWindow", "Bitmessage", None))
        self.treeWidgetYourIdentities.headerItem().setText(
            0, _translate("MainWindow", "Identities", None)
        )
        self.pushButtonNewAddress.setText(
            _translate("MainWindow", "New Identity", None)
        )
        self.inboxSearchLineEdit.setPlaceholderText(
            _translate("MainWindow", "Search", None)
        )
        self.inboxSearchOption.setItemText(0, _translate("MainWindow", "All", None))
        self.inboxSearchOption.setItemText(1, _translate("MainWindow", "To", None))
        self.inboxSearchOption.setItemText(2, _translate("MainWindow", "From", None))
        self.inboxSearchOption.setItemText(3, _translate("MainWindow", "Subject", None))
        self.inboxSearchOption.setItemText(4, _translate("MainWindow", "Message", None))
        self.tableWidgetInbox.setSortingEnabled(True)
        item = self.tableWidgetInbox.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "To", None))
        item = self.tableWidgetInbox.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "From", None))
        item = self.tableWidgetInbox.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Subject", None))
        item = self.tableWidgetInbox.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Received", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.inbox),
            _translate("MainWindow", "Messages", None)
        )
        self.tableWidgetAddressBook.setSortingEnabled(True)
        item = self.tableWidgetAddressBook.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Address book", None))
        item = self.tableWidgetAddressBook.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Address", None))
        self.pushButtonAddAddressBook.setText(
            _translate("MainWindow", "Add Contact", None)
        )
        self.pushButtonFetchNamecoinID.setText(
            _translate("MainWindow", "Fetch Namecoin ID", None)
        )
        self.label_3.setText(_translate("MainWindow", "Subject:", None))
        self.label_2.setText(_translate("MainWindow", "From:", None))
        self.label.setText(_translate("MainWindow", "To:", None))
        # self.textEditMessage.setHtml("")
        self.tabWidgetSend.setTabText(
            self.tabWidgetSend.indexOf(self.sendDirect),
            _translate("MainWindow", "Send ordinary Message", None)
        )
        self.label_8.setText(_translate("MainWindow", "From:", None))
        self.label_7.setText(_translate("MainWindow", "Subject:", None))
        # self.textEditMessageBroadcast.setHtml("")
        self.tabWidgetSend.setTabText(
            self.tabWidgetSend.indexOf(self.sendBroadcast),
            _translate("MainWindow", "Send Message to your Subscribers", None)
        )
        self.pushButtonTTL.setText(_translate("MainWindow", "TTL:", None))
        hours = 48
        try:
            hours = int(BMConfigParser().getint("bitmessagesettings", "ttl") / 60 / 60)
        except Exception:
            pass
        self.labelHumanFriendlyTTLDescription.setText(
            _translate(
                "MainWindow",
                "%n hour(s)",
                None,
                QtCore.QCoreApplication.CodecForTr,
                hours
            )
        )
        self.pushButtonClear.setText(_translate("MainWindow", "Clear", None))
        self.pushButtonSend.setText(_translate("MainWindow", "Send", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.send), _translate("MainWindow", "Send", None)
        )
        self.treeWidgetSubscriptions.headerItem().setText(
            0, _translate("MainWindow", "Subscriptions", None)
        )
        self.pushButtonAddSubscription.setText(
            _translate("MainWindow", "Add new Subscription", None)
        )
        self.inboxSearchLineEditSubscriptions.setPlaceholderText(
            _translate("MainWindow", "Search", None)
        )
        self.inboxSearchOptionSubscriptions.setItemText(
            0, _translate("MainWindow", "All", None)
        )
        self.inboxSearchOptionSubscriptions.setItemText(
            1, _translate("MainWindow", "From", None)
        )
        self.inboxSearchOptionSubscriptions.setItemText(
            2, _translate("MainWindow", "Subject", None)
        )
        self.inboxSearchOptionSubscriptions.setItemText(
            3, _translate("MainWindow", "Message", None)
        )
        self.tableWidgetInboxSubscriptions.setSortingEnabled(True)
        item = self.tableWidgetInboxSubscriptions.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "To", None))
        item = self.tableWidgetInboxSubscriptions.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "From", None))
        item = self.tableWidgetInboxSubscriptions.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Subject", None))
        item = self.tableWidgetInboxSubscriptions.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Received", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.subscriptions),
            _translate("MainWindow", "Subscriptions", None)
        )
        self.treeWidgetChans.headerItem().setText(
            0, _translate("MainWindow", "Chans", None)
        )
        self.pushButtonAddChan.setText(_translate("MainWindow", "Add Chan", None))
        self.inboxSearchLineEditChans.setPlaceholderText(
            _translate("MainWindow", "Search", None)
        )
        self.inboxSearchOptionChans.setItemText(
            0, _translate("MainWindow", "All", None)
        )
        self.inboxSearchOptionChans.setItemText(1, _translate("MainWindow", "To", None))
        self.inboxSearchOptionChans.setItemText(
            2, _translate("MainWindow", "From", None)
        )
        self.inboxSearchOptionChans.setItemText(
            3, _translate("MainWindow", "Subject", None)
        )
        self.inboxSearchOptionChans.setItemText(
            4, _translate("MainWindow", "Message", None)
        )
        self.tableWidgetInboxChans.setSortingEnabled(True)
        item = self.tableWidgetInboxChans.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "To", None))
        item = self.tableWidgetInboxChans.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "From", None))
        item = self.tableWidgetInboxChans.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Subject", None))
        item = self.tableWidgetInboxChans.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Received", None))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.chans), _translate("MainWindow", "Chans", None)
        )
        self.blackwhitelist.retranslateUi()
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.blackwhitelist),
            _translate("blacklist", "Blacklist", None)
        )
        self.networkstatus.retranslateUi()
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.networkstatus),
            _translate("networkstatus", "Network Status", None)
        )
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.menuSettings.setTitle(_translate("MainWindow", "Settings", None))
        self.menuHelp.setTitle(_translate("MainWindow", "Help", None))
        self.actionImport_keys.setText(_translate("MainWindow", "Import keys", None))
        self.actionManageKeys.setText(_translate("MainWindow", "Manage keys", None))
        self.actionExit.setText(_translate("MainWindow", "Quit", None))
        self.actionExit.setShortcut(_translate("MainWindow", "Ctrl+Q", None))
        self.actionHelp.setText(_translate("MainWindow", "Help", None))
        self.actionHelp.setShortcut(_translate("MainWindow", "F1", None))
        self.actionSupport.setText(_translate("MainWindow", "Contact support", None))
        self.actionAbout.setText(_translate("MainWindow", "About", None))
        self.actionSettings.setText(_translate("MainWindow", "Settings", None))
        self.actionRegenerateDeterministicAddresses.setText(
            _translate("MainWindow", "Regenerate deterministic addresses", None)
        )
        self.actionDeleteAllTrashedMessages.setText(
            _translate("MainWindow", "Delete all trashed messages", None)
        )
        self.actionJoinChan.setText(
            _translate("MainWindow", "Join / Create chan", None)
        )
        self.updateNetworkSwitchMenuLabel()


if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    MainWindow = settingsmixin.SMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
