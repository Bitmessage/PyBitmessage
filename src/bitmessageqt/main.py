import locale
import os
import sys
from PyQt4 import QtCore, QtGui

import l10n
import paths
import settingsmixin
import widgets
from bmconfigparser import BMConfigParser
from debug import logger
from foldertree import AddressBookCompleter
from tr import _translate


class Window(settingsmixin.SMainWindow):
    """The main PyBitmessage's window"""

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        widgets.load('main.ui', self)

        self.qmytranslator = self.qsystranslator = None
        self.blackwhitelist.rerenderBlackWhiteList()

        addressBookCompleter = AddressBookCompleter()
        addressBookCompleter.setCompletionMode(
            QtGui.QCompleter.PopupCompletion)
        addressBookCompleter.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        addressBookCompleterModel = QtGui.QStringListModel()
        addressBookCompleter.setModel(addressBookCompleterModel)
        self.lineEditTo.setCompleter(addressBookCompleter)

        self.lineEditTo.cursorPositionChanged.connect(
            addressBookCompleter.onCursorPositionChanged)

        # Put the colored icon on the status bar
        self.statusbar.insertPermanentWidget(0, self.pushButtonStatusIcon)

        # Hide all menu action containers
        for toolbar in (
            self.inboxContextMenuToolbar,
            self.addressContextMenuToolbarYourIdentities,
            self.addressContextMenuToolbar,
            self.addressBookContextMenuToolbar,
            self.subscriptionsContextMenuToolbar,
            self.sentContextMenuToolbar
        ):
            toolbar.setVisible(False)

        # splitters
        for splitter in (
            self.inboxHorizontalSplitter,
            self.sendHorizontalSplitter,
            self.subscriptionsHorizontalSplitter,
            self.chansHorizontalSplitter
        ):
            splitter.setStretchFactor(0, 0)
            splitter.setStretchFactor(1, 1)
            splitter.setCollapsible(0, False)
            splitter.setCollapsible(1, False)

        for splitter in (
            self.inboxMessagecontrolSplitter,
            self.subscriptionsMessagecontrolSplitter,
            self.chansMessagecontrolSplitter
        ):
            splitter.setStretchFactor(0, 0)
            splitter.setStretchFactor(1, 1)
            splitter.setStretchFactor(2, 2)
            splitter.setCollapsible(0, False)
            splitter.setCollapsible(1, False)
            splitter.setCollapsible(2, False)
            splitter.handle(1).setEnabled(False)

        self.sendMessagecontrolSplitter.handle(1).setEnabled(False)

    def updateNetworkSwitchMenuLabel(self, dontconnect=None):
        """
        Set the label for "Go online"/"Go offline" menu action
        depending on 'dontconnect' setting
        """
        if dontconnect is None:
            dontconnect = BMConfigParser().safeGetBoolean(
                'bitmessagesettings', 'dontconnect')
        self.actionNetworkSwitch.setText(
            _translate("MainWindow", "Go online", None)
            if dontconnect else
            _translate("MainWindow", "Go offline", None)
        )

    def retranslateUi(self):
        """Update widgets' texts which is not taken from ui-file"""
        self.updateHumanFriendlyTTLDescription(int(
            self.horizontalSliderTTL.tickPosition() ** 3.199 + 3600))
        self.networkstatus.retranslateUi()

    # FIXME: this is not best place for this func
    def change_translation(self, newlocale=None):
        """Change translation language for the application"""
        if newlocale is None:
            newlocale = l10n.getTranslationLanguage()
        try:
            if not self.qmytranslator.isEmpty():
                QtGui.QApplication.removeTranslator(self.qmytranslator)
        except:
            pass
        try:
            if not self.qsystranslator.isEmpty():
                QtGui.QApplication.removeTranslator(self.qsystranslator)
        except:
            pass

        self.qmytranslator = QtCore.QTranslator()
        translationpath = os.path.join(
            paths.codePath(), 'translations', 'bitmessage_' + newlocale)
        self.qmytranslator.load(translationpath)
        QtGui.QApplication.installTranslator(self.qmytranslator)

        self.qsystranslator = QtCore.QTranslator()
        if paths.frozen:
            translationpath = os.path.join(
                paths.codePath(), 'translations', 'qt_' + newlocale)
        else:
            translationpath = os.path.join(
                str(QtCore.QLibraryInfo.location(
                    QtCore.QLibraryInfo.TranslationsPath)), 'qt_' + newlocale)
        self.qsystranslator.load(translationpath)
        QtGui.QApplication.installTranslator(self.qsystranslator)

        lang = locale.normalize(l10n.getTranslationLanguage())
        langs = [
            lang.split(".")[0] + "." + l10n.encoding,
            lang.split(".")[0] + "." + 'UTF-8',
            lang
        ]
        if 'win32' in sys.platform or 'win64' in sys.platform:
            langs = [l10n.getWindowsLocale(lang)]
        for lang in langs:
            try:
                l10n.setlocale(locale.LC_ALL, lang)
                if 'win32' not in sys.platform and 'win64' not in sys.platform:
                    l10n.encoding = locale.nl_langinfo(locale.CODESET)
                else:
                    l10n.encoding = locale.getlocale()[1]
                logger.info("Successfully set locale to %s", lang)
                break
            except:
                logger.error("Failed to set locale to %s", lang, exc_info=True)
