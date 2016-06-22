﻿# A simple upnp module to forward port for BitMessage
# Reference: http://mattscodecave.com/posts/using-python-and-upnp-to-forward-a-port
import httplib
from random import randint
import socket
from struct import unpack, pack
import threading
import time
from helper_threading import *
import shared
import tr

def createRequestXML(service, action, arguments=[]):
    from xml.dom.minidom import Document

    doc = Document()

    # create the envelope element and set its attributes
    envelope = doc.createElementNS('', 's:Envelope')
    envelope.setAttribute('xmlns:s', 'http://schemas.xmlsoap.org/soap/envelope/')
    envelope.setAttribute('s:encodingStyle', 'http://schemas.xmlsoap.org/soap/encoding/')

    # create the body element
    body = doc.createElementNS('', 's:Body')

    # create the function element and set its attribute
    fn = doc.createElementNS('', 'u:%s' % action)
    fn.setAttribute('xmlns:u', 'urn:schemas-upnp-org:service:%s' % service)

    # setup the argument element names and values
    # using a list of tuples to preserve order

    # container for created nodes
    argument_list = []

    # iterate over arguments, create nodes, create text nodes,
    # append text nodes to nodes, and finally add the ready product
    # to argument_list
    for k, v in arguments:
        tmp_node = doc.createElement(k)
        tmp_text_node = doc.createTextNode(v)
        tmp_node.appendChild(tmp_text_node)
        argument_list.append(tmp_node)

    # append the prepared argument nodes to the function element
    for arg in argument_list:
        fn.appendChild(arg)

    # append function element to the body element
    body.appendChild(fn)

    # append body element to envelope element
    envelope.appendChild(body)

    # append envelope element to document, making it the root element
    doc.appendChild(envelope)

    # our tree is ready, conver it to a string
    return doc.toxml()

class UPnPError(Exception):
    def __init__(self, message):
        self.message

class Router:
    name = ""
    path = ""
    address = None
    routerPath = None
    extPort = None
    
    def __init__(self, ssdpResponse, address):
        import urllib2
        from xml.dom.minidom import parseString
        from urlparse import urlparse
        from debug import logger

        self.address = address

        row = ssdpResponse.split('\r\n')
        header = {}
        for i in range(1, len(row)):
            part = row[i].split(': ')
            if len(part) == 2:
                header[part[0].lower()] = part[1]

        try:
            self.routerPath = urlparse(header['location'])
            if not self.routerPath or not hasattr(self.routerPath, "hostname"):
                logger.error ("UPnP: no hostname: %s", header['location'])
        except KeyError:
            logger.error ("UPnP: missing location header")

        # get the profile xml file and read it into a variable
        directory = urllib2.urlopen(header['location']).read()

        # create a DOM object that represents the `directory` document
        dom = parseString(directory)

        self.name = dom.getElementsByTagName('friendlyName')[0].childNodes[0].data
        # find all 'serviceType' elements
        service_types = dom.getElementsByTagName('serviceType')

        for service in service_types:
            if service.childNodes[0].data.find('WANIPConnection') > 0 or \
                service.childNodes[0].data.find('WANPPPConnection') > 0:
                self.path = service.parentNode.getElementsByTagName('controlURL')[0].childNodes[0].data
                self.upnp_schema = service.childNodes[0].data.split(':')[-2]

    def AddPortMapping(self, externalPort, internalPort, internalClient, protocol, description, leaseDuration = 0, enabled = 1):
        from debug import logger
        resp = self.soapRequest(self.upnp_schema + ':1', 'AddPortMapping', [
                ('NewRemoteHost', ''),
                ('NewExternalPort', str(externalPort)),
                ('NewProtocol', protocol),
                ('NewInternalPort', str(internalPort)),
                ('NewInternalClient', internalClient),
                ('NewEnabled', str(enabled)),
                ('NewPortMappingDescription', str(description)),
                ('NewLeaseDuration', str(leaseDuration))
            ])
        self.extPort = externalPort
        logger.info("Successfully established UPnP mapping for %s:%i on external port %i", internalClient, internalPort, externalPort)
        return resp

    def DeletePortMapping(self, externalPort, protocol):
        from debug import logger
        resp = self.soapRequest(self.upnp_schema + ':1', 'DeletePortMapping', [
                ('NewRemoteHost', ''),
                ('NewExternalPort', str(externalPort)),
                ('NewProtocol', protocol),
            ])
        logger.info("Removed UPnP mapping on external port %i", externalPort)
        return resp

    def GetExternalIPAddress(self):
        from xml.dom.minidom import parseString
        resp = self.soapRequest(self.upnp_schema + ':1', 'GetExternalIPAddress')
        dom = parseString(resp)
        return dom.getElementsByTagName('NewExternalIPAddress')[0].childNodes[0].data
    
    def soapRequest(self, service, action, arguments=[]):
        from xml.dom.minidom import parseString
        from debug import logger
        conn = httplib.HTTPConnection(self.routerPath.hostname, self.routerPath.port)
        conn.request(
            'POST',
            self.path,
            createRequestXML(service, action, arguments),
            {
                'SOAPAction': '"urn:schemas-upnp-org:service:%s#%s"' % (service, action),
                'Content-Type': 'text/xml'
                }
            )
        resp = conn.getresponse()
        conn.close()
        if resp.status == 500:
            respData = resp.read()
            try:
                dom = parseString(respData)
                errinfo = dom.getElementsByTagName('errorDescription')
                if len(errinfo) > 0:
                    logger.error("UPnP error: %s", respData)
                    raise UPnPError(errinfo[0].childNodes[0].data)
            except:
                raise UPnPError("Unable to parse SOAP error: %s" %(respData))
        return resp

class uPnPThread(threading.Thread, StoppableThread):
    SSDP_ADDR = "239.255.255.250"
    GOOGLE_DNS = "8.8.8.8"
    SSDP_PORT = 1900
    SSDP_MX = 2
    SSDP_ST = "urn:schemas-upnp-org:device:InternetGatewayDevice:1"

    def __init__ (self):
        threading.Thread.__init__(self, name="uPnPThread")
        self.localPort = shared.config.getint('bitmessagesettings', 'port')
        try:
            self.extPort = shared.config.getint('bitmessagesettings', 'extport')
        except:
            self.extPort = None
        self.localIP = self.getLocalIP()
        self.routers = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.localIP, 10000))
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        self.sock.settimeout(5)
        self.sendSleep = 60
        self.initStop()

    def run(self):
        from debug import logger
        
        logger.debug("Starting UPnP thread")
        logger.debug("Local IP: %s", self.localIP)
        lastSent = 0
        while shared.shutdown == 0 and shared.safeConfigGetBoolean('bitmessagesettings', 'upnp'):
            if time.time() - lastSent > self.sendSleep and len(self.routers) == 0:
                try:
                    self.sendSearchRouter()
                except:
                    pass
                lastSent = time.time()
            try:
                while shared.shutdown == 0 and shared.safeConfigGetBoolean('bitmessagesettings', 'upnp'):
                    resp,(ip,port) = self.sock.recvfrom(1000)
                    if resp is None:
                        continue
                    newRouter = Router(resp, ip)
                    for router in self.routers:
                        if router.location == newRouter.location:
                            break
                    else:
                        logger.debug("Found UPnP router at %s", ip)
                        self.routers.append(newRouter)
                        self.createPortMapping(newRouter)
                        shared.UISignalQueue.put(('updateStatusBar', tr._translate("MainWindow",'UPnP port mapping established on port %1').arg(str(self.extPort))))
                        break
            except socket.timeout as e:
                pass
            except:
                logger.error("Failure running UPnP router search.", exc_info=True)
            for router in self.routers:
                if router.extPort is None:
                    self.createPortMapping(router)
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            self.sock.close()
        except:
            pass
        deleted = False
        for router in self.routers:
            if router.extPort is not None:
                deleted = True
                self.deletePortMapping(router)
        shared.extPort = None
        if deleted:
            shared.UISignalQueue.put(('updateStatusBar', tr._translate("MainWindow",'UPnP port mapping removed')))
        logger.debug("UPnP thread done")

    def getLocalIP(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.connect((uPnPThread.GOOGLE_DNS, 1))
        return s.getsockname()[0]

    def sendSearchRouter(self):
        from debug import logger
        ssdpRequest = "M-SEARCH * HTTP/1.1\r\n" + \
                    "HOST: %s:%d\r\n" % (uPnPThread.SSDP_ADDR, uPnPThread.SSDP_PORT) + \
                    "MAN: \"ssdp:discover\"\r\n" + \
                    "MX: %d\r\n" % (uPnPThread.SSDP_MX, ) + \
                    "ST: %s\r\n" % (uPnPThread.SSDP_ST, ) + "\r\n"

        try:
            logger.debug("Sending UPnP query")
            self.sock.sendto(ssdpRequest, (uPnPThread.SSDP_ADDR, uPnPThread.SSDP_PORT))
        except:
            logger.exception("UPnP send query failed")

    def createPortMapping(self, router):
        from debug import logger

        for i in range(50):
            try:
                routerIP, = unpack('>I', socket.inet_aton(router.address))
                localIP = self.localIP
                if i == 0:
                    extPort = self.localPort # try same port first
                elif i == 1 and self.extPort:
                    extPort = self.extPort # try external port from last time next
                else:
                    extPort = randint(32767, 65535)
                logger.debug("Attempt %i, requesting UPnP mapping for %s:%i on external port %i", i, localIP, self.localPort,  extPort)
                router.AddPortMapping(extPort, self.localPort, localIP, 'TCP', 'BitMessage')
                shared.extPort = extPort
                self.extPort = extPort
                shared.config.set('bitmessagesettings', 'extport', str(extPort))
                break
            except UPnPError:
                logger.debug("UPnP error: ", exc_info=True)

    def deletePortMapping(self, router):
        router.DeletePortMapping(router.extPort, 'TCP')



