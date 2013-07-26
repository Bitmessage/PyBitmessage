import shared
import ConfigParser
import sys
import os

storeConfigFilesInSameDirectoryAsProgramByDefault = False  # The user may de-select Portable Mode in the settings if they want the config files to stay in the application data folder.

def loadConfig():
    # First try to load the config file (the keys.dat file) from the program
    # directory
    shared.config.read('keys.dat')
    try:
        shared.config.get('bitmessagesettings', 'settingsversion')
        print 'Loading config files from same directory as program'
        shared.appdata = ''
    except:
        # Could not load the keys.dat file in the program directory. Perhaps it
        # is in the appdata directory.
        shared.appdata = shared.lookupAppdataFolder()
        shared.config = ConfigParser.SafeConfigParser()
        shared.config.read(shared.appdata + 'keys.dat')
        try:
            shared.config.get('bitmessagesettings', 'settingsversion')
            print 'Loading existing config files from', shared.appdata
        except:
            # This appears to be the first time running the program; there is
            # no config file (or it cannot be accessed). Create config file.
            shared.config.add_section('bitmessagesettings')
            shared.config.set('bitmessagesettings', 'settingsversion', '6')
            shared.config.set('bitmessagesettings', 'port', '8444')
            shared.config.set(
                'bitmessagesettings', 'timeformat', '%%a, %%d %%b %%Y  %%I:%%M %%p')
            shared.config.set('bitmessagesettings', 'blackwhitelist', 'black')
            shared.config.set('bitmessagesettings', 'startonlogon', 'false')
            if 'linux' in sys.platform:
                shared.config.set(
                    'bitmessagesettings', 'minimizetotray', 'false')
                                  # This isn't implimented yet and when True on
                                  # Ubuntu causes Bitmessage to disappear while
                                  # running when minimized.
            else:
                shared.config.set(
                    'bitmessagesettings', 'minimizetotray', 'true')
            shared.config.set(
                'bitmessagesettings', 'showtraynotifications', 'true')
            shared.config.set('bitmessagesettings', 'startintray', 'false')
            shared.config.set('bitmessagesettings', 'socksproxytype', 'none')
            shared.config.set(
                'bitmessagesettings', 'sockshostname', 'localhost')
            shared.config.set('bitmessagesettings', 'socksport', '9050')
            shared.config.set(
                'bitmessagesettings', 'socksauthentication', 'false')
            shared.config.set(
                'bitmessagesettings', 'sockslisten', 'false')
            shared.config.set('bitmessagesettings', 'socksusername', '')
            shared.config.set('bitmessagesettings', 'sockspassword', '')
            shared.config.set('bitmessagesettings', 'keysencrypted', 'false')
            shared.config.set(
                'bitmessagesettings', 'messagesencrypted', 'false')
            shared.config.set('bitmessagesettings', 'defaultnoncetrialsperbyte', str(
                shared.networkDefaultProofOfWorkNonceTrialsPerByte))
            shared.config.set('bitmessagesettings', 'defaultpayloadlengthextrabytes', str(
                shared.networkDefaultPayloadLengthExtraBytes))
            shared.config.set('bitmessagesettings', 'minimizeonclose', 'false')
            shared.config.set(
                'bitmessagesettings', 'maxacceptablenoncetrialsperbyte', '0')
            shared.config.set(
                'bitmessagesettings', 'maxacceptablepayloadlengthextrabytes', '0')
            shared.config.set('bitmessagesettings', 'dontconnect', 'true')

            if storeConfigFilesInSameDirectoryAsProgramByDefault:
                # Just use the same directory as the program and forget about
                # the appdata folder
                shared.appdata = ''
                print 'Creating new config files in same directory as program.'
            else:
                print 'Creating new config files in', shared.appdata
                if not os.path.exists(shared.appdata):
                    os.makedirs(shared.appdata)
            if not sys.platform.startswith('win'):
                os.umask(0o077)
            with open(shared.appdata + 'keys.dat', 'wb') as configfile:
                shared.config.write(configfile)
