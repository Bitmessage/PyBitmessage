# -*- coding: utf-8 -*-


try:
    import winsound

    def connect_plugin(sound_file):
        winsound.PlaySound(sound_file, winsound.SND_FILENAME)
except ImportError:
    import os
    import subprocess

    play_cmd = {}

    def connect_plugin(sound_file):
        global play_cmd

        ext = os.path.splitext(sound_file)[-1]
        try:
            subprocess.call([play_cmd[ext], sound_file])
            return
        except (KeyError, AttributeError):
            pass

        programs = ['gst123']
        if ext == '.wav':
            programs.append('aplay')
        elif ext == '.mp3':
            programs += ['mpg123', 'mpg321', 'mpg321-mpg123']
        for cmd in programs:
            try:
                subprocess.call([cmd, sound_file])
            except OSError:
                pass  # log here!
            else:
                play_cmd[ext] = cmd
                break
