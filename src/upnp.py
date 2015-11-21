# A simple upnp module to forward port for BitMessage
# Reference: http://mattscodecave.com/posts/using-python-and-upnp-to-forward-a-port
import socket
import httplib
from shared import config

routers = []

def searchRouter():
    SSDP_ADDR = "239.255.255.250"
    SSDP_PORT = 1900
    SSDP_MX = 2
    SSDP_ST = "urn:schemas-upnp-org:device:InternetGatewayDevice:1"

    ssdpRequest = "M-SEARCH * HTTP/1.1\r\n" + \
                    "HOST: %s:%d\r\n" % (SSDP_ADDR, SSDP_PORT) + \
                    "MAN: \"ssdp:discover\"\r\n" + \
                    "MX: %d\r\n" % (SSDP_MX, ) + \
                    "ST: %s\r\n" % (SSDP_ST, ) + "\r\n"

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(ssdpRequest, (SSDP_ADDR, SSDP_PORT))
    routers = []
    sock.settimeout(0.5)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        sock.settimeout(2)
        logger.debug("Sending UPnP query")
        sock.sendto(ssdpRequest, (SSDP_ADDR, SSDP_PORT))
    except:
        logger.exception("UPnP sock failed")
    try:
        while True:
            resp,(ip,port) = sock.recvfrom(1000)
            if resp is None:
                continue
            routers.append(Router(resp, ip))
            resp,(ip,port) = sock.recvfrom(1000)
    except:pass
        
    return routers

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
    def __init__(self, ssdpResponse, address):
        import urllib2
        from xml.dom.minidom import parseString
        from urlparse import urlparse

        self.address = address

        row = ssdpResponse.split('\r\n')
        header = {}
        for i in range(1, len(row)):
            part = row[i].split(': ')
            if len(part) == 2:
                header[part[0].lower()] = part[1]

        self.routerPath = urlparse(header['location'])

        # get the profile xml file and read it into a variable
        directory = urllib2.urlopen(header['location']).read()

        # create a DOM object that represents the `directory` document
        dom = parseString(directory)

        self.name = dom.getElementsByTagName('friendlyName')[0].childNodes[0].data
        # find all 'serviceType' elements
        service_types = dom.getElementsByTagName('serviceType')

        for service in service_types:
            if service.childNodes[0].data.find('WANIPConnection') > 0:
                self.path = service.parentNode.getElementsByTagName('controlURL')[0].childNodes[0].data

        # get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            logger.debug("Connecting to %s:%i", self.address, self.routerPath.port)
            s.connect ((self.address, self.routerPath.port))
        except:
            pass
        self.localAddress = s.getsockname()[0]
        logger.debug("Local IP: %s", self.localAddress)
        try:
            s.close()
        except:
            pass

    def AddPortMapping(self, externalPort, internalPort, internalClient, protocol, description, leaseDuration = 0, enabled = 1):
        resp = self.soapRequest('WANIPConnection:1', 'AddPortMapping', [
                ('NewExternalPort', str(externalPort)),
                ('NewProtocol', protocol),
                ('NewInternalPort', str(internalPort)),
                ('NewInternalClient', internalClient),
                ('NewEnabled', str(enabled)),
                ('NewPortMappingDescription', str(description)),
                ('NewLeaseDuration', str(leaseDuration))
            ])
        self.extPort = externalPort
        return resp

    def DeletePortMapping(self, externalPort, protocol):
        from debug import logger
        resp = self.soapRequest('WANIPConnection:1', 'DeletePortMapping', [
                ('NewExternalPort', str(externalPort)),
                ('NewProtocol', protocol),
            ])
        logger.info("Removed UPnP mapping on external port %i", extPort)
        return resp

    def GetExternalIPAddress(self):
        from xml.dom.minidom import parseString
        resp = self.soapRequest('WANIPConnection:1', 'GetExternalIPAddress')
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
        resp = conn.getresponse().read()
        dom = parseString(resp)
        errinfo = dom.getElementsByTagName('errorDescription')
        if len(errinfo) > 0:
            logger.error("UPnP error: %s", resp)
            raise UPnPError(errinfo[0].childNodes[0].data) 
        return resp

def createPortMappingInternal(router):
    from debug import logger

    for i in range(0, 50):
        try:
            routerIP, = unpack('>I', socket.inet_aton(router.address))
            localIP = router.localAddress
            localPort = shared.config.getint('bitmessagesettings', 'port')
            if i == 0:
                extPort = localPort # try same port first
            else:
                extPort = randint(32767, 65535)
            logger.debug("Requesting UPnP mapping for %s:%i on external port %i", localIP, localPort,  extPort)
            router.AddPortMapping(extPort, localPort, localIP, 'TCP', 'BitMessage')
            logger.info("Successfully established UPnP mapping for %s:%i on external port %i", localIP, localPort, extPort)
            shared.extPort = extPort
            break
        except UPnPError:
            logger.debug("UPnP error: ", exc_info=True)

def createPortMapping():
    from debug import logger
    global routers

    routers = searchRouter()
    logger.debug("Found %i UPnP routers", len(routers))

    for router in routers:
        createPortMappingInternal(router)

def deletePortMapping():
    localPort = config.getint('bitmessagesettings', 'port')
    for router in routers:
        if hasattr(router, "extPort"):
            router.DeletePortMapping(router.extPort, 'TCP')
