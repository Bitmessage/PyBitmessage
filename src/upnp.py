# pylint: disable=too-many-statements,too-many-branches,protected-access,no-self-use
"""
Complete UPnP port forwarding implementation in separate thread.
Reference: http://mattscodecave.com/posts/using-python-and-upnp-to-forward-a-port
"""

import httplib
import socket
import time
import urllib2
from random import randint
from urlparse import urlparse
from xml.dom.minidom import Document, parseString

import queues
import state
import tr
from bmconfigparser import BMConfigParser
from debug import logger
from network import BMConnectionPool, knownnodes, StoppableThread
from network.node import Peer


def createRequestXML(service, action, arguments=None):
    """Router UPnP requests are XML formatted"""

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
    if arguments is not None:
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
    """Handle a UPnP error"""

    def __init__(self, message):
        super(UPnPError, self).__init__()
        logger.error(message)


class Router:  # pylint: disable=old-style-class
    """Encapulate routing"""
    name = ""
    path = ""
    address = None
    routerPath = None
    extPort = None

    def __init__(self, ssdpResponse, address):

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
                logger.error("UPnP: no hostname: %s", header['location'])
        except KeyError:
            logger.error("UPnP: missing location header")

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

    def AddPortMapping(
            self,
            externalPort,
            internalPort,
            internalClient,
            protocol,
            description,
            leaseDuration=0,
            enabled=1,
    ):  # pylint: disable=too-many-arguments
        """Add UPnP port mapping"""

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
        logger.info("Successfully established UPnP mapping for %s:%i on external port %i",
                    internalClient, internalPort, externalPort)
        return resp

    def DeletePortMapping(self, externalPort, protocol):
        """Delete UPnP port mapping"""

        resp = self.soapRequest(self.upnp_schema + ':1', 'DeletePortMapping', [
            ('NewRemoteHost', ''),
            ('NewExternalPort', str(externalPort)),
            ('NewProtocol', protocol),
        ])
        logger.info("Removed UPnP mapping on external port %i", externalPort)
        return resp

    def GetExternalIPAddress(self):
        """Get the external address"""

        resp = self.soapRequest(
            self.upnp_schema + ':1', 'GetExternalIPAddress')
        dom = parseString(resp.read())
        return dom.getElementsByTagName(
            'NewExternalIPAddress')[0].childNodes[0].data

    def soapRequest(self, service, action, arguments=None):
        """Make a request to a router"""

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
                if errinfo:
                    logger.error("UPnP error: %s", respData)
                    raise UPnPError(errinfo[0].childNodes[0].data)
            except:
                raise UPnPError("Unable to parse SOAP error: %s" % (respData))
        return resp


class uPnPThread(StoppableThread):
    """Start a thread to handle UPnP activity"""

    SSDP_ADDR = "239.255.255.250"
    GOOGLE_DNS = "8.8.8.8"
    SSDP_PORT = 1900
    SSDP_MX = 2
    SSDP_ST = "urn:schemas-upnp-org:device:InternetGatewayDevice:1"

    def __init__(self):
        super(uPnPThread, self).__init__(name="uPnPThread")
        try:
            self.extPort = BMConfigParser().getint('bitmessagesettings', 'extport')
        except:
            self.extPort = None
        self.localIP = self.getLocalIP()
        self.routers = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.localIP, 0))
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        self.sock.settimeout(5)
        self.sendSleep = 60

    def run(self):
        """Start the thread to manage UPnP activity"""

        logger.debug("Starting UPnP thread")
        logger.debug("Local IP: %s", self.localIP)
        lastSent = 0

        # wait until asyncore binds so that we know the listening port
        bound = False
        while state.shutdown == 0 and not self._stopped and not bound:
            for s in BMConnectionPool().listeningSockets.values():
                if s.is_bound():
                    bound = True
            if not bound:
                time.sleep(1)

        # pylint: disable=attribute-defined-outside-init
        self.localPort = BMConfigParser().getint('bitmessagesettings', 'port')

        while state.shutdown == 0 and BMConfigParser().safeGetBoolean('bitmessagesettings', 'upnp'):
            if time.time() - lastSent > self.sendSleep and not self.routers:
                try:
                    self.sendSearchRouter()
                except:
                    pass
                lastSent = time.time()
            try:
                while state.shutdown == 0 and BMConfigParser().safeGetBoolean('bitmessagesettings', 'upnp'):
                    resp, (ip, _) = self.sock.recvfrom(1000)
                    if resp is None:
                        continue
                    newRouter = Router(resp, ip)
                    for router in self.routers:
                        if router.routerPath == newRouter.routerPath:
                            break
                    else:
                        logger.debug("Found UPnP router at %s", ip)
                        self.routers.append(newRouter)
                        self.createPortMapping(newRouter)
                        try:
                            self_peer = Peer(
                                newRouter.GetExternalIPAddress(),
                                self.extPort
                            )
                        except:
                            logger.debug('Failed to get external IP')
                        else:
                            with knownnodes.knownNodesLock:
                                knownnodes.addKnownNode(
                                    1, self_peer, is_self=True)
                        queues.UISignalQueue.put(('updateStatusBar', tr._translate(
                            "MainWindow", 'UPnP port mapping established on port %1'
                        ).arg(str(self.extPort))))
                        break
            except socket.timeout:
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
        if deleted:
            queues.UISignalQueue.put(('updateStatusBar', tr._translate("MainWindow", 'UPnP port mapping removed')))
        logger.debug("UPnP thread done")

    def getLocalIP(self):
        """Get the local IP of the node"""

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.connect((uPnPThread.GOOGLE_DNS, 1))
        return s.getsockname()[0]

    def sendSearchRouter(self):
        """Querying for UPnP services"""

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
        """Add a port mapping"""

        for i in range(50):
            try:
                localIP = self.localIP
                if i == 0:
                    extPort = self.localPort  # try same port first
                elif i == 1 and self.extPort:
                    extPort = self.extPort  # try external port from last time next
                else:
                    extPort = randint(32767, 65535)
                logger.debug(
                    "Attempt %i, requesting UPnP mapping for %s:%i on external port %i",
                    i,
                    localIP,
                    self.localPort,
                    extPort)
                router.AddPortMapping(extPort, self.localPort, localIP, 'TCP', 'BitMessage')
                self.extPort = extPort
                BMConfigParser().set('bitmessagesettings', 'extport', str(extPort))
                BMConfigParser().save()
                break
            except UPnPError:
                logger.debug("UPnP error: ", exc_info=True)

    def deletePortMapping(self, router):
        """Delete a port mapping"""
        router.DeletePortMapping(router.extPort, 'TCP')
