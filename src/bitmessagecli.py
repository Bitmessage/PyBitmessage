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

import imghdr
import ntpath
import json
import sys
import os
import xmlrpclib
import socket
import time
import datetime
import inspect
import re

from bmconfigparser import BMConfigParser
from collections import OrderedDict
import ConfigParser

api = ''
keysName = 'keys.dat'
keysPath = 'keys.dat'
usrPrompt = 0  # 0 = First Start, 1 = prompt, 2 = no prompt if the program is starting up
knownAddresses = dict({'addresses': []})
cmdStr = 'buildknownaddresses'

# menu by this order
cmdTbl = OrderedDict()
cmdTbl['Command'] = 'Description'
cmdTbl['s1'] = '-'
cmdTbl['help'] = 'This help'
cmdTbl['daemon'] = 'Try to start PyBitmessage daemon locally'
cmdTbl['apiTest'] = 'Daemon API connection tests'
cmdTbl['status'] = 'Get the summary of running daemon'
cmdTbl['addInfo'] = 'Request detailed info to a address'
cmdTbl['bmSettings'] = 'PyBitmessage settings "keys.dat"'
cmdTbl['exit'] = 'Use anytime to return to main menu'
cmdTbl['quit'] = 'Quit this CLI'
cmdTbl['shutdown'] = 'Shutdown the connectable daemon via. API'
cmdTbl['s2'] = '-'
cmdTbl['listAddresses'] = 'List user\'s addresse(s) (Senders)'
cmdTbl['generateAddress'] = 'Generate a new sender address'
cmdTbl['getAddress'] = 'Get determinist address from passphrase'
cmdTbl['s3'] = '-'
cmdTbl['listAddressBookEntries'] = 'List the "Address Book" (Contacts)'
cmdTbl['addAddressBookEntry'] = 'Add a address to the "Address Book"'
cmdTbl['deleteAddressBookEntry'] = 'Delete a address from the "Address Book"'
cmdTbl['s4'] = '-'
cmdTbl['listsubscrips'] = 'List subscriped addresses'
cmdTbl['subscribe'] = 'Subscribes to an address'
cmdTbl['unsubscribe'] = 'Unsubscribe from an address'
cmdTbl['s5'] = '-'
cmdTbl['create'] = 'Create a channel'
cmdTbl['join'] = 'Join to a channel'
cmdTbl['leave'] = 'Leave from a channel'
cmdTbl['s6'] = '-'
cmdTbl['buildKnownAddresses'] = 'Retrieve addresse(s) label for message heads'
cmdTbl['s7'] = '-'
cmdTbl['inbox'] = 'List all inbox message heads'
cmdTbl['outbox'] = 'List all outbox message heads heads'
cmdTbl['news'] = 'List all "unread" inbox message heads'
cmdTbl['send'] = 'Send out new message or broadcast'
cmdTbl['s8'] = '-'
cmdTbl['read'] = 'Read a message from in(out)box'
cmdTbl['readAll'] = 'Mard "read" for all inbox message(s)'
cmdTbl['unreadAll'] = 'Mark "unread" for all inbox message(s)'
cmdTbl['s9'] = '-'
cmdTbl['save'] = 'Save(Dump) a in(out)box message to disk'
cmdTbl['delete'] = 'Delete a(ll) in(out)box messages from remote'
cmdShorts = dict()

retStrings = dict({'none': '', 'usercancel': '\n     User canceled.\n', 'invalidinput': '\n     Invalid input.\n', 'invalidindex': '\n     Invalid message index.\n', 'invalidaddr': '\n     Invalid address.\n', 'indexoutofbound': '\n     Reach end of index.\n', })
inputShorts = dict({'yes': ['y', 'yes'], 'no': ['n', 'no'], 'exit': ['e', 'ex', 'exit'], 'save': ['save', 's', 'sv'], 'deterministic': ['d', 'dt'], 'random': ['r', 'rd', 'random'], 'message': ['m', 'msg', 'message'], 'broadcast': ['b', 'br', 'brd', 'broadcast'], 'inbox': ['i', 'in', 'ib', 'inbox'], 'outbox': ['o', 'ou', 'out', 'ob', 'outbox'], 'dump': ['d', 'dp', 'dump'], 'save': ['s', 'sa', 'save'], 'reply': ['r', 'rp', 'reply'], 'forward': ['f', 'fw', 'forward'], 'delete': ['d', 'del', 'delete'], 'all': ['a', 'all'], })

inputs = dict()


def duplicated(out):

    global cmdShorts

    seen = dict()
    dups = list()
    dcmds = dict()
    for x in out:
        if x not in seen:
            seen[x] = 1
        else:
            if seen[x] == 1:
                dups.append(x)
            seen[x] += 1
    for x in dups:
        for cmd in cmdShorts:
            if x in cmdShorts[cmd]:
                dcmds[cmd] = cmdShorts[cmd]
    return dcmds


def cmdGuess():

    global cmdTbl, cmdShorts

    cmdWords = ['dae', 'mon', 'api', 'Test', 'fo', 'Set', 'tings', 'list', 'Addresses', 'gene', 'rate', 'dress', 'Address', 'Boo', 'Entries', 'entry', 'lete', 'subscrips', 'scribe', 'reate', 'oin', 'lea', 'build', 'Known', 'in', 'out', 'box', 'new', 'end', 'ead', 'eave', 'un', 've', 'ubs', 'shut', 'down', 'tatus', 'All', 'get', 'bke', 'quit', 'exit']
    cmdWords2 = ['api', 'Test', 'info', 'Settings', 'list', 'add', 'Addresses', 'gene', 'rate', 'Address', 'Boo', 'Entries', 'entry', 'lete', 'subscrips', 'scribe', 'reate', 'oin', 'lea', 'build', 'Known', 'inbox', 'outbox', 'box', 'new', 'end', 'ead', 'eave', 'ubs', 'shut', 'down', 'tatus', 'All', 'get', 'bke', 'creat', 'join', 'read', 'delete', 'news', 'send', 'uit', 'xit', 'un', 'lea', 've']
    cmdWords.sort(key=lambda item: (-len(item), item))
    cmdWords2.sort(key=lambda item: (-len(item), item))

    out = list()
    # shorten1
    for cmd in cmdTbl:
        lcmd = cmd.lower()
        for words in cmdWords:
            lwords = words.lower()
            lcmd = lcmd.replace(lwords, lwords[0], 1)
        cmdShorts[cmd] = [cmd.lower(), lcmd]
        out.append(lcmd)

    cmdShorts['help'] = list(['help', 'h', '?'])
    dcmds = duplicated(out)
    if any(dcmds):
        print '\n     cmdGuess Fail!'
        print '     duplicated =', dcmds
        print '     Change your "cmdWords1" please.\n'
        return False

    # shorten2
    for cmd in cmdTbl:
        lcmd = cmd.lower()
        for words in cmdWords2:
            lwords = words.lower()
            lcmd = lcmd.replace(lwords, lwords[0], 1)
        if lcmd not in cmdShorts[cmd]:
            if len(lcmd) < len(cmdShorts[cmd][1]):
                cmdShorts[cmd].insert(1, lcmd)
            else:
                cmdShorts[cmd].append(lcmd)
            out.append(lcmd)

    dcmds = duplicated(out)
    if any(dcmds):
        print '\n     cmdGuess Fail!'
        print '     duplicated =', dcmds
        print '     Change your "cmdWords2" please.\n'
        return False

    cmdShorts['Command'] = ''
    return True


def showCmdTbl():

    global cmdTbl, cmdShorts

    url = 'https://github.com/Dokument/PyBitmessage-Daemon'
    print ' '
    print ''.join([5 * ' ', 73 * '-'])
    print ''.join([5 * ' ', '|', url[:int(len(url)/2)].rjust(35), url[int(len(url)/2):].ljust(36), '|'])
    print ''.join([5 * ' ', 73 * '-'])
    for cmd in cmdTbl:
        lcmd = ('' if len(cmd) > 18 else cmd + ' ') + str(cmdShorts[cmd][1:])
        if len(lcmd) > 23:
            lcmd = lcmd[:20] + '...'
        des = cmdTbl[cmd]
        if len(des) > 45:
            des = des[:42] + '...'
        if des == '-':
            print ''.join([5 * ' ', '|', 24 * '-', '|', 46 * '-', '|'])
        else:
            print ''.join([5 * ' ',
                           '| ',
                            lcmd.ljust(23),
                            '| ',
                            des.ljust(45),
                            '|'])
    print ''.join([5 * ' ', 73 * '-'])


class InputException(Exception):
    def __init__(self, resKey):
        Exception.__init__(self, resKey)
        self.resKey =  resKey

    def __str__(self):
        return self.resKey


def inputAddress(prompt='What is the address?'):

    global usrPrompt, retStrings

    src = retStrings['invalidaddr']
    while True:
        address = userInput(prompt + '\nTry again or')
        if not validAddress(address):
            print src
            continue
        else:
            break

    return address


class BMAPIWrapperConectionException(Exception):
    def __init__(self, ex):
        Exception.__init__(self, ex)
        self.msg = str(ex)

    def __str__(self):
        return self.msg


class BMAPIWrapper(str):

    def __init__(self, conn='http://127.0.0.1:8442'):
        self.conn = conn
        print '     RPC initialed:', self.conn
        self.xmlrpc = xmlrpclib.ServerProxy(self.conn)

    def __getattr__(self, apiname):
        attr = getattr(self.xmlrpc, apiname)
        def wrapper(*args, **kwargs):
            error = 0
            result = ''
            errormsg =''
            try:
                response = attr(*args, **kwargs)
                # print response
                if apiname in ['add', 'helloWorld', 'statusBar', '']:
                    result = response
                else:
                    if "API Error" in response or 'RPC ' in response:
                        error = 1
                        errormsg = '\n     ' + response + '\n'
                    else:
                        try:
                            if apiname in ['getAllInboxMessageIDs', 'getAllInboxMessageIds']:
                                result = json.loads(response)['inboxMessageIds']
                            elif apiname in ['getInboxMessageByID', 'getInboxMessageById']:
                                result = json.loads(response)['inboxMessage']
                            elif apiname in ['GetAllInboxMessages', 'getInboxMessagesByReceiver', 'getInboxMessagesByAddress']:
                                result = json.loads(response)['inboxMessages']
                            elif apiname in ['getAllSentMessageIDs', 'getAllSentMessageIds']:
                                result = json.loads(response)['sentMessageIds']
                            elif apiname in ['getAllSentMessages', 'getSentMessagesByAddress', 'getSentMessagesBySender', 'getSentMessageByAckData']:
                                result = json.loads(response)['sentMessages']
                            elif apiname in ['getSentMessageByID', 'getSentMessageById']:
                                result = json.loads(response)['sentMessage']
                            elif apiname in ['listAddressBookEntries', 'listAddressbook', 'listAddresses', 'listAddressbook', 'createDeterministicAddresses']:
                                result = json.loads(response)['addresses']
                            elif apiname in ['listSubscriptions']:
                                result = json.loads(response)['subscriptions']
                            elif apiname in ['decodeAddress', 'clientStatus', 'getMessageDataByDestinationHash', 'getMessageDataByDestinationTag']:
                                result = json.loads(response)
                            elif apiname in ['addSubscription', 'deleteSubscription', 'createChan', 'joinChan', 'leaveChan', 'sendMessage', 'sendBroadcast', 'getStatus', 'trashMessage', 'trashInboxMessage', 'trashSentMessageByAckData', 'trashSentMessage', 'addAddressBookEntry', 'addAddressbook', 'deleteAddressBookEntry', 'deleteAddressbook', 'createRandomAddress', 'getDeterministicAddress', 'deleteAddress','disseminatePreEncryptedMsg', 'disseminatePubkey', 'deleteAndVacuum', 'shutdown']:
                                result = response
                            else:
                                error = 99
                                errormsg = '\n     BMAPIWrapper error: unexpected api.\n'
                        except ValueError as e:  # json.loads error
                            error = 2
                            result = response
                            errormsg = '\n     Server returns unexpected data, maybe a network problem there?\n'

            except (socket.error, xmlrpclib.ProtocolError) as e:  # Connection error
                error = -1
                result = ''
                errormsg = '\n     Connection error: %s.\n' % str(e)
            except Exception:  # Unexpected error
                error = -99
                result = ''
                errormsg = '\n     Unexpected error: %s.\n' % sys.exc_info()[0]

            # print json.dumps({'error': error, 'result': result, 'errormsg': errormsg})
            return {'error': error, 'result': result, 'errormsg': errormsg}

        return wrapper


def inputIndex(prompt='Input a index: ', maximum=-1, alter=[]):

    global usrPrompt, retStrings, retStrings

    while True:
        cinput = userInput(prompt + '\nTry again, (c) or').lower()
        try:
            if cinput == "c":
                cinput = '-1'
                raise InputException('usercancel')

            elif cinput in alter:
                break

            elif int(cinput) < 0 or (maximum >= 0 and int(cinput) > maximum):
                src = retStrings['invalidindex']
                print src

            else:
                break

        except InputException as e:
            raise InputException(e)

        except ValueError:
            src = retStrings['invalidinput']
            print src

    return cinput


def userInput(message):
    """Checks input for exit or quit. Also formats for input, etc"""

    global usrPrompt, cmdStr, retStrings

    stack = list(inspect.stack())
    where = ''.join([
        str(stack[3][2]),
        stack[3][3],
        str(stack[2][2]),
        stack[1][3],
        str(stack[1][2]),
        stack[3][3],
        cmdStr
        ])
    print ('\n%s (exit) to cancel.\nPress Enter to input default [%s]: ' % (message, inputs.get(where, '')))
    uInput = raw_input('> ')

    if uInput.lower() == 'exit':  # Returns the user to the main menu
        raise InputException('usercancel')

    elif uInput == '':  # Return last value.
        return inputs.get(where, '')

    else:
        inputs[where] = uInput

    return uInput


def restartBmNotify():
    """Prompt the user to restart Bitmessage"""

    print
    print '     *******************************************************************'
    print '     WARNING: If Bitmessage is running locally, you must restart it now.'
    print '     *******************************************************************\n'


# Begin keys.dat interactions


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

    print('     {0} Initalized in the same directory as this CLI.\n'
          '     You will now need to configure the {0} file.\n'.format(keysName))


def apiInit(apiEnabled):
    """Initialise the API"""

    global usrPrompt, keysPath
    BMConfigParser().read(keysPath)
    isValid = False

    if apiEnabled is False:  # API information there but the api is disabled.
        uInput = userInput('The API is not enabled. Would you like to do that now, (Y)es or (N)o?').lower()

        if uInput == "y":
            BMConfigParser().set('bitmessagesettings', 'apienabled', 'true')  # Sets apienabled to true in keys.dat
            with open(keysPath, 'wb') as configfile:
                BMConfigParser().write(configfile)

            print 'Done'
            restartBmNotify()
            isValid = True

        elif uInput == "n":
            print
            print '     ************************************************************'
            print '            Daemon will not work when the API is disabled.       '
            print '     Please refer to the Bitmessage Wiki on how to setup the API.'
            print '     ************************************************************\n'

        else:
            print '\n     Invalid Entry\n'

    elif apiEnabled:  # API correctly setup
        # Everything is as it should be
        isValid = True

    else:  # API information was not present.
        print '\n     ' + str(keysPath) + ' not properly configured!\n'
        uInput = userInput('Would you like to do this now, (Y)es or (N)o?').lower()

        if uInput == "y":  # User said yes, initalize the api by writing these values to the keys.dat file
            print ' '

            apiUsr = userInput("API Username")
            apiPwd = userInput("API Password")
            apiPort = userInput("API Port")
            apiEnabled = userInput("API Enabled? (True) or (False)").lower()
            daemon = userInput("Daemon mode Enabled? (True) or (False)").lower()

            if (daemon != 'true' and daemon != 'false'):
                print '\n     Invalid Entry for Daemon.\n'

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

            print '     Finished configuring the keys.dat file with API information.\n'
            restartBmNotify()
            isValid = True

        elif uInput == "n":
            print
            print '     ***********************************************************'
            print '     Please refer to the Bitmessage Wiki on how to setup the API.'
            print '     ***********************************************************\n'

        else:
            print '     \nInvalid entry\n'

    return isValid


def apiData():
    """TBC"""

    global keysName
    global keysPath
    global usrPrompt

    print '\n     Configure file searching:', os.path.realpath(keysPath)
    BMConfigParser().read(keysPath)  # First try to load the config file (the keys.dat file) from the program directory

    try:
        BMConfigParser().get('bitmessagesettings', 'port')
        appDataFolder = ''
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError) as e:
        pass
        # Could not load the keys.dat file in the program directory. Perhaps it is in the appdata directory.
        appDataFolder = lookupAppdataFolder()
        keysPath = appDataFolder + keysPath
        print '\n     Configure file searching:', os.path.realpath(keysPath)
        BMConfigParser().read(keysPath)

        try:
            BMConfigParser().get('bitmessagesettings', 'port')
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError) as e:
            # keys.dat was not there either, something is wrong.
            print
            print '     *************************************************************'
            print '        WARNING: There was a problem on accessing congfigure file.'
            print '     Make sure that daemon is in the same directory as Bitmessage. '
            print '     *************************************************************\n'

            finalCheck = False
            uInput = userInput('Would you like to create a "keys.dat" file in current working directory, (Y)es or (N)o?').lower()

            if (uInput == "y" or uInput == "yes"):
                configInit()
                keysPath = keysName
                finalCheck = True

            elif (uInput == "n" or uInput == "no"):
                print '\n     Trying Again.\n'

            else:
                print '\n     Invalid Input.\n'

            if not finalCheck:
                return ''

    try:  # checks to make sure that everyting is configured correctly. Excluding apiEnabled, it is checked after
        BMConfigParser().get('bitmessagesettings', 'apiport')
        BMConfigParser().get('bitmessagesettings', 'apiinterface')
        BMConfigParser().get('bitmessagesettings', 'apiusername')
        BMConfigParser().get('bitmessagesettings', 'apipassword')

    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError) as e:
        isValid = apiInit("")  # Initalize the keys.dat file with API information
        if not isValid:
            print '\n      Config file not valid.\n'
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

    ret = "http://" + apiUsername + ":" + apiPassword + "@" + apiInterface + ":" + str(apiPort) + "/"
    print '\n     API data successfully imported.'

    # Build the api credentials
    return ret


# End keys.dat interactions

def apiTest():
    """Tests the API connection to bitmessage. Returns true if it is connected."""

    response = api.add(2, 3)
    return response['result'] == 5


def bmSettings():
    """Allows the viewing and modification of keys.dat settings."""

    global keysPath
    global usrPrompt, inputShorts, retStrings

    #keysPath = 'keys.dat'

    BMConfigParser().read(keysPath)  # Read the keys.dat
    try:
        print '     Configure file loading:', os.path.realpath(keysPath)
        port = BMConfigParser().get('bitmessagesettings', 'port')
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError) as e:
        print '\n     File not found.\n'
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
    print '     -----------------------------------'
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
    print '     ------------------------------------'
    print '     |   Current Connection Settings   |'
    print '     -----------------------------------'
    print '     socksproxytype = ' + socksproxytype
    print '     sockshostname = ' + sockshostname
    print '     socksport = ' + socksport
    print '     socksauthentication = ' + str(socksauthentication)
    print '     socksusername = ' + socksusername
    print '     sockspassword = ' + sockspassword
    print ' '

    src = retStrings['usercancel']
    uInput = userInput('Would you like to modify any of these settings, (n)o or (Y)es?').lower()

    if uInput not in ['n', 'no']:
        while True:  # loops if they mistype the setting name, they can exit the loop with 'exit'
            invalidInput = False
            uInput = userInput('What setting would you like to modify?').lower()
            print ' '

            if uInput == "port":
                print '     Current port number: ' + port
                uInput = userInput("Input the new port number.")
                BMConfigParser().set('bitmessagesettings', 'port', str(uInput))
            elif uInput == "startonlogon":
                print '     Current status: ' + str(startonlogon)
                uInput = userInput("Input the new status.")
                BMConfigParser().set('bitmessagesettings', 'startonlogon', str(uInput))
            elif uInput == "minimizetotray":
                print '     Current status: ' + str(minimizetotray)
                uInput = userInput("Input the new status.")
                BMConfigParser().set('bitmessagesettings', 'minimizetotray', str(uInput))
            elif uInput == "showtraynotifications":
                print '     Current status: ' + str(showtraynotifications)
                uInput = userInput("Input the new status.")
                BMConfigParser().set('bitmessagesettings', 'showtraynotifications', str(uInput))
            elif uInput == "startintray":
                print '     Current status: ' + str(startintray)
                uInput = userInput("Input the new status.")
                BMConfigParser().set('bitmessagesettings', 'startintray', str(uInput))
            elif uInput == "defaultnoncetrialsperbyte":
                print '     Current default nonce trials per byte: ' + defaultnoncetrialsperbyte
                uInput = userInput("Input the new defaultnoncetrialsperbyte.")
                BMConfigParser().set('bitmessagesettings', 'defaultnoncetrialsperbyte', str(uInput))
            elif uInput == "defaultpayloadlengthextrabytes":
                print '     Current default payload length extra bytes: ' + defaultpayloadlengthextrabytes
                uInput = userInput("Input the new defaultpayloadlengthextrabytes.")
                BMConfigParser().set('bitmessagesettings', 'defaultpayloadlengthextrabytes', str(uInput))
            elif uInput == "daemon":
                print '     Current status: ' + str(daemon)
                uInput = userInput("Input the new status.").lower()
                BMConfigParser().set('bitmessagesettings', 'daemon', str(uInput))
            elif uInput == "socksproxytype":
                print '     Current socks proxy type: ' + socksproxytype
                print "Possibilities: 'none', 'SOCKS4a', 'SOCKS5'."
                uInput = userInput("Input the new socksproxytype.")
                BMConfigParser().set('bitmessagesettings', 'socksproxytype', str(uInput))
            elif uInput == "sockshostname":
                print '     Current socks host name: ' + sockshostname
                uInput = userInput("Input the new sockshostname.")
                BMConfigParser().set('bitmessagesettings', 'sockshostname', str(uInput))
            elif uInput == "socksport":
                print '     Current socks port number: ' + socksport
                uInput = userInput("Input the new socksport.")
                BMConfigParser().set('bitmessagesettings', 'socksport', str(uInput))
            elif uInput == "socksauthentication":
                print '     Current status: ' + str(socksauthentication)
                uInput = userInput("Input the new status.")
                BMConfigParser().set('bitmessagesettings', 'socksauthentication', str(uInput))
            elif uInput == "socksusername":
                print '     Current socks username: ' + socksusername
                uInput = userInput("Input the new socksusername.")
                BMConfigParser().set('bitmessagesettings', 'socksusername', str(uInput))
            elif uInput == "sockspassword":
                print '     Current socks password: ' + sockspassword
                uInput = userInput("Input the new password.")
                BMConfigParser().set('bitmessagesettings', 'sockspassword', str(uInput))
            else:
                print "\n     Invalid field. Please try again.\n"
                invalidInput = True

            if invalidInput is not True:  # don't prompt if they made a mistake.
                uInput = userInput("Would you like to change another setting, (n)o or (Y)es?").lower()

                if uInput in inputShorts['no']:
                    with open(keysPath, 'wb') as configfile:
                        src = BMConfigParser().write(configfile)
                    restartBmNotify()
                    break

    return src


def validAddress(address):
    """Predicate to test address validity"""

    print '     Validating...', address
    response = api.decodeAddress(address)
    if response['error'] != 0:
        print response['errormsg']
        return False

    return 'success' in response['result']['status'].lower()


def getAddress(passphrase, vNumber, sNumber):
    """Get a deterministic address"""

    passPhrase = passphrase.encode('base64')  # passphrase must be encoded
    print '     Getting address:', passphrase
    response = api.getDeterministicAddress(passPhrase, vNumber, sNumber)
    if response['error'] != 0:
        return response['errormsg']

    print '     Address:', response['result']


def subscribe(address, label):
    """Subscribe to an address"""

    label = label.encode('base64')
    print '     Subscribing address:', label
    response = api.addSubscription(address, label)
    if response['error'] != 0:
        return response['errormsg']

    return '\n    ' + response['result']


def unsubscribe(address):
    """Unsusbcribe from an address"""

    print '     unSubscribing address:', address
    response = api.deleteSubscription(address)
    if response['error'] != 0:
        return response['errormsg']

    return '\n     ' + response['result']


def listSubscriptions():
    """List subscriptions"""

    print '     Subscribed list retriving...'
    response = api.listSubscriptions()
    if response['error'] != 0:
        return response['errormsg']

    jsonAddresses = response['result']
    numAddresses = len(jsonAddresses)
    print
    print '     -----------------------------------------------------------------------'
    print '     | # |       Label       |               Address               |Enabled|'
    print '     |---|-------------------|-------------------------------------|-------|'
    for addNum in range(0, numAddresses):  # processes all of the addresses and lists them out
        label = (jsonAddresses[addNum]['label'].decode('base64')).encode(
            'utf-8')              # may still misdiplay in some consoles
        address = str(jsonAddresses[addNum]['address'])
        enabled = str(jsonAddresses[addNum]['enabled'])

        if len(label) > 19:
            label = label[:16] + '...'

        print ''.join([
            '     |',
            str(addNum).ljust(3),
            '|',
            label.ljust(19),
            '|',
            address.ljust(37),
            '|',
            enabled.ljust(7),
            '|',
        ])

    print ''.join([
        '     ',
        71 * '-',
        '\n',
    ])

    return ''


def createChan(password):
    """Create a channel"""

    base64 = password.encode('base64')
    print '     Channel creating...', password
    response = api.createChan(base64)
    if response['error'] != 0:
        return response['errormsg']

    return '\n     ' + response['result']


def joinChan():
    """Join a channel"""

    uInput = ''
    address = inputAddress('Enter channel address')
    while uInput == '':
        uInput = userInput('Enter channel name[1~]')
    password = uInput.encode('base64')

    print '     Channel joining...', uInput
    response = api.joinChan(password, address)
    if response['error'] != 0:
        return response['errormsg']

    return '\n     ' + response['result']


def leaveChan():
    """Leave a channel"""

    address = inputAddress("Enter channel address")
    print '     Channel leaving...', 'address'
    response = api.leaveChan(address)
    if response['error'] != 0:
        return response['errormsg']

    return '\n     ' + response['result']


def listAdd():
    """List all of the addresses and their info"""

    print '     Retriving...', 'Senders'
    response = api.listAddresses()
    if response['error'] != 0:
        return response['errormsg']

    jsonAddresses = response['result']
    numAddresses = len(jsonAddresses)  # Number of addresses
    # print '\nAddress Index,Label,Address,Stream,Enabled\n'
    print
    print '     --------------------------------------------------------------------------'
    print '     | # |       Label       |               Address               |S#|Enabled|'
    print '     |---|-------------------|-------------------------------------|--|-------|'
    for addNum in range(0, numAddresses):  # processes all of the addresses and lists them out
        label = jsonAddresses[addNum]['label'].encode(
            'utf-8')              # may still misdiplay in some consoles
        address = str(jsonAddresses[addNum]['address'])
        stream = str(jsonAddresses[addNum]['stream'])
        enabled = str(jsonAddresses[addNum]['enabled'])

        if len(label) > 19:
            label = label[:16] + '...'

        print ''.join([
            '     |',
            str(addNum).ljust(3),
            '|',
            label.ljust(19),
            '|',
            address.ljust(37),
            '|',
            stream.ljust(2),
            '|',
            enabled.ljust(7),
            '|',
        ])

    print ''.join([
        '     ',
        74 * '-',
        '\n',
    ])

    return ''


def genAdd(lbl, deterministic, passphrase, numOfAdd, addVNum, streamNum, ripe):
    """Generate address"""

    global usrPrompt

    if deterministic is False:  # Generates a new address with the user defined label. non-deterministic
        addressLabel = lbl.encode('base64')
        print '     Address requesting...', lbl
        response = api.createRandomAddress(addressLabel)
        if response['error'] != 0:
            return response['errormsg']

    else:  # Generates a new deterministic address with the user inputs.
        passPhrase = passphrase.encode('base64')
        print '     Address deterministic...', passphrase
        response = api.createDeterministicAddresses(passPhrase, numOfAdd, addVNum, streamNum, ripe)
        if response['error'] != 0:
            return response['errormsg']

    return '\n     Address:', response['result']


def dump2File(fileName, fileData, deCoded):
    """Allows attachments and messages/broadcats to be saved"""

    global inputShorts

    # This section finds all invalid characters and replaces them with ~
    for s in ' /\\:*?"<>|':
        fileName = fileName.replace(s, '~')

    directory = os.path.abspath('attachments')

    if not os.path.exists(directory):
        try:
            os.makedirs(directory)

        except OSError as e:
            return '\n     %s.\n' % str(e)
            # return '\n     Failed creating ' + directory + '\n'
        except Exception:
            return '\n     Unexpected error: %s.\n' % sys.exc_info()[0]

    filePath = os.path.join(directory, fileName)

    if not deCoded:
        x = filter(lambda z: not re.match(r'^\s*$', z), fileData)
        trydecode = False
        if len(x) % 4 == 0:  # check by length before decode.
            trydecode = True
        else:
            print ''.join([
                '\n     -----------------------------------',
                '\n     Contents seems not "BASE64" encoded. (base on length check)',
                '\n     Start[{}] ~ Ends[{}].'.format(x[:3], x[-3:]),
                '\n     About: {} (bytes).'.format((int(len(x)*(3/4))) - (2 if x[-2:] == '==' else 1 if x[-1] == '=' else 0)),
                '\n     FileName: "{}"'.format(fileName),
                ])
            uInput = userInput('Try to decode it anyway, (n)o or (Y)es?')
            if uInput not in inputShorts['no']:
                trydecode = True

        if trydecode is True:
            try:
                y = x.decode('base64', 'strict')
                if x == y.encode('base64').replace('\n', ''):  # double check decoded string.
                    fileData = y
                else:
                    print '\n     Failed on "BASE64" re-encode checking.\n'

            except ValueError:
                return '\n     Failed on "BASE64" decoding.\n'
        else:
            print '\n     Not "BASE64" contents, dump to file directly.'

    try:
        with open(filePath, 'wb+') as path_to_file:
                path_to_file.write(fileData)

    except IOError as e:
        return '\n     %s.\n' % str(e)
        # return '\n     Failed on operating: "' + filePath + '"\n'
    except Exception:
        return '\n     Unexpected error: %s.\n' % sys.exc_info()[0]

    return '     Successfully saved to: "' + filePath + '"'


def attachment():
    """Allows users to attach a file to their message or broadcast"""

    theAttachmentS = ''

    global inputShorts

    while True:

        isImage = False
        theAttachment = ''

        while True:  # loops until valid path is entered
            filePath = userInput(
                '\nPlease enter the path to the attachment or just the attachment name if in this folder[Max:180MB].')

            try:
                with open(filePath):
                    break
            except IOError:
                print '\n     Failed open file on: ', filePath + '\n'

        # print filesize, and encoding estimate with confirmation if file is over X size (1mb?)
        invSize = os.path.getsize(filePath)
        invSize = (invSize / 1024)  # Converts to kilobytes
        round(invSize, 2)  # Rounds to two decimal places

        if invSize > 500.0:  # If over 500KB
            print ''.join([
                '\n     WARNING:The file that you are trying to attach is ',
                invSize,
                'KB and will take considerable time to send.\n'
            ])
            uInput = userInput('Are you sure you still want to attach it, (y)es or (N)o?').lower()

            if uInput not in inputShorts['yes']:
                return '\n     Attachment discarded.'

        elif invSize > 184320.0:  # If larger than 180MB, discard.
            return '\n     Attachment too big, maximum allowed size:180MB\n'

        pathLen = len(str(ntpath.basename(filePath)))  # Gets the length of the filepath excluding the filename
        fileName = filePath[(len(str(filePath)) - pathLen):]  # reads the filename

        filetype = imghdr.what(filePath)  # Tests if it is an image file
        if filetype is not None:
            print
            print '     ---------------------------------------------------'
            print '     Attachment detected as an Image.'
            print '     <img> tags will automatically be included,'
            print '     allowing the recipient to view the image'
            print '     using the "View HTML code..." option in Bitmessage.'
            print '     ---------------------------------------------------\n'
            isImage = True
            time.sleep(2)

        # Alert the user that the encoding process may take some time.
        print '     Encoding Attachment, Please Wait ...'

        with open(filePath, 'rb') as f:  # Begin the actual encoding
            data = f.read(188743680)  # Reads files up to 180MB, the maximum size for Bitmessage.
            data = data.encode("base64")

        if isImage:  # If it is an image, include image tags in the message
            theAttachment = """
<!-- Note: Image attachment below. Please use the right click "View HTML code ..." option to view it. -->
<!-- Sent using Bitmessage Daemon. https://github.com/Dokument/PyBitmessage-Daemon -->

Filename: %s
Filesize: %sKB
Encoding: base64

<center>
    <div id="image">
        <img alt="%s" src="data:image/%s;base64, %s"/>
    </div>
</center>""" % (fileName, invSize, fileName, filetype, data)
        else:  # Else it is not an image so do not include the embedded image code.
            theAttachment = """
<!-- Note: File attachment below. Please use a base64 decoder, or Daemon, to save it. -->
<!-- Sent using Bitmessage Daemon. https://github.com/Dokument/PyBitmessage-Daemon -->

Filename:%s
Filesize:%sKB
Encoding:base64

<attachment alt="%s" src="data:file/%s;base64, %s"/>""" % (fileName, invSize, fileName, fileName, data)

        uInput = userInput('Would you like to add another attachment, (y)es or (N)o?').lower()

        if uInput in inputShorts['yes']:  # Allows multiple attachments to be added to one message
            theAttachmentS = str(theAttachmentS) + str(theAttachment) + '\n\n'
        else:
            break

    theAttachmentS = theAttachmentS + theAttachment
    return theAttachmentS


def sendMsg(toAddress, fromAddress, subject, message):
    """
    With no arguments sent, sendMsg fills in the blanks.
    subject and message must be encoded before they are passed.
    """

    global usrPrompt, retStrings, inputShorts

    if validAddress(toAddress) is False:
        toAddress = inputAddress("What is the To Address indeed?")

    if validAddress(fromAddress) is False:
        print '     Sender retriving...', fromAddress
        response = api.listAddresses()
        if response['error'] != 0:
            return response['errormsg']
        
        jsonAddresses = response['result']
        numAddresses = len(jsonAddresses)  # Number of addresses

        if numAddresses > 1:  # Ask what address to send from if multiple addresses
            found = False
            while True:
                fromAddress = userInput('Enter an Address or Address Label to send from.')

                for addNum in range(0, numAddresses):  # processes all of the addresses
                    label = jsonAddresses[addNum]['label']
                    address = jsonAddresses[addNum]['address']
                    if fromAddress == label:  # address entered was a label and is found
                        fromAddress = address
                        found = True
                        break

                if found is False:
                    if validAddress(fromAddress) is False:
                        print '\n     Invalid Address. Please try again.\n'

                    else:
                        for addNum in range(0, numAddresses):  # processes all of the addresses
                            address = jsonAddresses[addNum]['address']
                            if fromAddress == address:  # address entered was a found in our addressbook.
                                found = True
                                break

                        if found is False:
                            print '\n     The address entered is not one of yours. Please try again.\n'

                if found:
                    break  # Address was found

        else:  # Only one address in address book
            print '\n     Using the only address in the addressbook to send from.\n'
            fromAddress = jsonAddresses[0]['address']

    if subject == '':
        subject = userInput('Enter your Subject.')
        subject = subject.encode('base64')

    if message == '':
        while True:
            try:
                message += ''.join([
                    '\n',
                    raw_input('Continue enter your message line by line, end with <CTL-D>.\n> '),
                    ])
            except EOFError:
                break

        uInput = userInput('Would you like to add an attachment, (y)es or (N)o?').lower()
        if uInput in inputShorts['yes']:
            message = message + '\n\n' + attachment()

        message = message.encode('base64')

    while True:
        print '     Message sending...', subject.decode('base64')
        ackData = api.sendMessage(toAddress, fromAddress, subject, message)
        if ackData['error'] == 1:
            return ackData['errormsg']
        elif ackData['error'] != 0:
            print ackData['errormsg']
            uInput = userInput('Would you like to try again, (n)o or (Y)es?').lower()
            if uInput in inputShorts['no']:
                break

    if ackData['error'] == 0:
        print '     Fetching send status...'
        status = api.getStatus(ackData['result'])
        if status['error'] == 1:
            return status['errormsg']
        elif status['error'] != 0:
            print status['errormsg']
        else:
            return '     Message Status:' + status['result']

    return ''


def sendBrd(fromAddress, subject, message):
    """Send a broadcast"""

    global usrPrompt, inputShorts
    if fromAddress == '':
        print '     Retriving...', 'Senders'
        response = api.listAddresses()
        if response['error'] != 0:
            return response['errormsg']

        jsonAddresses = response['result']
        numAddresses = len(jsonAddresses)  # Number of addresses

        if numAddresses > 1:  # Ask what address to send from if multiple addresses
            found = False
            while True:
                fromAddress = userInput('Enter an Address or Address Label to send from.')

                for addNum in range(0, numAddresses):  # processes all of the addresses
                    label = jsonAddresses[addNum]['label']
                    address = jsonAddresses[addNum]['address']
                    if fromAddress == label:  # address entered was a label and is found
                        fromAddress = address
                        found = True
                        break

                if found is False:
                    if validAddress(fromAddress) is False:
                        print '\n     Invalid Address. Please try again.\n'

                    else:
                        for addNum in range(0, numAddresses):  # processes all of the addresses
                            address = jsonAddresses[addNum]['address']
                            if fromAddress == address:  # address entered was a found in our addressbook.
                                found = True
                                break

                        if found is False:
                            print '\n     The address entered is not one of yours. Please try again.\n'

                if found:
                    break  # Address was found

        else:  # Only one address in address book
            print '     Using the only address in the addressbook to send from.\n'
            fromAddress = jsonAddresses[0]['address']

    if subject == '':
        subject = userInput('Enter your Subject.')
    subject = subject.encode('base64')
    if message == '':
        while True:
            try:
                message += ''.join([
                    '\n',
                    raw_input('Continue enter your message line by line, end with <CTL-D>.\n> '),
                    ])
            except EOFError:
                break

        uInput = userInput('Would you like to add an attachment, (y)es or (N)o?').lower()
        if uInput in inputShorts['yes']:
            message = message + '\n\n' + attachment()

        message = message.encode('base64')

    while True:
        print '     Broadcast message sending...'
        ackData = api.sendBroadcast(fromAddress, subject, message)
        if ackData['error'] == 1:
            return ackData['errormsg']
        elif status['error'] != 0:
            print '\n     %s.\n' % str(e)
            uInput = userInput('Would you like to try again, no or (Y)es?').lower()
            if uInput in inputShorts['no']:
                break

    if ackData['error'] == 0:
        print '     Fetching send status...'
        status = api.getStatus(ackData['result'])
        if status['error'] == 1:
            return status['errormsg']
        elif status['error'] != 0:
            print status['errormsg']
        else:
            return '     Message Status:' + status['result']

    return ''


def inbox(unreadOnly=False, pageNum=20):
    """Lists the messages by: message index, To Address Label, From Address Label, Subject, Received Time)"""

    print '     Inbox index fetching...'
    response = api.getAllInboxMessageIDs()
    if response['error'] != 0:
        return response['errormsg']

    messageIds = response['result']
    numMessages = len(messageIds)
    messagesPrinted = 0
    messagesUnread = 0
    for msgNum in range(numMessages - 1, -1, -1):  # processes all of the messages in the inbox
        messageID = messageIds[msgNum]['msgid']
        print '     -----------------------------------'
        print '     Inbox message retriving...', messageID
        response = api.getInboxMessageByID(messageID)
        if response['error'] == 1:
            return response['errormsg']
        elif response['error'] != 0:
            print '\n     Retrieve failed on:', msgNum, messageID
            print response['errormsg']
        else:
            message = response['result'][0]
            # if we are displaying all messages or if this message is unread then display it
            if not unreadOnly or not message['read']:
                print '     -----------------------------------'
                print '     Inbox index: {}/{}'.format(msgNum, numMessages - 1)  # message index
                print '     Message ID:', message['msgid']
                print '     Read:', message['read']
                print '     To:', getLabelForAddress(message['toAddress'])  # Get the to address
                print '     From:', getLabelForAddress(message['fromAddress'])  # Get the from address
                print '     Subject:', message['subject'].decode('base64')  # Get the subject
                print '     Received:', datetime.datetime.fromtimestamp(float(message['receivedTime'])).strftime('%Y-%m-%d %H:%M:%S')
                print '     Base64Len:', str(len(message['message']))
                messagesPrinted += 1
                if not message['read']:
                    messagesUnread += 1

                if messagesPrinted % pageNum == 0 and messagesPrinted != 0:
                    try:
                        uInput = userInput('Paused on {}/{}, next [{}],'.format(msgNum, numMessages - 1, msgNum - pageNum if msgNum > pageNum else 0))

                    except InputException as e:
                        raise InputException(str(e))

    print '     -----------------------------------'
    print '     There are %d unread messages of %d messages in the inbox.' % (messagesUnread, numMessages)
    print '     -----------------------------------'

    return ''


def outbox(pageNum=20):
    """TBC"""

    print '     All outbox messages downloading...'
    response = api.getAllSentMessages()
    if response['error'] != 0:
        return response['errormsg']

    outboxMessages = response['result']
    numMessages = len(outboxMessages)
    for msgNum in range(numMessages - 1, -1, -1):  # processes all of the messages in the outbox
        message = outboxMessages[msgNum]
        print '     -----------------------------------'
        print '     Outbox index: {}/{}'.format(msgNum, numMessages - 1)  # message index
        print '     Message ID:', message['msgid']
        print '     To:', getLabelForAddress(message['toAddress'])  # Get the to address
        # Get the from address
        print '     From:', getLabelForAddress(message['fromAddress'])
        print '     Subject:', message['subject'].decode('base64')  # Get the subject
        print '     Status:', message['status']  # Get the status
        print '     Ack:', message['ackData']  # Get the ackData
        print '     Last Action Time:', datetime.datetime.fromtimestamp(float(message['lastActionTime'])).strftime('%Y-%m-%d %H:%M:%S')
        print '     Base64Len:', str(len(message['message']))

        if msgNum % pageNum == 0 and msgNum != 0:
            uInput = userInput('Paused on {}/{}, next [{}],'.format(msgNum, numMessages - 1, msgNum - pageNum if msgNum > pageNum else 0))

    print '     -----------------------------------'
    print '     There are ', numMessages, ' messages in the outbox.'
    print '     -----------------------------------\n'

    return ''


def attDetect(content='', textmsg='', attPrefix='', askSave=True):

    global inputShorts

    attPos = msgPos = 0
    # Hard way search attachments
    while True:  # Allows multiple messages to be downloaded/saved
        try:
            attPos = content.index(';base64,', attPos) + 9  # Finds the attachment position
            attEndPos = content.index('/>', attPos) - 1  # Finds the end of the attachment

            attPre = attPos - 9  # back for ;base64, | <img src=";base64, | <attachment src=";base64,
            # try remove prefix <xxxx | <xxxxxxxxxxx
            pBack = 0
            if attPre >= (msgPos + 12):
                if '<' == content[attPre - 12]:
                    pBack = 12
            elif attPre - msgPos + 5 >= 0:
                if '<' == content[attPre - 5]:
                    pBack = 5
            attPre = attPre - pBack

            try:
                fnPos = content.index('alt="', msgPos, attPos) + 5  # Finds position of the filename
                fnEndPos = content.index('" src=', msgPos, attPos)  # Finds the end position
                # fnLen = fnEndPos - fnPos #Finds the length of the filename
                fn = content[fnPos:fnEndPos]

                attPre = fnPos - 5  # back for alt=" | <img alt=" | <attachment alt="
                # try remove prefix <xxxx | <xxxxxxxxxxx
                pBack = 0
                if attPre >= (msgPos + 12):
                    if '<' == content[attPre - 12]:
                        pBack = 12
                elif attPre - msgPos + 5 >= 0:
                    if '<' == content[attPre - 5]:
                        pBack = 5
                attPre = attPre - pBack

            except ValueError:
                fn = 'notdetected'
            fn = '{}_attachment_{}_{}'.format(attPrefix, str(attPos), fn)

            this_attachment = content[attPos:attEndPos]
            x = filter(lambda z: not re.match(r'^\s*$', z), this_attachment)
            # x = x.replace('\n', '').strip()
            trydecode = False
            if len(x) % 4 == 0:  # check by length before decode.
                trydecode = True
            else:
                print ''.join([
                    '\n     -----------------------------------',
                    '\n     Embeded mesaage seems not "BASE64" encoded. (base on length check)',
                    '\n     Offset: {}, about: {} (bytes).'.format(attPos, (int(len(x)*3/4)) - (2 if x[-2:] == '==' else 1 if x[-1] == '=' else 0)),
                    '\n     Start[{}] ~ Ends[{}].'.format(x[:3], x[-3:]),
                    '\n     FileName: "{}"'.format(fn),
                ])
                uInput = userInput('Try to decode anyway, (n)o or (Y)es?')
                if uInput not in inputShorts['no']:
                    trydecode = True
            if trydecode is True:
                try:
                    y = x.decode('base64', 'strict')
                    if x == y.encode('base64').replace('\n', ''):  # double check decoded string.
                        print '     This embeded message decoded successfully:', fn
                        if askSave is True:
                            uInput = userInput('Download the "decoded" attachment, (y)es or (No)?\nName: {},'.format(fn)).lower()
                            if uInput in inputShorts['yes']:
                                src = dump2File(fn, y, True)
                        else:
                            src = dump2File(fn, y, True)

                        print src
                        attmsg = ''.join([
                            '\n     -----------------------------------',
                            '\n     Attachment: "{}"'.format(fn),
                            '\n     Size: {}(bytes)'.format(int(len(x)*(3/4)) - (2 if x[-2:] == '==' else 1 if x[-1] == '=' else 0)),
                            '\n     -----------------------------------',
                            ])
                        # remove base64 and '<att' prefix and suffix '/>' stuff
                        textmsg = textmsg + content[msgPos:attPre] + attmsg
                        attEndPos += 3
                        msgPos = attEndPos
                    else:
                        print '\n     Failed on decode this embeded "BASE64" like message on re-encode check.\n'

                except ValueError:
                    pass
                    print '\n     Failed on decode this emdeded "BASE64" encoded like message.\n'
                except Exception:
                    print '\n     Unexpected error: %s.\n' % sys.exc_info()[0]

            else:
                print '\n    Skiped a embeded "BASE64" encoded like message.'

            if attEndPos != msgPos:
                textmsg = textmsg + content[msgPos:attEndPos]
                msgPos = attEndPos

        except ValueError:
            textmsg = textmsg + content[msgPos:]
            break
        except Exception:
            print '\n     Unexpected error: %s.\n' % sys.exc_info()[0]


    return textmsg


def readSentMsg(cmd='read', msgNum=-1, messageID='', trunck=380, withAtta=False):
    """Opens a sent message for reading"""

    print '     All outbox messages downloading...', str(msgNum)
    if messageID == '':
        response = api.getAllSentMessages()
        if response['error'] != 0:
            return response['errormsg']

        message = response['result'][msgNum]
    else:
        response = api.getSentMessageByID(messageID)
        if response['error'] != 0:
            return response['errormsg']

        message = response['result'][0]

    subject = message['subject'].decode('base64')
    content = message['message'].decode('base64')
    full = len(content)
    textmsg = ''
    textmsg = content if withAtta else attDetect(content, textmsg, 'outbox_' + subject, cmd != 'save')

    print '    ', 74 * '-'
    print '     Message index:', str(msgNum)  # message outdex
    print '     Message ID:', message['msgid']
    print '     To:', getLabelForAddress(message['toAddress'])  # Get the to address
    # Get the from address
    print '     From:', getLabelForAddress(message['fromAddress'])
    print '     Subject:', subject  # Get the subject
    print '     Status:', message['status']  # Get the status
    print '     Ack:', message['ackData']  # Get the ackData

    print '     Last Action Time:', datetime.datetime.fromtimestamp(float(message['lastActionTime'])).strftime('%Y-%m-%d %H:%M:%S')
    print '     Length: {}/{}'.format(trunck if trunck <= full else full, full)
    print '     Message:\n'
    print textmsg if trunck < 0 or len(textmsg) <= trunck else textmsg[:trunck] + '\n\n     ~< MESSAGE TOO LONG TRUNCKED TO SHOW >~'
    print '    ', 74 * '-'

    if cmd == 'save':
        ret = dump2File('outbox_' + subject, textmsg, True)
        print ret

    return ''


def readMsg(cmd='read', msgNum=-1, messageID='', trunck=380, withAtta=False):
    """Open a message for reading"""

    print '     Inbox message reading...', str(msgNum)
    response = api.getInboxMessageByID(messageID, True)
    if response['error'] != 0:
        return response['errormsg']

    message = response['result'][0]
    subject = message['subject'].decode('base64')
    content = message['message'].decode('base64')  # Message that you are replying too.
    full = len(content)
    textmsg = ''
    textmsg = content if withAtta else attDetect(content, textmsg, 'inbox_' + subject, cmd != 'save')

    print '    ', 74 * '-'
    print '     Inbox index :', msgNum  # message index
    print '     Message ID:', message['msgid']
    print '     Read:', message['read']
    print '     To:', getLabelForAddress(message['toAddress'])  # Get the to address
    # Get the from address
    print '     From:', getLabelForAddress(message['fromAddress'])
    print '     Subject:', subject  # Get the subject
    print '     Received:', datetime.datetime.fromtimestamp(float(message['receivedTime'])).strftime('%Y-%m-%d %H:%M:%S')
    print '     Length: {}/{}'.format(trunck if trunck <= full else full, full)
    print '     Message:\n'
    print textmsg if trunck < 0 or len(textmsg) <= trunck else textmsg[:trunck] + '\n\n     ~< MESSAGE TOO LONG TRUNCKED TO SHOW >~'
    print '    ', 74 * '-'

    if cmd == 'save':
        ret = dump2File('inbox_' + subject + str(full), textmsg, True)
        print ret

    return ''


def replyMsg(msgNum=-1, messageID='', forwardORreply=''):
    """Allows you to reply to the message you are currently on. Saves typing in the addresses and subject."""

    global inputShorts, retStrings

    forwardORreply = forwardORreply.lower()  # makes it lowercase
    print '     Inbox message {}... {}'.format(forwardORreply, msgNum)
    response = api.getInboxMessageByID(messageID, True)
    if response['error'] != 0:
        return response['errormsg']

    message = response['result'][0]
    subject = message['subject'].decode('base64')
    content = message['message'].decode('base64')  # Message that you are replying too.
    full = len(content)
    textmsg = ''
    textmsg = attDetect(content, textmsg, subject, True)

    if forwardORreply == 'forward':
        attachMessage = ''.join([
            '> To: ', fwdFrom,
            '\n> From: ', fromAdd,
            '\n> Subject: ', subject,
            '\n> Received: ', recvTime,
            '\n> Message:',
            ])
    else:
        attachMessage = ''
    for line in textmsg.splitlines():
        attachMessage = attachMessage + '> ' + line + '\n'

    fromAdd = message['toAddress']  # Address it was sent To, now the From address
    fwdFrom = message['fromAddress']  # Address it was sent To, will attached to fwd
    recvTime = datetime.datetime.fromtimestamp(float(message['receivedTime'])).strftime('%Y-%m-%d %H:%M:%S')

    if forwardORreply == 'reply':
        toAdd = message['fromAddress']  # Address it was From, now the To address
        subject = "Re: " + re.sub('^Re: *', '', subject)

    elif forwardORreply == 'forward':
        subject = "Fwd: " + re.sub('^Fwd: *', '', subject)
        toAdd = inputAddress("What is the To Address?")

    else:
        return '\n     Invalid Selection. Reply or Forward only'

    subject = subject.encode('base64')

    newMessage = ''
    while True:
        try:
            print ''.join([
                '     Drafting:\n',
                newMessage,
                '     -----------------------------------',
                ])
            newMessage += ''.join([
                '\n',
                raw_input('Continue enter your message line by line, end with <CTL-D>.\n> '),
                ])
        except EOFError:
            break

    src = retStrings['usercancel']
    uInput = userInput('Would you like to add an attachment, (y)es or (N)o?').lower()
    if uInput in inputShorts['yes']:
        newMessage = newMessage + '\n\n' + attachment()

    newMessage = newMessage + '\n\n------------------------------------------------------\n'
    newMessage = newMessage + attachMessage
    newMessage = newMessage.encode('base64')

    print newMessage
    uInput = userInput('Realy want to send upper message, (n)o or (Y)es?').lower()
    if uInput not in inputShorts['no']:
        src = sendMsg(toAdd, fromAdd, subject, newMessage)

    return src


def delMsg(msgNum=-1, messageID=''):
    """Deletes a specified message from the inbox"""

    print '     Inbox message deleting...', messageID
    response = api.trashMessage(messageID)
    if response['error'] != 0:
        return response['errormsg']

    return '\n     ' + response['result']


def delSentMsg(msgNum=-1, messageID=''):
    """Deletes a specified message from the outbox"""

    if messageID == '':
        print '     All outbox messages downloading...', str(msgNum)
        response = api.getAllSentMessages()
        if response['error'] != 0:
            return response['errormsg']

        outboxMessages = response['result']
        # gets the message ackData via the message index number
        ackData = outboxMessages[msgNum]['ackData']
        print '     Outbox message deleting...', ackData
        response = api.trashSentMessageByAckData(ackData)
        if response['error'] != 0:
            return response['errormsg']
    else:
        print '     Outbox message deleting...', messageID
        response = api.trashSentMessage(messageID)
        if response['error'] != 0:
            return response['errormsg']

    return '\n     ' + response['result']


def toReadInbox(cmd='read', trunck=380, withAtta=False):

    global inputShorts, retStrings

    numMessages = 0
    print '     Inbox index fetching...'
    response = api.getAllInboxMessageIDs()
    if response['error'] != 0:
        return response['errormsg']

    messageIds = response['result']
    numMessages = len(messageIds)
    if numMessages < 1:
        return '     Zero message found.\n'

    src = retStrings['usercancel']
    if cmd != 'delete':
        msgNum = int(inputIndex('Input the index of the message to {} [0-{}]: '.format(cmd, numMessages - 1), numMessages - 1))

        nextNum = msgNum
        ret = ''
        while msgNum >= 0:  # save, read
            nextNum += 1
            messageID = messageIds[msgNum]['msgid']
            if cmd == 'save':
                ret = readMsg(cmd, msgNum, messageID, trunck, withAtta)
                return ret

            else:
                ret = readMsg(cmd, msgNum, messageID)
            print ret

            uInput = userInput('Would you like to set this message to unread, (y)es or (N)o?').lower()
            if uInput in inputShorts['yes']:
                ret = markMessageReadbit(msgNum, messageID, False)

            else:
                uInput = userInput('Would you like to (f)orward, (r)eply, (s)ave, (d)ump or Delete this message?').lower()

                if uInput in inputShorts['reply']:
                    ret = replyMsg(msgNum, messageID, 'reply')

                elif uInput in inputShorts['forward']:
                    ret = replyMsg(msgNum, messageID, 'forward')

                elif uInput in inputShorts['save']:
                    ret = readMsg('save', msgNum, messageID, withAtta=False)

                elif uInput in inputShorts['dump']:
                    ret = readMsg('save', msgNum, messageID, withAtta=True)

                else:
                    uInput = userInput('Are you sure to delete, (y)es or (N)o?').lower()  # Prevent accidental deletion
                    if uInput in inputShorts['yes']:
                        # nextNum -= 1
                        # numMessages -= 1
                        ret = delMsg(msgNum, messageID)

            print ret
            if nextNum < numMessages:
                uInput = userInput('Next message, (n)o or (Y)es?').lower()  # Prevent
                msgNum = nextNum if uInput not in inputShorts['no'] else -1
                src = retStrings['indexoutofbound']
            else:
                msgNum = -1

    else:
        uInput = inputIndex('Input the index of the message you wish to delete or (A)ll to empty the inbox [0-{}]: '.format(numMessages - 1), numMessages - 1, inputShorts['all'][0]).lower()

        if uInput in inputShorts['all']:
            ret = inbox(False)
            print ret
            uInput = userInput('Are you sure to delete all this {} message(s), (y)es or (N)o?'.format(numMessages)).lower()  # Prevent accidental deletion
            if uInput in inputShorts['yes']:
                for msgNum in range(0, numMessages):  # processes all of the messages in the outbox
                    ret = delMsg(msgNum, messageIds[msgNum]['msgid'])
                    print ret
                src = ''

        else:
            nextNum = msgNum = int(uInput)
            while msgNum >= 0:  # save, read
                nextNum += 1
                messageID = messageIds[msgNum]['msgid']
                ret = readMsg(cmd, msgNum, messageID)
                print ret

                uInput = userInput('Are you sure to delete, (y)es or (N)o?').lower()  # Prevent accidental deletion
                if uInput in inputShorts['yes']:
                    # nextNum -= 1
                    # numMessages -= 1
                    ret = delMsg(msgNum, messageID)
                    print ret

                if nextNum < numMessages:
                    uInput = userInput('Next message, (n)o or (Y)es?').lower()  # Prevent
                    msgNum = nextNum if uInput not in inputShorts['no'] else -1
                else:
                    msgNum = -1
                    src = retStrings['indexoutofbound']

    return src


def toReadOutbox(cmd='read', trunck=380, withAtta=False):

    global inputShorts, retStrings

    print '     Outbox index fetching...'
    response = api.getAllSentMessageIDs()
    if response['error'] != 0:
        return response['errormsg']

    messageIds = response['result']
    numMessages = len(messageIds)
    if numMessages < 1:
        return '     Zero message found.\n'

    src = retStrings['usercancel']
    if cmd != 'delete':
        msgNum = int(inputIndex('Input the index of the message open [0-{}]: '.format(numMessages - 1), numMessages - 1))

        nextNum = msgNum
        ret = ''
        while msgNum >= 0:  # save, read
            nextNum += 1
            messageID = messageIds[msgNum]['msgid']
            if cmd == 'save':
                ret = readSentMsg(cmd, msgNum, messageID, trunck, withAtta)
                return ret

            else:
                ret = readSentMsg(cmd, msgNum, messageID)

            print ret
            # Gives the user the option to delete the message
            uInput = userInput('Would you like to (s)ave, (d)ump or Delete this message directly?').lower()

            if uInput in inputShorts['save']:
                ret = readSentMsg('save', msgNum, messageID, withAtta=False)

            elif uInput in inputShorts['dump']:
                ret = readSentMsg('save', msgNum, messageID, withAtta=True)

            else:
                uInput = userInput('Are you sure to delete, (y)es or (N)o?').lower()  # Prevent accidental deletion
                if uInput in inputShorts['yes']:
                    nextNum -= 1
                    numMessages -= 1
                    ret = delSentMsg(msgNum, messageID)

            print ret
            if nextNum < numMessages:
                uInput = userInput('Next message, (n)o or (Y)es?').lower()  # Prevent
                msgNum = nextNum if uInput not in inputShorts['no'] else -1
            else:
                msgNum = -1
                src = retStrings['indexoutofbound']

    else:
        uInput = inputIndex('Input the index of the message you wish to delete or (A)ll to empty the outbox [0-{}]: '.format(numMessages - 1), numMessages - 1, inputShorts['all'][0]).lower()

        if uInput in inputShorts['all']:
            ret = outbox()
            print ret
            uInput = userInput('Are you sure to delete all this {} message(s), (y)es or (N)o?'.format(numMessages)).lower()  # Prevent accidental deletion
            if uInput in inputShorts['yes']:
                for msgNum in range(0, numMessages):  # processes all of the messages in the outbox
                    ret = delSentMsg(msgNum, messageIds[msgNum]['msgid'])
                    print ret
                src = ''

        else:
            nextNum = msgNum = int(uInput)
            while msgNum >= 0:  # save, read
                nextNum += 1

                messageID = messageIds[msgNum]['msgid']
                ret = readSentMsg(cmd, msgNum, messageID)
                print ret

                uInput = userInput('Are you sure to delete this message, (y)es or (N)o?').lower()  # Prevent accidental deletion
                if uInput in inputShorts['yes']:
                    nextNum -= 1
                    numMessages -= 1
                    ret = delSentMsg(msgNum, messageID)
                    print ret

                if nextNum < numMessages:
                    uInput = userInput('Next message, (n)o or (Y)es?').lower()  # Prevent
                    msgNum = nextNum if uInput not in inputShorts['no'] else -1
                    src = retStrings['indexoutofbound']
                else:
                    msgNum = -1

    return src


def getLabelForAddress(address):
    """Get label for an address"""

    for entry in knownAddresses['addresses']:
        if entry['address'] == address:
            return "%s (%s)" % (entry['label'], entry['address'])

    return address


def buildKnownAddresses():
    """Build known addresses"""

    # add from address book
    errors = ''
    newentry = []
    print '     Retriving...', 'Contacts'
    addresses = api.listAddressBookEntries()
    if addresses['error'] != 0:
        print addresses['errormsg']
    else:
        for entry in addresses['result']:
            isnew = True
            for old in knownAddresses['addresses']:
                if entry['address'] == old['address']:
                    isnew = False
                    break
            if isnew is True:
                newentry.append({'label': entry['label'].decode('base64').encode('utf-8'), 'address': entry['address']})
        if any(newentry):
            for new in newentry:
                knownAddresses['addresses'].append(new)

    newentry = []
    print '     Retriving...', 'Senders'
    addresses = api.listAddresses()
    if addresses['error'] != 0:
        print addresses['errormsg']
    else:
        for entry in addresses['result']:
            isnew = True
            for old in knownAddresses['addresses']:
                if entry['address'] == old['address']:
                    isnew = False
                    break
            if isnew is True:
                newentry.append({'label': entry['label'].encode('utf-8'), 'address': entry['address']})
        if any(newentry):
            for new in newentry:
                knownAddresses['addresses'].append(new)

    return ''


def listAddressBookEntries(printKnown=False):
    """List addressbook entries"""

    if not printKnown:
        print '     Retriving...', 'Contacts'
        response = api.listAddressBookEntries()
        if response['error'] != 0:
            return response['errormsg']
        addressBook = response['result']
    else:
        addressBook = knownAddresses['addresses']

    print
    print '     --------------------------------------------------------------'
    print '     |        Label       |                Address                |'
    print '     |--------------------|---------------------------------------|'
    for entry in addressBook:
        label = entry['label'].decode('base64').encode('utf-8') if not printKnown else entry['label']
        address = entry['address']
        if len(label) > 19:
            label = label[:16] + '...'
        print '     | ' + label.ljust(19) + '| ' + address.ljust(37) + ' |'
    print '     --------------------------------------------------------------'

    return ''


def addAddressToAddressBook(address, label):
    """Add an address to an addressbook"""

    print '     Adding...', label
    response = api.addAddressBookEntry(address, label.encode('base64'))
    if response['error'] != 0:
        return response['errormsg']

    return '\n     ' + response['result']


def deleteAddressFromAddressBook(address):
    """Delete an address from an addressbook"""

    print '     Deleting...', address
    response = api.deleteAddressBookEntry(address)
    if response['error'] != 0:
        return response['errormsg']

    return '\n     ' + response['result']


def getAPIErrorCode(response):
    """Get API error code"""

    if "API Error" in response or 'RPC ' in response:
        # if we got an API error return the number by getting the number
        # after the second space and removing the trailing colon
        return int(response.split()[2][:-1])


def markMessageReadbit(msgNum=-1, messageID='', read=False):
    """Mark a mesasge as unread/read"""

    print '     Marking...', str(msgNum),
    response = api.getInboxMessageByID(messageID, read)
    if response['error'] != 0:
        print 'Failed.'
        return response['errormsg']

    print 'OK.'
    return ''


def markAllMessagesReadbit(read=False):
    """Mark all messages as unread/read"""

    print '     Inbox index fetching...', 'mark'
    response = api.getAllInboxMessageIDs()
    if response['error'] != 0:
        return response['errormsg']

    messageIds = response['result']
    numMessages = len(messageIds)
    if numMessages < 1:
        return '     Zero message found.\n'

    for msgNum in range(0, numMessages):  # processes all of the messages in the inbox
        src = markMessageReadbit(msgNum, messageIds[msgNum]['msgid'], read)
        print src

    return ''


def addInfo(address):

    print '     Address decoding...', address
    response = api.decodeAddress(address)
    if response['error'] != 0:
        return response['errormsg']

    addinfo = response['result']
    print '     ------------------------------'
    if 'success' in addinfo['status'].lower():
        print '     Valid Address'
        print '     Address Version: %s' % str(addinfo['addressVersion'])
        print '     Stream Number: %s\n' % str(addinfo['streamNumber'])
    else:
        print '\n     Invalid Address !\n'

    return ''


def clientStatus():
    """Print the client status"""

    try:
        print '     Client status fetching...'
        client_status = api.clientStatus()['result']
        inboxMessageIds = api.getAllInboxMessageIDs()
        inumMessages = len(inboxMessageIds['result'])
        outboxMessageIds = api.getAllSentMessageIDs()
        onumMessages = len(outboxMessageIds['result'])

    except ValueError as e:
        pass

    print '     ------------------------------'
    for key in client_status.keys():
        print '    ', key, ':', str(client_status[key])
    print '     InboxMessages:', str(inumMessages)
    print '     OutboxMessages:', str(onumMessages)
    # print '     Message.dat:', str(boxSize)
    # print '     knownNodes.dat:', str(knownNodes)
    # print '     debug.log:', str(debugSize)
    print '     ------------------------------\n'

    return ''


def shutdown():
    """Shutdown the API"""

    print '     Shutdown command sending...'
    response = api.shutdown()
    if response['error'] != 0:
        return response['errormsg']

    return '\n     ' + response['result']


def UI(cmdInput):
    """Main user menu"""

    global usrPrompt, inputShorts, cmdShorts, retStrings

    src = 'MUST WRONG'
    uInput = ''

    if not any(cmdShorts):
        if not cmdGuess():
            raise SystemExit('\n     Bye\n')

    if cmdInput in cmdShorts['help']:
        src = showCmdTbl()

    elif cmdInput in cmdShorts['daemon']:
        src = "TODO: Start daemon locally."

    elif cmdInput in cmdShorts['apiTest']:  # tests the API Connection.
        print '     API connection test has:',
        print 'PASSED' if apiTest() else 'FAILED\n'
        src = ''

    elif cmdInput in cmdShorts['addInfo']:
        while uInput == '':
            uInput = userInput('Input the Bitmessage Address.')
        src = addInfo(uInput)

    elif cmdInput in cmdShorts['bmSettings']:  # tests the API Connection.
        src = bmSettings()

    elif cmdInput in cmdShorts['quit']:  # Quits the application
        raise SystemExit('\n     Bye\n')

    elif cmdInput in cmdShorts['listAddresses']:  # Lists all of the identities in the addressbook
        src = listAdd()

    elif cmdInput in cmdShorts['generateAddress']:  # Generates a new address
        uInput = userInput('Would you like to create a (d)eterministic or (R)andom address?').lower()

        if uInput in inputShorts['deterministic']:  # Creates a deterministic address
            deterministic = True

            lbl = ''
            passphrase = userInput('Input the Passphrase.')  # .encode('base64')
            numOfAdd = int(userInput('How many addresses would you like to generate?'))
            addVNum = 3
            streamNum = 1
            isRipe = userInput('Shorten the address, (Y)es or no?').lower()

            if isRipe in inputShorts['yes']:
                ripe = True
                src = genAdd(lbl, deterministic, passphrase, numOfAdd, addVNum, streamNum, ripe)

            else:
                ripe = False
                src = genAdd(lbl, deterministic, passphrase, numOfAdd, addVNum, streamNum, ripe)

        else:  # Creates a random address with user-defined label
            deterministic = False
            lbl = null = ''
            while lbl == '':
                lbl = userInput('Input the label for the new address.')
            src = genAdd(lbl, deterministic, null, null, null, null, null)

    elif cmdInput in cmdShorts['getAddress']:  # Gets the address for/from a passphrase
        while len(uInput) < 6:
            uInput = userInput('Input a strong address passphrase.[6-]')
        src = getAddress(uInput, 4, 1)

    elif cmdInput in cmdShorts['subscribe']:  # Subsribe to an address
        address = inputAddress('What address would you like to subscribe?')
        while uInput == '':
            uInput = userInput('Enter a label for this address.')
        src = subscribe(address, uInput)

    elif cmdInput in cmdShorts['unsubscribe']:  # Unsubscribe from an address
        address = inputAddress("What address would you like to unsubscribe from?")
        uInput = userInput('Are you sure to unsubscribe: [{}]?'.format(address))
        if uInput in inputShorts['yes']:
            src = unsubscribe(address)

    elif cmdInput in cmdShorts['listsubscrips']:  # Unsubscribe from an address
        src = listSubscriptions()

    elif cmdInput in cmdShorts['create']:
        while uInput == '':
            uInput = userInput('Enter channel name')
        src = createChan(uInput)

    elif cmdInput in cmdShorts['join']:
        src = joinChan()

    elif cmdInput in cmdShorts['leave']:
        src = leaveChan()

    elif cmdInput in cmdShorts['buildKnownAddresses']:  # Retrieve all of the addressbooks
        src = buildKnownAddresses()
        print src,
        src = listAddressBookEntries(True)

    elif cmdInput in cmdShorts['inbox']:
        src = inbox(False)

    elif cmdInput in cmdShorts['news']:
        src = inbox(True)

    elif cmdInput in cmdShorts['outbox']:
        src = outbox()

    elif cmdInput in cmdShorts['send']:  # Sends a message or broadcast
        uInput = userInput('Would you like to send a (b)roadcast or (M)essage?').lower()
        null = ''
        if uInput in inputShorts['broadcast']:
            src = sendBrd(null, null, null)
        else:
            src = sendMsg(null, null, null, null)

    elif cmdInput in cmdShorts['delete']:
        withAtta = True
        uInput = userInput('Would you like to delete message(s) from the (i)nbox or (O)utbox?').lower()

        if uInput in inputShorts['inbox']:
            src = toReadInbox(cmd='delete', withAtta=withAtta)

        else:
            src = toReadOutbox(cmd='delete', withAtta=withAtta)

    elif cmdInput in cmdShorts['read']:  # Opens a message from the inbox for viewing.
        withAtta = False
        uInput = userInput('Would you like to read a message from the (i)nbox or (O)utbox?').lower()

        if uInput in inputShorts['inbox']:
            src = toReadInbox(cmd='read', withAtta=withAtta)

        else:
            src = toReadOutbox(cmd='read', withAtta=withAtta)

    elif cmdInput in cmdShorts['save']:
        uInput = userInput('Would you like to save a message from the (i)nbox or (O)utbox?').lower()

        if uInput in inputShorts['inbox']:
            withAtta = True
            uInput = userInput('Would you like to decode and (s)ave or (D)ump directly?').lower()
            if uInput in inputShorts['save']:
                withAtta = False
            src = toReadInbox(cmd='save', trunck=-1, withAtta=withAtta)

        else:
            withAtta = True
            uInput = userInput('Would you like to decode and (s)ave or (D)ump directly?').lower()
            if uInput in inputShorts['save']:
                withAtta = False

            src = toReadOutbox(cmd='save', trunck=-1, withAtta=withAtta)

    elif cmdInput in cmdShorts['quit']:
        src = '\n     You are already at the main menu. Use "quit" to quit.\n'

    elif cmdInput in cmdShorts['listAddressBookEntries']:
        src = listAddressBookEntries()

    elif cmdInput in cmdShorts['addAddressBookEntry']:
        label = ''
        while uInput == '':
            uInput = userInput('Enter address to add.')
        while label == '':
            label = userInput('Enter label')
        src = addAddressToAddressBook(uInput, label)

    elif cmdInput in cmdShorts['deleteAddressBookEntry']:
        while uInput == '':
            uInput = userInput('Enter address to delete.')
        src = deleteAddressFromAddressBook(uInput)

    elif cmdInput in cmdShorts['readAll']:
        src = markAllMessagesReadbit(True)

    elif cmdInput in cmdShorts['unreadAll']:
        src = markAllMessagesReadbit(False)

    elif cmdInput in cmdShorts['status']:
        src = clientStatus()

    elif cmdInput in cmdShorts['shutdown']:
        src = shutdown()

    else:
        src = '\n     "' + cmdInput + '" is not a command.\n'

    if src is None:
        src = retStrings['none']
        usrPrompt = 1
    elif 'Connection' in src or 'ProtocolError' in src:
        usrPrompt = 0
    else:
        usrPrompt = 1

    print src


def main():
    """Entrypoint for the CLI app"""

    global conn, api, usrPrompt, cmdStr

    if usrPrompt == 0:
        print
        print '     ------------------------------'
        print '     | Bitmessage Daemon by .dok  |'
        print '     | Version 0.3.1 for BM 0.6.2 |'
        print '     ------------------------------'

        conn = apiData()
        if conn != '':
            api = BMAPIWrapper(conn)
            if apiTest() is False:
                print
                print '     ****************************************************************'
                print '        WARNING: You are not connected to the Bitmessage client.'
                print '     Either Bitmessage is not running or your settings are incorrect.'
                print '     Use the command "apiTest" or "bmSettings" to resolve this issue.'
                print '     ****************************************************************\n'

            print '\nType (H)elp for a list of commands.\nPress Enter for default cmd [{}]: '.format(cmdStr)  # Startup message
            usrPrompt = 2
        else:
            print
            print '     *****************************************************'
            print '        WARNING: API not functionable till you finish the'
            print '     configuration.'
            print '     *****************************************************\n'
            print '\nType (H)elp for a list of commands.\nPress Enter for default cmd [{}]: '.format(cmdStr)  # Startup message
            usrPrompt = 0

    elif usrPrompt == 1:
        print '\nType (H)elp for a list of commands.\nPress Enter for default cmd [{}]: '.format(cmdStr)  # Startup message
        usrPrompt = 2

    try:
        cmdInput = raw_input('>').lower().replace(" ", "")
        if cmdInput != '':
            cmdStr = cmdInput  # save as last cmd for replay
        UI(cmdStr)

    except EOFError:
        UI("quit")


if __name__ == "__main__":
    while True:
        try:
            main()
        except InputException as e:
            print retStrings.get(e.resKey, '\n     Not defined error raised: %s.\n' % e.resKey)
            usrPrompt = 1

