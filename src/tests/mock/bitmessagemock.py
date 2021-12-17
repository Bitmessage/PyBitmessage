"""
Bitmessage mock
"""
from pybitmessage.class_addressGenerator import addressGenerator
from pybitmessage.class_singleWorker import singleWorker
from pybitmessage.class_objectProcessor import objectProcessor
from pybitmessage.inventory import Inventory
from pybitmessage.bmconfigparser import BMConfigParser


# pylint: disable=too-few-public-methods,no-init,old-style-class
class MockMain:
    """Mock main function"""

    # pylint: disable=no-self-use
    def start(self):
        """Start main application"""
        # pylint: disable=too-many-statements,too-many-branches,too-many-locals, unused-variable
        config = BMConfigParser()
        daemon = config.safeGetBoolean('bitmessagesettings', 'daemon')

        # Start the address generation thread
        addressGeneratorThread = addressGenerator()
        # close the main program even if there are threads left
        addressGeneratorThread.daemon = True
        addressGeneratorThread.start()

        # Start the thread that calculates POWs
        singleWorkerThread = singleWorker()
        # close the main program even if there are threads left
        singleWorkerThread.daemon = True
        singleWorkerThread.start()

        # Start the thread that calculates POWs
        objectProcessorThread = objectProcessor()
        # DON'T close the main program even the thread remains.
        # This thread checks the shutdown variable after processing
        # each object.
        objectProcessorThread.daemon = False
        objectProcessorThread.start()

        Inventory()  # init


def main():
    """Triggers main module"""
    mainprogram = MockMain()
    mainprogram.start()


if __name__ == "__main__":
    main()
