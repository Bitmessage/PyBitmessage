"""This module is for thread start."""

from pybitmessage import state
from pybitmessage.bitmessagekivy.mpybit import NavigateApp
from class_addressGenerator import FakeAddressGenerator
# from class_sqlThread import sqlThread


def main():
    """main method for starting threads"""
    if state.enableObjProc:
        # Start the address generation thread
        addressGeneratorThread = FakeAddressGenerator()
        # close the main program even if there are threads left
        addressGeneratorThread.daemon = True
        addressGeneratorThread.start()

        # sqlLookup = sqlThread()
        # DON'T close the main program even if there are threads left.
        # The closeEvent should command this thread to exit gracefully.
        # sqlLookup.daemon = False
        # sqlLookup.start()

    state.kivyapp = NavigateApp()
    state.kivyapp.run()


if __name__ == '__main__':
    main()
