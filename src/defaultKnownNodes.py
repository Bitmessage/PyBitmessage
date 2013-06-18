import pickle
import socket
from struct import *
import time
import random
import sys
from time import strftime, localtime

def createDefaultKnownNodes(appdata):
    ############## Stream 1 ################
    stream1 = {}

    stream1['85.171.174.131'] = (8444,int(time.time()))
    stream1['23.28.68.159'] = (8444,int(time.time()))
    stream1['66.108.210.240'] = (8080,int(time.time()))
    stream1['204.236.246.212'] = (8444,int(time.time()))
    stream1['78.81.56.239'] = (8444,int(time.time()))
    stream1['122.60.235.157'] = (8444,int(time.time()))
    stream1['204.236.246.212'] = (8444,int(time.time()))
    stream1['24.98.219.109'] = (8444,int(time.time()))


    ############# Stream 2 #################
    stream2 = {}
    # None yet

    ############# Stream 3 #################
    stream3 = {}
    # None yet

    allKnownNodes = {}
    allKnownNodes[1] = stream1
    allKnownNodes[2] = stream2
    allKnownNodes[3] = stream3

    #print stream1
    #print allKnownNodes

    output = open(appdata + 'knownnodes.dat', 'wb')

    # Pickle dictionary using protocol 0.
    pickle.dump(allKnownNodes, output)

    output.close()
    return allKnownNodes

def readDefaultKnownNodes(appdata):
    pickleFile = open(appdata + 'knownnodes.dat', 'rb')
    knownNodes = pickle.load(pickleFile)
    pickleFile.close()
    knownNodes
    for stream, storedValue in knownNodes.items():
        for host,value in storedValue.items():
            port, storedtime = storedValue[host]
            print host, '\t', port, '\t', unicode(strftime('%a, %d %b %Y  %I:%M %p',localtime(storedtime)))

if __name__ == "__main__":

    APPNAME = "PyBitmessage"
    from os import path, environ
    if sys.platform == 'darwin':
        from AppKit import NSSearchPathForDirectoriesInDomains
        # http://developer.apple.com/DOCUMENTATION/Cocoa/Reference/Foundation/Miscellaneous/Foundation_Functions/Reference/reference.html#//apple_ref/c/func/NSSearchPathForDirectoriesInDomains
        # NSApplicationSupportDirectory = 14
        # NSUserDomainMask = 1
        # True for expanding the tilde into a fully qualified path
        appdata = path.join(NSSearchPathForDirectoriesInDomains(14, 1, True)[0], APPNAME) + '/'
    elif 'win' in sys.platform:
        appdata = path.join(environ['APPDATA'], APPNAME) + '\\'
    else:
        appdata = path.expanduser(path.join("~", "." + APPNAME + "/"))


    print 'New list of all known nodes:', createDefaultKnownNodes(appdata)
    readDefaultKnownNodes(appdata)


