# -*- coding: utf-8 -*-
"""
Sound notification plugin using external executable or winsound (on Windows)
"""

try:
    import winsound

    def connect_plugin(sound_file):
        """Plugin's entry point"""
        winsound.PlaySound(sound_file, winsound.SND_FILENAME)
except ImportError:
    import os
    import subprocess

    play_cmd = {}

    def _subprocess(*args):
        FNULL = open(os.devnull, 'wb')
        subprocess.call(
            args, stdout=FNULL, stderr=subprocess.STDOUT, close_fds=True)

    def connect_plugin(sound_file):
        """This function implements the entry point."""
        global play_cmd  # pylint: disable=global-statement

        ext = os.path.splitext(sound_file)[-1]
        try:
            return _subprocess(play_cmd[ext], sound_file)
        except (KeyError, AttributeError):
            pass

        programs = ['gst123', 'gst-play-1.0']
        if ext == '.wav':
            programs.append('aplay')
        elif ext == '.mp3':
            programs += ['mpg123', 'mpg321', 'mpg321-mpg123']
        for cmd in programs:
            try:
                _subprocess(cmd, sound_file)
            except OSError:
                pass  # log here!
            else:
                play_cmd[ext] = cmd
                break
