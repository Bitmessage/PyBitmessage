#!/usr/bin/env python
"""Custom tests runner script for tox and python3"""
import random  # noseq
import sys
import unittest

from os import environ, mkdir
from subprocess import Popen, TimeoutExpired
from time import sleep


def unittest_discover():
    """Explicit test suite creation"""
    loader = unittest.defaultTestLoader
    loader.sortTestMethodsUsing = lambda a, b: random.randint(-1, 1)
    return loader.discover('src.bitmessagekivy.tests')


if __name__ == "__main__":
    with open("/proc/self/cgroup", "rt", encoding='ascii', errors='replace') as f:
        in_docker = "docker" in f.read()

    if in_docker:
        try:
            mkdir("../out")
        except FileExistsError:  # flake8: noqa:F821
            pass

        ffmpeg = Popen([  # pylint: disable=consider-using-with
                       "ffmpeg", "-y", "-nostdin", "-f", "x11grab", "-video_size", "vga",
                       "-draw_mouse", "0", "-i", environ['DISPLAY'],
                       "-codec:v", "libvpx-vp9", "-lossless", "1", "-r", "30",
                       "../out/test.webm"
                       ])
        sleep(2)  # let ffmpeg start
    result = unittest.TextTestRunner(verbosity=2).run(unittest_discover())
    if in_docker:
        ffmpeg.terminate()
        try:
            ffmpeg.wait(10)
        except TimeoutExpired:
            ffmpeg.kill()
    sys.exit(not result.wasSuccessful())
