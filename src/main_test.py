"""This module is for thread start."""
import state
from bitmessagekivy.mpybit import NavigateApp
from fake_addressGenerator import FakeAddressGenerator
from threads import sqlThread

def main():
    if state.enableObjProc:
        # Start the address generation thread
        addressGeneratorThread = FakeAddressGenerator()
        # close the main program even if there are threads left
        addressGeneratorThread.daemon = True
        addressGeneratorThread.start()

        sqlLookup = sqlThread()
        # DON'T close the main program even if there are threads left.
        # The closeEvent should command this thread to exit gracefully.
        sqlLookup.daemon = False
        sqlLookup.start()

    state.kivyapp = NavigateApp()
    state.kivyapp.run()



if __name__ == '__main__':
    main()
