from class_addressGenerator import FakeAddressGenerator
from class_singleWorker import MockSingleWorker
from class_objectProcessor import MockObjectProcessor
from inventory import MockInventory


class MockMain():
    """Mock main function"""

    def start(self):
        """Start main application"""
        # pylint: disable=too-many-statements,too-many-branches,too-many-locals

        config = BMConfigParser()
        daemon = config.safeGetBoolean('bitmessagesettings', 'daemon')

        # Start the address generation thread
        addressGeneratorThread = FakeAddressGenerator()
        # close the main program even if there are threads left
        addressGeneratorThread.daemon = True
        addressGeneratorThread.start()

        # Start the thread that calculates POWs
        singleWorkerThread = MockSingleWorker()
        # close the main program even if there are threads left
        singleWorkerThread.daemon = True
        singleWorkerThread.start()

        # Start the thread that calculates POWs
        objectProcessorThread = MockObjectProcessor()
        # DON'T close the main program even the thread remains.
        # This thread checks the shutdown variable after processing
        # each object.
        objectProcessorThread.daemon = False
        objectProcessorThread.start()

        MockInventory()  # init


def main():
    """Triggers main module"""
    mainprogram = MockMain()
    mainprogram.start()


if __name__ == "__main__":
    main()
