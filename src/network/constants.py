"""
Network protocol constants
"""


ADDRESS_ALIVE = 10800  #: address is online if online less than this many seconds ago
MAX_ADDR_COUNT = 1000  #: protocol specification says max 1000 addresses in one addr command
MAX_MESSAGE_SIZE = 1600100  #: ~1.6 MB which is the maximum possible size of an inv message.
MAX_OBJECT_PAYLOAD_SIZE = 2**18  #: 2**18 = 256kB is the maximum size of an object payload
MAX_OBJECT_COUNT = 50000  #: protocol specification says max 50000 objects in one inv command
MAX_TIME_OFFSET = 3600  #: maximum time offset
