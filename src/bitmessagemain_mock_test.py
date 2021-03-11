import state
from bitmessagekivy.mpybit import NavigateApp
from threads import addressGenerator, sqlThread     

def main():
    if state.enableObjProc:
        print('....................................................line(8)(sqlThread)')

        # Start the address generation thread
        addressGeneratorThread = addressGenerator()
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
