from PyQt4 import uic
import os.path
import sys
from shared import codePath

def resource_path(resFile):
    baseDir = codePath()
    for subDir in ["ui", "bitmessageqt"]:
        if os.path.isdir(os.path.join(baseDir, subDir)) and os.path.isfile(os.path.join(baseDir, subDir, resFile)):
            return os.path.join(baseDir, subDir, resFile)

def load(resFile, widget):
    uic.loadUi(resource_path(resFile), widget)
