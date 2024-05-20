"""Test cases for ObjectProcessor"""

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
        gpk = b"\x00" * 8  # nonce
        gpk += b"\x00" * 8  # expiresTime
        gpk += b"\x00" * 4  # getpubkey object type
        gpk += b"\x04"  # addressVersion
        gpk += b"\x01"  # streamNumber
        gpk += b"\00" * 4  # behaviour bitfield
        gpk += sample_pubsigningkey
        gpk += sample_pubencryptionkey

        # ackdata not in state.ackdataForWhichImWatching
        state.ackdataForWhichImWatching = {}
        self.processor.checkackdata(gpk)
        mock_logger.assert_called_with('This object is not an acknowledgement bound for me.')

        # ackdata is in state.ackdataForWhichImWatching
        state.ackdataForWhichImWatching = {gpk[16:]: gpk}
        self.processor.checkackdata(gpk)
        self.assertEqual(len(state.ackdataForWhichImWatching), 0)
        mock_UISignalQueue_put.assert_called_once()


    @patch("pybitmessage.class_objectProcessor.protocol.checkIPAddress")
    @patch("pybitmessage.class_objectProcessor.decodeVarint")
    @patch("pybitmessage.class_objectProcessor.knownnodes.addKnownNode")
    def test_processonion(self, mock_addknownNode, mock_decodeVarient, mock_checkIPAddress):
        """Test processonion"""
        data = b"\x00" * 100
        # decode varient called 3 times returns -> addressversion & lenth
        # stream & length, port & length
        mock_decodeVarient.side_effect = [(3, 1), (2, 1), (8080, 4), ]
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
        gpk += b"\x03"  # addressVersion 4
        gpk += b"\x01"  # streamNumber
        gpk += HASH  # hash

        # set address corresponding to tag
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
        pk = b"\x00" * 8  # nonce
        pk += b"\x00" * 8  # expiresTime
        pk += b"\x00\x00\x00\x01"  # getpubkey object type
        pk += b"\x02"  # addressVersion
        pk += b"\x01"  # streamNumber
        pk += b"\00" * 4  # behaviour bitfield
        pk += sample_pubsigningkey
        pk += sample_pubencryptionkey
        self.processor.processpubkey(pk)

    def test_processpubkey_version3(
        self,
    ):
        """Test processpubkey with version 3"""
        pk = b"\x00" * 8  # nonce
        pk += b"\x00" * 8  # expiresTime
        pk += b"\x00\x00\x00\x01"  # getpubkey object type
        pk += b"\x03"  # addressVersion
        pk += b"\x01"  # streamNumber
        pk += b"\00" * 4  # behaviour bitfield
        pk += sample_pubsigningkey
        pk += sample_pubencryptionkey
        pk += b"\x01"  # nonce_trials_per_byte
        pk += b"\x01"  # extra_bytes
        signature = op.highlevelcrypto.sign(pk[8:], hexPrivkey=sample_privsigningkey)  # signature
        pk += hex(len(signature)).encode()  # sig_length
        pk += signature
        self.processor.processpubkey(pk)
        
    def test_processpubkey_version4(
        self
    ):
        """Test processpubkey with version 4"""
        pk = b"\x00" * 8  # nonce
        pk += b"\x00" * 8  # expiresTime
        pk += b"\x00\x00\x00\x01"  # getpubkey object type
        pk += b"\x04"  # addressVersion
        pk += b"\x01"  # streamNumber
        pk += b"\00" * 4  # behaviour bitfield
        pk += sample_pubsigningkey
        pk += sample_pubencryptionkey
        self.processor.processpubkey(pk)

    # @patch(
    #     "pybitmessage.class_objectProcessor.helper_inbox.isMessageAlreadyInInbox",
    #     return_value=False,
    # )
    # @patch(
    #     "pybitmessage.class_objectProcessor.helper_msgcoding.MsgDecode",
    #     return_value=MagicMock(subject="Test Subject", body="Test Body"),
    # )
    # @patch("pybitmessage.class_objectProcessor.helper_inbox.insert")
    # @patch("pybitmessage.class_objectProcessor.queues.UISignalQueue.put")
    # def test_processmsg_valid_message(
    #     self,
    #     mock_UISignalQueue_put,
    #     mock_insert,
    #     mock_MsgDecode,
    #     mock_isMessageAlreadyInInbox,
    # ):
    #     msg = b"\x00" * 8  # nonce
    #     msg += b"\x00" * 8  # expiresTime
    #     msg += b"\x00\x00\x00\x02"  # getpubkey object type
    #     msg += b"\x04"  # addressVersion
    #     msg += b"\x01"  # streamNumber
       
    #     with patch(
    #         "pybitmessage.class_objectProcessor.decodeVarint", return_value=(1, 1)
    #     ), patch(
    #         "pybitmessage.class_objectProcessor.highlevelcrypto.verify",
    #         return_value=True,
    #     ):
    #         self.processor.processmsg(data)
    #         mock_insert.assert_called()
    #         mock_UISignalQueue_put.assert_called()

    @patch(
        "pybitmessage.class_objectProcessor.state.neededPubkeys",
        {"address1": "data1", "address2": "data2"},
    )
    @patch("pybitmessage.class_objectProcessor.objectProcessor.sendMessages")
    def test_possibleNewPubkey_with_needed_pubkey(self, mock_sendMessages):
        self.processor.possibleNewPubkey("address1")
        mock_sendMessages.assert_called_with("address1")

    @patch(
        "pybitmessage.class_objectProcessor.state.neededPubkeys",
        {"address1": "data1", "address2": "data2"},
    )
    @patch("pybitmessage.class_objectProcessor.objectProcessor.sendMessages")
    def test_possibleNewPubkey_with_unneeded_pubkey(self, mock_sendMessages):
        self.processor.possibleNewPubkey("address3")
        mock_sendMessages.assert_not_called()

    @patch(
        "pybitmessage.class_objectProcessor.state.neededPubkeys",
        {"address1": "data1", "address2": "data2"},
    )
    @patch("pybitmessage.class_objectProcessor.objectProcessor.sendMessages")
    def test_possibleNewPubkey_with_multiple_needed_pubkeys(self, mock_sendMessages):
        self.processor.possibleNewPubkey("address1")
        self.processor.possibleNewPubkey("address2")
        self.assertEqual(mock_sendMessages.call_count, 2)
