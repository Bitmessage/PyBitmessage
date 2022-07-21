# pylint: disable=too-many-lines,import-error,no-name-in-module,unused-argument, no-else-return,  unused-variable
# pylint: disable=too-many-ancestors,too-many-locals,useless-super-delegation, attribute-defined-outside-init
# pylint: disable=protected-access, super-with-arguments, pointless-statement, no-method-argument, too-many-function-args
# pylint: disable=import-outside-toplevel,ungrouped-imports,wrong-import-order,unused-import,arguments-differ
# pylint: disable=invalid-name,unnecessary-comprehension,broad-except,simplifiable-if-expression,no-member, consider-using-in
# pylint: disable=too-many-return-statements, unnecessary-pass, bad-option-value, abstract-method, consider-using-f-string


"""
Bitmessage mock
"""

from pybitmessage.class_addressGenerator import addressGenerator
from pybitmessage.inventory import Inventory
from pybitmessage.bmconfigparser import BMConfigParser
from pybitmessage import state


class MockMain:
    """Mock main function"""

    def start(self):
        """Start main application"""
        # pylint: disable=too-many-statements,too-many-branches, unused-variable
        config = BMConfigParser()
        daemon = config.safeGetBoolean('bitmessagesettings', 'daemon')
        # Start the address generation thread
        addressGeneratorThread = addressGenerator()
        # close the main program even if there are threads left
        addressGeneratorThread.daemon = True
        addressGeneratorThread.start()
        Inventory()
        from pybitmessage.mpybit import NavigateApp
        state.kivyapp = NavigateApp()
        state.kivyapp.run()


def main():
    """Triggers main module"""
    mainprogram = MockMain()
    mainprogram.start()


if __name__ == "__main__":
    main()
