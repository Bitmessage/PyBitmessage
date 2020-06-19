# -*- coding: utf-8 -*-
"""Sound Module"""

# sound type constants
SOUND_NONE = 0
SOUND_KNOWN = 1
SOUND_UNKNOWN = 2
SOUND_CONNECTED = 3
SOUND_DISCONNECTED = 4
SOUND_CONNECTION_GREEN = 5


# returns true if the given sound category is a connection sound
# rather than a received message sound
def is_connection_sound(category):
    """Check if sound type is related to connectivity"""
    return category in (
        SOUND_CONNECTED,
        SOUND_DISCONNECTED,
        SOUND_CONNECTION_GREEN
    )


extensions = ('wav', 'mp3', 'oga')
