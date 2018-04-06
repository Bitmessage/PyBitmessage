import ConfigParser
from bmconfigparser import BMConfigParser
import defaults
import sys
import os
import locale
import random
import string
import platform
from distutils.version import StrictVersion

from namecoin import ensureNamecoinOptions
import paths
import state
import helper_random

storeConfigFilesInSameDirectoryAsProgramByDefault = False  # The user may de-select Portable Mode in the settings if they want the config files to stay in the application data folder.

def _loadTrustedPeer():
    try:
        trustedPeer = BMConfigParser().get('bitmessagesettings', 'trustedpeer')
    except ConfigParser.Error:
        # This probably means the trusted peer wasn't specified so we
        # can just leave it as None
        return

    host, port = trustedPeer.split(':')
    state.trustedPeer = state.Peer(host, int(port))

def loadConfig():
    if state.appdata:
        BMConfigParser().read(state.appdata + 'keys.dat')
        #state.appdata must have been specified as a startup option.
        try:
            BMConfigParser().get('bitmessagesettings', 'settingsversion')
            print 'Loading config files from directory specified on startup: ' + state.appdata
            needToCreateKeysFile = False
        except:
            needToCreateKeysFile = True

    else:
        BMConfigParser().read(paths.lookupExeFolder() + 'keys.dat')
        try:
            BMConfigParser().get('bitmessagesettings', 'settingsversion')
            print 'Loading config files from same directory as program.'
            needToCreateKeysFile = False
            state.appdata = paths.lookupExeFolder()
        except:
            # Could not load the keys.dat file in the program directory. Perhaps it
            # is in the appdata directory.
            state.appdata = paths.lookupAppdataFolder()
            BMConfigParser().read(state.appdata + 'keys.dat')
            try:
                BMConfigParser().get('bitmessagesettings', 'settingsversion')
                print 'Loading existing config files from', state.appdata
                needToCreateKeysFile = False
            except:
                needToCreateKeysFile = True

    if needToCreateKeysFile:
        # This appears to be the first time running the program; there is
        # no config file (or it cannot be accessed). Create config file.
        BMConfigParser().add_section('bitmessagesettings')
        BMConfigParser().set('bitmessagesettings', 'settingsversion', '10')
        BMConfigParser().set('bitmessagesettings', 'port', '8444')
        BMConfigParser().set(
            'bitmessagesettings', 'timeformat', '%%c')
        BMConfigParser().set('bitmessagesettings', 'blackwhitelist', 'black')
        BMConfigParser().set('bitmessagesettings', 'startonlogon', 'false')
        if 'linux' in sys.platform:
            BMConfigParser().set(
                'bitmessagesettings', 'minimizetotray', 'false')
                              # This isn't implimented yet and when True on
                              # Ubuntu causes Bitmessage to disappear while
                              # running when minimized.
        else:
            BMConfigParser().set(
                'bitmessagesettings', 'minimizetotray', 'true')
        BMConfigParser().set(
            'bitmessagesettings', 'showtraynotifications', 'true')
        BMConfigParser().set('bitmessagesettings', 'startintray', 'false')
        BMConfigParser().set('bitmessagesettings', 'socksproxytype', 'none')
        BMConfigParser().set(
            'bitmessagesettings', 'sockshostname', 'localhost')
        BMConfigParser().set('bitmessagesettings', 'socksport', '9050')
        BMConfigParser().set(
            'bitmessagesettings', 'socksauthentication', 'false')
        BMConfigParser().set(
            'bitmessagesettings', 'sockslisten', 'false')
        BMConfigParser().set('bitmessagesettings', 'socksusername', '')
        BMConfigParser().set('bitmessagesettings', 'sockspassword', '')
        BMConfigParser().set('bitmessagesettings', 'keysencrypted', 'false')
        BMConfigParser().set(
            'bitmessagesettings', 'messagesencrypted', 'false')
        BMConfigParser().set('bitmessagesettings', 'defaultnoncetrialsperbyte', str(
            defaults.networkDefaultProofOfWorkNonceTrialsPerByte))
        BMConfigParser().set('bitmessagesettings', 'defaultpayloadlengthextrabytes', str(
            defaults.networkDefaultPayloadLengthExtraBytes))
        BMConfigParser().set('bitmessagesettings', 'minimizeonclose', 'false')
        BMConfigParser().set(
            'bitmessagesettings', 'maxacceptablenoncetrialsperbyte', '0')
        BMConfigParser().set(
            'bitmessagesettings', 'maxacceptablepayloadlengthextrabytes', '0')
        BMConfigParser().set('bitmessagesettings', 'dontconnect', 'true')
        BMConfigParser().set('bitmessagesettings', 'userlocale', 'system')
        BMConfigParser().set('bitmessagesettings', 'useidenticons', 'True')
        BMConfigParser().set('bitmessagesettings', 'identiconsuffix', ''.join(helper_random.randomchoice("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz") for x in range(12)))# a twelve character pseudo-password to salt the identicons
        BMConfigParser().set('bitmessagesettings', 'replybelow', 'False')
        BMConfigParser().set('bitmessagesettings', 'maxdownloadrate', '0')
        BMConfigParser().set('bitmessagesettings', 'maxuploadrate', '0')
        BMConfigParser().set('bitmessagesettings', 'maxoutboundconnections', '8')
        BMConfigParser().set('bitmessagesettings', 'ttl', '367200')
        
         #start:UI setting to stop trying to send messages after X days/months
        BMConfigParser().set(
            'bitmessagesettings', 'stopresendingafterxdays', '')
        BMConfigParser().set(
            'bitmessagesettings', 'stopresendingafterxmonths', '')
        #BMConfigParser().set(
        #    'bitmessagesettings', 'timeperiod', '-1')
        #end

        # Are you hoping to add a new option to the keys.dat file? You're in
        # the right place for adding it to users who install the software for
        # the first time. But you must also add it to the keys.dat file of
        # existing users. To do that, search the class_sqlThread.py file for the
        # text: "right above this line!"

        ensureNamecoinOptions()

        if storeConfigFilesInSameDirectoryAsProgramByDefault:
            # Just use the same directory as the program and forget about
            # the appdata folder
            state.appdata = ''
            print 'Creating new config files in same directory as program.'
        else:
            print 'Creating new config files in', state.appdata
            if not os.path.exists(state.appdata):
                os.makedirs(state.appdata)
        if not sys.platform.startswith('win'):
            os.umask(0o077)
        BMConfigParser().save()

    _loadTrustedPeer()

def isOurOperatingSystemLimitedToHavingVeryFewHalfOpenConnections():
    try:
        if sys.platform[0:3]=="win":
            VER_THIS=StrictVersion(platform.version())
            return StrictVersion("5.1.2600")<=VER_THIS and StrictVersion("6.0.6000")>=VER_THIS
        return False
    except Exception as err:
        return False
