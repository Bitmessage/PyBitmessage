"""Test cases for ObjectProcessor"""

from binascii import hexlify
import threading
import state
import pybitmessage.class_objectProcessor as op

try:
    from unittest.mock import patch, MagicMock
except ImportError:
    from mock import patch, MagicMock, Mock

from .partial import TestPartialRun
from mockbm.class_objectProcessor import (
    mockFunctionToPass,
    sqlExecuteMock,
    sqlQueryMock,
    SqlReadyMock,
)
from .samples import (
    sample_pubsigningkey,
    sample_pubencryptionkey,
    sample_privencryptionkey,
    sample_deterministic_addr4,
    sample_deterministic_addr3,
    sample_privsigningkey
)


class TestObjectProcessor(TestPartialRun):
    """Test class for ObjectProcessor"""

    @classmethod
    def setUpClass(cls):
        super(TestObjectProcessor, cls).setUpClass()

        op.sqlQuery = sqlQueryMock
        op.sqlExecute = sqlExecuteMock
        op.sql_ready = SqlReadyMock
        op.shared.reloadBroadcastSendersForWhichImWatching = mockFunctionToPass
        op.shared.reloadMyAddressHashes = mockFunctionToPass
        cls.queues = op.queues
        cls.processor = op.objectProcessor()
        cls.processor.start()

    @classmethod
    def tearDownClass(cls):
        super(TestObjectProcessor, cls).tearDownClass()
        for thread in threading.enumerate():
            if thread.name == "objectProcessor":
                op.queues.objectProcessorQueue.put(('checkShutdownVariable', 'no data'))

    @patch("pybitmessage.class_objectProcessor.logger.debug")
    @patch("pybitmessage.class_objectProcessor.queues.UISignalQueue.put")
    def test_checkackdata(self, mock_UISignalQueue_put, mock_logger):
        """test checkdata"""
        data = b"\x00" * 8  # nonce
        data += b"\x00" * 8  # expiresTime
        data += b"\x00" * 4  # getpubkey object type
        data += b"\x04"  # addressVersion
        data += b"\x01"  # streamNumber
        data += b"\00" * 4  # behaviour bitfield
        data += sample_pubsigningkey
        data += sample_pubencryptionkey

        # ackdata not in state.ackdataForWhichImWatching
        state.ackdataForWhichImWatching = {}
        self.processor.checkackdata(data)
        mock_logger.assert_called_with('This object is not an acknowledgement bound for me.')

        # ackdata is in state.ackdataForWhichImWatching
        state.ackdataForWhichImWatching = {data[16:]: data}
        self.processor.checkackdata(data)
        self.assertEqual(len(state.ackdataForWhichImWatching), 0)
        mock_UISignalQueue_put.assert_called_once()


    @patch("pybitmessage.class_objectProcessor.protocol.checkIPAddress")
    @patch("pybitmessage.class_objectProcessor.decodeVarint")
    @patch("pybitmessage.class_objectProcessor.knownnodes.addKnownNode")
    def test_processonion(self, mock_addknownNode, mock_decodeVarint, mock_checkIPAddress):
        """Test processonion"""
        data = b"\x00" * 100
        # decode varient called 3 times returns -> addressversion & lenth
        # stream & length, port & length
        mock_decodeVarint.side_effect = [(3, 1), (2, 1), (8080, 4), ]
        mock_checkIPAddress.return_value = "127.0.0.1"
        self.processor.processonion(data)
        mock_addknownNode.assert_called_once()

    @patch("pybitmessage.class_objectProcessor.queues.workerQueue.put")
    def test_processgetpubkey_V3(
        self, mock_workerqueue_put
    ):
        """Test processgetpukey with address version 3"""
        HASH = b"\x01" * 20
        gpk = b"\x00" * 8  # nonce
        gpk += b"\x00" * 8  # expiresTime
        gpk += b"\x00" * 4  # getpubkey object type
        gpk += b"\x03"  # addressVersion 3
        gpk += b"\x01"  # streamNumber
        gpk += HASH  # hash

        # set address corresponding to hash
        op.shared.myAddressesByHash[HASH] = sample_deterministic_addr3

        self.processor.processgetpubkey(gpk)
        mock_workerqueue_put.assert_called_once()

    @patch("pybitmessage.class_objectProcessor.queues.workerQueue.put")
    def test_processgetpubkey_V4(
        self, mock_workerqueue_put
    ):
        """Test processgetpukey with address version 4"""
        TAG = b"\x01" * 32
        gpk = b"\x00" * 8  # nonce
        gpk += b"\x00" * 8  # expiresTime
        gpk += b"\x00" * 4  # getpubkey object type
        gpk += b"\x04"  # addressVersion 4
        gpk += b"\x01"  # streamNumber
        gpk += TAG  # tag

        # set address corresponding to tag
        op.shared.myAddressesByTag[TAG] = sample_deterministic_addr4

        self.processor.processgetpubkey(gpk)
        mock_workerqueue_put.assert_called_once()

    def test_processpubkey_version2(
        self,
    ):
        """Test processpubkey with version 2"""
        ppk = b"\x00" * 8  # nonce
        ppk += b"\x00" * 8  # expiresTime
        ppk += b"\x00\x00\x00\x01"  # getpubkey object type
        ppk += b"\x02"  # addressVersion
        ppk += b"\x01"  # streamNumber
        ppk += b"\00" * 4  # behaviour bitfield
        ppk += sample_pubsigningkey
        ppk += sample_pubencryptionkey
        self.processor.processpubkey(ppk)

    def test_processpubkey_version3(
        self,
    ):
        """Test processpubkey with version 3"""
        ppk = b"\x00" * 8  # nonce
        ppk += b"\x00" * 8  # expiresTime
        ppk += b"\x00\x00\x00\x01"  # getpubkey object type
        ppk += b"\x03"  # addressVersion
        ppk += b"\x01"  # streamNumber
        ppk += b"\00" * 4  # behaviour bitfield
        ppk += sample_pubsigningkey
        ppk += sample_pubencryptionkey
        ppk += b"\x01"  # nonce_trials_per_byte
        ppk += b"\x01"  # extra_bytes
        signature = op.highlevelcrypto.sign(ppk[8:-2], hexPrivkey=hexlify(sample_privsigningkey))  # signature
        ppk += hex(len(signature)).encode()  # sig_length
        ppk += signature
        self.processor.processpubkey(ppk)
        
    def test_processpubkey_version4(
        self
    ):
        """Test processpubkey with version 4"""
        Tag = b"\00" * 32
        pk = b"\x00" * 8  # nonce
        pk += b"\x00" * 8  # expiresTime
        pk += b"\x00\x00\x00\x01"  # getpubkey object type
        pk += b"\x04"  # addressVersion
        pk += b"\x01"  # streamNumber
        pk += Tag  # tag

        data_to_encrypt = b"\00" * 4  # behaviour bitfield
        data_to_encrypt += sample_pubsigningkey
        data_to_encrypt += sample_pubencryptionkey
        data_to_encrypt += b"\x01"  # nonce_trials_per_byte
        data_to_encrypt += b"\x01"  # extra_bytes
        signature = op.highlevelcrypto.sign(pk[8:], hexPrivkey=hexlify(sample_privsigningkey))  # signature
        data_to_encrypt += hex(len(signature)).encode()  # sig_length
        data_to_encrypt += signature
        
        cryptor = op.highlevelcrypto.makeCryptor(sample_privencryptionkey)
        encrypted_data = cryptor.encrypt(data_to_encrypt, hexlify(sample_pubencryptionkey))
        pk += encrypted_data
        
        state.neededPubkeys[Tag] = (sample_deterministic_addr4, cryptor)
        self.processor.processpubkey(pk)

    @patch("pybitmessage.class_objectProcessor.objectProcessor.sendMessages")
    def test_possibleNewPubkey_with_addressV3(self, mock_sendMessages):
        """Test possibleNewPubkey with version 3 address"""
        state.neededPubkeys = {sample_deterministic_addr3: "pubkey2"}

        self.processor.possibleNewPubkey(sample_deterministic_addr3)
        mock_sendMessages.assert_called_with(sample_deterministic_addr3)

    @patch("pybitmessage.class_objectProcessor.highlevelcrypto.double_sha512")
    @patch("pybitmessage.class_objectProcessor.objectProcessor.sendMessages")
    def test_possibleNewPubkey_with_addressV4(self, mock_sendMessages, mock_double_sha512):
        """Test possibleNewPubkey with version 4 address"""
        fake_encrypted_data = "\x01" * 64
        state.neededPubkeys = {fake_encrypted_data[32:]: "pubkey"}

        mock_double_sha512.return_value = fake_encrypted_data
        self.processor.possibleNewPubkey(sample_deterministic_addr4)
        mock_sendMessages.assert_called_with(sample_deterministic_addr4)


