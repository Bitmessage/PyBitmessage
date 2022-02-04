"""Mock kivy app with mock threads."""

from pybitmessage import state
from pybitmessage.mpybit import NavigateApp
from pybitmessage.class_addressGenerator import addressGenerator


def main():
    """main method for starting threads"""
    # Start the address generation thread
    addressGeneratorThread = addressGenerator()
    # close the main program even if there are threads left
    addressGeneratorThread.daemon = True
    addressGeneratorThread.start()

    state.kivyapp = NavigateApp()
    state.kivyapp.run()


if __name__ == '__main__':
    main()
