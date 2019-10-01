"""
src/helper_startup.py
=====================

Helper Start performs all the startup operations.
"""
# pylint: disable=too-many-branches,too-many-statements
from __future__ import print_function

import configparser
import os
import platform
import sys
from distutils.version import StrictVersion

import defaults
import helper_random
import paths
import state
from bmconfigparser import BMConfigParser

# The user may de-select Portable Mode in the settings if they want
# the config files to stay in the application data folder.
StoreConfigFilesInSameDirectoryAsProgramByDefault = False


def _loadTrustedPeer():
    trustedPeer = ''
    try:
        trustedPeer = BMConfigParser().get('bitmessagesettings', 'trustedpeer')
    except configparser.Error:
        # This probably means the trusted peer wasn't specified so we
        # can just leave it as None
        return
    try:
        # import pdb;pdb.set_trace()
        if trustedPeer != None:
            host, port = trustedPeer.split(':')
            state.trustedPeer = state.Peer(host, int(port))
    except ValueError:
        sys.exit(
            'Bad trustedpeer config setting! It should be set as'
            ' trustedpeer=<hostname>:<portnumber>'
        )


def loadConfig():
    """Load the config"""
    config = BMConfigParser()

    if state.appdata:
        config.read(state.appdata + 'keys.dat')
        # state.appdata must have been specified as a startup option.
        needToCreateKeysFile = config.safeGet(
            'bitmessagesettings', 'settingsversion') is None
        if not needToCreateKeysFile:
            print(
                'Loading config files from directory specified'
                ' on startup: %s' % state.appdata)
    else:
        config.read(paths.lookupExeFolder() + 'keys.dat')
        try:
            config.get('bitmessagesettings', 'settingsversion')
            print('Loading config files from same directory as program.')
            needToCreateKeysFile = False
            state.appdata = paths.lookupExeFolder()
        except:
            # Could not load the keys.dat file in the program directory.
            # Perhaps it is in the appdata directory.
            state.appdata = paths.lookupAppdataFolder()
            config.read(state.appdata + 'keys.dat')
            needToCreateKeysFile = config.safeGet(
                'bitmessagesettings', 'settingsversion') is None
            if not needToCreateKeysFile:
                print('Loading existing config files from', state.appdata)

    if needToCreateKeysFile:

        # This appears to be the first time running the program; there is
        # no config file (or it cannot be accessed). Create config file.
        config.add_section('bitmessagesettings')
        config.set('bitmessagesettings', 'settingsversion', '10')
        config.set('bitmessagesettings', 'port', '8444')
        config.set('bitmessagesettings', 'timeformat', '%%c')
        config.set('bitmessagesettings', 'blackwhitelist', 'black')
        config.set('bitmessagesettings', 'startonlogon', 'false')
        if 'linux' in sys.platform:
            config.set('bitmessagesettings', 'minimizetotray', 'false')
        # This isn't implimented yet and when True on
        # Ubuntu causes Bitmessage to disappear while
        # running when minimized.
        else:
            config.set('bitmessagesettings', 'minimizetotray', 'true')
        config.set('bitmessagesettings', 'showtraynotifications', 'true')
        config.set('bitmessagesettings', 'startintray', 'false')
        config.set('bitmessagesettings', 'socksproxytype', 'none')
        config.set('bitmessagesettings', 'sockshostname', 'localhost')
        config.set('bitmessagesettings', 'socksport', '9050')
        config.set('bitmessagesettings', 'socksauthentication', 'false')
        config.set('bitmessagesettings', 'socksusername', '')
        config.set('bitmessagesettings', 'sockspassword', '')
        config.set('bitmessagesettings', 'keysencrypted', 'false')
        config.set('bitmessagesettings', 'messagesencrypted', 'false')
        config.set(
            'bitmessagesettings', 'defaultnoncetrialsperbyte',
            str(defaults.networkDefaultProofOfWorkNonceTrialsPerByte))
        config.set(
            'bitmessagesettings', 'defaultpayloadlengthextrabytes',
            str(defaults.networkDefaultPayloadLengthExtraBytes))
        config.set('bitmessagesettings', 'minimizeonclose', 'false')
        config.set('bitmessagesettings', 'dontconnect', 'true')
        config.set('bitmessagesettings', 'replybelow', 'False')
        config.set('bitmessagesettings', 'maxdownloadrate', '0')
        config.set('bitmessagesettings', 'maxuploadrate', '0')

        # UI setting to stop trying to send messages after X days/months
        config.set('bitmessagesettings', 'stopresendingafterxdays', '')
        config.set('bitmessagesettings', 'stopresendingafterxmonths', '')

        # Are you hoping to add a new option to the keys.dat file? You're in
        # the right place for adding it to users who install the software for
        # the first time. But you must also add it to the keys.dat file of
        # existing users. To do that, search the class_sqlThread.py file
        # for the text: "right above this line!"

        if StoreConfigFilesInSameDirectoryAsProgramByDefault:
            # Just use the same directory as the program and forget about
            # the appdata folder
            state.appdata = ''
            print('Creating new config files in same directory as program.')
        else:
            print('Creating new config files in', state.appdata)
            if not os.path.exists(state.appdata):
                os.makedirs(state.appdata)
        if not sys.platform.startswith('win'):
            os.umask(0o077)
        config.save()
    else:
        updateConfig()

    _loadTrustedPeer()

def updateConfig():
    """Save the config"""
    config = BMConfigParser()
    # Used python2.7
    # settingsversion = int(BMConfigParser().get('bitmessagesettings', 'settingsversion') \
    settingsversion = BMConfigParser().safeGetInt('bitmessagesettings', 'settingsvesion')
    if settingsversion == 1:
        config.set('bitmessagesettings', 'socksproxytype', 'none')
        config.set('bitmessagesettings', 'sockshostname', 'localhost')
        config.set('bitmessagesettings', 'socksport', '9050')
        config.set('bitmessagesettings', 'socksauthentication', 'false')
        config.set('bitmessagesettings', 'socksusername', '')
        config.set('bitmessagesettings', 'sockspassword', '')
        config.set('bitmessagesettings', 'sockslisten', 'false')
        config.set('bitmessagesettings', 'keysencrypted', 'false')
        config.set('bitmessagesettings', 'messagesencrypted', 'false')
        settingsversion = 2
    # let class_sqlThread update SQL and continue
    elif settingsversion == 4:
        config.set(
            'bitmessagesettings', 'defaultnoncetrialsperbyte',
            str(defaults.networkDefaultProofOfWorkNonceTrialsPerByte))
        config.set(
            'bitmessagesettings', 'defaultpayloadlengthextrabytes',
            str(defaults.networkDefaultPayloadLengthExtraBytes))
        settingsversion = 5

    if settingsversion == 5:
        config.set(
            'bitmessagesettings', 'maxacceptablenoncetrialsperbyte', '0')
        config.set(
            'bitmessagesettings', 'maxacceptablepayloadlengthextrabytes', '0')
        settingsversion = 7

    if not config.has_option('bitmessagesettings', 'sockslisten'):
        config.set('bitmessagesettings', 'sockslisten', 'false')

    if not config.has_option('bitmessagesettings', 'userlocale'):
        config.set('bitmessagesettings', 'userlocale', 'system')

    if not config.has_option('bitmessagesettings', 'sendoutgoingconnections'):
        config.set('bitmessagesettings', 'sendoutgoingconnections', 'True')

    if not config.has_option('bitmessagesettings', 'useidenticons'):
        config.set('bitmessagesettings', 'useidenticons', 'True')
    if not config.has_option('bitmessagesettings', 'identiconsuffix'):
        # acts as a salt
        config.set(
            'bitmessagesettings', 'identiconsuffix', ''.join(
                helper_random.randomchoice("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
                for x in range(12)
            )
        )  # a twelve character pseudo-password to salt the identicons

    # Add settings to support no longer resending messages after
    # a certain period of time even if we never get an ack
    if settingsversion == 7:
        config.set('bitmessagesettings', 'stopresendingafterxdays', '')
        config.set('bitmessagesettings', 'stopresendingafterxmonths', '')
        settingsversion = 8

    # With the change to protocol version 3, reset the user-settable
    # difficulties to 1
    if settingsversion == 8:
        config.set(
            'bitmessagesettings', 'defaultnoncetrialsperbyte',
            str(defaults.networkDefaultProofOfWorkNonceTrialsPerByte))
        config.set(
            'bitmessagesettings', 'defaultpayloadlengthextrabytes',
            str(defaults.networkDefaultPayloadLengthExtraBytes))
        previousTotalDifficulty = int(
            config.getint(
                'bitmessagesettings', 'maxacceptablenoncetrialsperbyte')
        ) / 320
        previousSmallMessageDifficulty = int(
            config.getint(
                'bitmessagesettings', 'maxacceptablepayloadlengthextrabytes')
        ) / 14000
        config.set(
            'bitmessagesettings', 'maxacceptablenoncetrialsperbyte',
            str(previousTotalDifficulty * 1000))
        config.set(
            'bitmessagesettings', 'maxacceptablepayloadlengthextrabytes',
            str(previousSmallMessageDifficulty * 1000))
        settingsversion = 9

    # Adjust the required POW values for each of this user's addresses
    # to conform to protocol v3 norms.
    if settingsversion == 9:
        for addressInKeysFile in config.addresses():
            try:
                previousTotalDifficulty = float(
                    config.getint(
                        addressInKeysFile, 'noncetrialsperbyte')) / 320
                previousSmallMessageDifficulty = float(
                    config.getint(
                        addressInKeysFile, 'payloadlengthextrabytes')) / 14000
                if previousTotalDifficulty <= 2:
                    previousTotalDifficulty = 1
                if previousSmallMessageDifficulty < 1:
                    previousSmallMessageDifficulty = 1
                config.set(
                    addressInKeysFile, 'noncetrialsperbyte',
                    str(int(previousTotalDifficulty * 1000)))
                config.set(
                    addressInKeysFile, 'payloadlengthextrabytes',
                    str(int(previousSmallMessageDifficulty * 1000)))
            except Exception:
                continue
        config.set('bitmessagesettings', 'maxdownloadrate', '0')
        config.set('bitmessagesettings', 'maxuploadrate', '0')
        settingsversion = 10

    # sanity check
    if config.safeGetInt(
            'bitmessagesettings', 'maxacceptablenoncetrialsperbyte') == 0:
        config.set(
            'bitmessagesettings', 'maxacceptablenoncetrialsperbyte',
            str(defaults.ridiculousDifficulty *
                defaults.networkDefaultProofOfWorkNonceTrialsPerByte)
        )
    if config.safeGetInt('bitmessagesettings', 'maxacceptablepayloadlengthextrabytes') == 0:
        config.set(
            'bitmessagesettings', 'maxacceptablepayloadlengthextrabytes',
            str(defaults.ridiculousDifficulty *
                defaults.networkDefaultPayloadLengthExtraBytes)
        )

    if not config.has_option('bitmessagesettings', 'onionhostname'):
        config.set('bitmessagesettings', 'onionhostname', '')
    if not config.has_option('bitmessagesettings', 'onionport'):
        config.set('bitmessagesettings', 'onionport', '8444')
    if not config.has_option('bitmessagesettings', 'onionbindip'):
        config.set('bitmessagesettings', 'onionbindip', '127.0.0.1')
    if not config.has_option('bitmessagesettings', 'smtpdeliver'):
        config.set('bitmessagesettings', 'smtpdeliver', '')
    if not config.has_option(
            'bitmessagesettings', 'hidetrayconnectionnotifications'):
        config.set(
            'bitmessagesettings', 'hidetrayconnectionnotifications', 'false')
    if config.safeGetInt('bitmessagesettings', 'maxoutboundconnections') < 1:
        config.set('bitmessagesettings', 'maxoutboundconnections', '8')
        print('WARNING: your maximum outbound connections must be a number.')

    # TTL is now user-specifiable. Let's add an option to save
    # whatever the user selects.
    if not config.has_option('bitmessagesettings', 'ttl'):
        config.set('bitmessagesettings', 'ttl', '367200')

    config.set('bitmessagesettings', 'settingsversion', str(settingsversion))
    config.save()


def isOurOperatingSystemLimitedToHavingVeryFewHalfOpenConnections():
    """Check for (mainly XP and Vista) limitations"""
    try:
        if sys.platform[0:3] == "win":
            VER_THIS = StrictVersion(platform.version())
            return (
                StrictVersion("5.1.2600") <= VER_THIS and
                StrictVersion("6.0.6000") >= VER_THIS
            )
        return False
    except Exception:
        pass
