# pylint: disable=unused-import, wrong-import-position, ungrouped-imports
# flake8: noqa:E401, E402

"""Mock kivy app with mock threads."""

import os
from kivy.config import Config
from mockbm import multiqueue
import state

from mockbm.class_addressGenerator import FakeAddressGenerator  # noqa:E402
from bitmessagekivy.mpybit import NavigateApp  # noqa:E402
from mockbm import network  # noqa:E402

stats = network.stats
objectracker = network.objectracker


def main():
    """main method for starting threads"""
    addressGeneratorThread = FakeAddressGenerator()
    addressGeneratorThread.daemon = True
    addressGeneratorThread.start()
    state.kivyapp = NavigateApp()
    state.kivyapp.run()
    addressGeneratorThread.stopThread()


if __name__ == "__main__":
    os.environ['INSTALL_TESTS'] = "True"
    main()
