#!/usr/bin/python2.7
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
usrPrompt = 0 #0 = First Start, 1 = prompt, 2 = no prompt if the program is starting up
knownAddresses = dict()

def userInput(message): #Checks input for exit or quit. Also formats for input, etc
    global usrPrompt
    print '\n' + message
    uInput = raw_input('> ')

    if (uInput.lower() == 'exit'): #Returns the user to the main menu
        usrPrompt = 1
        main()
        
    elif (uInput.lower() == 'quit'): #Quits the program
        print '\n     Bye\n'
        sys.exit()
        os.exit()
    else:
        return uInput
    
def restartBmNotify(): #Prompts the user to restart Bitmessage. 
    print '\n     *******************************************************************'
    print '     WARNING: If Bitmessage is running locally, you must restart it now.'
    print '     *******************************************************************\n'

def safeConfigGetBoolean(section,field):
    global keysPath
    config = ConfigParser.SafeConfigParser()
    config.read(keysPath)
    
    try:
        return config.getboolean(section,field)
    except:
        return False

#Begin keys.dat interactions
def lookupAppdataFolder(): #gets the appropriate folders for the .dat files depending on the OS. Taken from bitmessagemain.py
    APPNAME = "PyBitmessage"
    from os import path, environ
    if sys.platform == 'darwin':
        if "HOME" in environ:
            dataFolder = path.join(os.environ["HOME"], "Library/Application support/", APPNAME) + '/'
        else:
            print '     Could not find home folder, please report this message and your OS X version to the Daemon Github.'
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
    config.set('bitmessagesettings', 'port', '8444')  #Sets the bitmessage port to stop the warning about the api not properly being setup. This is in the event that the keys.dat is in a different directory or is created locally to connect to a machine remotely.
    config.set('bitmessagesettings','apienabled','true') #Sets apienabled to true in keys.dat
    
    with open(keysName, 'wb') as configfile:
        config.write(configfile)

    print '\n     ' + str(keysName) + ' Initalized in the same directory as daemon.py'
    print '     You will now need to configure the ' + str(keysName) + ' file.\n'

def apiInit(apiEnabled):
    global keysPath
    global usrPrompt
    config = ConfigParser.SafeConfigParser()
    config.read(keysPath)
    

    
    if (apiEnabled == False): #API information there but the api is disabled.
        uInput = userInput("The API is not enabled. Would you like to do that now, (Y)es or (N)o?").lower()

        if uInput == "y": #
            config.set('bitmessagesettings','apienabled','true') #Sets apienabled to true in keys.dat
            with open(keysPath, 'wb') as configfile:
                config.write(configfile)
                
            print 'Done'
            restartBmNotify()
            return True
            
        elif uInput == "n":
            print '     \n************************************************************'
            print '            Daemon will not work when the API is disabled.       '
            print '     Please refer to the Bitmessage Wiki on how to setup the API.'
            print '     ************************************************************\n'
            usrPrompt = 1
            main()
            
        else:
            print '\n     Invalid Entry\n'
            usrPrompt = 1
            main()
    elif (apiEnabled == True): #API correctly setup
        #Everything is as it should be
        return True
    
    else: #API information was not present.
        print '\n     ' + str(keysPath) + ' not properly configured!\n'
        uInput = userInput("Would you like to do this now, (Y)es or (N)o?").lower()

        if uInput == "y": #User said yes, initalize the api by writing these values to the keys.dat file
            print ' '
            
            apiUsr = userInput("API Username")
            apiPwd = userInput("API Password")
            apiInterface = userInput("API Interface. (127.0.0.1)")
            apiPort = userInput("API Port")
            apiEnabled = userInput("API Enabled? (True) or (False)").lower()
            daemon = userInput("Daemon mode Enabled? (True) or (False)").lower()

            if (daemon != 'true' and daemon != 'false'):
                print '\n     Invalid Entry for Daemon.\n'
                uInput = 1
                main()
                
            print '     -----------------------------------\n'
                
            config.set('bitmessagesettings', 'port', '8444') #sets the bitmessage port to stop the warning about the api not properly being setup. This is in the event that the keys.dat is in a different directory or is created locally to connect to a machine remotely.
            config.set('bitmessagesettings','apienabled','true')
            config.set('bitmessagesettings', 'apiport', apiPort)
            config.set('bitmessagesettings', 'apiinterface', '127.0.0.1')
            config.set('bitmessagesettings', 'apiusername', apiUsr)
            config.set('bitmessagesettings', 'apipassword', apiPwd)
            config.set('bitmessagesettings', 'daemon', daemon)
            with open(keysPath, 'wb') as configfile:
                config.write(configfile)
            
            print '\n     Finished configuring the keys.dat file with API information.\n'
            restartBmNotify()
            return True
        
        elif uInput == "n":
            print '\n     ***********************************************************'
            print '     Please refer to the Bitmessage Wiki on how to setup the API.'
            print '     ***********************************************************\n'
            usrPrompt = 1
            main()
        else:
            print '     \nInvalid entry\n'
            usrPrompt = 1
            main()


def apiData():
    global keysName
    global keysPath
    global usrPrompt
    
    config = ConfigParser.SafeConfigParser()    
    config.read(keysPath) #First try to load the config file (the keys.dat file) from the program directory

    try:
        config.get('bitmessagesettings','port')
        appDataFolder = ''
    except:
        #Could not load the keys.dat file in the program directory. Perhaps it is in the appdata directory.
        appDataFolder = lookupAppdataFolder()
        keysPath = appDataFolder + keysPath
        config = ConfigParser.SafeConfigParser()
        config.read(keysPath)

        try:
            config.get('bitmessagesettings','port')
        except:
            #keys.dat was not there either, something is wrong.
            print '\n     ******************************************************************'
            print '     There was a problem trying to access the Bitmessage keys.dat file'
            print '                    or keys.dat is not set up correctly'
            print '       Make sure that daemon is in the same directory as Bitmessage. '
            print '     ******************************************************************\n'

            uInput = userInput("Would you like to create a keys.dat in the local directory, (Y)es or (N)o?").lower()
    
            if (uInput == "y" or uInput == "yes"):
                configInit()
                keysPath = keysName
                usrPrompt = 0
                main()
            elif (uInput == "n" or uInput == "no"):
                print '\n     Trying Again.\n'
                usrPrompt = 0
                main()
            else:
                print '\n     Invalid Input.\n'

            usrPrompt = 1
            main()

    try: #checks to make sure that everyting is configured correctly. Excluding apiEnabled, it is checked after
        config.get('bitmessagesettings', 'apiport')
        config.get('bitmessagesettings', 'apiinterface')
        config.get('bitmessagesettings', 'apiusername')
        config.get('bitmessagesettings', 'apipassword')
    except:
        apiInit("") #Initalize the keys.dat file with API information

    #keys.dat file was found or appropriately configured, allow information retrieval
    apiEnabled = apiInit(safeConfigGetBoolean('bitmessagesettings','apienabled')) #if false it will prompt the user, if true it will return true

    config.read(keysPath)#read again since changes have been made
    apiPort = int(config.get('bitmessagesettings', 'apiport'))
    apiInterface = config.get('bitmessagesettings', 'apiinterface')
    apiUsername = config.get('bitmessagesettings', 'apiusername')
    apiPassword = config.get('bitmessagesettings', 'apipassword')
    
    print '\n     API data successfully imported.\n'
        
    return "http://" + apiUsername + ":" + apiPassword + "@" + apiInterface+ ":" + str(apiPort) + "/" #Build the api credentials
        
#End keys.dat interactions


def apiTest(): #Tests the API connection to bitmessage. Returns true if it is connected.

    try:
        result = api.add(2,3)
    except:
        return False

    if (result == 5):
        return True
    else:
        return False

def bmSettings(): #Allows the viewing and modification of keys.dat settings. 
    global keysPath
    global usrPrompt
    config = ConfigParser.SafeConfigParser()
    keysPath = 'keys.dat'
    
    config.read(keysPath)#Read the keys.dat
    try:
        port = config.get('bitmessagesettings', 'port')
    except:
        print '\n     File not found.\n'
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


    print '\n     -----------------------------------'
    print '     |   Current Bitmessage Settings   |'
    print '     -----------------------------------'
    print '     port = ' + port
    print '     startonlogon = ' + str(startonlogon)
    print '     minimizetotray = ' + str(minimizetotray)
    print '     showtraynotifications = ' + str(showtraynotifications)
    print '     startintray = ' + str(startintray)
    print '     defaultnoncetrialsperbyte = ' + defaultnoncetrialsperbyte
    print '     defaultpayloadlengthextrabytes = ' + defaultpayloadlengthextrabytes
    print '     daemon = ' + str(daemon)
    print '\n     ------------------------------------'
    print '     |   Current Connection Settings   |'
    print '     -----------------------------------'
    print '     socksproxytype = ' + socksproxytype
    print '     sockshostname = ' + sockshostname
    print '     socksport = ' + socksport
    print '     socksauthentication = ' + str(socksauthentication)
    print '     socksusername = ' + socksusername
    print '     sockspassword = ' + sockspassword
    print ' '

    uInput = userInput("Would you like to modify any of these settings, (Y)es or (N)o?").lower()
    
    if uInput == "y":
        while True: #loops if they mistype the setting name, they can exit the loop with 'exit'
            invalidInput = False
            uInput = userInput("What setting would you like to modify?").lower()
            print ' '

            if uInput == "port":
                print '     Current port number: ' + port
                uInput = userInput("Enter the new port number.")
                config.set('bitmessagesettings', 'port', str(uInput))
            elif uInput == "startonlogon":
                print '     Current status: ' + str(startonlogon)
                uInput = userInput("Enter the new status.")
                config.set('bitmessagesettings', 'startonlogon', str(uInput))
            elif uInput == "minimizetotray":
                print '     Current status: ' + str(minimizetotray)
                uInput = userInput("Enter the new status.")
                config.set('bitmessagesettings', 'minimizetotray', str(uInput))
            elif uInput == "showtraynotifications":
                print '     Current status: ' + str(showtraynotifications)
                uInput = userInput("Enter the new status.")
                config.set('bitmessagesettings', 'showtraynotifications', str(uInput))
            elif uInput == "startintray":
                print '     Current status: ' + str(startintray)
                uInput = userInput("Enter the new status.")
                config.set('bitmessagesettings', 'startintray', str(uInput))
            elif uInput == "defaultnoncetrialsperbyte":
                print '     Current default nonce trials per byte: ' + defaultnoncetrialsperbyte
                uInput = userInput("Enter the new defaultnoncetrialsperbyte.")
                config.set('bitmessagesettings', 'defaultnoncetrialsperbyte', str(uInput))
            elif uInput == "defaultpayloadlengthextrabytes":
                print '     Current default payload length extra bytes: ' + defaultpayloadlengthextrabytes
                uInput = userInput("Enter the new defaultpayloadlengthextrabytes.")
                config.set('bitmessagesettings', 'defaultpayloadlengthextrabytes', str(uInput))
            elif uInput == "daemon":
                print '     Current status: ' + str(daemon)
                uInput = userInput("Enter the new status.").lower()
                config.set('bitmessagesettings', 'daemon', str(uInput))
            elif uInput == "socksproxytype":
                print '     Current socks proxy type: ' + socksproxytype
                print "Possibilities: 'none', 'SOCKS4a', 'SOCKS5'."
                uInput = userInput("Enter the new socksproxytype.")
                config.set('bitmessagesettings', 'socksproxytype', str(uInput))
            elif uInput == "sockshostname":
                print '     Current socks host name: ' + sockshostname
                uInput = userInput("Enter the new sockshostname.")
                config.set('bitmessagesettings', 'sockshostname', str(uInput))
            elif uInput == "socksport":
                print '     Current socks port number: ' + socksport
                uInput = userInput("Enter the new socksport.")
                config.set('bitmessagesettings', 'socksport', str(uInput))
            elif uInput == "socksauthentication":
                print '     Current status: ' + str(socksauthentication)
                uInput = userInput("Enter the new status.")
                config.set('bitmessagesettings', 'socksauthentication', str(uInput))
            elif uInput == "socksusername":
                print '     Current socks username: ' + socksusername
                uInput = userInput("Enter the new socksusername.")
                config.set('bitmessagesettings', 'socksusername', str(uInput))
            elif uInput == "sockspassword":
                print '     Current socks password: ' + sockspassword
                uInput = userInput("Enter the new password.")
                config.set('bitmessagesettings', 'sockspassword', str(uInput))
            else:
                print "\n     Invalid input. Please try again.\n"
                invalidInput = True
                
            if invalidInput != True: #don't prompt if they made a mistake. 
                uInput = userInput("Would you like to change another setting, (Y)es or (N)o?").lower()

                if uInput != "y":
                    print '\n     Changes Made.\n'
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

def getAddress(passphrase,vNumber,sNumber):
    passphrase = passphrase.encode('base64')#passphrase must be encoded

    return api.getDeterministicAddress(passphrase,vNumber,sNumber)

def subscribe():
    global usrPrompt

    while True:
        address = userInput("What address would you like to subscribe to?")

        if (address == "c"):
                usrPrompt = 1
                print ' '
                main()
        elif (validAddress(address)== False):
            print '\n     Invalid. "c" to cancel. Please try again.\n'
        else:
            break
    
    label = userInput("Enter a label for this address.")
    label = label.encode('base64')
    
    api.addSubscription(address,label)
    print ('\n     You are now subscribed to: ' + address + '\n')

def unsubscribe():
    global usrPrompt
    
    while True:
        address = userInput("What address would you like to unsubscribe from?")

        if (address == "c"):
                usrPrompt = 1
                print ' '
                main()
        elif (validAddress(address)== False):
            print '\n     Invalid. "c" to cancel. Please try again.\n'
        else:
            break
    
    
    uInput = userInput("Are you sure, (Y)es or (N)o?").lower()
    
    api.deleteSubscription(address)
    print ('\n     You are now unsubscribed from: ' + address + '\n')

def listSubscriptions():
    global usrPrompt
    #jsonAddresses = json.loads(api.listSubscriptions())
    #numAddresses = len(jsonAddresses['addresses']) #Number of addresses
    print '\nLabel, Address, Enabled\n'
    try:
        print api.listSubscriptions()
    except:
        print '\n     Connection Error\n'
        usrPrompt = 0
        main()
        
    '''for addNum in range (0, numAddresses): #processes all of the addresses and lists them out
        label = jsonAddresses['addresses'][addNum]['label']
        address = jsonAddresses['addresses'][addNum]['address']
        enabled = jsonAddresses['addresses'][addNum]['enabled']

        print label, address, enabled
    '''
    print ' '

def createChan():
    global usrPrompt
    password = userInput("Enter channel name")
    password = password.encode('base64')
    try:
        print api.createChan(password)
    except:
        print '\n     Connection Error\n'
        usrPrompt = 0
        main()


def joinChan():
    global usrPrompt
    while True:
        address = userInput("Enter channel address")
        
        if (address == "c"):
                usrPrompt = 1
                print ' '
                main()
        elif (validAddress(address)== False):
            print '\n     Invalid. "c" to cancel. Please try again.\n'
        else:
            break
    
    password = userInput("Enter channel name")
    password = password.encode('base64')
    try:
        print api.joinChan(password,address)
    except:
        print '\n     Connection Error\n'
        usrPrompt = 0
        main()

def leaveChan():
    global usrPrompt
    while True:
        address = userInput("Enter channel address")
        
        if (address == "c"):
                usrPrompt = 1
                print ' '
                main()
        elif (validAddress(address)== False):
            print '\n     Invalid. "c" to cancel. Please try again.\n'
        else:
            break
    
    try:
        print api.leaveChan(address)
    except:
        print '\n     Connection Error\n'
        usrPrompt = 0
        main()


def listAdd(): #Lists all of the addresses and their info
    global usrPrompt
    try:
        jsonAddresses = json.loads(api.listAddresses())
        numAddresses = len(jsonAddresses['addresses']) #Number of addresses
    except:
        print '\n     Connection Error\n'
        usrPrompt = 0
        main()

    #print '\nAddress Number,Label,Address,Stream,Enabled\n'
    print '\n     --------------------------------------------------------------------------'
    print '     | # |       Label       |               Address               |S#|Enabled|'
    print '     |---|-------------------|-------------------------------------|--|-------|'
    for addNum in range (0, numAddresses): #processes all of the addresses and lists them out
        label = str(jsonAddresses['addresses'][addNum]['label'])
        address = str(jsonAddresses['addresses'][addNum]['address'])
        stream = str(jsonAddresses['addresses'][addNum]['stream'])
        enabled = str(jsonAddresses['addresses'][addNum]['enabled'])

        if (len(label) > 19):
            label = label[:16] + '...'
            
        print '     |' + str(addNum).ljust(3) + '|' + label.ljust(19) + '|' + address.ljust(37) + '|' + stream.ljust(1), '|' + enabled.ljust(7) + '|'

    print '     --------------------------------------------------------------------------\n'

def genAdd(lbl,deterministic, passphrase, numOfAdd, addVNum, streamNum, ripe): #Generate address
    global usrPrompt
    if deterministic == False: #Generates a new address with the user defined label. non-deterministic
        addressLabel = lbl.encode('base64')
        try:
            generatedAddress = api.createRandomAddress(addressLabel)
        except:
            print '\n     Connection Error\n'
            usrPrompt = 0
            main()
            
        return generatedAddress
    
    elif deterministic == True: #Generates a new deterministic address with the user inputs.
        passphrase = passphrase.encode('base64')
        try:
            generatedAddress = api.createDeterministicAddresses(passphrase, numOfAdd, addVNum, streamNum, ripe)
        except:
            print '\n     Connection Error\n'
            usrPrompt = 0
            main()
        return generatedAddress
    else:
        return 'Entry Error'

def delMilAddr(): #Generate address
    global usrPrompt
    try:
        response = api.listAddresses2()
        # if api is too old just return then fail
        if "API Error 0020" in response: return
        addresses = json.loads(response)
        for entry in addresses['addresses']:
            if entry['label'].decode('base64')[:6] == "random":
                api.deleteAddress(entry['address'])
    except:
        print '\n     Connection Error\n'
        usrPrompt = 0
        main()

def genMilAddr(): #Generate address
    global usrPrompt
    maxn = 0
    try:
        response = api.listAddresses2()
        if "API Error 0020" in response: return
        addresses = json.loads(response)
        for entry in addresses['addresses']:
            if entry['label'].decode('base64')[:6] == "random":
                newn = int(entry['label'].decode('base64')[6:])
                if maxn < newn:
                    maxn = newn
    except:
        print "\n Some error\n"
    print "\n    Starting at " + str(maxn) + "\n"
    for i in range(maxn, 10000):
        lbl = "random" + str(i)
        addressLabel = lbl.encode('base64')
        try:
            generatedAddress = api.createRandomAddress(addressLabel)
        except:
            print '\n     Connection Error\n'
            usrPrompt = 0
            main()

def saveFile(fileName, fileData): #Allows attachments and messages/broadcats to be saved

    #This section finds all invalid characters and replaces them with ~
    fileName = fileName.replace(" ", "")
    fileName = fileName.replace("/", "~")
    #fileName = fileName.replace("\\", "~") How do I get this to work...?
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
        
    filePath = directory +'/'+ fileName

    '''try: #Checks if file already exists
        with open(filePath):
            print 'File Already Exists'
            return
    except IOError: pass'''


    f = open(filePath, 'wb+') #Begin saving to file
    f.write(fileData.decode("base64"))
    f.close

    print '\n     Successfully saved '+ filePath + '\n'

def attachment(): #Allows users to attach a file to their message or broadcast
    theAttachmentS = ''
    
    while True:

        isImage = False
        theAttachment = ''
        
        while True:#loops until valid path is entered
            filePath = userInput('\nPlease enter the path to the attachment or just the attachment name if in this folder.')  

            try:
                with open(filePath): break
            except IOError:
                print '\n     %s was not found on your filesystem or can not be opened.\n' % filePath
                pass

        #print filesize, and encoding estimate with confirmation if file is over X size (1mb?)
        invSize = os.path.getsize(filePath)
        invSize = (invSize / 1024) #Converts to kilobytes
        round(invSize,2) #Rounds to two decimal places

        if (invSize > 500.0):#If over 500KB
            print '\n     WARNING:The file that you are trying to attach is ', invSize, 'KB and will take considerable time to send.\n'
            uInput = userInput('Are you sure you still want to attach it, (Y)es or (N)o?').lower()

            if uInput != "y":
                print '\n     Attachment discarded.\n'
                return ''
        elif (invSize > 184320.0): #If larger than 180MB, discard.
            print '\n     Attachment too big, maximum allowed size:180MB\n'
            main()
        
        pathLen = len(str(ntpath.basename(filePath))) #Gets the length of the filepath excluding the filename
        fileName = filePath[(len(str(filePath)) - pathLen):] #reads the filename
            
        filetype = imghdr.what(filePath) #Tests if it is an image file
        if filetype is not None:
            print '\n     ---------------------------------------------------'
            print '     Attachment detected as an Image.'
            print '     <img> tags will automatically be included,'
            print '     allowing the recipient to view the image'
            print '     using the "View HTML code..." option in Bitmessage.'
            print '     ---------------------------------------------------\n'
            isImage = True
            time.sleep(2)
            
        print '\n     Encoding Attachment, Please Wait ...\n' #Alert the user that the encoding process may take some time.
        
        with open(filePath, 'rb') as f: #Begin the actual encoding
            data = f.read(188743680) #Reads files up to 180MB, the maximum size for Bitmessage.
            data = data.encode("base64")

        if (isImage == True): #If it is an image, include image tags in the message
            theAttachment = """
<!-- Note: Image attachment below. Please use the right click "View HTML code ..." option to view it. -->
<!-- Sent using Bitmessage Daemon. https://github.com/Dokument/PyBitmessage-Daemon -->
 
Filename:%s 
Filesize:%sKB 
Encoding:base64 
 
<center>
    <div id="image">
        <img alt = "%s" src='data:image/%s;base64, %s' />
    </div>
</center>""" % (fileName,invSize,fileName,filetype,data)
        else: #Else it is not an image so do not include the embedded image code.
            theAttachment = """
<!-- Note: File attachment below. Please use a base64 decoder, or Daemon, to save it. -->
<!-- Sent using Bitmessage Daemon. https://github.com/Dokument/PyBitmessage-Daemon -->
 
Filename:%s 
Filesize:%sKB 
Encoding:base64 
 
<attachment alt = "%s" src='data:file/%s;base64, %s' />""" % (fileName,invSize,fileName,fileName,data)

        uInput = userInput('Would you like to add another attachment, (Y)es or (N)o?').lower()

        if (uInput == 'y' or uInput == 'yes'):#Allows multiple attachments to be added to one message
            theAttachmentS = str(theAttachmentS) + str(theAttachment)+ '\n\n'
        elif (uInput == 'n' or uInput == 'no'):
            break
        
    theAttachmentS = theAttachmentS + theAttachment
    return theAttachmentS

def sendMsg(toAddress, fromAddress, subject, message): #With no arguments sent, sendMsg fills in the blanks. subject and message must be encoded before they are passed.
    global usrPrompt
    if (validAddress(toAddress)== False):
        while True:
            toAddress = userInput("What is the To Address?")

            if (toAddress == "c"):
                usrPrompt = 1
                print ' '
                main()
            elif (validAddress(toAddress)== False):
                print '\n     Invalid Address. "c" to cancel. Please try again.\n'
            else:
                break
        
        
    if (validAddress(fromAddress)== False):
        try:            
            jsonAddresses = json.loads(api.listAddresses())
            numAddresses = len(jsonAddresses['addresses']) #Number of addresses
        except:
            print '\n     Connection Error\n'
            usrPrompt = 0
            main()
        
        if (numAddresses > 1): #Ask what address to send from if multiple addresses
            found = False
            while True:
                print ' '
                fromAddress = userInput("Enter an Address or Address Label to send from.")

                if fromAddress == "exit":
                    usrPrompt = 1
                    main()

                for addNum in range (0, numAddresses): #processes all of the addresses
                    label = jsonAddresses['addresses'][addNum]['label']
                    address = jsonAddresses['addresses'][addNum]['address']
                    #stream = jsonAddresses['addresses'][addNum]['stream']
                    #enabled = jsonAddresses['addresses'][addNum]['enabled']
                    if (fromAddress == label): #address entered was a label and is found
                        fromAddress = address
                        found = True
                        break
                
                if (found == False):
                    if(validAddress(fromAddress)== False):
                        print '\n     Invalid Address. Please try again.\n'
                    
                    else:
                        for addNum in range (0, numAddresses): #processes all of the addresses
                            #label = jsonAddresses['addresses'][addNum]['label']
                            address = jsonAddresses['addresses'][addNum]['address']
                            #stream = jsonAddresses['addresses'][addNum]['stream']
                            #enabled = jsonAddresses['addresses'][addNum]['enabled']
                            if (fromAddress == address): #address entered was a found in our addressbook.
                                found = True
                                break
                            
                        if (found == False):
                            print '\n     The address entered is not one of yours. Please try again.\n'
                
                if (found == True):
                    break #Address was found
        
        else: #Only one address in address book
            print '\n     Using the only address in the addressbook to send from.\n'
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
        print '\n     Message Status:', api.getStatus(ackData), '\n'
    except:
        print '\n     Connection Error\n'
        usrPrompt = 0
        main()


def sendBrd(fromAddress, subject, message): #sends a broadcast
    global usrPrompt
    if (fromAddress == ''):

        try:
            jsonAddresses = json.loads(api.listAddresses())
            numAddresses = len(jsonAddresses['addresses']) #Number of addresses
        except:
            print '\n     Connection Error\n'
            usrPrompt = 0
            main()
        
        if (numAddresses > 1): #Ask what address to send from if multiple addresses
            found = False
            while True:
                fromAddress = userInput("\nEnter an Address or Address Label to send from.")

                if fromAddress == "exit":
                    usrPrompt = 1
                    main()

                for addNum in range (0, numAddresses): #processes all of the addresses
                    label = jsonAddresses['addresses'][addNum]['label']
                    address = jsonAddresses['addresses'][addNum]['address']
                    #stream = jsonAddresses['addresses'][addNum]['stream']
                    #enabled = jsonAddresses['addresses'][addNum]['enabled']
                    if (fromAddress == label): #address entered was a label and is found
                        fromAddress = address
                        found = True
                        break
                
                if (found == False):
                    if(validAddress(fromAddress)== False):
                        print '\n     Invalid Address. Please try again.\n'
                    
                    else:
                        for addNum in range (0, numAddresses): #processes all of the addresses
                            #label = jsonAddresses['addresses'][addNum]['label']
                            address = jsonAddresses['addresses'][addNum]['address']
                            #stream = jsonAddresses['addresses'][addNum]['stream']
                            #enabled = jsonAddresses['addresses'][addNum]['enabled']
                            if (fromAddress == address): #address entered was a found in our addressbook.
                                found = True
                                break
                            
                        if (found == False):
                            print '\n     The address entered is not one of yours. Please try again.\n'
                
                if (found == True):
                    break #Address was found
        
        else: #Only one address in address book
            print '\n     Using the only address in the addressbook to send from.\n'
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
        print '\n     Message Status:', api.getStatus(ackData), '\n'
    except:
        print '\n     Connection Error\n'
        usrPrompt = 0
        main()

def inbox(unreadOnly = False): #Lists the messages by: Message Number, To Address Label, From Address Label, Subject, Received Time)
    global usrPrompt
    try:
        inboxMessages = json.loads(api.getAllInboxMessages())
        numMessages = len(inboxMessages['inboxMessages'])
    except:
        print '\n     Connection Error\n'
        usrPrompt = 0
        main()

    messagesPrinted = 0
    messagesUnread = 0
    for msgNum in range (0, numMessages): #processes all of the messages in the inbox
        message = inboxMessages['inboxMessages'][msgNum]
        # if we are displaying all messages or if this message is unread then display it
        if not unreadOnly or not message['read']:
            print '     -----------------------------------\n'
            print '     Message Number:',msgNum #Message Number
            print '     To:', getLabelForAddress(message['toAddress']) #Get the to address
            print '     From:', getLabelForAddress(message['fromAddress']) #Get the from address
            print '     Subject:', message['subject'].decode('base64') #Get the subject
            print '     Received:', datetime.datetime.fromtimestamp(float(message['receivedTime'])).strftime('%Y-%m-%d %H:%M:%S')
            messagesPrinted += 1
            if not message['read']: messagesUnread += 1

        if (messagesPrinted%20 == 0 and messagesPrinted != 0):
            uInput = userInput('(Press Enter to continue or type (Exit) to return to the main menu.)').lower()
            
    print '\n     -----------------------------------'
    print '     There are %d unread messages of %d messages in the inbox.' % (messagesUnread, numMessages)
    print '     -----------------------------------\n'

def outbox():
    global usrPrompt
    try:
        outboxMessages = json.loads(api.getAllSentMessages())
        numMessages = len(outboxMessages['sentMessages'])
    except:
        print '\n     Connection Error\n'
        usrPrompt = 0
        main()

    for msgNum in range (0, numMessages): #processes all of the messages in the outbox
        print '\n     -----------------------------------\n'
        print '     Message Number:',msgNum #Message Number
        #print '     Message ID:', outboxMessages['sentMessages'][msgNum]['msgid']
        print '     To:', getLabelForAddress(outboxMessages['sentMessages'][msgNum]['toAddress']) #Get the to address
        print '     From:', getLabelForAddress(outboxMessages['sentMessages'][msgNum]['fromAddress']) #Get the from address
        print '     Subject:', outboxMessages['sentMessages'][msgNum]['subject'].decode('base64') #Get the subject
        print '     Status:', outboxMessages['sentMessages'][msgNum]['status'] #Get the subject
        
        print '     Last Action Time:', datetime.datetime.fromtimestamp(float(outboxMessages['sentMessages'][msgNum]['lastActionTime'])).strftime('%Y-%m-%d %H:%M:%S')

        if (msgNum%20 == 0 and msgNum != 0):
            uInput = userInput('(Press Enter to continue or type (Exit) to return to the main menu.)').lower()

    print '\n     -----------------------------------'
    print '     There are ',numMessages,' messages in the outbox.'
    print '     -----------------------------------\n'

def readSentMsg(msgNum): #Opens a sent message for reading
    global usrPrompt
    try:
        outboxMessages = json.loads(api.getAllSentMessages())
        numMessages = len(outboxMessages['sentMessages'])
    except:
        print '\n     Connection Error\n'
        usrPrompt = 0
        main()
            
    print ' '

    if (msgNum >= numMessages):
        print '\n     Invalid Message Number.\n'
        main()

    #Begin attachment detection
    message = outboxMessages['sentMessages'][msgNum]['message'].decode('base64')

    while True: #Allows multiple messages to be downloaded/saved
        if (';base64,' in message): #Found this text in the message, there is probably an attachment.
            attPos= message.index(";base64,") #Finds the attachment position
            attEndPos = message.index("' />") #Finds the end of the attachment
            #attLen = attEndPos - attPos #Finds the length of the message


            if ('alt = "' in message): #We can get the filename too
                fnPos = message.index('alt = "') #Finds position of the filename
                fnEndPos = message.index('" src=') #Finds the end position
                #fnLen = fnEndPos - fnPos #Finds the length of the filename

                fileName = message[fnPos+7:fnEndPos]
            else:
                fnPos = attPos
                fileName = 'Attachment'

            uInput = userInput('\n     Attachment Detected. Would you like to save the attachment, (Y)es or (N)o?').lower()
            if (uInput == "y" or uInput == 'yes'):
                
                attachment = message[attPos+9:attEndPos]                    
                saveFile(fileName,attachment)

            message = message[:fnPos] + '~<Attachment data removed for easier viewing>~' + message[(attEndPos+4):]

        else:
            break
            
    #End attachment Detection
            
    print '\n     To:', getLabelForAddress(outboxMessages['sentMessages'][msgNum]['toAddress']) #Get the to address
    print '     From:', getLabelForAddress(outboxMessages['sentMessages'][msgNum]['fromAddress']) #Get the from address
    print '     Subject:', outboxMessages['sentMessages'][msgNum]['subject'].decode('base64') #Get the subject
    print '     Status:', outboxMessages['sentMessages'][msgNum]['status'] #Get the subject
    print '     Last Action Time:', datetime.datetime.fromtimestamp(float(outboxMessages['sentMessages'][msgNum]['lastActionTime'])).strftime('%Y-%m-%d %H:%M:%S')
    print '     Message:\n'
    print message #inboxMessages['inboxMessages'][msgNum]['message'].decode('base64')
    print ' '

def readMsg(msgNum): #Opens a message for reading
    global usrPrompt
    try:
        inboxMessages = json.loads(api.getAllInboxMessages())
        numMessages = len(inboxMessages['inboxMessages'])
    except:
        print '\n     Connection Error\n'
        usrPrompt = 0
        main()

    if (msgNum >= numMessages):
        print '\n     Invalid Message Number.\n'
        main()

    #Begin attachment detection
    message = inboxMessages['inboxMessages'][msgNum]['message'].decode('base64')

    while True: #Allows multiple messages to be downloaded/saved
        if (';base64,' in message): #Found this text in the message, there is probably an attachment.
            attPos= message.index(";base64,") #Finds the attachment position
            attEndPos = message.index("' />") #Finds the end of the attachment
            #attLen = attEndPos - attPos #Finds the length of the message


            if ('alt = "' in message): #We can get the filename too
                fnPos = message.index('alt = "') #Finds position of the filename
                fnEndPos = message.index('" src=') #Finds the end position
                #fnLen = fnEndPos - fnPos #Finds the length of the filename

                fileName = message[fnPos+7:fnEndPos]
            else:
                fnPos = attPos
                fileName = 'Attachment'

            uInput = userInput('\n     Attachment Detected. Would you like to save the attachment, (Y)es or (N)o?').lower()
            if (uInput == "y" or uInput == 'yes'):
                
                attachment = message[attPos+9:attEndPos]                    
                saveFile(fileName,attachment)

            message = message[:fnPos] + '~<Attachment data removed for easier viewing>~' + message[(attEndPos+4):]

        else:
            break
            
    #End attachment Detection
    print '\n     To:', getLabelForAddress(inboxMessages['inboxMessages'][msgNum]['toAddress']) #Get the to address
    print '     From:', getLabelForAddress(inboxMessages['inboxMessages'][msgNum]['fromAddress']) #Get the from address
    print '     Subject:', inboxMessages['inboxMessages'][msgNum]['subject'].decode('base64') #Get the subject
    print '     Received:',datetime.datetime.fromtimestamp(float(inboxMessages['inboxMessages'][msgNum]['receivedTime'])).strftime('%Y-%m-%d %H:%M:%S')
    print '     Message:\n'
    print message #inboxMessages['inboxMessages'][msgNum]['message'].decode('base64')
    print ' '
    return inboxMessages['inboxMessages'][msgNum]['msgid']

def replyMsg(msgNum,forwardORreply): #Allows you to reply to the message you are currently on. Saves typing in the addresses and subject.
    global usrPrompt
    forwardORreply = forwardORreply.lower() #makes it lowercase
    try:
        inboxMessages = json.loads(api.getAllInboxMessages())
    except:
        print '\n     Connection Error\n'
        usrPrompt = 0
        main()
    
    fromAdd = inboxMessages['inboxMessages'][msgNum]['toAddress']#Address it was sent To, now the From address
    message = inboxMessages['inboxMessages'][msgNum]['message'].decode('base64') #Message that you are replying too.
    
    subject = inboxMessages['inboxMessages'][msgNum]['subject']
    subject = subject.decode('base64')
    
    if (forwardORreply == 'reply'):
        toAdd = inboxMessages['inboxMessages'][msgNum]['fromAddress'] #Address it was From, now the To address
        subject = "Re: " + subject
        
    elif (forwardORreply == 'forward'):
        subject = "Fwd: " + subject
        
        while True:
            toAdd = userInput("What is the To Address?")

            if (toAdd == "c"):
                usrPrompt = 1
                print ' '
                main()
            elif (validAddress(toAdd)== False):
                print '\n     Invalid Address. "c" to cancel. Please try again.\n'
            else:
                break
    else:
        print '\n     Invalid Selection. Reply or Forward only'
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

def delMsg(msgNum): #Deletes a specified message from the inbox
    global usrPrompt
    try:
        inboxMessages = json.loads(api.getAllInboxMessages())
        msgId = inboxMessages['inboxMessages'][int(msgNum)]['msgid'] #gets the message ID via the message index number
        
        msgAck = api.trashMessage(msgId)
    except:
        print '\n     Connection Error\n'
        usrPrompt = 0
        main()
        
    return msgAck

def delSentMsg(msgNum): #Deletes a specified message from the outbox
    global usrPrompt
    try:
        outboxMessages = json.loads(api.getAllSentMessages())
        msgId = outboxMessages['sentMessages'][int(msgNum)]['msgid'] #gets the message ID via the message index number
        msgAck = api.trashSentMessage(msgId)
    except:
        print '\n     Connection Error\n'
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
        if "API Error 0020" in response: return
        addressBook = json.loads(response)
        for entry in addressBook['addresses']:
            if entry['address'] not in knownAddresses:
                knownAddresses[entry['address']] = "%s (%s)" % (entry['label'].decode('base64'), entry['address'])
    except:
        print '\n     Connection Error\n'
        usrPrompt = 0
        main()

    # add from my addresses
    try:
        response = api.listAddresses2()
        # if api is too old just return then fail
        if "API Error 0020" in response: return
        addresses = json.loads(response)
        for entry in addresses['addresses']:
            if entry['address'] not in knownAddresses:
                knownAddresses[entry['address']] = "%s (%s)" % (entry['label'].decode('base64'), entry['address'])
    except:
        print '\n     Connection Error\n'
        usrPrompt = 0
        main()

def listAddressBookEntries():
    try:
        response = api.listAddressBookEntries()
        if "API Error" in response:
            return getAPIErrorCode(response)
        addressBook = json.loads(response)
        print
        print '     --------------------------------------------------------------'
        print '     |        Label       |                Address                |'
        print '     |--------------------|---------------------------------------|'
        for entry in addressBook['addresses']:
            label = entry['label'].decode('base64')
            address = entry['address']
            if (len(label) > 19): label = label[:16] + '...'
            print '     | ' + label.ljust(19) + '| ' + address.ljust(37) + ' |'
        print '     --------------------------------------------------------------'
        print

    except:
        print '\n     Connection Error\n'
        usrPrompt = 0
        main()

def addAddressToAddressBook(address, label):
    try:
        response = api.addAddressBookEntry(address, label.encode('base64'))
        if "API Error" in response:
            return getAPIErrorCode(response)
    except:
        print '\n     Connection Error\n'
        usrPrompt = 0
        main()

def deleteAddressFromAddressBook(address):
    try:
        response = api.deleteAddressBookEntry(address)
        if "API Error" in response:
            return getAPIErrorCode(response)
    except:
        print '\n     Connection Error\n'
        usrPrompt = 0
        main()

def getAPIErrorCode(response):
    if "API Error" in response:
        # if we got an API error return the number by getting the number
        # after the second space and removing the trailing colon
        return int(response.split()[2][:-1])

def markMessageRead(messageID):
    try:
        response = api.getInboxMessageByID(messageID, True)
        if "API Error" in response:
            return getAPIErrorCode(response)
    except:
        print '\n     Connection Error\n'
        usrPrompt = 0
        main()

def markMessageUnread(messageID):
    try:
        response = api.getInboxMessageByID(messageID, False)
        if "API Error" in response:
            return getAPIErrorCode(response)
    except:
        print '\n     Connection Error\n'
        usrPrompt = 0
        main()

def markAllMessagesRead():
    try:
        inboxMessages = json.loads(api.getAllInboxMessages())['inboxMessages']
    except:
        print '\n     Connection Error\n'
        usrPrompt = 0
        main()
    for message in inboxMessages:
        if not message['read']:
            markMessageRead(message['msgid'])

def markAllMessagesUnread():
    try:
        inboxMessages = json.loads(api.getAllInboxMessages())['inboxMessages']
    except:
        print '\n     Connection Error\n'
        usrPrompt = 0
        main()
    for message in inboxMessages:
        if message['read']:
            markMessageUnread(message['msgid'])

def clientStatus():
    try:
        clientStatus = json.loads(api.clientStatus())
    except:
        print '\n     Connection Error\n'
        usrPrompt = 0
        main()
    print "\nnetworkStatus: " + clientStatus['networkStatus'] + "\n"
    print "\nnetworkConnections: " + str(clientStatus['networkConnections']) + "\n"
    print "\nnumberOfPubkeysProcessed: " + str(clientStatus['numberOfPubkeysProcessed']) + "\n"
    print "\nnumberOfMessagesProcessed: " + str(clientStatus['numberOfMessagesProcessed']) + "\n"
    print "\nnumberOfBroadcastsProcessed: " + str(clientStatus['numberOfBroadcastsProcessed']) + "\n"


def UI(usrInput): #Main user menu
    global usrPrompt
    
    if usrInput == "help" or usrInput == "h" or usrInput == "?":
        print ' '
        print '     -------------------------------------------------------------------------'
        print '     |        https://github.com/Dokument/PyBitmessage-Daemon                |'
        print '     |-----------------------------------------------------------------------|'
        print '     | Command                | Description                                  |'
        print '     |------------------------|----------------------------------------------|'
        print '     | help                   | This help file.                              |'
        print '     | apiTest                | Tests the API                                |'
        print '     | addInfo                | Returns address information (If valid)       |'        
        print '     | bmSettings             | BitMessage settings                          |'
        print '     | exit                   | Use anytime to return to main menu           |'
        print '     | quit                   | Quits the program                            |'
        print '     |------------------------|----------------------------------------------|'
        print '     | listAddresses          | Lists all of the users addresses             |'
        print '     | generateAddress        | Generates a new address                      |'
        print '     | getAddress             | Get determinist address from passphrase      |'
        print '     |------------------------|----------------------------------------------|'
        print '     | listAddressBookEntries | Lists entries from the Address Book          |'
        print '     | addAddressBookEntry    | Add address to the Address Book              |'
        print '     | deleteAddressBookEntry | Deletes address from the Address Book        |'
        print '     |------------------------|----------------------------------------------|'
        print '     | subscribe              | Subscribes to an address                     |'
        print '     | unsubscribe            | Unsubscribes from an address                 |'
       #print '     | listSubscriptions      | Lists all of the subscriptions.              |'
        print '     |------------------------|----------------------------------------------|'
	print '     | create                 | Creates a channel                            |'
        print '     | join                   | Joins a channel                              |'
        print '     | leave                  | Leaves a channel                             |'
	print '     |------------------------|----------------------------------------------|'
        print '     | inbox                  | Lists the message information for the inbox  |'
        print '     | outbox                 | Lists the message information for the outbox |'
        print '     | send                   | Send a new message or broadcast              |'
        print '     | unread                 | Lists all unread inbox messages              |'
        print '     | read                   | Reads a message from the inbox or outbox     |'
        print '     | save                   | Saves message to text file                   |'
        print '     | delete                 | Deletes a message or all messages            |'
        print '     -------------------------------------------------------------------------'
        print ' '
        main()

    elif usrInput == "apitest": #tests the API Connection.
        if (apiTest() == True):
            print '\n     API connection test has: PASSED\n'
        else:
            print '\n     API connection test has: FAILED\n'
        main()

    elif usrInput == "addinfo":
        tmp_address = userInput('\nEnter the Bitmessage Address.')
        address_information = api.decodeAddress(tmp_address)
        address_information = eval(address_information)

        print '\n------------------------------'
        
        if 'success' in str(address_information.get('status')).lower():
            print ' Valid Address'            
            print ' Address Version: %s' % str(address_information.get('addressVersion'))
            print ' Stream Number: %s' % str(address_information.get('streamNumber'))
        else:
            print ' Invalid Address !'

        print '------------------------------\n'
        main()
        
    elif usrInput == "bmsettings": #tests the API Connection.
        bmSettings()
        print ' '
        main()
        
    elif usrInput == "quit": #Quits the application
        print '\n     Bye\n'
        sys.exit()
        os.exit()
        
    elif usrInput == "listaddresses": #Lists all of the identities in the addressbook
        listAdd()
        main()
        
    elif usrInput == "generateaddress": #Generates a new address
        uInput = userInput('\nWould you like to create a (D)eterministic or (R)andom address?').lower()

        if uInput == "d" or uInput == "determinstic": #Creates a deterministic address
            deterministic = True

            #lbl = raw_input('Label the new address:') #currently not possible via the api
            lbl = ''
            passphrase = userInput('Enter the Passphrase.')#.encode('base64')
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
                print '\n     Invalid input\n'
                main()

            
        elif uInput == "r" or uInput == "random": #Creates a random address with user-defined label
            deterministic = False
            null = ''
            lbl = userInput('Enter the label for the new address.')
            
            print genAdd(lbl,deterministic, null,null, null, null, null)
            main()
            
        else:
            print '\n     Invalid input\n'
            main()
        
    elif usrInput == "getaddress": #Gets the address for/from a passphrase
        phrase = userInput("Enter the address passphrase.")
        print '\n     Working...\n'
        #vNumber = int(raw_input("Enter the address version number:"))
        #sNumber = int(raw_input("Enter the address stream number:"))

        address = getAddress(phrase,4,1)#,vNumber,sNumber)
        print ('\n     Address: ' + address + '\n')

        usrPrompt = 1
        main()

    elif usrInput == "subscribe": #Subsribe to an address
        subscribe()
        usrPrompt = 1
        main()
    elif usrInput == "unsubscribe": #Unsubscribe from an address
        unsubscribe()
        usrPrompt = 1
        main()
    elif usrInput == "listsubscriptions": #Unsubscribe from an address
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
        print '\n     Loading...\n'
        inbox()
        main()

    elif usrInput == "unread":
        print '\n     Loading...\n'
        inbox(True)
        main()

    elif usrInput == "outbox":
        print '\n     Loading...\n'
        outbox()
        main()

    elif usrInput == 'send': #Sends a message or broadcast
        uInput = userInput('Would you like to send a (M)essage or (B)roadcast?').lower()

        if (uInput == 'm' or uInput == 'message'):
            null = ''
            sendMsg(null,null,null,null)
            main()
        elif (uInput =='b' or uInput == 'broadcast'):
            null = ''
            sendBrd(null,null,null)
            main()


    elif usrInput == "read": #Opens a message from the inbox for viewing. 
        
        uInput = userInput("Would you like to read a message from the (I)nbox or (O)utbox?").lower()

        if (uInput != 'i' and uInput != 'inbox' and uInput != 'o' and uInput != 'outbox'):
            print '\n     Invalid Input.\n'
            usrPrompt = 1
            main()

        msgNum = int(userInput("What is the number of the message you wish to open?"))

        if (uInput == 'i' or uInput == 'inbox'):
            print '\n     Loading...\n'
            messageID = readMsg(msgNum)

            uInput = userInput("\nWould you like to keep this message unread, (Y)es or (N)o?").lower()

            if not (uInput == 'y' or uInput == 'yes'):
                markMessageRead(messageID)
                usrPrompt = 1

            uInput = userInput("\nWould you like to (D)elete, (F)orward, (R)eply to, or (Exit) this message?").lower()

            if (uInput == 'r' or uInput == 'reply'):
                print '\n     Loading...\n'
                print ' '
                replyMsg(msgNum,'reply')
                usrPrompt = 1
                
            elif (uInput == 'f' or uInput == 'forward'):
                print '\n     Loading...\n'
                print ' '
                replyMsg(msgNum,'forward')
                usrPrompt = 1

            elif (uInput == "d" or uInput == 'delete'):
                uInput = userInput("Are you sure, (Y)es or (N)o?").lower()#Prevent accidental deletion

                if uInput == "y":
                    delMsg(msgNum)
                    print '\n     Message Deleted.\n'
                    usrPrompt = 1
                else:
                    usrPrompt = 1
            else:
                print '\n     Invalid entry\n'
                usrPrompt = 1
                
        elif (uInput == 'o' or uInput == 'outbox'):
            readSentMsg(msgNum)

            uInput = userInput("Would you like to (D)elete, or (Exit) this message?").lower() #Gives the user the option to delete the message

            if (uInput == "d" or uInput == 'delete'):
                uInput = userInput('Are you sure, (Y)es or (N)o?').lower() #Prevent accidental deletion

                if uInput == "y":
                    delSentMsg(msgNum)
                    print '\n     Message Deleted.\n'
                    usrPrompt = 1
                else:
                    usrPrompt = 1
            else:
                print '\n     Invalid Entry\n'
                usrPrompt = 1
                
        main()
        
    elif usrInput == "save":
        
        uInput = userInput("Would you like to save a message from the (I)nbox or (O)utbox?").lower()

        if (uInput != 'i' and uInput == 'inbox' and uInput != 'o' and uInput == 'outbox'):
            print '\n     Invalid Input.\n'
            usrPrompt = 1
            main()

        if (uInput == 'i' or uInput == 'inbox'):
            inboxMessages = json.loads(api.getAllInboxMessages())
            numMessages = len(inboxMessages['inboxMessages'])

            while True:
                msgNum = int(userInput("What is the number of the message you wish to save?"))

                if (msgNum >= numMessages):
                    print '\n     Invalid Message Number.\n'
                else:
                    break
            
            subject =  inboxMessages['inboxMessages'][msgNum]['subject'].decode('base64') 
            message =  inboxMessages['inboxMessages'][msgNum]['message']#Don't decode since it is done in the saveFile function
            
        elif (uInput == 'o' or uInput == 'outbox'):      
            outboxMessages = json.loads(api.getAllSentMessages())
            numMessages = len(outboxMessages['sentMessages'])

            while True:
                msgNum = int(userInput("What is the number of the message you wish to save?"))

                if (msgNum >= numMessages):
                    print '\n     Invalid Message Number.\n'
                else:
                    break
            
            subject =  outboxMessages['sentMessages'][msgNum]['subject'].decode('base64') 
            message =  outboxMessages['sentMessages'][msgNum]['message']#Don't decode since it is done in the saveFile function
        
        subject = subject +'.txt'
        saveFile(subject,message)
        
        usrPrompt = 1
        main()
        
    elif usrInput == "delete": #will delete a message from the system, not reflected on the UI.
        
        uInput = userInput("Would you like to delete a message from the (I)nbox or (O)utbox?").lower()

        if (uInput == 'i' or uInput == 'inbox'):  
            inboxMessages = json.loads(api.getAllInboxMessages())
            numMessages = len(inboxMessages['inboxMessages'])
            
            while True:           
                msgNum = userInput('Enter the number of the message you wish to delete or (A)ll to empty the inbox.').lower()

                if (msgNum == 'a' or msgNum == 'all'):
                    break
                elif (int(msgNum) >= numMessages):
                    print '\n     Invalid Message Number.\n'
                else:
                    break
                    
            uInput = userInput("Are you sure, (Y)es or (N)o?").lower()#Prevent accidental deletion

            if uInput == "y":
                if (msgNum == 'a' or msgNum == 'all'):
                    print ' '
                    for msgNum in range (0, numMessages): #processes all of the messages in the inbox
                        print '     Deleting message ', msgNum+1, ' of ', numMessages
                        delMsg(0)

                    print '\n     Inbox is empty.'
                    usrPrompt = 1
                else:
                    delMsg(int(msgNum))
                    
                print '\n     Notice: Message numbers may have changed.\n'
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
                    print '\n     Invalid Message Number.\n'
                else:
                    break

            uInput = userInput("Are you sure, (Y)es or (N)o?").lower()#Prevent accidental deletion

            if uInput == "y":
                if (msgNum == 'a' or msgNum == 'all'):
                    print ' '
                    for msgNum in range (0, numMessages): #processes all of the messages in the outbox
                        print '     Deleting message ', msgNum+1, ' of ', numMessages
                        delSentMsg(0)

                    print '\n     Outbox is empty.'
                    usrPrompt = 1
                else:
                    delSentMsg(int(msgNum))
                print '\n     Notice: Message numbers may have changed.\n'
                main()
            else:
                usrPrompt = 1
        else:
            print '\n     Invalid Entry.\n'
            userPrompt = 1
            main()

    elif usrInput == "exit":
        print '\n     You are already at the main menu. Use "quit" to quit.\n'
        usrPrompt = 1
        main()

    elif usrInput == "listaddressbookentries":
        res = listAddressBookEntries()
        if res == 20: print '\n     Error: API function not supported.\n'
        usrPrompt = 1
        main()

    elif usrInput == "addaddressbookentry":
        address = userInput('Enter address')
        label = userInput('Enter label')
        res = addAddressToAddressBook(address, label)
        if res == 16: print '\n     Error: Address already exists in Address Book.\n'
        if res == 20: print '\n     Error: API function not supported.\n'
        usrPrompt = 1
        main()

    elif usrInput == "deleteaddressbookentry":
        address = userInput('Enter address')
        res = deleteAddressFromAddressBook(address)
        if res == 20: print '\n     Error: API function not supported.\n'
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
        print '\n     "',usrInput,'" is not a command.\n'
        usrPrompt = 1
        main()
    
def main():
    global api
    global usrPrompt
    
    if (usrPrompt == 0):
        print '\n     ------------------------------'
        print '     | Bitmessage Daemon by .dok  |'
        print '     | Version 0.2.6 for BM 0.3.5 |'
        print '     ------------------------------'
        api = xmlrpclib.ServerProxy(apiData()) #Connect to BitMessage using these api credentials

        if (apiTest() == False):
            print '\n     ****************************************************************'
            print '        WARNING: You are not connected to the Bitmessage client.'
            print '     Either Bitmessage is not running or your settings are incorrect.'
            print '     Use the command "apiTest" or "bmSettings" to resolve this issue.'
            print '     ****************************************************************\n'
            
        print 'Type (H)elp for a list of commands.' #Startup message
        usrPrompt = 2
        
        #if (apiTest() == False):#Preform a connection test #taken out until I get the error handler working
        #    print '*************************************'
        #    print 'WARNING: No connection to Bitmessage.'
        #    print '*************************************'
        #    print ' '
    elif (usrPrompt == 1):
        print '\nType (H)elp for a list of commands.' #Startup message
        usrPrompt = 2

    try:
        UI((raw_input('>').lower()).replace(" ", ""))
    except EOFError:
        UI("quit")

if __name__ == "__main__":
    main()
