import ctypes
from PyQt4 import QtCore, QtGui
import ssl
import sys
import time

import account
from configparser import BMConfigParser
from debug import logger
from foldertree import AccountMixin
from helper_sql import *
from l10n import getTranslationLanguage
from openclpow import openclAvailable, openclEnabled
import paths
from proofofwork import bmpow
from pyelliptic.openssl import OpenSSL
import shared
import state
from version import softwareVersion

# this is BM support address going to Peter Surda
SUPPORT_ADDRESS = 'BM-2cTkCtMYkrSPwFTpgcBrMrf5d8oZwvMZWK'
SUPPORT_LABEL = 'PyBitmessage support'
SUPPORT_MY_LABEL = 'My new address'
SUPPORT_SUBJECT = 'Support request'
SUPPORT_MESSAGE = '''You can use this message to send a report to one of the PyBitmessage core developers regarding PyBitmessage or the mailchuck.com email service. If you are using PyBitmessage involuntarily, for example because your computer was infected with ransomware, this is not an appropriate venue for resolving such issues.

Please describe what you are trying to do:

Please describe what you expect to happen:

Please describe what happens instead:


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Please write above this line and if possible, keep the information about your environment below intact.

PyBitmessage version: {}
Operating system: {}
Architecture: {}bit
Python Version: {}
OpenSSL Version: {}
Frozen: {}
Portable mode: {}
C PoW: {}
OpenCL PoW: {}
Locale: {}
SOCKS: {}
UPnP: {}
Connected hosts: {}
'''

def checkAddressBook(myapp):
    queryreturn = sqlQuery('''SELECT * FROM addressbook WHERE address=?''', SUPPORT_ADDRESS)
    if queryreturn == []:
        sqlExecute('''INSERT INTO addressbook VALUES (?,?)''', str(QtGui.QApplication.translate("Support", SUPPORT_LABEL)), SUPPORT_ADDRESS)
        myapp.rerenderAddressBook()

def checkHasNormalAddress():
    for address in account.getSortedAccounts():
        acct = account.accountClass(address)
        if acct.type == AccountMixin.NORMAL and BMConfigParser().safeGetBoolean(address, 'enabled'):
            return address
    return False

def createAddressIfNeeded(myapp):
    if not checkHasNormalAddress():
        shared.addressGeneratorQueue.put(('createRandomAddress', 4, 1, str(QtGui.QApplication.translate("Support", SUPPORT_MY_LABEL)), 1, "", False, protocol.networkDefaultProofOfWorkNonceTrialsPerByte, protocol.networkDefaultPayloadLengthExtraBytes))
    while shared.shutdown == 0 and not checkHasNormalAddress():
        time.sleep(.2)
    myapp.rerenderComboBoxSendFrom()
    return checkHasNormalAddress()

def createSupportMessage(myapp):
    checkAddressBook(myapp)
    address = createAddressIfNeeded(myapp)
    if shared.shutdown:
        return

    myapp.ui.lineEditSubject.setText(str(QtGui.QApplication.translate("Support", SUPPORT_SUBJECT)))
    addrIndex = myapp.ui.comboBoxSendFrom.findData(address, QtCore.Qt.UserRole, QtCore.Qt.MatchFixedString | QtCore.Qt.MatchCaseSensitive)
    if addrIndex == -1: # something is very wrong
        return
    myapp.ui.comboBoxSendFrom.setCurrentIndex(addrIndex)
    myapp.ui.lineEditTo.setText(SUPPORT_ADDRESS)
    
    version = softwareVersion
    os = sys.platform
    if os == "win32":
        windowsversion = sys.getwindowsversion()
        os = "Windows " + str(windowsversion[0]) + "." + str(windowsversion[1])
    else:
        try:
            from os import uname
            unixversion = uname()
            os = unixversion[0] + " " + unixversion[2]
        except:
            pass
    architecture = "32" if ctypes.sizeof(ctypes.c_voidp) == 4 else "64"
    pythonversion = sys.version
    
    SSLEAY_VERSION = 0
    OpenSSL._lib.SSLeay.restype = ctypes.c_long
    OpenSSL._lib.SSLeay_version.restype = ctypes.c_char_p
    OpenSSL._lib.SSLeay_version.argtypes = [ctypes.c_int]
    opensslversion = "%s (Python internal), %s (external for PyElliptic)" % (ssl.OPENSSL_VERSION, OpenSSL._lib.SSLeay_version(SSLEAY_VERSION))

    frozen = "N/A"
    if paths.frozen:
        frozen = paths.frozen
    portablemode = "True" if state.appdata == paths.lookupExeFolder() else "False"
    cpow = "True" if bmpow else "False"
    #cpow = QtGui.QApplication.translate("Support", cpow)
    openclpow = str(BMConfigParser().safeGet('bitmessagesettings', 'opencl')) if openclEnabled() else "None"
    #openclpow = QtGui.QApplication.translate("Support", openclpow)
    locale = getTranslationLanguage()
    try:
        socks = BMConfigParser().get('bitmessagesettings', 'socksproxytype')
    except:
        socks = "N/A"
    try:
        upnp = BMConfigParser().get('bitmessagesettings', 'upnp')
    except:
        upnp = "N/A"
    connectedhosts = len(shared.connectedHostsList)

    myapp.ui.textEditMessage.setText(str(QtGui.QApplication.translate("Support", SUPPORT_MESSAGE)).format(version, os, architecture, pythonversion, opensslversion, frozen, portablemode, cpow, openclpow, locale, socks, upnp, connectedhosts))

    # single msg tab
    myapp.ui.tabWidgetSend.setCurrentIndex(0)
    # send tab
    myapp.ui.tabWidget.setCurrentIndex(1)
