import os
import sys


def setup():
    """Add path to this file to sys.path"""
    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)
    sys.path.insert(0, app_dir)
    return app_dir
