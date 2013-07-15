import shared
import socket
import defaultKnownNodes
import pickle
import time

def knownNodes():
    try:
        # We shouldn't have to use the shared.knownNodesLock because this had
        # better be the only thread accessing knownNodes right now.
        pickleFile = open(shared.appdata + 'knownnodes.dat', 'rb')
        shared.knownNodes = pickle.load(pickleFile)
        pickleFile.close()
    except:
        defaultKnownNodes.createDefaultKnownNodes(shared.appdata)
        pickleFile = open(shared.appdata + 'knownnodes.dat', 'rb')
        shared.knownNodes = pickle.load(pickleFile)
        pickleFile.close()
    if shared.config.getint('bitmessagesettings', 'settingsversion') > 6:
        print 'Bitmessage cannot read future versions of the keys file (keys.dat). Run the newer version of Bitmessage.'
        raise SystemExit
        

def dns():
    # DNS bootstrap. This could be programmed to use the SOCKS proxy to do the
    # DNS lookup some day but for now we will just rely on the entries in
    # defaultKnownNodes.py. Hopefully either they are up to date or the user
    # has run Bitmessage recently without SOCKS turned on and received good
    # bootstrap nodes using that method.
    if shared.config.get('bitmessagesettings', 'socksproxytype') == 'none':
        try:
            for item in socket.getaddrinfo('bootstrap8080.bitmessage.org', 80):
                print 'Adding', item[4][0], 'to knownNodes based on DNS boostrap method'
                shared.knownNodes[1][item[4][0]] = (8080, int(time.time()))
        except:
            print 'bootstrap8080.bitmessage.org DNS bootstrapping failed.'
        try:
            for item in socket.getaddrinfo('bootstrap8444.bitmessage.org', 80):
                print 'Adding', item[4][0], 'to knownNodes based on DNS boostrap method'
                shared.knownNodes[1][item[4][0]] = (8444, int(time.time()))
        except:
            print 'bootstrap8444.bitmessage.org DNS bootstrapping failed.'
    else:
        print 'DNS bootstrap skipped because SOCKS is used.'
        
