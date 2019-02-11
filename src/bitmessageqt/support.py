"""Composing support request message functions."""

import ctypes
import os
import ssl
import sys
import time

import account
import defaults
import network.stats
import paths
import proofofwork
import queues
import state
from bmconfigparser import BMConfigParser
from foldertree import AccountMixin
from helper_sql import sqlExecute, sqlQuery
from l10n import getTranslationLanguage
from openclpow import openclEnabled
from pyelliptic.openssl import OpenSSL
from settings import getSOCKSProxyType
from tr import _translate
from version import softwareVersion


# this is BM support address going to Peter Surda
OLD_SUPPORT_ADDRESS = 'BM-2cTkCtMYkrSPwFTpgcBrMrf5d8oZwvMZWK'
SUPPORT_ADDRESS = 'BM-2cUdgkDDAahwPAU6oD2A7DnjqZz3hgY832'
SUPPORT_LABEL = _translate("Support", "PyBitmessage support")
SUPPORT_MY_LABEL = _translate("Support", "My new address")
SUPPORT_SUBJECT = _translate("Support", "Support request")
SUPPORT_MESSAGE = _translate("Support", '''
You can use this message to send a report to one of the PyBitmessage core \
developers regarding PyBitmessage or the mailchuck.com email service. \
If you are using PyBitmessage involuntarily, for example because \
your computer was infected with ransomware, this is not an appropriate venue \
for resolving such issues.

Please describe what you are trying to do:

Please describe what you expect to happen:

Please describe what happens instead:


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Please write above this line and if possible, keep the information about your \
environment below intact.

PyBitmessage version: {}
Operating system: {}
Architecture: {}bit
Python Version: {}
OpenSSL Version: {}
Qt API: {}
Frozen: {}
Portable mode: {}
C PoW: {}
OpenCL PoW: {}
Locale: {}
SOCKS: {}
UPnP: {}
Connected hosts: {}
''')


def checkAddressBook(myapp):
    """
    Add "PyBitmessage support" address to address book, remove old one if found.
    """
    sqlExecute('DELETE from addressbook WHERE address=?', OLD_SUPPORT_ADDRESS)
    queryreturn = sqlQuery(
        'SELECT * FROM addressbook WHERE address=?', SUPPORT_ADDRESS)
    if queryreturn == []:
        sqlExecute(
            'INSERT INTO addressbook VALUES (?,?)',
            SUPPORT_LABEL.encode('utf-8'), SUPPORT_ADDRESS)
        myapp.rerenderAddressBook()


def checkHasNormalAddress():
    """Returns first enabled normal address or False if not found."""
    for address in account.getSortedAccounts():
        acct = account.accountClass(address)
        if acct.type == AccountMixin.NORMAL and BMConfigParser().safeGetBoolean(
                address, 'enabled'):
            return address
    return False


def createAddressIfNeeded(myapp):
    """Checks if user has any anabled normal address, creates new one if no."""
    if not checkHasNormalAddress():
        queues.addressGeneratorQueue.put((
            'createRandomAddress', 4, 1,
            SUPPORT_MY_LABEL.encode('utf-8'),
            1, "", False,
            defaults.networkDefaultProofOfWorkNonceTrialsPerByte,
            defaults.networkDefaultPayloadLengthExtraBytes
        ))
    while state.shutdown == 0 and not checkHasNormalAddress():
        time.sleep(.2)
    myapp.rerenderComboBoxSendFrom()
    return checkHasNormalAddress()


def createSupportMessage(myapp):
    """
    Prepare the support request message and switch to tab "Send"
    """
    checkAddressBook(myapp)
    address = createAddressIfNeeded(myapp)
    if state.shutdown:
        return

    myapp.ui.lineEditSubject.setText(SUPPORT_SUBJECT)
    # addrIndex = myapp.ui.comboBoxSendFrom.findData(
    #     address, QtCore.Qt.UserRole,
    #     QtCore.Qt.MatchFixedString | QtCore.Qt.MatchCaseSensitive
    # )
    addrIndex = myapp.ui.comboBoxSendFrom.findData(address)
    if addrIndex == -1:  # something is very wrong
        return
    myapp.ui.comboBoxSendFrom.setCurrentIndex(addrIndex)
    myapp.ui.lineEditTo.setText(SUPPORT_ADDRESS)

    version = softwareVersion
    commit = paths.lastCommit().get('commit')
    if commit:
        version += " GIT " + commit

    if sys.platform.startswith("win"):
        # pylint: disable=no-member
        osname = "Windows %s.%s" % sys.getwindowsversion()[:2]
    else:
        try:
            unixversion = os.uname()
            osname = unixversion[0] + " " + unixversion[2]
        except:
            pass
    architecture = "32" if ctypes.sizeof(ctypes.c_voidp) == 4 else "64"
    pythonversion = sys.version

    opensslversion = "%s (Python internal), %s (external for PyElliptic)" % (
        ssl.OPENSSL_VERSION, OpenSSL._version)

    qtapi = os.environ.get('QT_API', 'fallback')

    frozen = "N/A"
    if paths.frozen:
        frozen = paths.frozen
    portablemode = str(state.appdata == paths.lookupExeFolder())
    cpow = "True" if proofofwork.bmpow else "False"
    openclpow = str(
        BMConfigParser().safeGet('bitmessagesettings', 'opencl')
    ) if openclEnabled() else "None"
    locale = getTranslationLanguage()
    socks = getSOCKSProxyType(BMConfigParser()) or 'N/A'
    upnp = BMConfigParser().safeGet('bitmessagesettings', 'upnp', 'N/A')
    connectedhosts = len(network.stats.connectedHostsList())

    myapp.ui.textEditMessage.setText(SUPPORT_MESSAGE.format(
        version, osname, architecture, pythonversion, opensslversion, qtapi,
        frozen, portablemode, cpow, openclpow, locale, socks, upnp,
        connectedhosts
    ))

    # single msg tab
    myapp.ui.tabWidgetSend.setCurrentIndex(
        myapp.ui.tabWidgetSend.indexOf(myapp.ui.sendDirect)
    )
    # send tab
    myapp.ui.tabWidget.setCurrentIndex(
        myapp.ui.tabWidget.indexOf(myapp.ui.send)
    )
