from PyQt4 import uic
import os.path
import sys


def resource_path(path):
    try:
        return os.path.join(sys._MEIPASS, path)
    except:
        return os.path.join(os.path.dirname(__file__), path)


def load(path, widget):
    uic.loadUi(resource_path(path), widget)
