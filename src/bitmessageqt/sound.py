# -*- coding: utf-8 -*-

# sound type constants
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *
SOUND_NONE = 0
SOUND_KNOWN = 1
SOUND_UNKNOWN = 2
SOUND_CONNECTED = 3
SOUND_DISCONNECTED = 4
SOUND_CONNECTION_GREEN = 5


# returns true if the given sound category is a connection sound
# rather than a received message sound
def is_connection_sound(category):
    return category in (
        SOUND_CONNECTED,
        SOUND_DISCONNECTED,
        SOUND_CONNECTION_GREEN
    )

extensions = ('wav', 'mp3', 'oga')
