"""Tests for AddressGenerator (with thread or not)"""

from binascii import unhexlify

from .partial import TestPartialRun
from .samples import (
    sample_seed, sample_deterministic_addr3, sample_deterministic_addr4,
    sample_deterministic_ripe)


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
        self.assertEqual(
            self.worker_queue.get(),
            ('sendOutOrStoreMyV4Pubkey', sample_deterministic_addr4))
        self.assertEqual(
            self.config.get(sample_deterministic_addr4, 'label'), 'test')
        self.assertTrue(
            self.config.getboolean(sample_deterministic_addr4, 'chan'))
        self.assertTrue(
            self.config.getboolean(sample_deterministic_addr4, 'enabled'))
