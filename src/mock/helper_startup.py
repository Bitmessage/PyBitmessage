import os
from pybitmessage.bmconfigparser import config


def loadConfig():
    """Loading mock test data"""
    config.read(os.path.join(os.environ['BITMESSAGE_HOME'], 'keys.dat'))
