"""
src/bitmessageqt/widgets.py
===========================
"""

import os.path

from PyQt4 import uic

import paths


def resource_path(resFile):
    """Return the path of the resource"""
    baseDir = paths.codePath()
    for subDir in ["ui", "bitmessageqt"]:
        if os.path.isdir(os.path.join(baseDir, subDir)) and os.path.isfile(os.path.join(baseDir, subDir, resFile)):
            return os.path.join(baseDir, subDir, resFile)
    return None


def load(resFile, widget):
    """Load a resource"""
    uic.loadUi(resource_path(resFile), widget)
