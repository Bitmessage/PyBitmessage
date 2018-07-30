#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# pylint: disable=too-many-lines,global-statement,too-many-branches,too-many-statements,inconsistent-return-statements
# pylint: disable=too-many-nested-blocks,too-many-locals,protected-access,too-many-arguments,too-many-function-args
# pylint: disable=no-member
"""
Created by Adam Melton (.dok) referenceing https://bitmessage.org/wiki/API_Reference for API documentation
Distributed under the MIT/X11 software license. See http://www.opensource.org/licenses/mit-license.php.

This is an example of a daemon client for PyBitmessage 0.6.2, by .dok (Version 0.3.1) , modified

TODO: fix the following (currently ignored) violations:

"""

import sys
import os

from bmconfigparser import BMConfigParser
try:
    import ConfigParser as ConfigParser
    from urllib import quote
except ImportError:
    import configparser as ConfigParser
    from urllib.parse import quote

keysName = 'keys.dat'
keysPath = 'keys.dat'


def userInput(message):
    """Checks input for exit or quit. Also formats for input, etc"""

    print(message)
    uInput = raw_input('> ')

    return uInput


def lookupAppdataFolder():
    """gets the appropriate folders for the .dat files depending on the OS. Taken from bitmessagemain.py"""

    APPNAME = "PyBitmessage"
    if sys.platform == 'darwin':
        if "HOME" in os.environ:
            dataFolder = os.path.join(os.environ["HOME"], "Library/Application support/", APPNAME) + '/'
        else:
            print(
                '     Could not find home folder, please report '
                'this message and your OS X version to the Daemon Github.')
            sys.exit(1)

    elif 'win32' in sys.platform or 'win64' in sys.platform:
        dataFolder = os.path.join(os.environ['APPDATA'], APPNAME) + '\\'
    else:
        dataFolder = os.path.expanduser(os.path.join("~", ".config/" + APPNAME + "/"))
    return dataFolder


def configInit():
    """Initialised the configuration"""

    BMConfigParser().add_section('bitmessagesettings')
    # Sets the bitmessage port to stop the warning about the api not properly
    # being setup. This is in the event that the keys.dat is in a different
    # directory or is created locally to connect to a machine remotely.
    BMConfigParser().set('bitmessagesettings', 'port', '8444')
    BMConfigParser().set('bitmessagesettings', 'apienabled', 'true')  # Sets apienabled to true in keys.dat

    with open(keysName, 'wb') as configfile:
        BMConfigParser().write(configfile)

    print('     {0} Initalized in the same directory as this CLI.\n' \
            '     You will now need to configure the {0} file.\n'.format(keysName))


def restartBmNotify():
    """Prompt the user to restart Bitmessage"""

    print
    print('     *******************************************************************')
    print('     WARNING: If Bitmessage is running locally, you must restart it now.')
    print('     *******************************************************************\n')


def apiInit(apiEnabled):
    """Initialise the API"""

    global keysPath
    BMConfigParser().read(keysPath)
    isValid = False

    if apiEnabled is False:  # API information there but the api is disabled.
        uInput = userInput('The API is not enabled. Would you like to do that now, (Y)es or (N)o?').lower()

        if uInput == "y":
            BMConfigParser().set('bitmessagesettings', 'apienabled', 'true')  # Sets apienabled to true in keys.dat
            with open(keysPath, 'wb') as configfile:
                BMConfigParser().write(configfile)

            print('Done')
            restartBmNotify()
            isValid = True

        elif uInput == "n":
            print
            print('     ************************************************************')
            print('            Daemon will not work when the API is disabled.       ')
            print('     Please refer to the Bitmessage Wiki on how to setup the API.')
            print('     ************************************************************\n')

        else:
            print('\n     Invalid Entry\n')

    elif apiEnabled:  # API correctly setup
        # Everything is as it should be
        isValid = True

    else:  # API information was not present.
        print('\n     ' + str(keysPath) + ' not properly configured!\n')
        uInput = userInput('Would you like to do this now, (Y)es or (N)o?').lower()

        if uInput == "y":  # User said yes, initalize the api by writing these values to the keys.dat file
            print

            apiUsr = userInput("API Username")
            apiPwd = userInput("API Password")
            apiPort = userInput("API Port")
            apiEnabled = userInput("API Enabled? (True) or (False)").lower()
            daemon = userInput("Daemon mode Enabled? (True) or (False)").lower()

            if (daemon != 'true' and daemon != 'false'):
                print('\n     Invalid Entry for Daemon.\n')

            # sets the bitmessage port to stop the warning about the api not properly
            # being setup. This is in the event that the keys.dat is in a different
            # directory or is created locally to connect to a machine remotely.
            BMConfigParser().set('bitmessagesettings', 'port', '8444')
            BMConfigParser().set('bitmessagesettings', 'apienabled', 'true')
            BMConfigParser().set('bitmessagesettings', 'apiport', apiPort)
            BMConfigParser().set('bitmessagesettings', 'apiinterface', '127.0.0.1')
            BMConfigParser().set('bitmessagesettings', 'apiusername', apiUsr)
            BMConfigParser().set('bitmessagesettings', 'apipassword', apiPwd)
            BMConfigParser().set('bitmessagesettings', 'daemon', daemon)
            with open(keysPath, 'wb') as configfile:
                BMConfigParser().write(configfile)

            print('     Finished configuring the keys.dat file with API information.\n')
            restartBmNotify()
            isValid = True

        elif uInput == "n":
            print
            print('     ***********************************************************')
            print('     Please refer to the Bitmessage Wiki on how to setup the API.')
            print('     ***********************************************************\n')

        else:
            print('     \nInvalid entry\n')

    return isValid


def apiData():
    """TBC"""

    global keysName
    global keysPath

    print('\n     Configure file searching: %s' % os.path.realpath(keysPath))
    BMConfigParser().read(keysPath)  # First try to load the config file (the keys.dat file) from the program directory

    try:
        BMConfigParser().get('bitmessagesettings', 'port')
        appDataFolder = ''
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError) as err:
        pass
        # Could not load the keys.dat file in the program directory. Perhaps it is in the appdata directory.
        appDataFolder = lookupAppdataFolder()
        keysPath = appDataFolder + keysPath
        print('\n     Configure file searching: %s' % os.path.realpath(keysPath))
        BMConfigParser().read(keysPath)

        try:
            BMConfigParser().get('bitmessagesettings', 'port')
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError) as err:
            # keys.dat was not there either, something is wrong.
            print
            print('     *************************************************************')
            print('        WARNING: There was a problem on accessing congfigure file.')
            print('     Make sure that daemon is in the same directory as Bitmessage. ')
            print('     *************************************************************\n')

            finalCheck = False
            uInput = userInput('Would you like to create a "keys.dat" file in current working directory, (Y)es or (N)o?').lower()

            if (uInput == "y" or uInput == "yes"):
                configInit()
                keysPath = keysName
                f = True

            elif (uInput == "n" or uInput == "no"):
                print('\n     Trying Again.\n')

            else:
                print('\n     Invalid Input.\n')

            if not finalCheck:
                return ''

    try:  # checks to make sure that everyting is configured correctly. Excluding apiEnabled, it is checked after
        BMConfigParser().get('bitmessagesettings', 'apiport')
        BMConfigParser().get('bitmessagesettings', 'apiinterface')
        BMConfigParser().get('bitmessagesettings', 'apiusername')
        BMConfigParser().get('bitmessagesettings', 'apipassword')

    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError) as err:
        isValid = apiInit("")  # Initalize the keys.dat file with API information
        if not isValid:
            print('\n      Config file not valid.\n')
            return ''

    # keys.dat file was found or appropriately configured, allow information retrieval
    # apiEnabled =
    # apiInit(BMConfigParser().safeGetBoolean('bitmessagesettings','apienabled'))
    # #if false it will prompt the user, if true it will return true

    BMConfigParser().read(keysPath)  # read again since changes have been made
    apiPort = int(BMConfigParser().get('bitmessagesettings', 'apiport'))
    apiInterface = BMConfigParser().get('bitmessagesettings', 'apiinterface')
    apiUsername = BMConfigParser().get('bitmessagesettings', 'apiusername')
    apiPassword = BMConfigParser().get('bitmessagesettings', 'apipassword')

    ret = "http://" + quote(apiUsername) + ":" + quote(apiPassword) + "@" + apiInterface + ":" + str(apiPort) + "/"
    print('\n     API data successfully imported.')

    # Build the api credentials
    return ret


def bmSettings():
    """Allows the viewing and modification of keys.dat settings."""

    global keysPath
    global usrPrompt

    BMConfigParser().read(keysPath)  # Read the keys.dat
    try:
        print('     Configure file loading: %s' % os.path.realpath(keysPath))
        port = BMConfigParser().get('bitmessagesettings', 'port')
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError) as err:
        print('\n     File not found.\n')
        return ''

    startonlogon = BMConfigParser().safeGetBoolean('bitmessagesettings', 'startonlogon')
    minimizetotray = BMConfigParser().safeGetBoolean('bitmessagesettings', 'minimizetotray')
    showtraynotifications = BMConfigParser().safeGetBoolean('bitmessagesettings', 'showtraynotifications')
    startintray = BMConfigParser().safeGetBoolean('bitmessagesettings', 'startintray')
    defaultnoncetrialsperbyte = BMConfigParser().get('bitmessagesettings', 'defaultnoncetrialsperbyte')
    defaultpayloadlengthextrabytes = BMConfigParser().get('bitmessagesettings', 'defaultpayloadlengthextrabytes')
    daemon = BMConfigParser().safeGetBoolean('bitmessagesettings', 'daemon')

    socksproxytype = BMConfigParser().get('bitmessagesettings', 'socksproxytype')
    sockshostname = BMConfigParser().get('bitmessagesettings', 'sockshostname')
    socksport = BMConfigParser().get('bitmessagesettings', 'socksport')
    socksauthentication = BMConfigParser().safeGetBoolean('bitmessagesettings', 'socksauthentication')
    socksusername = BMConfigParser().get('bitmessagesettings', 'socksusername')
    sockspassword = BMConfigParser().get('bitmessagesettings', 'sockspassword')

    print
    print('     -----------------------------------')
    print('     |   Current Bitmessage Settings   |')
    print('     -----------------------------------')
    print('     port = ' + port)
    print('     startonlogon = ' + str(startonlogon))
    print('     minimizetotray = ' + str(minimizetotray))
    print('     showtraynotifications = ' + str(showtraynotifications))
    print('     startintray = ' + str(startintray))
    print('     defaultnoncetrialsperbyte = ' + defaultnoncetrialsperbyte)
    print('     defaultpayloadlengthextrabytes = ' + defaultpayloadlengthextrabytes)
    print('     daemon = ' + str(daemon))
    print('     ------------------------------------')
    print('     |   Current Connection Settings   |')
    print('     -----------------------------------')
    print('     socksproxytype = ' + socksproxytype)
    print('     sockshostname = ' + sockshostname)
    print('     socksport = ' + socksport)
    print('     socksauthentication = ' + str(socksauthentication))
    print('     socksusername = ' + socksusername)
    print('     sockspassword = ' + sockspassword)
    print

    uInput = userInput('Would you like to modify any of these settings, (n)o or (Y)es?').lower()

    if uInput in ['y', 'yes']:
        while True:  # loops if they mistype the setting name, they can exit the loop with 'exit'
            invalidInput = False
            uInput = userInput('What setting would you like to modify?').lower()
            print

            if uInput == "port":
                print('     Current port number: ' + port)
                uInput = userInput("Input the new port number.")
                BMConfigParser().set('bitmessagesettings', 'port', str(uInput))
            elif uInput == "startonlogon":
                print('     Current status: ' + str(startonlogon))
                uInput = userInput("Input the new status.")
                BMConfigParser().set('bitmessagesettings', 'startonlogon', str(uInput))
            elif uInput == "minimizetotray":
                print('     Current status: ' + str(minimizetotray))
                uInput = userInput("Input the new status.")
                BMConfigParser().set('bitmessagesettings', 'minimizetotray', str(uInput))
            elif uInput == "showtraynotifications":
                print('     Current status: ' + str(showtraynotifications))
                uInput = userInput("Input the new status.")
                BMConfigParser().set('bitmessagesettings', 'showtraynotifications', str(uInput))
            elif uInput == "startintray":
                print('     Current status: ' + str(startintray))
                uInput = userInput("Input the new status.")
                BMConfigParser().set('bitmessagesettings', 'startintray', str(uInput))
            elif uInput == "defaultnoncetrialsperbyte":
                print('     Current default nonce trials per byte: ' + defaultnoncetrialsperbyte)
                uInput = userInput("Input the new defaultnoncetrialsperbyte.")
                BMConfigParser().set('bitmessagesettings', 'defaultnoncetrialsperbyte', str(uInput))
            elif uInput == "defaultpayloadlengthextrabytes":
                print('     Current default payload length extra bytes: ' + defaultpayloadlengthextrabytes)
                uInput = userInput("Input the new defaultpayloadlengthextrabytes.")
                BMConfigParser().set('bitmessagesettings', 'defaultpayloadlengthextrabytes', str(uInput))
            elif uInput == "daemon":
                print('     Current status: ' + str(daemon))
                uInput = userInput("Input the new status.").lower()
                BMConfigParser().set('bitmessagesettings', 'daemon', str(uInput))
            elif uInput == "socksproxytype":
                print('     Current socks proxy type: ' + socksproxytype)
                print("Possibilities: 'none', 'SOCKS4a', 'SOCKS5'.")
                uInput = userInput("Input the new socksproxytype.")
                BMConfigParser().set('bitmessagesettings', 'socksproxytype', str(uInput))
            elif uInput == "sockshostname":
                print('     Current socks host name: ' + sockshostname)
                uInput = userInput("Input the new sockshostname.")
                BMConfigParser().set('bitmessagesettings', 'sockshostname', str(uInput))
            elif uInput == "socksport":
                print('     Current socks port number: ' + socksport)
                uInput = userInput("Input the new socksport.")
                BMConfigParser().set('bitmessagesettings', 'socksport', str(uInput))
            elif uInput == "socksauthentication":
                print('     Current status: ' + str(socksauthentication))
                uInput = userInput("Input the new status.")
                BMConfigParser().set('bitmessagesettings', 'socksauthentication', str(uInput))
            elif uInput == "socksusername":
                print('     Current socks username: ' + socksusername)
                uInput = userInput("Input the new socksusername.")
                BMConfigParser().set('bitmessagesettings', 'socksusername', str(uInput))
            elif uInput == "sockspassword":
                print('     Current socks password: ' + sockspassword)
                uInput = userInput("Input the new password.")
                BMConfigParser().set('bitmessagesettings', 'sockspassword', str(uInput))
            else:
                print("\n     Invalid field. Please try again.\n")
                invalidInput = True

            if invalidInput is not True:  # don't prompt if they made a mistake.
                uInput = userInput("Would you like to change another setting, (n)o or (Y)es?").lower()

                if uInput in ['n', 'no']:
                    with open(keysPath, 'wb') as configfile:
                        src = BMConfigParser().write(configfile)
                    restartBmNotify()
                    break


def main():
    apiData()  # configuration file "keys.dat" searching
    bmSettings()


if __name__ == "__main__":
    main()
