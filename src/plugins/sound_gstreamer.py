# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst  # noqa: E402

Gst.init(None)
_player = Gst.ElementFactory.make("playbin", "player")


def connect_plugin(sound_file):
    _player.set_state(Gst.State.NULL)
    _player.set_property("uri", "file://" + sound_file)
    _player.set_state(Gst.State.PLAYING)
