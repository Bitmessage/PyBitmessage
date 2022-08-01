"""Mock kivy app with mock threads."""
# pylint: disable=unused-import
# flake8: noqa:E401

from pybitmessage import state
from pybitmessage.bitmessagekivy.mpybit import NavigateApp

import multiqueue
from class_addressGenerator import FakeAddressGenerator


def main():
    """main method for starting threads"""
    # Start the address generation thread
    addressGeneratorThread = FakeAddressGenerator()
    # close the main program even if there are threads left
    addressGeneratorThread.daemon = True
    addressGeneratorThread.start()

    state.kivyapp = NavigateApp()
    state.kivyapp.run()


if __name__ == '__main__':
    main()
