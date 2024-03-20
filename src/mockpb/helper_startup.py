import os
from pybitmessage.bmconfigparser import config


def loadConfig():
    """Loading mock test data"""
    config.read(os.path.join(os.environ['BITMESSAGE_HOME'], 'keys.dat'))


def total_encrypted_messages_per_month():
    """Loading mock total encrypted message """
    encrypted_messages_per_month = 0
    return encrypted_messages_per_month
