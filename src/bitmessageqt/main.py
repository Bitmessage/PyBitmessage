from PyQt4 import QtCore, QtGui

import settingsmixin
import widgets
from bmconfigparser import BMConfigParser
from foldertree import AddressBookCompleter
from retranslateui import RetranslateMixin
from tr import _translate


class Window(settingsmixin.SMainWindow, RetranslateMixin):
    """The main PyBitmessage's window"""

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        widgets.load('bitmessageui.ui', self)

        self.addressBookCompleter = AddressBookCompleter()
        self.addressBookCompleter.setCompletionMode(
            QtGui.QCompleter.PopupCompletion)
        self.addressBookCompleter.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.addressBookCompleterModel = QtGui.QStringListModel()
        self.addressBookCompleter.setModel(self.addressBookCompleterModel)
        self.lineEditTo.setCompleter(self.addressBookCompleter)

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
