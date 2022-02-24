"""
Startup operations.
"""
# pylint: disable=too-many-branches,too-many-statements

import ctypes
import logging
import os
import platform
import socket
import sys
import time
from distutils.version import StrictVersion
from struct import pack

try:
    import defaults
    import helper_random
    import paths
    import state
    from bmconfigparser import config, config_ready

except ImportError:
    from . import defaults, helper_random, paths, state
    from bmconfigparser import config, config_ready

try:
    from plugins.plugin import get_plugin
except ImportError:
    get_plugin = None


logger = logging.getLogger('default')

# The user may de-select Portable Mode in the settings if they want
# the config files to stay in the application data folder.
StoreConfigFilesInSameDirectoryAsProgramByDefault = False


def loadConfig():
    """Load the config"""
    if state.appdata:
        config.read(state.appdata + 'keys.dat')
        # state.appdata must have been specified as a startup option.
        needToCreateKeysFile = config.safeGet(
            'bitmessagesettings', 'settingsversion') is None
        if not needToCreateKeysFile:
            logger.info(
                'Loading config files from directory specified'
                ' on startup: %s', state.appdata)
    else:
        config.read(paths.lookupExeFolder() + 'keys.dat')

        if config.safeGet('bitmessagesettings', 'settingsversion'):
            logger.info('Loading config files from same directory as program.')
            needToCreateKeysFile = False
            state.appdata = paths.lookupExeFolder()
        else:
            # Could not load the keys.dat file in the program directory.
            # Perhaps it is in the appdata directory.
            state.appdata = paths.lookupAppdataFolder()
            config.read(state.appdata + 'keys.dat')
            needToCreateKeysFile = config.safeGet(
                'bitmessagesettings', 'settingsversion') is None
            if not needToCreateKeysFile:
                logger.info(
                    'Loading existing config files from %s', state.appdata)

    if needToCreateKeysFile:

        # This appears to be the first time running the program; there is
        # no config file (or it cannot be accessed). Create config file.
        # config.add_section('bitmessagesettings')
        config.read()
        config.set('bitmessagesettings', 'settingsversion', '10')
        if 'linux' in sys.platform:
            config.set('bitmessagesettings', 'minimizetotray', 'false')
        # This isn't implimented yet and when True on
        # Ubuntu causes Bitmessage to disappear while
        # running when minimized.
        else:
            config.set('bitmessagesettings', 'minimizetotray', 'true')
        config.set(
            'bitmessagesettings', 'defaultnoncetrialsperbyte',
            str(defaults.networkDefaultProofOfWorkNonceTrialsPerByte))
        config.set(
            'bitmessagesettings', 'defaultpayloadlengthextrabytes',
            str(defaults.networkDefaultPayloadLengthExtraBytes))
        config.set('bitmessagesettings', 'dontconnect', 'true')
        # UI setting to stop trying to send messages after X days/months
        # config.set('bitmessagesettings', 'stopresendingafterxdays', '')
        # config.set('bitmessagesettings', 'stopresendingafterxmonths', '')

        # Are you hoping to add a new option to the keys.dat file? You're in
        # the right place for adding it to users who install the software for
        # the first time. But you must also add it to the keys.dat file of
        # existing users. To do that, search the class_sqlThread.py file
        # for the text: "right above this line!"

        if StoreConfigFilesInSameDirectoryAsProgramByDefault:
            # Just use the same directory as the program and forget about
            # the appdata folder
            state.appdata = ''
            logger.info(
                'Creating new config files in same directory as program.')
        else:
            logger.info('Creating new config files in %s', state.appdata)
            if not os.path.exists(state.appdata):
                os.makedirs(state.appdata)
        if not sys.platform.startswith('win'):
            os.umask(0o077)
        config.save()
    else:
        updateConfig()
    config_ready.set()


def updateConfig():
    """Save the config"""
    settingsversion = config.getint('bitmessagesettings', 'settingsversion')
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
                helper_random.randomchoice(
                    "123456789ABCDEFGHJKLMNPQRSTUVWXYZ"
                    "abcdefghijkmnopqrstuvwxyz") for x in range(12))
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
            str(defaults.ridiculousDifficulty
                * defaults.networkDefaultProofOfWorkNonceTrialsPerByte)
        )
    if config.safeGetInt(
            'bitmessagesettings', 'maxacceptablepayloadlengthextrabytes') == 0:
        config.set(
            'bitmessagesettings', 'maxacceptablepayloadlengthextrabytes',
            str(defaults.ridiculousDifficulty
                * defaults.networkDefaultPayloadLengthExtraBytes)
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
        logger.warning('Your maximum outbound connections must be a number.')

    # TTL is now user-specifiable. Let's add an option to save
    # whatever the user selects.
    if not config.has_option('bitmessagesettings', 'ttl'):
        config.set('bitmessagesettings', 'ttl', '367200')

    config.set('bitmessagesettings', 'settingsversion', str(settingsversion))
    config.save()


def adjustHalfOpenConnectionsLimit():
    """Check and satisfy half-open connections limit (mainly XP and Vista)"""
    if config.safeGet(
            'bitmessagesettings', 'socksproxytype', 'none') != 'none':
        state.maximumNumberOfHalfOpenConnections = 4
        return

    is_limited = False
    try:
        if sys.platform[0:3] == "win":
            # Some XP and Vista systems can only have 10 outgoing
            # connections at a time.
            VER_THIS = StrictVersion(platform.version())
            is_limited = (
                StrictVersion("5.1.2600") <= VER_THIS
                and StrictVersion("6.0.6000") >= VER_THIS
            )
    except ValueError:
        pass

    state.maximumNumberOfHalfOpenConnections = 9 if is_limited else 64


def fixSocket():
    """Add missing socket options and methods mainly on Windows"""
    if sys.platform.startswith('linux'):
        socket.SO_BINDTODEVICE = 25

    if not sys.platform.startswith('win'):
        return

    # Python 2 on Windows doesn't define a wrapper for
    # socket.inet_ntop but we can make one ourselves using ctypes
    if not hasattr(socket, 'inet_ntop'):
        addressToString = ctypes.windll.ws2_32.WSAAddressToStringA

        def inet_ntop(family, host):
            """Converting an IP address in packed
            binary format to string format"""
            if family == socket.AF_INET:
                if len(host) != 4:
                    raise ValueError("invalid IPv4 host")
                host = pack("hH4s8s", socket.AF_INET, 0, host, "\0" * 8)
            elif family == socket.AF_INET6:
                if len(host) != 16:
                    raise ValueError("invalid IPv6 host")
                host = pack("hHL16sL", socket.AF_INET6, 0, 0, host, 0)
            else:
                raise ValueError("invalid address family")
            buf = "\0" * 64
            lengthBuf = pack("I", len(buf))
            addressToString(host, len(host), None, buf, lengthBuf)
            return buf[0:buf.index("\0")]
        socket.inet_ntop = inet_ntop

    # Same for inet_pton
    if not hasattr(socket, 'inet_pton'):
        stringToAddress = ctypes.windll.ws2_32.WSAStringToAddressA

        def inet_pton(family, host):
            """Converting an IP address in string format
            to a packed binary format"""
            buf = "\0" * 28
            lengthBuf = pack("I", len(buf))
            if stringToAddress(str(host),
                               int(family),
                               None,
                               buf,
                               lengthBuf) != 0:
                raise socket.error("illegal IP address passed to inet_pton")
            if family == socket.AF_INET:
                return buf[4:8]
            elif family == socket.AF_INET6:
                return buf[8:24]
            else:
                raise ValueError("invalid address family")
        socket.inet_pton = inet_pton

    # These sockopts are needed on for IPv6 support
    if not hasattr(socket, 'IPPROTO_IPV6'):
        socket.IPPROTO_IPV6 = 41
    if not hasattr(socket, 'IPV6_V6ONLY'):
        socket.IPV6_V6ONLY = 27


def start_proxyconfig():
    """Check socksproxytype and start any proxy configuration plugin"""
    if not get_plugin:
        return
    config_ready.wait()
    proxy_type = config.safeGet('bitmessagesettings', 'socksproxytype')
    if proxy_type and proxy_type not in ('none', 'SOCKS4a', 'SOCKS5'):
        try:
            proxyconfig_start = time.time()
            if not get_plugin('proxyconfig', name=proxy_type)(config):
                raise TypeError()
        except TypeError:
            # cannot import shutdown here ):
            logger.error(
                'Failed to run proxy config plugin %s',
                proxy_type, exc_info=True)
            config.setTemp('bitmessagesettings', 'dontconnect', 'true')
        else:
            logger.info(
                'Started proxy config plugin %s in %s sec',
                proxy_type, time.time() - proxyconfig_start)
