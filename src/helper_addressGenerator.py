"""
Create random address
"""

import time

import defaults
import queues
import state

from bitmessageqt import account
from bitmessageqt.foldertree import AccountMixin
from bmconfigparser import BMConfigParser


def checkHasNormalAddress():
    """method for checking address"""
    for address in account.getSortedAccounts():
        acct = account.accountClass(address)
        if acct.type == AccountMixin.NORMAL and BMConfigParser().safeGetBoolean(address, 'enabled'):
            return address
    return False


def createAddressIfNeeded(label_text, streamNumberForAddress=1):
    """method for creating random address"""
    if not checkHasNormalAddress():
        queues.addressGeneratorQueue.put((
            'createRandomAddress', 4, streamNumberForAddress,
            label_text,
            1, "", False,
            defaults.networkDefaultProofOfWorkNonceTrialsPerByte,
            defaults.networkDefaultPayloadLengthExtraBytes
        ))
    while state.shutdown == 0 and not checkHasNormalAddress():
        time.sleep(.2)
    return checkHasNormalAddress()
