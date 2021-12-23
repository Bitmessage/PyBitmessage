"""
Network protocol constants
"""


#: address is online if online less than this many seconds ago
ADDRESS_ALIVE = 10800
#: protocol specification says max 1000 addresses in one addr command
MAX_ADDR_COUNT = 1000
#: ~1.6 MB which is the maximum possible size of an inv message.
MAX_MESSAGE_SIZE = 1600100
#: 2**18 = 256kB is the maximum size of an object payload
MAX_OBJECT_PAYLOAD_SIZE = 2**18
#: protocol specification says max 50000 objects in one inv command
MAX_OBJECT_COUNT = 50000
#: maximum time offset
MAX_TIME_OFFSET = 3600
