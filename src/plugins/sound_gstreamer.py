# -*- coding: utf-8 -*-
"""
Sound notification plugin using gstreamer
"""
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst  # noqa: E402

Gst.init(None)
_player = Gst.ElementFactory.make("playbin", "player")


def connect_plugin(sound_file):
    """Entry point for sound file"""
    _player.set_state(Gst.State.NULL)
    _player.set_property("uri", "file://" + sound_file)
    _player.set_state(Gst.State.PLAYING)
