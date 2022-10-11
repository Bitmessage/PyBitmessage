# pylint: disable=unused-import, wrong-import-position, ungrouped-imports
# flake8: noqa:E401, E402

"""Mock kivy app with mock threads."""

import os
from kivy.config import Config
import multiqueue
from pybitmessage import state

if os.environ.get('INSTALL_TESTS', False):
    Config.set('graphics', 'height', 1280)
    Config.set('graphics', 'width', 720)
    Config.set('graphics', 'position', 'custom')
    Config.set('graphics', 'top', 0)
    Config.set('graphics', 'left', 0)


from pybitmessage.mock.class_addressGenerator import FakeAddressGenerator  # noqa:E402
from pybitmessage.bitmessagekivy.mpybit import NavigateApp  # noqa:E402
from pybitmessage.mock.network import stats, objectracker  # noqa:E402


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
