from struct import unpack

from addresses import decodeVarint
from debug import logger
from shared import unpackNetworkAddress

class AddressMessageParser:
    def __init__(self, data, remoteProtocolVersion):
        # Byte array of data to parse.
        self.data = data
        # Position of where the next datum starts, in bytes.
        self.position = 0
        # Protocol version of the peer with which this message corresponds.
        self.remoteProtocolVersion = remoteProtocolVersion

    def parse(self):
        #logger.debug('Parsing addr message %s' % (repr(self.data)))
        listOfAddressDetailsToBroadcast = []

        numberOfAddresses = self.__consumeNumberOfAddresses()
        if not numberOfAddresses:
            raise StopIteration
        logger.debug('addr message contains %d IP addresses.', numberOfAddresses)

        needToWriteKnownNodes = False
        for addressIndex in range(numberOfAddresses):
            try:
                hostDetails = self.__consumeAddress()
            except Exception as err:
                logger.exception('ERROR TRYING TO UNPACK addr message.')
                break
            if not hostDetails:
                continue

            timestamp, stream, services, host, port = hostDetails
            yield hostDetails

    def __consumeNumberOfAddresses(self):
        numberOfAddresses, lengthOfNumberOfAddresses  = decodeVarint(
                self.data[self.position:self.position+10])
        self.position += lengthOfNumberOfAddresses

        # Sanity checks
        if numberOfAddresses > 1000:
            logger.debug('addr message contains too many addresses. Ignoring.')
            return 0
        if numberOfAddresses == 0:
            logger.debug('addr message contains no addresses.')
            return 0

        if      ( self.remoteProtocolVersion == 1 and
                  len(self.data) != lengthOfNumberOfAddresses + (34 * numberOfAddresses)
                ) or (
                  self.remoteProtocolVersion == 2 and
                  len(self.data) != lengthOfNumberOfAddresses + (38 * numberOfAddresses)
                ):
            logger.debug('addr message (%s) does not contain the correct amount of data. Ignoring.'
                    % (repr(self.data)))
            return 0

        return numberOfAddresses

    def __consumeTimestamp(self):
        if self.remoteProtocolVersion == 1:
            #logging.debug('at %s, timestamp data: %s'
            #        % (self.position, repr(self.data[self.position : self.position + 4])))
            timestamp, = unpack(
                    '>I', self.data[self.position : self.position + 4])
            self.position += 4
        elif self.remoteProtocolVersion == 2:
            #logger.debug('at %s, timestamp data: %s'
            #        % (self.position, repr(self.data[self.position : self.position + 8])))
            timestamp, = unpack(
                    '>Q', self.data[self.position : self.position + 8])
            self.position += 8
        return timestamp

    def __consumeStream(self):
        #logger.debug('at %s, stream data: %s'
        #        % (self.position, repr(self.data[self.position : self.position + 4])))
        stream, = unpack('>I', self.data[self.position : self.position + 4])
        self.position += 4
        return stream

    def __consumeServices(self):
        #logger.debug('at %s, services data: %s'
        #        % (self.position, repr(self.data[self.position : self.position + 8])))
        services, = unpack('>Q', self.data[self.position : self.position + 8])
        self.position += 8
        return services

    def __consumeHost(self):
        #logger.debug('at %s, host data: %s' 
        #        % (self.position, repr(self.data[self.position : self.position + 16])))
        hostdata = self.data[self.position : self.position + 16]
        self.position += 16
        host = unpackNetworkAddress(hostdata)
        #logger.debug('host: %s' % (host))
        return host

    def __consumePort(self):
        #logger.debug('at %s, port data: %s'
        #        % (self.position, repr(self.data[self.position : self.position + 2])))
        port, = unpack('>H', self.data[self.position : self.position + 2])
        #logger.debug('port: %s' % (port))
        self.position += 2
        return port

    # Consume one entry in the addr_list.
    # Returns (timestamp, stream, services, host, port) tuple on success,
    # and None on failure.
    def __consumeAddress(self):
        past_position = self.position
        try:
            timestamp = self.__consumeTimestamp()
            stream = self.__consumeStream()
            services = self.__consumeServices()
            host = self.__consumeHost()
            port = self.__consumePort()
            addressDetails = (timestamp, stream, services, host, port)
        except Exception as err:
            logger.warning('Could not read address in addr message. Err: %s' % (err))
            addressDetails = None
        finally:
            if self.remoteProtocolVersion == 1:
                self.position = past_position + 34
            elif self.remoteProtocolVersion == 2:
                self.position = past_position + 38
        return addressDetails
