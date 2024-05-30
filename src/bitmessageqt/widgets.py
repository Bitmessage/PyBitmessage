from qtpy import uic
import os.path
import paths


def resource_path(resFile):
    baseDir = paths.codePath()
    for subDir in ("ui", "bitmessageqt"):
        path = os.path.join(baseDir, subDir, resFile)
        if os.path.isfile(path):
            return path


def load(resFile, widget):
    uic.loadUi(resource_path(resFile), widget)
