#!/usr/bin/env python
"""Custom tests runner script for tox and python3"""
import os
import random  # noseq
import subprocess
import sys
import unittest

from time import sleep


def unittest_discover():
    """Explicit test suite creation"""
    loader = unittest.defaultTestLoader
    loader.sortTestMethodsUsing = lambda a, b: random.randint(-1, 1)
    return loader.discover('src.bitmessagekivy.tests')


if __name__ == "__main__":
    in_docker = os.path.exists("/.dockerenv")

    if in_docker:
        try:
            os.mkdir("../out")
        except FileExistsError:  # noqa:F821
            pass

        ffmpeg = subprocess.Popen([  # pylint: disable=consider-using-with
            "ffmpeg", "-y", "-nostdin", "-f", "x11grab", "-video_size", "720x1280",
            "-v", "quiet", "-nostats",
            "-draw_mouse", "0", "-i", os.environ['DISPLAY'],
            "-codec:v", "libvpx-vp9", "-lossless", "1", "-r", "60",
            "../out/test.webm"
        ])
        sleep(2)  # let ffmpeg start
    result = unittest.TextTestRunner(verbosity=2).run(unittest_discover())
    sleep(1)
    if in_docker:
        ffmpeg.terminate()
        try:
            ffmpeg.wait(10)
        except subprocess.TimeoutExpired:
            ffmpeg.kill()
    sys.exit(not result.wasSuccessful())
