# -*- coding: utf-8 -*-

from pybitmessage.bitmessageqt import sound

import pycanberra

_canberra = pycanberra.Canberra()

_theme = {
    sound.SOUND_UNKNOWN: 'message-new-email',
    sound.SOUND_CONNECTED: 'network-connectivity-established',
    sound.SOUND_DISCONNECTED: 'network-connectivity-lost',
    sound.SOUND_CONNECTION_GREEN: 'network-connectivity-established'
}


def connect_plugin(category, label=None):
    try:
        _canberra.play(0, pycanberra.CA_PROP_EVENT_ID, _theme[category], None)
    except (KeyError, pycanberra.CanberraException):
        pass
