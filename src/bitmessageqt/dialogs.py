"""
All dialogs are available in this module.
"""
# pylint: disable=too-few-public-methods
from unqstr import ustr

from qtpy import QtWidgets

import paths
from bitmessageqt import widgets
from .address_dialogs import (
    AddAddressDialog, EmailGatewayDialog, NewAddressDialog,
    NewSubscriptionDialog, RegenerateAddressesDialog,
    SpecialAddressBehaviorDialog
)
from .newchandialog import NewChanDialog
from .settings import SettingsDialog
from tr import _translate
from version import softwareVersion

__all__ = [
    "NewChanDialog", "AddAddressDialog", "NewAddressDialog",
    "NewSubscriptionDialog", "RegenerateAddressesDialog",
    "SpecialAddressBehaviorDialog", "EmailGatewayDialog",
    "SettingsDialog"
]


class AboutDialog(QtWidgets.QDialog):
    """The "About" dialog"""
    def __init__(self, parent=None):
        super(AboutDialog, self).__init__(parent)
        widgets.load('about.ui', self)
        last_commit = paths.lastCommit()
        version = softwareVersion
        commit = last_commit.get('commit')
        if commit:
            version += '-' + commit[:7]
        self.labelVersion.setText(
            ustr(self.labelVersion.text()).replace(
                ':version:', version
            ).replace(':branch:', commit or 'v%s' % version)
        )
        self.labelVersion.setOpenExternalLinks(True)

        try:
            self.label_2.setText(
                ustr(self.label_2.text()).replace(
                    '2022', ustr(last_commit.get('time').year)
                ))
        except AttributeError:
            pass

        self.setFixedSize(QtWidgets.QWidget.sizeHint(self))


class IconGlossaryDialog(QtWidgets.QDialog):
    """The "Icon Glossary" dialog, explaining the status icon colors"""
    def __init__(self, parent=None, config=None):
        super(IconGlossaryDialog, self).__init__(parent)
        widgets.load('iconglossary.ui', self)

        # .. todo:: FIXME: check the window title visibility here
        self.groupBox.setTitle('')

        self.labelPortNumber.setText(_translate(
            "iconGlossaryDialog",
            "You are using TCP port {0}."
            " (This can be changed in the settings)."
        ).format(config.getint('bitmessagesettings', 'port')))
        self.setFixedSize(QtWidgets.QWidget.sizeHint(self))


class HelpDialog(QtWidgets.QDialog):
    """The "Help" dialog"""
    def __init__(self, parent=None):
        super(HelpDialog, self).__init__(parent)
        widgets.load('help.ui', self)
        self.setFixedSize(QtWidgets.QWidget.sizeHint(self))


class ConnectDialog(QtWidgets.QDialog):
    """The "Connect" dialog"""
    def __init__(self, parent=None):
        super(ConnectDialog, self).__init__(parent)
        widgets.load('connect.ui', self)
        self.setFixedSize(QtWidgets.QWidget.sizeHint(self))
