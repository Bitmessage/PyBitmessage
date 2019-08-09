from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *
from PyQt4 import uic
import os.path
import paths
import sys

def resource_path(resFile):
    baseDir = paths.codePath()
    for subDir in ["ui", "bitmessageqt"]:
        if os.path.isdir(os.path.join(baseDir, subDir)) and os.path.isfile(os.path.join(baseDir, subDir, resFile)):
            return os.path.join(baseDir, subDir, resFile)

def load(resFile, widget):
    uic.loadUi(resource_path(resFile), widget)
