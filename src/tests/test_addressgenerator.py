"""Tests for AddressGenerator (with thread or not)"""

from binascii import unhexlify

from six.moves import queue

from .partial import TestPartialRun
from .samples import (
    sample_seed, sample_deterministic_addr3, sample_deterministic_addr4,
    sample_deterministic_ripe)

TEST_LABEL = 'test'


class TestAddressGenerator(TestPartialRun):
    """Test case for AddressGenerator thread"""

    @classmethod
    def setUpClass(cls):
        super(TestAddressGenerator, cls).setUpClass()

        import defaults
        import queues
        from class_addressGenerator import addressGenerator

        cls.state.enableGUI = False

        cls.command_queue = queues.addressGeneratorQueue
        cls.return_queue = queues.apiAddressGeneratorReturnQueue
        cls.worker_queue = queues.workerQueue

        cls.config.set(
            'bitmessagesettings', 'defaultnoncetrialsperbyte',
            str(defaults.networkDefaultProofOfWorkNonceTrialsPerByte))
        cls.config.set(
            'bitmessagesettings', 'defaultpayloadlengthextrabytes',
            str(defaults.networkDefaultPayloadLengthExtraBytes))

        thread = addressGenerator()
        thread.daemon = True
        thread.start()

    def _execute(self, command, *args):
        self.command_queue.put((command,) + args)
        try:
            return self.return_queue.get(timeout=30)[0]
        except (IndexError, queue.Empty):
            self.fail('Failed to execute command %s' % command)

    def test_deterministic(self):
        """Test deterministic commands"""
        self.command_queue.put((
            'getDeterministicAddress', 3, 1,
            TEST_LABEL, 1, sample_seed, False))
        self.assertEqual(sample_deterministic_addr3, self.return_queue.get())

        self.assertEqual(
            sample_deterministic_addr3,
            self._execute(
                'createDeterministicAddresses', 3, 1, TEST_LABEL, 2,
                sample_seed, False, 0, 0))

        try:
            self.assertEqual(
                self.worker_queue.get(timeout=30),
                ('sendOutOrStoreMyV3Pubkey',
                 unhexlify(sample_deterministic_ripe)))

            self.worker_queue.get(timeout=30)  # get the next addr's task
        except queue.Empty:
            self.fail('No commands in the worker queue')

        self.assertEqual(
            sample_deterministic_addr4,
            self._execute('createChan', 4, 1, TEST_LABEL, sample_seed, True))
        try:
            self.assertEqual(
                self.worker_queue.get(),
                ('sendOutOrStoreMyV4Pubkey', sample_deterministic_addr4))
        except queue.Empty:
            self.fail('No commands in the worker queue')
        self.assertEqual(
            self.config.get(sample_deterministic_addr4, 'label'), TEST_LABEL)
        self.assertTrue(
            self.config.getboolean(sample_deterministic_addr4, 'chan'))
        self.assertTrue(
            self.config.getboolean(sample_deterministic_addr4, 'enabled'))
