# pylint: disable=no-name-in-module, import-error

"""
Bitmessage mock
"""

from pybitmessage.class_addressGenerator import addressGenerator
from pybitmessage.inventory import Inventory
from pybitmessage.mpybit import NavigateApp
from pybitmessage import state


class MockMain(object):  # pylint: disable=too-few-public-methods
    """Mock main function"""

    def __init__(self):
        """Start main application"""
        addressGeneratorThread = addressGenerator()
        # close the main program even if there are threads left
        addressGeneratorThread.start()
        Inventory()
        state.kivyapp = NavigateApp()
        state.kivyapp.run()


def main():
    """Triggers main module"""
    MockMain()


if __name__ == "__main__":
    main()
