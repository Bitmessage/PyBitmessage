"""
src/state.py
=================================
"""
import collections


# Network protocols availability, initialised below
networkProtocolAvailability = None

sqlReady = False  # set to true by sqlTread when ready for processing

trustedPeer = None
Peer = collections.namedtuple('Peer', ['host', 'port'])


def resetNetworkProtocolAvailability():
    """This method helps to reset the availability of network protocol"""
    # pylint: disable=global-statement
    global networkProtocolAvailability
    networkProtocolAvailability = {'IPv4': None, 'IPv6': None, 'onion': None}


resetNetworkProtocolAvailability()

association = ''

navinstance = None

mail_id = 0

myAddressObj = None

detailPageType = None

ackdata = None

status = None

screen_density = None

msg_counter_objs = None

check_sent_acc = None

sent_count = 0

inbox_count = 0

trash_count = 0

draft_count = 0

all_count = 0

searcing_text = ''

search_screen = ''

send_draft_mail = None

is_allmail = False

in_composer = False

availabe_credit = 0

in_sent_method = False

in_search_mode = False

imageDir = None
