"""
Custom dialog classes
"""
# pylint: disable=too-few-public-methods
from PyQt4 import QtGui

import paths
import widgets
from address_dialogs import (
    AddAddressDialog, EmailGatewayDialog, NewAddressDialog,
    NewSubscriptionDialog, RegenerateAddressesDialog,
    SpecialAddressBehaviorDialog
)
from newchandialog import NewChanDialog
from settings import SettingsDialog
from tr import _translate
from version import softwareVersion


__all__ = [
    "NewChanDialog", "AddAddressDialog", "NewAddressDialog",
    "NewSubscriptionDialog", "RegenerateAddressesDialog",
    "SpecialAddressBehaviorDialog", "EmailGatewayDialog",
    "SettingsDialog"
]


class AboutDialog(QtGui.QDialog):
    """The `About` dialog"""
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)
        widgets.load('about.ui', self)
        last_commit = paths.lastCommit()
        version = softwareVersion
        commit = last_commit.get('commit')
        if commit:
            version += '-' + commit[:7]
        self.labelVersion.setText(
            self.labelVersion.text().replace(
                ':version:', version
            ).replace(':branch:', commit or 'v%s' % version)
        )
        self.labelVersion.setOpenExternalLinks(True)

        try:
            self.label_2.setText(
                self.label_2.text().replace(
                    '2020', str(last_commit.get('time').year)
                ))
        except AttributeError:
            pass

        self.setFixedSize(QtGui.QWidget.sizeHint(self))


class IconGlossaryDialog(QtGui.QDialog):
    """The `Icon Glossary` dialog, explaining the status icon colors"""
    def __init__(self, parent=None, config=None):
        super(IconGlossaryDialog, self).__init__(parent)
        widgets.load('iconglossary.ui', self)

        # .. todo:: FIXME: check the window title visibility here
        self.groupBox.setTitle('')

        self.labelPortNumber.setText(_translate(
            "iconGlossaryDialog",
            "You are using TCP port %1. (This can be changed in the settings)."
        ).arg(config.getint('bitmessagesettings', 'port')))
        self.setFixedSize(QtGui.QWidget.sizeHint(self))


class HelpDialog(QtGui.QDialog):
    """The `Help` dialog"""
    def __init__(self, parent=None):
        super(HelpDialog, self).__init__(parent)
        widgets.load('help.ui', self)
        self.setFixedSize(QtGui.QWidget.sizeHint(self))


class ConnectDialog(QtGui.QDialog):
    """The `Connect` dialog"""
    def __init__(self, parent=None):
        super(ConnectDialog, self).__init__(parent)
        widgets.load('connect.ui', self)
        self.setFixedSize(QtGui.QWidget.sizeHint(self))
