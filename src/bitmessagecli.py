#!/usr/bin/env python2.7.x
# Created by Adam Melton (.dok) referenceing https://bitmessage.org/wiki/API_Reference for API documentation
# Distributed under the MIT/X11 software license. See http://www.opensource.org/licenses/mit-license.php.

# This is an example of a daemon client for PyBitmessage 0.4.2, by .dok (Version 0.3.0)


import ConfigParser
import xmlrpclib
import datetime
import hashlib
import getopt
import imghdr
import ntpath
import json
import time
import sys
import os

api = ''
keysName = 'keys.dat'
keysPath = 'keys.dat'
usrPrompt = 0  # 0 = First Start, 1 = prompt, 2 = no prompt if the program is starting up
knownAddresses = dict()


def userInput(message):  # Checks input for exit or quit. Also formats for input, etc
    global usrPrompt
    print('\n' + message)
    uInput = raw_input('> ')

    if (uInput.lower() == 'exit'):  # Returns the user to the main menu
        usrPrompt = 1
        main()
    elif (uInput.lower() == 'quit'):  # Quits the program
        print('\n\tBye\n')
        sys.exit()
        os.exit()
    else:
        return uInput


def restartBmNotify():  # Prompts the user to restart Bitmessage.
    print('\n\t*******************************************************************')
    print('\tWARNING: If Bitmessage is running locally, you must restart it now.')
    print('\t*******************************************************************\n')


def safeConfigGetBoolean(section, field):
    global keysPath
    config = ConfigParser.SafeConfigParser()
    config.read(keysPath)

    try:
        return config.getboolean(section, field)
    except:
        return False


# Begin keys.dat interactions
def lookupAppdataFolder():  # gets the appropriate folders for the .dat files depending on the OS. Taken from bitmessagemain.py
    APPNAME = "PyBitmessage"
    from os import path, environ
    if sys.platform == 'darwin':
        if "HOME" in environ:
            dataFolder = path.join(os.environ["HOME"], "Library/Application support/", APPNAME) + '/'
        else:
            print('\tCould not find home folder, please report this message and your OS X version to the Github Issue Tracker.')
            os.exit()

    elif 'win32' in sys.platform or 'win64' in sys.platform:
        dataFolder = path.join(environ['APPDATA'], APPNAME) + '\\'
    else:
        dataFolder = path.expanduser(path.join("~", ".config/" + APPNAME + "/"))
    return dataFolder


def configInit():
    global keysName
    config = ConfigParser.SafeConfigParser()

    config.add_section('bitmessagesettings')
    config.set('bitmessagesettings', 'port', '8444')  # Sets the bitmessage port to stop the warning about the api not properly being setup. This is in the event that the keys.dat is in a different directory or is created locally to connect to a machine remotely.
    config.set('bitmessagesettings', 'apienabled', 'true')  # Sets apienabled to true in keys.dat

    with open(keysName, 'wb') as configfile:
        config.write(configfile)

    print('\n\t', str(keysName), 'Initalized in the same directory as daemon.py')
    print('\tYou will now need to configure the', str(keysName), 'file.\n')


def apiInit(apiEnabled):
    global keysPath
    global usrPrompt
    config = ConfigParser.SafeConfigParser()
    config.read(keysPath)

    if apiEnabled is False:  # API information is there but the api is disabled.
        uInput = userInput("The API is not enabled. Would you like to do that now, (Y)es or (N)o?").lower()
        if uInput == "y":
            config.set('bitmessagesettings', 'apienabled', 'true')  # Sets apienabled to true in keys.dat
            with open(keysPath, 'wb') as configfile:
                config.write(configfile)

            print 'Done'
            restartBmNotify()
            return True

        elif uInput == "n":
            print('\n\t************************************************************')
            print('\t       Daemon will not work when the API is disabled.       ')
            print('\tPlease refer to the Bitmessage Wiki on how to setup the API.')
            print('\t************************************************************\n')
            usrPrompt = 1
            main()

        else:
            print('\n\tInvalid Entry\n')
            usrPrompt = 1
            main()
    elif apiEnabled is True:  # API correctly setup
        # Everything is as it should be
        return True

    else:  # API information was not present.
        print('\n\t', str(keysPath), 'not properly configured!\n')
        uInput = userInput("Would you like to do this now, (Y)es or (N)o?").lower()

        if uInput == "y":  # User said yes, initalize the api by writing these values to the keys.dat file
            print(' ')
            apiUsr = userInput("API Username")
            apiPwd = userInput("API Password")
            # TODO: Unused var apiInterface
            apiInterface = userInput("API Interface. (127.0.0.1)")
            apiPort = userInput("API Port")
            apiEnabled = userInput("API Enabled? (True) or (False)").lower()
            daemon = userInput("Daemon mode Enabled? (True) or (False)").lower()

            if (daemon != 'true' and daemon != 'false'):
                print('\n\tInvalid Entry for Daemon.\n')
                uInput = 1
                main()

            print('\t-----------------------------------\n')

            config.set('bitmessagesettings', 'port', '8444')  # Sets the bitmessage port to stop the warning about the api not properly being setup. This is in the event that the keys.dat is in a different directory or is created locally to connect to a machine remotely.
            config.set('bitmessagesettings', 'apienabled', 'true')
            config.set('bitmessagesettings', 'apiport', apiPort)
            config.set('bitmessagesettings', 'apiinterface', '127.0.0.1')
            config.set('bitmessagesettings', 'apiusername', apiUsr)
            config.set('bitmessagesettings', 'apipassword', apiPwd)
            config.set('bitmessagesettings', 'daemon', daemon)
            with open(keysPath, 'wb') as configfile:
                config.write(configfile)

            print('\n\tFinished configuring the keys.dat file with API information.\n')
            restartBmNotify()
            return True

        elif uInput == "n":
            print('\n\t***********************************************************')
            print('\tPlease refer to the Bitmessage Wiki on how to setup the API.')
            print('\t***********************************************************\n')
            usrPrompt = 1
            main()
        else:
            print('\n\tInvalid entry\n')
            usrPrompt = 1
            main()


def apiData():
    global keysName
    global keysPath
    global usrPrompt

    config = ConfigParser.SafeConfigParser()
    config.read(keysPath)  # First try to load the config file (the keys.dat file) from the program directory

    try:
        config.get('bitmessagesettings', 'port')
        appDataFolder = ''
    except:
        # Could not load the keys.dat file in the program directory. Perhaps it is in the appdata directory.
        appDataFolder = lookupAppdataFolder()
        keysPath = appDataFolder + keysPath
        config = ConfigParser.SafeConfigParser()
        config.read(keysPath)

        try:
            config.get('bitmessagesettings', 'port')
        except:
            #keys.dat was not there either, something is wrong.
            print('\n\t******************************************************************')
            print('\tThere was a problem trying to access the Bitmessage keys.dat file')
            print('\t               or keys.dat is not set up correctly')
            print('\t  Make sure that daemon is in the same directory as Bitmessage. ')
            print('\t******************************************************************\n')

            uInput = userInput("Would you like to create a keys.dat in the local directory, (Y)es or (N)o?").lower()

            if (uInput == "y" or uInput == "yes"):
                configInit()
                keysPath = keysName
                usrPrompt = 0
                main()
            elif (uInput == "n" or uInput == "no"):
                print('\n\tTrying Again.\n')
                usrPrompt = 0
                main()
            else:
                print('\n\tInvalid Input.\n')

            usrPrompt = 1
            main()

    try:  # Checks to make sure that everyting is configured correctly. Excluding apiEnabled, it is checked after
        config.get('bitmessagesettings', 'apiport')
        config.get('bitmessagesettings', 'apiinterface')
        config.get('bitmessagesettings', 'apiusername')
        config.get('bitmessagesettings', 'apipassword')
    except:
        apiInit("")  # Initalize the keys.dat file with API information

    # keys.dat file was found or appropriately configured, allow information retrieval
    # TODO: Unused var apiEnabled
    apiEnabled = apiInit(safeConfigGetBoolean('bitmessagesettings', 'apienabled'))  # If false it will prompt the user, if true it will return true

    config.read(keysPath)  # Read again since changes have been made
    apiPort = int(config.get('bitmessagesettings', 'apiport'))
    apiInterface = config.get('bitmessagesettings', 'apiinterface')
    apiUsername = config.get('bitmessagesettings', 'apiusername')
    apiPassword = config.get('bitmessagesettings', 'apipassword')

    print('\n\tAPI data successfully imported.\n')

    return "http://" + apiUsername + ":" + apiPassword + "@" + apiInterface + ":" + str(apiPort) + "/"  # Build the api credentials

# End keys.dat interactions


def apiTest():  # Tests the API connection to bitmessage. Returns true if it is connected.

    try:
        result = api.add(2, 3)
    except:
        return False

    if (result == 5):
        return True
    else:
        return False


def bmSettings():  # Allows the viewing and modification of keys.dat settings. 
    global keysPath
    global usrPrompt
    config = ConfigParser.SafeConfigParser()
    keysPath = 'keys.dat'

    config.read(keysPath)  # Read the keys.dat
    try:
        port = config.get('bitmessagesettings', 'port')
    except:
        print('\n\tFile not found.\n')
        usrPrompt = 0
        main()

    startonlogon = safeConfigGetBoolean('bitmessagesettings', 'startonlogon')
    minimizetotray = safeConfigGetBoolean('bitmessagesettings', 'minimizetotray')
    showtraynotifications = safeConfigGetBoolean('bitmessagesettings', 'showtraynotifications')
    startintray = safeConfigGetBoolean('bitmessagesettings', 'startintray')
    defaultnoncetrialsperbyte = config.get('bitmessagesettings', 'defaultnoncetrialsperbyte')
    defaultpayloadlengthextrabytes = config.get('bitmessagesettings', 'defaultpayloadlengthextrabytes')
    daemon = safeConfigGetBoolean('bitmessagesettings', 'daemon')

    socksproxytype = config.get('bitmessagesettings', 'socksproxytype')
    sockshostname = config.get('bitmessagesettings', 'sockshostname')
    socksport = config.get('bitmessagesettings', 'socksport')
    socksauthentication = safeConfigGetBoolean('bitmessagesettings', 'socksauthentication')
    socksusername = config.get('bitmessagesettings', 'socksusername')
    sockspassword = config.get('bitmessagesettings', 'sockspassword')


    print('\n\t-----------------------------------')
    print('\t|   Current Bitmessage Settings   |')
    print('\t-----------------------------------')
    print('\tport = ' + port)
    print('\tstartonlogon = ' + str(startonlogon))
    print('\tminimizetotray = ' + str(minimizetotray))
    print('\tshowtraynotifications = ' + str(showtraynotifications))
    print('\tstartintray = ' + str(startintray))
    print('\tdefaultnoncetrialsperbyte = ' + defaultnoncetrialsperbyte)
    print('\tdefaultpayloadlengthextrabytes = ' + defaultpayloadlengthextrabytes)
    print('\tdaemon = ' + str(daemon))
    print('\n\t------------------------------------')
    print('\t|   Current Connection Settings   |')
    print('\t-----------------------------------')
    print('\tsocksproxytype = ' + socksproxytype)
    print('\tsockshostname = ' + sockshostname)
    print('\tsocksport = ' + socksport)
    print('\tsocksauthentication = ' + str(socksauthentication))
    print('\tsocksusername = ' + socksusername)
    print('\tsockspassword = ' + sockspassword)
    print(' ')

    uInput = userInput("Would you like to modify any of these settings, (Y)es or (N)o?").lower()

    if uInput == "y":
        while True:  # Loops if they mistype the setting name, they can exit the loop with 'exit'
            invalidInput = False
            uInput = userInput("What setting would you like to modify?").lower()
            print('\n')

            if uInput == "port":
                print('\tCurrent port number: ' + port)
                uInput = userInput("Enter the new port number.")
                config.set('bitmessagesettings', 'port', str(uInput))
            elif uInput == "startonlogon":
                print('\tCurrent status: ' + str(startonlogon))
                uInput = userInput("Enter the new status.")
                config.set('bitmessagesettings', 'startonlogon', str(uInput))
            elif uInput == "minimizetotray":
                print('\tCurrent status: ' + str(minimizetotray))
                uInput = userInput("Enter the new status.")
                config.set('bitmessagesettings', 'minimizetotray', str(uInput))
            elif uInput == "showtraynotifications":
                print('\tCurrent status: ' + str(showtraynotifications))
                uInput = userInput("Enter the new status.")
                config.set('bitmessagesettings', 'showtraynotifications', str(uInput))
            elif uInput == "startintray":
                print('\tCurrent status: ' + str(startintray))
                uInput = userInput("Enter the new status.")
                config.set('bitmessagesettings', 'startintray', str(uInput))
            elif uInput == "defaultnoncetrialsperbyte":
                print('\tCurrent default nonce trials per byte: ' + defaultnoncetrialsperbyte)
                uInput = userInput("Enter the new defaultnoncetrialsperbyte.")
                config.set('bitmessagesettings', 'defaultnoncetrialsperbyte', str(uInput))
            elif uInput == "defaultpayloadlengthextrabytes":
                print('\tCurrent default payload length extra bytes: ' + defaultpayloadlengthextrabytes)
                uInput = userInput("Enter the new defaultpayloadlengthextrabytes.")
                config.set('bitmessagesettings', 'defaultpayloadlengthextrabytes', str(uInput))
            elif uInput == "daemon":
                print('\tCurrent status: ' + str(daemon))
                uInput = userInput("Enter the new status.").lower()
                config.set('bitmessagesettings', 'daemon', str(uInput))
            elif uInput == "socksproxytype":
                print('\tCurrent socks proxy type: ' + socksproxytype)
                print "Possibilities: 'none', 'SOCKS4a', 'SOCKS5'."
                uInput = userInput("Enter the new socksproxytype.")
                config.set('bitmessagesettings', 'socksproxytype', str(uInput))
            elif uInput == "sockshostname":
                print('\tCurrent socks host name: ' + sockshostname)
                uInput = userInput("Enter the new sockshostname.")
                config.set('bitmessagesettings', 'sockshostname', str(uInput))
            elif uInput == "socksport":
                print('\tCurrent socks port number: ' + socksport)
                uInput = userInput("Enter the new socksport.")
                config.set('bitmessagesettings', 'socksport', str(uInput))
            elif uInput == "socksauthentication":
                print('\tCurrent status: ' + str(socksauthentication))
                uInput = userInput("Enter the new status.")
                config.set('bitmessagesettings', 'socksauthentication', str(uInput))
            elif uInput == "socksusername":
                print('\tCurrent socks username: ' + socksusername)
                uInput = userInput("Enter the new socksusername.")
                config.set('bitmessagesettings', 'socksusername', str(uInput))
            elif uInput == "sockspassword":
                print('\tCurrent socks password: ' + sockspassword)
                uInput = userInput("Enter the new password.")
                config.set('bitmessagesettings', 'sockspassword', str(uInput))
            else:
                print('\n\tInvalid input. Please try again.\n')
                invalidInput = True

            if invalidInput is not True:  # Don't prompt if they made a mistake.
                uInput = userInput("Would you like to change another setting, (Y)es or (N)o?").lower()

                if uInput != "y":
                    print('\n\tChanges Made.\n')
                    with open(keysPath, 'wb') as configfile:
                        config.write(configfile)
                    restartBmNotify()
                    break

    elif uInput == "n":
        usrPrompt = 1
        main()
    else:
        print "Invalid input."
        usrPrompt = 1
        main()


def validAddress(address):
    address_information = api.decodeAddress(address)
    address_information = eval(address_information)

    if 'success' in str(address_information.get('status')).lower():
        return True
    else:
        return False


def getAddress(passphrase, vNumber, sNumber):
    passphrase = passphrase.encode('base64')  # Passphrase must be encoded
    return api.getDeterministicAddress(passphrase, vNumber, sNumber)


def subscribe():
    global usrPrompt

    while True:
        address = userInput("What address would you like to subscribe to?")

        if (address == "c"):
                usrPrompt = 1
                print('\n')
                main()
        elif validAddress(address) is False:
            print '\n\tInvalid. "c" to cancel. Please try again.\n'
        else:
            break

    label = userInput("Enter a label for this address.")
    label = label.encode('base64')

    api.addSubscription(address, label)
    print('\n\tYou are now subscribed to: ' + address + '\n')


def unsubscribe():
    global usrPrompt

    while True:
        address = userInput("What address would you like to unsubscribe from?")

        if (address == "c"):
                usrPrompt = 1
                print('\n')
                main()
        elif validAddress(address) is False:
            print('\n\tInvalid. "c" to cancel. Please try again.\n')
        else:
            break

    uInput = userInput("Are you sure, (Y)es or (N)o?").lower()

    if uInput is 'y':
        api.deleteSubscription(address)
        print('\n\tYou are now unsubscribed from: ' + address + '\n')
    else:
        print('\n\tOperation canceled.\n')


def listSubscriptions():
    global usrPrompt
    #jsonAddresses = json.loads(api.listSubscriptions())
    #numAddresses = len(jsonAddresses['addresses'])  # Number of addresses
    print('\nLabel, Address, Enabled\n')
    try:
        print api.listSubscriptions()
    except:
        print('\n\tConnection Error\n')
        usrPrompt = 0
        main()

    '''for addNum in range (0, numAddresses):  # processes all of the addresses and lists them out
        label = jsonAddresses['addresses'][addNum]['label']
        address = jsonAddresses['addresses'][addNum]['address']
        enabled = jsonAddresses['addresses'][addNum]['enabled']

        print(label, address, enabled)
    '''
    print('\n')


def createChan():
    global usrPrompt
    password = userInput("Enter channel name")
    password = password.encode('base64')
    try:
        print(api.createChan(password))
    except:
        print('\n\tConnection Error\n')
        usrPrompt = 0
        main()


def joinChan():
    global usrPrompt
    while True:
        address = userInput("Enter channel address")

        if (address == "c"):
                usrPrompt = 1
                print('\n')
                main()
        elif validAddress(address) is False:
            print('\n\tInvalid. Press "c" to cancel. Please try again.\n')
        else:
            break

    password = userInput("Enter channel name")
    password = password.encode('base64')
    try:
        print(api.joinChan(password, address))
    except:
        print('\n\tConnection Error\n')
        usrPrompt = 0
        main()


def leaveChan():
    global usrPrompt
    while True:
        address = userInput("Enter channel address")
        if (address == "c"):
                usrPrompt = 1
                print('\n')
                main()
        elif validAddress(address) is False:
            print('\n\tnvalid. Press "c" to cancel. Please try again.\n')
        else:
            break

    try:
        print(api.leaveChan(address))
    except:
        print('\n\tConnection Error\n')
        usrPrompt = 0
        main()


def listAdd():  # Lists all of the addresses and their info
    global usrPrompt
    try:
        jsonAddresses = json.loads(api.listAddresses())
        numAddresses = len(jsonAddresses['addresses'])  # Number of addresses
    except:
        print('\n\tConnection Error\n')
        usrPrompt = 0
        main()

    #print '\nAddress Number,Label,Address,Stream,Enabled\n'
    print('\n\t--------------------------------------------------------------------------')
    print('\t| # |       Label       |               Address               |S#|Enabled|')
    print('\t|---|-------------------|-------------------------------------|--|-------|')

    for addNum in range (0, numAddresses):  # Processes all of the addresses and lists them out
        label = str(jsonAddresses['addresses'][addNum]['label'])
        address = str(jsonAddresses['addresses'][addNum]['address'])
        stream = str(jsonAddresses['addresses'][addNum]['stream'])
        enabled = str(jsonAddresses['addresses'][addNum]['enabled'])

        if (len(label) > 19):
            label = label[:16] + '...'

        print('\t|' + str(addNum).ljust(3) + '|' + label.ljust(19) +
              '|' + address.ljust(37) + '|' + stream.ljust(1), '|' +
              enabled.ljust(7) + '|')
    print('\t--------------------------------------------------------------------------\n')


def genAdd(lbl, deterministic, passphrase, numOfAdd, addVNum, streamNum, ripe):  # Generate address
    global usrPrompt
    if deterministic is False:  # Generates a new address with the user defined label. non-deterministic
        addressLabel = lbl.encode('base64')
        try:
            generatedAddress = api.createRandomAddress(addressLabel)
        except:
            print('\n\tConnection Error\n')
            usrPrompt = 0
            main()

        return generatedAddress

    elif deterministic is True:  # Generates a new deterministic address with the user inputs.
        passphrase = passphrase.encode('base64')
        try:
            generatedAddress = api.createDeterministicAddresses(passphrase, numOfAdd, addVNum, streamNum, ripe)
        except:
            print('\n\tConnection Error\n')
            usrPrompt = 0
            main()
        return generatedAddress
    else:
        return 'Entry Error'


def delMilAddr():  # Generate address
    global usrPrompt
    try:
        response = api.listAddresses2()
        # If API is too old just return then fail
        if "API Error 0020" in response:
            return 1
        addresses = json.loads(response)
        for entry in addresses['addresses']:
            if entry['label'].decode('base64')[:6] == "random":
                api.deleteAddress(entry['address'])
    except:
        print('\n\tConnection Error\n')
        usrPrompt = 0
        main()


def genMilAddr():  # Generate address
    global usrPrompt
    maxn = 0
    try:
        response = api.listAddresses2()
        if "API Error 0020" in response:
            return 1
        addresses = json.loads(response)
        for entry in addresses['addresses']:
            if entry['label'].decode('base64')[:6] == "random":
                newn = int(entry['label'].decode('base64')[6:])
                if maxn < newn:
                    maxn = newn
    except:
        print('\n\tSome error\n')
    print('\n\tStarting at ' + str(maxn) + '\n')

    for i in range(maxn, 10000):
        lbl = "random" + str(i)
        addressLabel = lbl.encode('base64')
        try:
            generatedAddress = api.createRandomAddress(addressLabel)
        except:
            print('\n\tConnection Error\n')
            usrPrompt = 0
            main()

def saveFile(fileName, fileData):  # Allows attachments and messages/broadcats to be saved

    # This section finds all invalid characters and replaces them with ~
    fileName = fileName.replace(" ", "")
    fileName = fileName.replace("/", "~")
    fileName = fileName.replace("\\\\", "~")
    fileName = fileName.replace(":", "~")
    fileName = fileName.replace("*", "~")
    fileName = fileName.replace("?", "~")
    fileName = fileName.replace('"', "~")
    fileName = fileName.replace("<", "~")
    fileName = fileName.replace(">", "~")
    fileName = fileName.replace("|", "~")

    directory = 'attachments'

    if not os.path.exists(directory):
        os.makedirs(directory)

    filePath = directory + '/' + fileName

    '''try:  # Checks if file already exists
        with open(filePath):
            print 'File Already Exists'
            return
    except IOError: pass'''

    f = open(filePath, 'wb+')
    f.write(fileData.decode("base64"))
    f.close

    print('\n\tSuccessfully saved ' + filePath + '\n')


def attachment():  # Allows users to attach a file to their message or broadcast
    theAttachmentS = ''
    while True:
        isImage = False
        theAttachment = ''

        while True:  # Loops until valid path is entered
            filePath = userInput('\nPlease enter the path to the attachment or just the attachment name if in this folder.')  

            try:
                with open(filePath):
                    break
            except IOError:
                print('\n\t%s was not found on your filesystem or can not be opened.\n' % filePath)
                pass

        # Print filesize and encoding estimate with confirmation if file is over X size (1mb?)
        invSize = os.path.getsize(filePath)
        invSize = (invSize / 1024)  # Converts to kB
        round(invSize, 2)  # Rounds to two decimal places

        if (invSize > 500.0):  # If over 500kB
            print('\n\tWARNING:The file that you are trying to attach is ', invSize, 'KB and will take considerable time to send.\n')
            uInput = userInput('Are you sure you still want to attach it, (Y)es or (N)o?').lower()

            if uInput != 'y':
                print('\n\tAttachment discarded.\n')
                return ''
        elif (invSize > 184320.0):  # If larger than 180MB, automatically discard.
            print('\n\tAttachment too big. Maximum allowed size: 180MB\n')
            main()

        pathLen = len(str(ntpath.basename(filePath)))  # Gets the length of the filepath excluding the filename
        fileName = filePath[(len(str(filePath)) - pathLen):]  # Reads the filename

        filetype = imghdr.what(filePath)  # Tests if it is an image file
        if filetype is not None:
            print('\n\t---------------------------------------------------')
            print('\tAttachment detected as an image.')
            print('\t<img> tags will automatically be included,')
            print('\tallowing the recipient to view the image')
            print('\tusing the "View HTML code..." option in Bitmessage.')
            print('\t---------------------------------------------------\n')
            isImage = True
            time.sleep(2)

        print('\n\tEncoding Attachment, Please Wait ...\n')  # Alert the user that the encoding process may take some time.

        with open(filePath, 'rb') as f:  # Begin the actual encoding
            data = f.read(188743680)  # Reads files up to 180MB, the maximum size for Bitmessage.
            data = data.encode("base64")

        if (isImage == True):  # If it is an image, include image tags in the message
            theAttachment = """
<!-- Note: Image attachment below. Please use the right click "View HTML code ..." option to view it. -->
<!-- Sent using Bitmessage CLI Daemon. https://github.com/Dokument/PyBitmessage-Daemon -->

Filename:%s 
Filesize:%sKB 
Encoding:base64 

<center>
    <div id="image">
        <img alt = "%s" src='data:image/%s;base64, %s' />
    </div>
</center>""" % (fileName, invSize, fileName, filetype, data)
        else:  # It is not an image, so do not include the embedded image code.
            theAttachment = """
<!-- Note: File attachment below. Please use a base64 decoder, or Daemon, to save it. -->
<!-- Sent using Bitmessage CLI Daemon. https://github.com/Dokument/PyBitmessage-Daemon -->

Filename:%s 
Filesize:%sKB 
Encoding:base64 

<attachment alt = "%s" src='data:file/%s;base64, %s' />""" % (fileName,invSize,fileName,fileName,data)

        uInput = userInput('Would you like to add another attachment, (Y)es or (N)o?').lower()
        if (uInput == 'y' or uInput == 'yes'):  # Allows multiple attachments to be added to one message
            theAttachmentS = str(theAttachmentS) + str(theAttachment) + '\n\n'
        elif (uInput == 'n' or uInput == 'no'):
            break

    theAttachmentS = theAttachmentS + theAttachment
    return theAttachmentS


def sendMsg(toAddress, fromAddress, subject, message):  # With no arguments sent, sendMsg fills in the blanks. subject and message must be encoded before they are passed.
    global usrPrompt
    if validAddress(toAddress) is False:
        while True:
            toAddress = userInput("What is the To Address?")
            if (toAddress == "c"):
                usrPrompt = 1
                print(' ')
                main()
            elif validAddress(toAddress) is False:
                print('\n\tInvalid Address. Press "c" to cancel. Please try again.\n')
            else:
                break

    if validAddress(fromAddress) is False:
        try:
            jsonAddresses = json.loads(api.listAddresses())
            numAddresses = len(jsonAddresses['addresses'])  # Number of addresses
        except:
            print('\n\tConnection Error\n')
            usrPrompt = 0
            main()

        if (numAddresses > 1):  # Ask what address to send from if multiple addresses
            found = False
            while True:
                print('\n')
                fromAddress = userInput("Enter an Address or Address Label to send from.")

                if fromAddress == "exit":
                    usrPrompt = 1
                    main()

                for addNum in range (0, numAddresses):  # processes all of the addresses
                    label = jsonAddresses['addresses'][addNum]['label']
                    address = jsonAddresses['addresses'][addNum]['address']
                    #stream = jsonAddresses['addresses'][addNum]['stream']
                    #enabled = jsonAddresses['addresses'][addNum]['enabled']
                    if (fromAddress == label):  # address entered was a label and is found
                        fromAddress = address
                        found = True
                        break

                if found is False:
                    if validAddress(fromAddress) is False:
                        print('\n\tInvalid Address. Please try again.\n')

                    else:
                        for addNum in range (0, numAddresses):  # Processes all of the addresses
                            #label = jsonAddresses['addresses'][addNum]['label']
                            address = jsonAddresses['addresses'][addNum]['address']
                            #stream = jsonAddresses['addresses'][addNum]['stream']
                            #enabled = jsonAddresses['addresses'][addNum]['enabled']
                            if fromAddress is address:  # Address entered was a found in our addressbook.
                                found = True
                                break

                        if found is False:
                            print('\n\tThe address entered is not one of yours. Please try again.\n')

                if found is True:
                    break  # Address was found

        else:  # Only one address in address book
            print('\n\tUsing the only address in the addressbook to send from.\n')
            fromAddress = jsonAddresses['addresses'][0]['address']

    if (subject == ''):
        subject = userInput("Enter your Subject.")
        subject = subject.encode('base64')
    if (message == ''):
        message = userInput("Enter your Message.")

        uInput = userInput('Would you like to add an attachment, (Y)es or (N)o?').lower()
        if uInput == "y":
            message = message + '\n\n' + attachment()

        message = message.encode('base64')

    try:
        ackData = api.sendMessage(toAddress, fromAddress, subject, message)
        print('\n\tMessage Status:', api.getStatus(ackData), '\n')
    except:
        print('\n\tConnection Error\n')
        usrPrompt = 0
        main()


def sendBrd(fromAddress, subject, message):  # Sends a broadcast
    global usrPrompt
    if (fromAddress == ''):
        try:
            jsonAddresses = json.loads(api.listAddresses())
            numAddresses = len(jsonAddresses['addresses'])  # Number of addresses
        except:
            print('\n\tConnection Error\n')
            usrPrompt = 0
            main()

        if (numAddresses > 1):  # Ask what address to send from if multiple addresses
            found = False
            while True:
                fromAddress = userInput("\nEnter an Address or Address Label to send from.")

                if fromAddress == "exit":
                    usrPrompt = 1
                    main()

                for addNum in range (0, numAddresses):  # Processes all of the addresses
                    label = jsonAddresses['addresses'][addNum]['label']
                    address = jsonAddresses['addresses'][addNum]['address']
                    #stream = jsonAddresses['addresses'][addNum]['stream']
                    #enabled = jsonAddresses['addresses'][addNum]['enabled']
                    if (fromAddress == label):  # Address entered was a label and is found
                        fromAddress = address
                        found = True
                        break

                if found is False:
                    if validAddress(fromAddress) is False:
                        print('\n\tInvalid Address. Please try again.\n')

                    else:
                        for addNum in range (0, numAddresses):  # Processes all of the addresses
                            #label = jsonAddresses['addresses'][addNum]['label']
                            address = jsonAddresses['addresses'][addNum]['address']
                            #stream = jsonAddresses['addresses'][addNum]['stream']
                            #enabled = jsonAddresses['addresses'][addNum]['enabled']
                            if (fromAddress == address):  #  Address entered was a found in our addressbook.
                                found = True
                                break

                        if found is False:
                            print('\n\tThe address entered is not one of yours. Please try again.\n')

                if found is True:
                    break  # Address was found

        else:  # Only one address in address book
            print('\n\tUsing the only address in the addressbook to send from.\n')
            fromAddress = jsonAddresses['addresses'][0]['address']

    if (subject == ''):
            subject = userInput("Enter your Subject.")
            subject = subject.encode('base64')
    if (message == ''):
            message = userInput("Enter your Message.")

            uInput = userInput('Would you like to add an attachment, (Y)es or (N)o?').lower()
            if uInput == "y":
                message = message + '\n\n' + attachment()
            message = message.encode('base64')

    try:
        ackData = api.sendBroadcast(fromAddress, subject, message)
        print('\n\tMessage Status:', api.getStatus(ackData), '\n')
    except:
        print('\n\tConnection Error\n')
        usrPrompt = 0
        main()


def inbox(unreadOnly=False):  # Lists the messages by: Message Number, To Address Label, From Address Label, Subject, Received Time)
    global usrPrompt
    try:
        inboxMessages = json.loads(api.getAllInboxMessages())
        numMessages = len(inboxMessages['inboxMessages'])
    except:
        print('\n\tConnection Error\n')
        usrPrompt = 0
        main()

    messagesPrinted = 0
    messagesUnread = 0
    for msgNum in range (0, numMessages):  # Processes all of the messages in the inbox
        message = inboxMessages['inboxMessages'][msgNum]
        # If we are displaying all messages or if this message is unread then display it
        if not unreadOnly or not message['read']:
            print('\n\t-----------------------------------\n')
            print('\tMessage Number:',msgNum)  # Message Number
            print('\tTo:', getLabelForAddress(message['toAddress']))  # Get the to address
            print('\tFrom:', getLabelForAddress(message['fromAddress']))  # Get the from address
            print('\tSubject:', message['subject'].decode('base64'))  # Get the subject
            print('\tReceived:', datetime.datetime.fromtimestamp(float(message['receivedTime'])).strftime('%Y-%m-%d %H:%M:%S'))
            messagesPrinted += 1
            if not message['read']:
                messagesUnread += 1

        if (messagesPrinted%20 == 0 and messagesPrinted != 0):
            uInput = userInput('(Press Enter to continue or type (Exit) to return to the main menu.)').lower()

    print('\n\t-----------------------------------')
    print('\tThere are %d unread messages of %d messages in the inbox.' % (messagesUnread, numMessages))
    print('\t-----------------------------------\n')


def outbox():
    global usrPrompt
    try:
        outboxMessages = json.loads(api.getAllSentMessages())
        numMessages = len(outboxMessages['sentMessages'])
    except:
        print('\n\tConnection Error\n')
        usrPrompt = 0
        main()

    for msgNum in range (0, numMessages):  # Processes all of the messages in the outbox
        print('\n\t-----------------------------------\n')
        print('\tMessage Number:', msgNum)  # Message Number
        #print('\tMessage ID:', outboxMessages['sentMessages'][msgNum]['msgid']))
        print('\tTo:', getLabelForAddress(outboxMessages['sentMessages'][msgNum]['toAddress']))  # Get the to address
        print('\tFrom:', getLabelForAddress(outboxMessages['sentMessages'][msgNum]['fromAddress']))  # Get the from address
        print('\tSubject:', outboxMessages['sentMessages'][msgNum]['subject'].decode('base64'))  # Get the subject
        print('\tStatus:', outboxMessages['sentMessages'][msgNum]['status'])  # Get the status
        print('\tLast Action Time:', datetime.datetime.fromtimestamp(float(outboxMessages['sentMessages'][msgNum]['lastActionTime'])).strftime('%Y-%m-%d %H:%M:%S'))

        if (msgNum % 20 == 0 and msgNum != 0):
            uInput = userInput('(Press Enter to continue or type (Exit) to return to the main menu.)').lower()

    print('\n\t-----------------------------------')
    print('\tThere are ', numMessages, ' messages in the outbox.')
    print('\t-----------------------------------\n')


def readSentMsg(msgNum):  # Opens a sent message for reading
    global usrPrompt
    try:
        outboxMessages = json.loads(api.getAllSentMessages())
        numMessages = len(outboxMessages['sentMessages'])
    except:
        print('\n\tConnection Error\n')
        usrPrompt = 0
        main()

    print(' ')

    if (msgNum >= numMessages):
        print('\n\tInvalid Message Number.\n')
        main()

    # Begin attachment detection
    message = outboxMessages['sentMessages'][msgNum]['message'].decode('base64')

    while True:  # Allows multiple messages to be downloaded/saved
        if (';base64,' in message):  # Found this text in the message, there is probably an attachment.
            attPos = message.index(";base64,")  # Finds the attachment position
            attEndPos = message.index("' />")  # Finds the end of the attachment
            #attLen = attEndPos - attPos #Finds the length of the message

            if ('alt = "' in message):  # We can get the filename too
                fnPos = message.index('alt = "')  # Finds position of the filename
                fnEndPos = message.index('" src=')  # Finds the end position
                #fnLen = fnEndPos - fnPos  # Finds the length of the filename

                fileName = message[(fnPos + 7):fnEndPos]
            else:
                fnPos = attPos
                fileName = 'Attachment'

            uInput = userInput('\nAttachment Detected. Would you like to save the attachment, (Y)es or (N)o?').lower()
            if (uInput == "y" or uInput == 'yes'):

                attachment = message[(attPos + 9):attEndPos]
                saveFile(fileName, attachment)

            message = message[:fnPos] + '~<Attachment data removed for easier viewing>~' + message[(attEndPos + 4):]

        else:
            break

    # End attachment Detection

    print('\n\tTo:', getLabelForAddress(outboxMessages['sentMessages'][msgNum]['toAddress']))  # Get the to address
    print('\tFrom:', getLabelForAddress(outboxMessages['sentMessages'][msgNum]['fromAddress']))  # Get the from address
    print('\tSubject:', outboxMessages['sentMessages'][msgNum]['subject'].decode('base64'))  # Get the subject
    print('\tStatus:', outboxMessages['sentMessages'][msgNum]['status'])  # Get the status
    print('\tLast Action Time:', datetime.datetime.fromtimestamp(float(outboxMessages['sentMessages'][msgNum]['lastActionTime'])).strftime('%Y-%m-%d %H:%M:%S'))
    print('\tMessage:\n')
    print(message)  # inboxMessages['inboxMessages'][msgNum]['message'].decode('base64')
    print(' ')


def readMsg(msgNum):  # Opens a received message for reading
    global usrPrompt
    try:
        inboxMessages = json.loads(api.getAllInboxMessages())
        numMessages = len(inboxMessages['inboxMessages'])
    except:
        print('\n\tConnection Error\n')
        usrPrompt = 0
        main()

    if (msgNum >= numMessages):
        print('\n\tInvalid Message Number.\n')
        main()

    # Begin attachment detection
    message = inboxMessages['inboxMessages'][msgNum]['message'].decode('base64')

    while True:  # Allows multiple messages to be downloaded/saved
        if (';base64,' in message):  # Found this text in the message, there is probably an attachment.
            attPos = message.index(";base64,")  # Finds the attachment position
            attEndPos = message.index("' />")  # Finds the end of the attachment
            #attLen = attEndPos - attPos  # Finds the length of the message

            if ('alt = "' in message):  # We can get the filename too
                fnPos = message.index('alt = "')  # Finds position of the filename
                fnEndPos = message.index('" src=')  # Finds the end position
                #fnLen = fnEndPos - fnPos  # Finds the length of the filename
                fileName = message[(fnPos + 7):fnEndPos]
            else:
                fnPos = attPos
                fileName = 'Attachment'

            uInput = userInput('\nAttachment Detected. Would you like to save the attachment, (Y)es or (N)o?').lower()
            if (uInput == "y" or uInput == 'yes'):
                attachment = message[(attPos + 9):attEndPos]
                saveFile(fileName, attachment)

            message = message[:fnPos] + '~<Attachment data removed for easier viewing>~' + message[(attEndPos + 4):]
        else:
            break

    # End attachment Detection

    print('\n\tTo:', getLabelForAddress(outboxMessages['sentMessages'][msgNum]['toAddress']))  # Get the to address
    print('\tFrom:', getLabelForAddress(outboxMessages['sentMessages'][msgNum]['fromAddress']))  # Get the from address
    print('\tSubject:', outboxMessages['sentMessages'][msgNum]['subject'].decode('base64'))  # Get the subject
    print('\tStatus:', outboxMessages['sentMessages'][msgNum]['status'])  # Get the status
    print('\tLast Action Time:', datetime.datetime.fromtimestamp(float(outboxMessages['sentMessages'][msgNum]['lastActionTime'])).strftime('%Y-%m-%d %H:%M:%S'))
    print('\tMessage:\n')
    print(message)  # inboxMessages['inboxMessages'][msgNum]['message'].decode('base64')
    print(' ')
    return inboxMessages['inboxMessages'][msgNum]['msgid']


def replyMsg(msgNum,forwardORreply):  # Allows to reply to the message you are currently on. Saves typing in the addresses and subject.
    global usrPrompt
    forwardORreply = forwardORreply.lower()  # makes it lowercase
    try:
        inboxMessages = json.loads(api.getAllInboxMessages())
    except:
        print('\n\tConnection Error\n')
        usrPrompt = 0
        main()

    fromAdd = inboxMessages['inboxMessages'][msgNum]['toAddress']  # Address it was sent To, now the From address
    message = inboxMessages['inboxMessages'][msgNum]['message'].decode('base64')  # Message that you are replying too.

    subject = inboxMessages['inboxMessages'][msgNum]['subject']
    subject = subject.decode('base64')

    if (forwardORreply == 'reply'):
        toAdd = inboxMessages['inboxMessages'][msgNum]['fromAddress']  # Address it was From, now the To address
        subject = "Re: " + subject

    elif (forwardORreply == 'forward'):
        subject = "Fwd: " + subject

        while True:
            toAdd = userInput("What is the To Address?")
            if (toAdd == "c"):
                usrPrompt = 1
                print(' ')
                main()
            elif (validAddress(toAdd) is False):
                print('\n\tInvalid Address. Press "c" to cancel. Please try again.\n')
            else:
                break
    else:
        print('\n\tInvalid Selection. Reply or Forward only.')
        usrPrompt = 0
        main()

    subject = subject.encode('base64')
    newMessage = userInput("Enter your Message.")

    uInput = userInput('Would you like to add an attachment, (Y)es or (N)o?').lower()
    if uInput == "y":
        newMessage = newMessage + '\n\n' + attachment()

    newMessage = newMessage + '\n\n------------------------------------------------------\n'
    newMessage = newMessage + message
    newMessage = newMessage.encode('base64')

    sendMsg(toAdd, fromAdd, subject, newMessage)
    main()


def delMsg(msgNum):  # Deletes a specified message from the inbox
    global usrPrompt
    try:
        inboxMessages = json.loads(api.getAllInboxMessages())
        msgId = inboxMessages['inboxMessages'][int(msgNum)]['msgid']  # Gets the message ID via the message index number
        msgAck = api.trashMessage(msgId)
    except:
        print('\n\tConnection Error\n')
        usrPrompt = 0
        main()

    return msgAck


def delSentMsg(msgNum):  # Deletes a specified message from the outbox
    global usrPrompt
    try:
        outboxMessages = json.loads(api.getAllSentMessages())
        msgId = outboxMessages['sentMessages'][int(msgNum)]['msgid']  # Gets the message ID via the message index number
        msgAck = api.trashSentMessage(msgId)
    except:
        print('\n\tConnection Error\n')
        usrPrompt = 0
        main()

    return msgAck


def getLabelForAddress(address):
    global usrPrompt

    if address in knownAddresses:
        return knownAddresses[address]
    else:
        buildKnownAddresses()
        if address in knownAddresses:
            return knownAddresses[address]

    return address


def buildKnownAddresses():
    # add from address book
    try:
        response = api.listAddressBookEntries()
        # if api is too old then fail
        if "API Error 0020" in response:
            return 1
        addressBook = json.loads(response)
        for entry in addressBook['addresses']:
            if entry['address'] not in knownAddresses:
                knownAddresses[entry['address']] = "%s (%s)" % (entry['label'].decode('base64'), entry['address'])
    except:
        print('\n\tConnection Error\n')
        usrPrompt = 0
        main()

    # Add from my addresses
    try:
        response = api.listAddresses2()
        # If API is too old just return then fail
        if "API Error 0020" in response:
            return 1
        addresses = json.loads(response)
        for entry in addresses['addresses']:
            if entry['address'] not in knownAddresses:
                knownAddresses[entry['address']] = "%s (%s)" % (entry['label'].decode('base64'), entry['address'])
    except:
        print('\n\tConnection Error\n')
        usrPrompt = 0
        main()


def listAddressBookEntries():
    try:
        response = api.listAddressBookEntries()
        if "API Error" in response:
            return getAPIErrorCode(response)
        addressBook = json.loads(response)
        print('\n')
        print('\t--------------------------------------------------------------')
        print('\t|        Label       |                Address                |')
        print('\t|--------------------|---------------------------------------|')
        for entry in addressBook['addresses']:
            label = entry['label'].decode('base64')
            address = entry['address']
            if (len(label) > 19):
                label = label[:16] + '...'
            print('\t| ' + label.ljust(19) + '| ' + address.ljust(37) + ' |')
        print('\t--------------------------------------------------------------')
        print

    except:
        print('\n\tConnection Error\n')
        usrPrompt = 0
        main()


def addAddressToAddressBook(address, label):
    try:
        response = api.addAddressBookEntry(address, label.encode('base64'))
        if "API Error" in response:
            return getAPIErrorCode(response)
    except:
        print('\n\tConnection Error\n')
        usrPrompt = 0
        main()


def deleteAddressFromAddressBook(address):
    try:
        response = api.deleteAddressBookEntry(address)
        if "API Error" in response:
            return getAPIErrorCode(response)
    except:
        print('\n\tConnection Error\n')
        usrPrompt = 0
        main()


def getAPIErrorCode(response):
    if "API Error" in response:
        # If we got an API error return the number by getting the number
        # After the second space and removing the trailing colon
        return int(response.split()[2][:-1])


def markMessageRead(messageID):
    try:
        response = api.getInboxMessageByID(messageID, True)
        if "API Error" in response:
            return getAPIErrorCode(response)
    except:
        print('\n\tConnection Error\n')
        usrPrompt = 0
        main()


def markMessageUnread(messageID):
    try:
        response = api.getInboxMessageByID(messageID, False)
        if "API Error" in response:
            return getAPIErrorCode(response)
    except:
        print('\n\tConnection Error\n')
        usrPrompt = 0
        main()


def markAllMessagesRead():
    try:
        inboxMessages = json.loads(api.getAllInboxMessages())['inboxMessages']
    except:
        print('\n\tConnection Error\n')
        usrPrompt = 0
        main()
    for message in inboxMessages:
        if not message['read']:
            markMessageRead(message['msgid'])


def markAllMessagesUnread():
    try:
        inboxMessages = json.loads(api.getAllInboxMessages())['inboxMessages']
    except:
        print('\n\tConnection Error\n')
        usrPrompt = 0
        main()
    for message in inboxMessages:
        if message['read']:
            markMessageUnread(message['msgid'])


def clientStatus():
    try:
        clientStatus = json.loads(api.clientStatus())
    except:
        print('\n\tConnection Error\n')
        usrPrompt = 0
        main()
    print('\nnetworkStatus:' + clientStatus['networkStatus'] + '\n')
    print('\nnetworkConnections:' + str(clientStatus['networkConnections']) + '\n')
    print('\nnumberOfPubkeysProcessed:' + str(clientStatus['numberOfPubkeysProcessed']) + '\n')
    print('\nnumberOfMessagesProcessed:' + str(clientStatus['numberOfMessagesProcessed']) + '\n')
    print('\nnumberOfBroadcastsProcessed:' + str(clientStatus['numberOfBroadcastsProcessed']) + '\n')


def UI(usrInput):  # Main UX
    global usrPrompt

    if usrInput == "help" or usrInput == "h" or usrInput == "?":
        print('\n')
        print('\t-------------------------------------------------------------------------')
        print('\t|        https://github.com/Dokument/PyBitmessage-Daemon                |')
        print('\t|-----------------------------------------------------------------------|')
        print('\t| Command                | Description                                  |')
        print('\t|------------------------|----------------------------------------------|')
        print('\t| help                   | This help file.                              |')
        print('\t| apiTest                | Tests the API                                |')
        print('\t| addInfo                | Returns address information (If valid)       |')
        print('\t| bmSettings             | BitMessage settings                          |')
        print('\t| exit                   | Use anytime to return to main menu           |')
        print('\t| quit                   | Quits the program                            |')
        print('\t|------------------------|----------------------------------------------|')
        print('\t| listAddresses          | Lists all of the users addresses             |')
        print('\t| generateAddress        | Generates a new address                      |')
        print('\t| getAddress             | Get determinist address from passphrase      |')
        print('\t|------------------------|----------------------------------------------|')
        print('\t| listAddressBookEntries | Lists entries from the Address Book          |')
        print('\t| addAddressBookEntry    | Add address to the Address Book              |')
        print('\t| deleteAddressBookEntry | Deletes address from the Address Book        |')
        print('\t|------------------------|----------------------------------------------|')
        print('\t| subscribe              | Subscribes to an address                     |')
        print('\t| unsubscribe            | Unsubscribes from an address                 |')
       #print('\t| listSubscriptions      | Lists all of the subscriptions.              |')
        print('\t|------------------------|----------------------------------------------|')
        print('\t| create                 | Creates a channel                            |')
        print('\t| join                   | Joins a channel                              |')
        print('\t| leave                  | Leaves a channel                             |')
        print('\t|------------------------|----------------------------------------------|')
        print('\t| inbox                  | Lists the message information for the inbox  |')
        print('\t| outbox                 | Lists the message information for the outbox |')
        print('\t| send                   | Send a new message or broadcast              |')
        print('\t| unread                 | Lists all unread inbox messages              |')
        print('\t| read                   | Reads a message from the inbox or outbox     |')
        print('\t| save                   | Saves message to text file                   |')
        print('\t| delete                 | Deletes a message or all messages            |')
        print('\t-------------------------------------------------------------------------')
        print('\n')
        main()

    elif usrInput == "apitest":  # Tests the API Connection.
        if apiTest() is True:
            print('\n\tAPI connection test has: PASSED\n')
        else:
            print('\n\tAPI connection test has: FAILED\n')
        main()

    elif usrInput == "addinfo":
        tmp_address = userInput('\nEnter the Bitmessage Address.')
        address_information = api.decodeAddress(tmp_address)
        address_information = eval(address_information)

        print('\n------------------------------')

        if 'success' in str(address_information.get('status')).lower():
            print(' Valid Address')
            print(' Address Version: %s' % str(address_information.get('addressVersion')))
            print(' Stream Number: %s' % str(address_information.get('streamNumber')))
        else:
            print(' Invalid Address !')

        print('------------------------------\n')
        main()

    elif usrInput == "bmsettings":  # Tests the API Connection.
        bmSettings()
        print('\n')
        main()

    elif usrInput == "quit":  # Quits the application
        print('\n\tBye\n')
        sys.exit()
        os.exit()

    elif usrInput == "listaddresses":  # Lists all of the identities in the addressbook
        listAdd()
        main()

    elif usrInput == "generateaddress":  # Generates a new address
        uInput = userInput('\nWould you like to create a (D)eterministic or (R)andom address?').lower()

        if uInput == "d" or uInput == "determinstic":  # Creates a deterministic address
            deterministic = True

            #lbl = raw_input('Label the new address:')  # currently not possible via the api
            lbl = ''
            passphrase = userInput('Enter the Passphrase.')  # .encode('base64')
            numOfAdd = int(userInput('How many addresses would you like to generate?'))
            #addVNum = int(raw_input('Address version number (default "0"):'))
            #streamNum = int(raw_input('Stream number (default "0"):'))
            addVNum = 3
            streamNum = 1
            isRipe = userInput('Shorten the address, (Y)es or (N)o?').lower()

            if isRipe == "y":
                ripe = True
                print genAdd(lbl,deterministic, passphrase, numOfAdd, addVNum, streamNum, ripe)
                main()
            elif isRipe == "n":
                ripe = False
                print genAdd(lbl, deterministic, passphrase, numOfAdd, addVNum, streamNum, ripe)
                main()
            elif isRipe == "exit":
                usrPrompt = 1
                main()
            else:
                print('\n\tInvalid input\n')
                main()


        elif uInput == "r" or uInput == "random":  # Creates a random address with user-defined label
            deterministic = False
            null = ''
            lbl = userInput('Enter the label for the new address.')

            print genAdd(lbl, deterministic, null, null, null, null, null)
            main()

        else:
            print('\n\tInvalid input\n')
            main()

    elif usrInput == "getaddress":  # Gets the address for/from a passphrase
        phrase = userInput("Enter the address passphrase.")
        print('\n\tWorking...\n')
        #vNumber = int(raw_input("Enter the address version number:"))
        #sNumber = int(raw_input("Enter the address stream number:"))

        address = getAddress(phrase, 4, 1)  # ,vNumber,sNumber)
        print ('\n     Address: ' + address + '\n')

        usrPrompt = 1
        main()

    elif usrInput == "subscribe":  # Subsribe to an address
        subscribe()
        usrPrompt = 1
        main()
    elif usrInput == "unsubscribe":  # Unsubscribe from an address
        unsubscribe()
        usrPrompt = 1
        main()
    elif usrInput == "listsubscriptions":  # Unsubscribe from an address
        listSubscriptions()
        usrPrompt = 1
        main()

    elif usrInput == "create":
        createChan()
        userPrompt = 1
        main()

    elif usrInput == "join":
        joinChan()
        userPrompt = 1
        main()

    elif usrInput == "leave":
        leaveChan()
        userPrompt = 1
        main()

    elif usrInput == "inbox":
        print('\n\tLoading...\n')
        inbox()
        main()

    elif usrInput == "unread":
        print('\n\tLoading...\n')
        inbox(True)
        main()

    elif usrInput == "outbox":
        print('\n\tLoading...\n')
        outbox()
        main()

    elif usrInput == 'send':  # Sends a message or broadcast
        uInput = userInput('Would you like to send a (M)essage or (B)roadcast?').lower()
        if (uInput == 'm' or uInput == 'message'):
            null = ''
            sendMsg(null, null, null, null)
            main()
        elif (uInput =='b' or uInput == 'broadcast'):
            null = ''
            sendBrd(null, null, null)
            main()

    elif usrInput == "read":  # Opens a message from the inbox for viewing. 
        uInput = userInput("Would you like to read a message from the (I)nbox or (O)utbox?").lower()
        if (uInput != 'i' and uInput != 'inbox' and uInput != 'o' and uInput != 'outbox'):
            print('\n\tInvalid Input.\n')
            usrPrompt = 1
            main()

        msgNum = int(userInput("What is the number of the message you wish to open?"))

        if (uInput == 'i' or uInput == 'inbox'):
            print('\n\tLoading...\n')
            messageID = readMsg(msgNum)

            uInput = userInput("\nWould you like to keep this message unread, (Y)es or (N)o?").lower()

            if not (uInput == 'y' or uInput == 'yes'):
                markMessageRead(messageID)
                usrPrompt = 1

            uInput = userInput("\nWould you like to (D)elete, (F)orward, (R)eply to, or (Exit) this message?").lower()

            if (uInput == 'r' or uInput == 'reply'):
                print('\n\tLoading...\n')
                print('\n')
                replyMsg(msgNum,'reply')
                usrPrompt = 1

            elif (uInput == 'f' or uInput == 'forward'):
                print('\n\tLoading...\n')
                print('\n')
                replyMsg(msgNum,'forward')
                usrPrompt = 1

            elif (uInput == "d" or uInput == 'delete'):
                uInput = userInput("Are you sure, (Y)es or (N)o?").lower()  # Prevent accidental deletion
                if uInput == "y":
                    delMsg(msgNum)
                    print('\n\tMessage Deleted.\n')
                    usrPrompt = 1
                else:
                    usrPrompt = 1
            else:
                print('\n\tInvalid entry\n')
                usrPrompt = 1

        elif (uInput == 'o' or uInput == 'outbox'):
            readSentMsg(msgNum)
            uInput = userInput("Would you like to (D)elete, or (Exit) this message?").lower()  # Gives the user the option to delete the message
            if (uInput == "d" or uInput == 'delete'):
                uInput = userInput('Are you sure, (Y)es or (N)o?').lower()  # Prevent accidental deletion
                if uInput == "y":
                    delSentMsg(msgNum)
                    print('\n\tMessage Deleted.\n')
                    usrPrompt = 1
                else:
                    usrPrompt = 1
            else:
                print('\n\tInvalid Entry\n')
                usrPrompt = 1
        main()

    elif usrInput == "save":
        uInput = userInput("Would you like to save a message from the (I)nbox or (O)utbox?").lower()
        if (uInput != 'i' and uInput == 'inbox' and uInput != 'o' and uInput == 'outbox'):
            print('\n\tInvalid Input.\n')
            usrPrompt = 1
            main()

        if (uInput == 'i' or uInput == 'inbox'):
            inboxMessages = json.loads(api.getAllInboxMessages())
            numMessages = len(inboxMessages['inboxMessages'])

            while True:
                msgNum = int(userInput("What is the number of the message you wish to save?"))
                if (msgNum >= numMessages):
                    print('\n\tInvalid Message Number.\n')
                else:
                    break

            subject =  inboxMessages['inboxMessages'][msgNum]['subject'].decode('base64') 
            message =  inboxMessages['inboxMessages'][msgNum]['message'] # Don't decode since it is done in the saveFile function

        elif (uInput == 'o' or uInput == 'outbox'):      
            outboxMessages = json.loads(api.getAllSentMessages())
            numMessages = len(outboxMessages['sentMessages'])

            while True:
                msgNum = int(userInput("What is the number of the message you wish to save?"))
                if (msgNum >= numMessages):
                    print('\n\tInvalid Message Number.\n')
                else:
                    break

            subject =  outboxMessages['sentMessages'][msgNum]['subject'].decode('base64') 
            message =  outboxMessages['sentMessages'][msgNum]['message']  # Don't decode since it is done in the saveFile function
        
        subject = subject +'.txt'
        saveFile(subject,message)
        
        usrPrompt = 1
        main()

    elif usrInput == "delete":  # Will delete a message from the system, not reflected on the UI.

        uInput = userInput("Would you like to delete a message from the (I)nbox or (O)utbox?").lower()
        if (uInput == 'i' or uInput == 'inbox'):  
            inboxMessages = json.loads(api.getAllInboxMessages())
            numMessages = len(inboxMessages['inboxMessages'])

            while True:
                msgNum = userInput('Enter the number of the message you wish to delete or (A)ll to empty the inbox.').lower()
                if (msgNum == 'a' or msgNum == 'all'):
                    break
                elif (int(msgNum) >= numMessages):
                    print('\n\tInvalid Message Number.\n')
                else:
                    break

            uInput = userInput("Are you sure, (Y)es or (N)o?").lower()  # Prevent accidental deletion

            if uInput == "y":
                if (msgNum == 'a' or msgNum == 'all'):
                    print('\n')
                    for msgNum in range (0, numMessages):  # Processes all of the messages in the inbox
                        print('\tDeleting message ', msgNum + 1, ' of ', numMessages)
                        delMsg(0)

                    print('\n\tInbox is empty.')
                    usrPrompt = 1
                else:
                    delMsg(int(msgNum))

                print('\n\tNotice: Message numbers may have changed.\n')
                main()
            else:
                usrPrompt = 1
        elif (uInput == 'o' or uInput == 'outbox'):
            outboxMessages = json.loads(api.getAllSentMessages())
            numMessages = len(outboxMessages['sentMessages'])

            while True:
                msgNum = userInput('Enter the number of the message you wish to delete or (A)ll to empty the inbox.').lower()

                if (msgNum == 'a' or msgNum == 'all'):
                    break
                elif (int(msgNum) >= numMessages):
                    print('\n\tInvalid Message Number.\n')
                else:
                    break

            uInput = userInput("Are you sure, (Y)es or (N)o?").lower()  # Prevent accidental deletion

            if uInput == "y":
                if (msgNum == 'a' or msgNum == 'all'):
                    print('\n')
                    for msgNum in range(0, numMessages):  # Processes all of the messages in the outbox
                        print('\tDeleting message ', msgNum + 1, ' of ', numMessages)
                        delSentMsg(0)

                    print('\n\tOutbox is empty.')
                    usrPrompt = 1
                else:
                    delSentMsg(int(msgNum))
                print('\n\tNotice: Message numbers may have changed.\n')
                main()
            else:
                usrPrompt = 1
        else:
            print('\n\tInvalid Entry.\n')
            # TODO: Unused var userPrompt
            userPrompt = 1
            main()

    elif usrInput == "exit":
        print('\n\tYou are already at the main menu. Use "quit" to quit.\n')
        usrPrompt = 1
        main()

    elif usrInput == "listaddressbookentries":
        res = listAddressBookEntries()
        if res == 20:
            print('\n\t[ERROR]: API function not supported.\n')
        usrPrompt = 1
        main()

    elif usrInput == "addaddressbookentry":
        address = userInput('Enter address')
        label = userInput('Enter label')
        res = addAddressToAddressBook(address, label)
        if res == 16:
            print('\n\t[ERROR]: Address already exists in Address Book.\n')
        if res == 20:
            print('\n\t[ERROR]: API function not supported.\n')
        usrPrompt = 1
        main()

    elif usrInput == "deleteaddressbookentry":
        address = userInput('Enter address')
        res = deleteAddressFromAddressBook(address)
        if res == 20:
            print('\n\t[ERROR] API function not supported.\n')
        usrPrompt = 1
        main()

    elif usrInput == "markallmessagesread":
        markAllMessagesRead()
        usrPrompt = 1
        main()

    elif usrInput == "markallmessagesunread":
        markAllMessagesUnread()
        usrPrompt = 1
        main()

    elif usrInput == "status":
        clientStatus()
        usrPrompt = 1
        main()

    elif usrInput == "million+":
        genMilAddr()
        usrPrompt = 1
        main()

    elif usrInput == "million-":
        delMilAddr()
        usrPrompt = 1
        main()

    else:
        print('\n\t"', usrInput, '" is not a command.\n')
        usrPrompt = 1
        main()


def main():
    global api
    global usrPrompt

    if (usrPrompt == 0):
        print('\n\t------------------------------')
        print('\t| Bitmessage Daemon by .dok  |')
        print('\t| Version 0.2.6 for BM 0.3.5 |')
        print('\t------------------------------')
        api = xmlrpclib.ServerProxy(apiData())  # Connect to BitMessage using these api credentials

        if apiTest() is False:
            print('\n\t****************************************************************')
            print('\t   WARNING: You are not connected to the Bitmessage client.')
            print('\tEither Bitmessage is not running or your settings are incorrect.')
            print('\tUse the command "apiTest" or "bmSettings" to resolve this issue.')
            print('\t****************************************************************\n')

        #if (apiTest() == False):  # Preform a connection test #taken out until I get the error handler working
        #    print '*************************************'
        #    print 'WARNING: No connection to Bitmessage.'
        #    print '*************************************'
        #    print('\n')

    print('\nType (H)elp for a list of commands.')  # Startup message
    usrPrompt = 2

    try:
        UI((raw_input('>').lower()).replace(" ", ""))
    except EOFError:
        UI("quit")

if __name__ == "__main__":
    main()
