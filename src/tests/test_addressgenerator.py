import unittest
from binascii import unhexlify

from pybitmessage import pathmagic

from .samples import (
    sample_seed, sample_deterministic_addr3, sample_deterministic_addr4,
    sample_deterministic_ripe)


class TestAddressGenerator(unittest.TestCase):
    """Test case for AddressGenerator (with thread or not)"""

    @classmethod
    def setUpClass(cls):
        pathmagic.setup()  # need this because of import state in network ):
        import queues
        import state

        state.enableGUI = False
        from class_addressGenerator import addressGenerator

        # import helper_startup
        # from bmconfigparser import BMConfigParser

        # helper_startup.loadConfig()
        # config = BMConfigParser()

        cls.command_queue = queues.addressGeneratorQueue
        cls.return_queue = queues.apiAddressGeneratorReturnQueue
        cls.worker_queue = queues.workerQueue

        thread = addressGenerator()
        thread.daemon = True
        thread.start()

    def _execute(self, command, *args):
        self.command_queue.put((command,) + args)
        try:
            return self.return_queue.get()[0]
        except IndexError:
            self.fail('Failed to execute command %s' % command)

    def test_createChan(self):
        """Test createChan command"""
        self.assertEqual(
            sample_deterministic_addr3,
            self._execute('createChan', 3, 1, 'test', sample_seed, True))
        self.assertEqual(
            self.worker_queue.get(),
            ('sendOutOrStoreMyV3Pubkey', unhexlify(sample_deterministic_ripe)))
        self.assertEqual(
            sample_deterministic_addr4,
            self._execute('createChan', 4, 1, 'test', sample_seed, True))
