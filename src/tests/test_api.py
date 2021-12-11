"""
Tests using API.
"""

import base64
import json
import time

from binascii import hexlify
from six.moves import xmlrpc_client  # nosec

import psutil

from .samples import (
    sample_seed, sample_deterministic_addr3, sample_deterministic_addr4, sample_statusbar_msg,
    sample_inbox_msg_ids, sample_test_subscription_address, sample_subscription_name)

from .test_process import TestProcessProto


class TestAPIProto(TestProcessProto):
    """Test case logic for testing API"""
    _process_cmd = ['pybitmessage', '-t']

    @classmethod
    def setUpClass(cls):
        """Setup XMLRPC proxy for pybitmessage API"""
        super(TestAPIProto, cls).setUpClass()
        cls.addresses = []
        cls.api = xmlrpc_client.ServerProxy(
            "http://username:password@127.0.0.1:8442/")
        for _ in range(5):
            if cls._get_readline('.api_started'):
                return
            time.sleep(1)


class TestAPIShutdown(TestAPIProto):
    """Separate test case for API command 'shutdown'"""
    def test_shutdown(self):
        """Shutdown the pybitmessage"""
        self.assertEqual(self.api.shutdown(), 'done')
        try:
            self.process.wait(20)
        except psutil.TimeoutExpired:
            self.fail(
                '%s has not stopped in 20 sec' % ' '.join(self._process_cmd))


# TODO: uncovered API commands
# disseminatePreEncryptedMsg
# disseminatePubkey
# getMessageDataByDestinationHash


class TestAPI(TestAPIProto):
    """Main API test case"""
    _seed = base64.encodestring(sample_seed)

    def _add_random_address(self, label):
        addr = self.api.createRandomAddress(base64.encodestring(label))
        return addr

    def test_user_password(self):
        """Trying to connect with wrong username/password"""
        api_wrong = xmlrpc_client.ServerProxy(
            "http://test:wrong@127.0.0.1:8442/")
        with self.assertRaises(xmlrpc_client.ProtocolError):
            api_wrong.clientStatus()

    def test_connection(self):
        """API command 'helloWorld'"""
        self.assertEqual(
            self.api.helloWorld('hello', 'world'),
            'hello-world'
        )

    def test_arithmetic(self):
        """API command 'add'"""
        self.assertEqual(self.api.add(69, 42), 111)

    def test_invalid_method(self):
        """Issuing nonexistent command 'test'"""
        self.assertEqual(
            self.api.test(),
            'API Error 0020: Invalid method: test'
        )

    def test_statusbar_method(self):
        """Test statusbar method"""
        self.api.clearUISignalQueue()
        self.assertEqual(
            self.api.statusBar(sample_statusbar_msg),
            'null'
        )
        self.assertEqual(
            self.api.getStatusBar(),
            sample_statusbar_msg
        )

    def test_message_inbox(self):
        """Test message inbox methods"""
        self.assertEqual(
            len(json.loads(
                self.api.getAllInboxMessages())["inboxMessages"]),
            4,
            # Custom AssertError message for details
            json.loads(self.api.getAllInboxMessages())["inboxMessages"]
        )
        self.assertEqual(
            len(json.loads(
                self.api.getAllInboxMessageIds())["inboxMessageIds"]),
            4
        )
        self.assertEqual(
            len(json.loads(
                self.api.getInboxMessageById(hexlify(sample_inbox_msg_ids[2])))["inboxMessage"]),
            1
        )
        self.assertEqual(
            len(json.loads(
                self.api.getInboxMessagesByReceiver(sample_deterministic_addr4))["inboxMessages"]),
            4
        )

    def test_message_trash(self):
        """Test message inbox methods"""

        messages_before_delete = len(json.loads(self.api.getAllInboxMessageIds())["inboxMessageIds"])
        self.assertEqual(
            self.api.trashMessage(hexlify(sample_inbox_msg_ids[0])),
            'Trashed message (assuming message existed).'
        )
        self.assertEqual(
            self.api.trashInboxMessage(hexlify(sample_inbox_msg_ids[1])),
            'Trashed inbox message (assuming message existed).'
        )
        self.assertEqual(
            len(json.loads(self.api.getAllInboxMessageIds())["inboxMessageIds"]),
            messages_before_delete - 2
        )
        self.assertEqual(
            self.api.undeleteMessage(hexlify(sample_inbox_msg_ids[0])),
            'Undeleted message'
        )
        self.assertEqual(
            self.api.undeleteMessage(hexlify(sample_inbox_msg_ids[1])),
            'Undeleted message'
        )
        self.assertEqual(
            len(json.loads(self.api.getAllInboxMessageIds())["inboxMessageIds"]),
            messages_before_delete
        )

    def test_clientstatus_consistency(self):
        """If networkStatus is notConnected networkConnections should be 0"""
        status = json.loads(self.api.clientStatus())
        if status["networkStatus"] == "notConnected":
            self.assertEqual(status["networkConnections"], 0)
        else:
            self.assertGreater(status["networkConnections"], 0)

    def test_list_addresses(self):
        """Checking the return of API command 'listAddresses'"""
        self.assertEqual(
            json.loads(self.api.listAddresses()).get('addresses'),
            self.addresses
        )

    def test_decode_address(self):
        """Checking the return of API command 'decodeAddress'"""
        result = json.loads(
            self.api.decodeAddress(sample_deterministic_addr4))
        self.assertEqual(result.get('status'), 'success')
        self.assertEqual(result['addressVersion'], 4)
        self.assertEqual(result['streamNumber'], 1)

    def test_create_deterministic_addresses(self):
        """Test creation of deterministic addresses"""
        self.assertEqual(
            self.api.getDeterministicAddress(self._seed, 4, 1),
            sample_deterministic_addr4)
        self.assertEqual(
            self.api.getDeterministicAddress(self._seed, 3, 1),
            sample_deterministic_addr3)
        self.assertRegexpMatches(
            self.api.getDeterministicAddress(self._seed, 2, 1),
            r'^API Error 0002:')

        # This is here until the streams will be implemented
        self.assertRegexpMatches(
            self.api.getDeterministicAddress(self._seed, 3, 2),
            r'API Error 0003:')
        self.assertRegexpMatches(
            self.api.createDeterministicAddresses(self._seed, 1, 4, 2),
            r'API Error 0003:')

        self.assertRegexpMatches(
            self.api.createDeterministicAddresses('', 1),
            r'API Error 0001:')
        self.assertRegexpMatches(
            self.api.createDeterministicAddresses(self._seed, 1, 2),
            r'API Error 0002:')
        self.assertRegexpMatches(
            self.api.createDeterministicAddresses(self._seed, 0),
            r'API Error 0004:')
        self.assertRegexpMatches(
            self.api.createDeterministicAddresses(self._seed, 1000),
            r'API Error 0005:')

        addresses = json.loads(
            self.api.createDeterministicAddresses(self._seed, 2, 4)
        )['addresses']
        self.assertEqual(len(addresses), 2)
        self.assertEqual(addresses[0], sample_deterministic_addr4)
        for addr in addresses:
            self.assertEqual(self.api.deleteAddress(addr), 'success')

    def test_create_random_address(self):
        """API command 'createRandomAddress': basic BM-address validation"""
        addr = self._add_random_address('random_1')
        self.assertRegexpMatches(addr, r'^BM-')
        self.assertRegexpMatches(addr[3:], r'[a-zA-Z1-9]+$')
        # Whitepaper says "around 36 character"
        self.assertLessEqual(len(addr[3:]), 40)
        self.assertEqual(self.api.deleteAddress(addr), 'success')

    def test_addressbook(self):
        """Testing API commands for addressbook manipulations"""
        # Initially it's empty
        self.assertEqual(
            json.loads(self.api.listAddressBookEntries()).get('addresses'),
            []
        )
        # Add known address
        self.api.addAddressBookEntry(
            sample_deterministic_addr4,
            base64.encodestring('tiger_4')
        )
        # Check addressbook entry
        entries = json.loads(
            self.api.listAddressBookEntries()).get('addresses')[0]
        self.assertEqual(
            entries['address'], sample_deterministic_addr4)
        self.assertEqual(
            base64.decodestring(entries['label']), 'tiger_4')
        # Try sending to this address (#1898)
        addr = self._add_random_address('random_2')
        # TODO: it was never deleted
        msg = base64.encodestring('test message')
        msg_subject = base64.encodestring('test_subject')
        result = self.api.sendMessage(
            sample_deterministic_addr4, addr, msg_subject, msg)
        self.assertNotRegexpMatches(result, r'^API Error')
        self.api.deleteAddress(addr)
        # Remove known address
        self.api.deleteAddressBookEntry(sample_deterministic_addr4)
        # Addressbook should be empty again
        self.assertEqual(
            json.loads(self.api.listAddressBookEntries()).get('addresses'),
            []
        )

    def test_subscriptions(self):
        """Testing the API commands related to subscriptions"""

        self.assertEqual(
            self.api.addSubscription(sample_test_subscription_address[0], sample_subscription_name.encode('base64')),
            'Added subscription.'
        )

        added_subscription = {'label': None, 'enabled': False}
        # check_address
        for sub in json.loads(self.api.listSubscriptions())['subscriptions']:
            # special address, added when sqlThread starts
            if sub['address'] == sample_test_subscription_address[0]:
                added_subscription = sub
                break

        self.assertEqual(
            base64.decodestring(added_subscription['label']) if added_subscription['label'] else None,
            sample_subscription_name)
        self.assertTrue(added_subscription['enabled'])

        for s in json.loads(self.api.listSubscriptions())['subscriptions']:
            # special address, added when sqlThread starts
            if s['address'] == sample_test_subscription_address[1]:
                self.assertEqual(
                    base64.decodestring(s['label']),
                    'Bitmessage new releases/announcements')
                self.assertTrue(s['enabled'])
                break
        else:
            self.fail(
                'Could not find Bitmessage new releases/announcements'
                ' in subscriptions')
        self.assertEqual(
            self.api.deleteSubscription(sample_test_subscription_address[0]),
            'Deleted subscription if it existed.')
        self.assertEqual(
            self.api.deleteSubscription(sample_test_subscription_address[1]),
            'Deleted subscription if it existed.')
        self.assertEqual(
            json.loads(self.api.listSubscriptions())['subscriptions'], [])

    def test_send(self):
        """Test message sending"""
        # self.api.createDeterministicAddresses(self._seed, 1, 4)
        addr = self._add_random_address('random_2')
        msg = base64.encodestring('test message')
        msg_subject = base64.encodestring('test_subject')
        ackdata = self.api.sendMessage(
            sample_deterministic_addr4, addr, msg_subject, msg)
        try:
            # Check ackdata and message status
            int(ackdata, 16)
            status = self.api.getStatus(ackdata)
            if status == 'notfound':
                raise KeyError
            self.assertIn(
                status, (
                    'msgqueued', 'awaitingpubkey', 'msgsent', 'ackreceived',
                    'doingpubkeypow', 'doingmsgpow', 'msgsentnoackexpected'
                ))
            # Find the message in sent
            for m in json.loads(
                    self.api.getSentMessagesByAddress(addr))['sentMessages']:
                if m['ackData'] == ackdata:
                    sent_msg = m['message']
                    break
            else:
                raise KeyError
            # Find the message in inbox
            # for m in json.loads(
            #     self.api.getInboxMessagesByReceiver(
            #         'BM-2cWzSnwjJ7yRP3nLEWUV5LisTZyREWSzUK'))['inboxMessages']:
            #     if m['subject'] == msg_subject:
            #         inbox_msg = m['message']
            #         break
        except ValueError:
            self.fail('sendMessage returned error or ackData is not hex')
        except KeyError:
            self.fail('Could not find sent message in sent messages')
        else:
            # Check found message
            try:
                self.assertEqual(sent_msg, msg.strip())
            except UnboundLocalError:
                self.fail('Could not find sent message in sent messages')
            # self.assertEqual(inbox_msg, msg.strip())
            self.assertEqual(json.loads(
                self.api.getSentMessageByAckData(ackdata)
            )['sentMessage'][0]['message'], sent_msg)
            # Trash the message
            self.assertEqual(
                self.api.trashSentMessageByAckData(ackdata),
                'Trashed sent message (assuming message existed).')
            # Empty trash
            self.assertEqual(self.api.deleteAndVacuum(), 'done')
            # The message should disappear
            self.assertIsNone(json.loads(
                self.api.getSentMessageByAckData(ackdata)))
        finally:
            self.assertEqual(self.api.deleteAddress(addr), 'success')

    def test_send_broadcast(self):
        """Test broadcast sending"""
        addr = self._add_random_address('random_2')
        msg = base64.encodestring('test broadcast')
        ackdata = self.api.sendBroadcast(
            addr, base64.encodestring('test_subject'), msg)

        try:
            int(ackdata, 16)
            status = self.api.getStatus(ackdata)
            if status == 'notfound':
                raise KeyError
            self.assertIn(status, (
                'doingbroadcastpow', 'broadcastqueued', 'broadcastsent'))

            start = time.time()
            while status == 'doingbroadcastpow':
                spent = int(time.time() - start)
                if spent > 30:
                    self.fail('PoW is taking too much time: %ss' % spent)
                time.sleep(1)  # wait for PoW to get final msgid on next step
                status = self.api.getStatus(ackdata)

            # Find the message and its ID in sent
            for m in json.loads(self.api.getAllSentMessages())['sentMessages']:
                if m['ackData'] == ackdata:
                    sent_msg = m['message']
                    sent_msgid = m['msgid']
                    break
            else:
                raise KeyError
        except ValueError:
            self.fail('sendBroadcast returned error or ackData is not hex')
        except KeyError:
            self.fail('Could not find sent broadcast in sent messages')
        else:
            # Check found message and its ID
            try:
                self.assertEqual(sent_msg, msg.strip())
            except UnboundLocalError:
                self.fail('Could not find sent message in sent messages')
            self.assertEqual(json.loads(
                self.api.getSentMessageById(sent_msgid)
            )['sentMessage'][0]['message'], sent_msg)
            self.assertIn(
                {'msgid': sent_msgid}, json.loads(
                    self.api.getAllSentMessageIds())['sentMessageIds'])
            # Trash the message by ID
            self.assertEqual(
                self.api.trashSentMessage(sent_msgid),
                'Trashed sent message (assuming message existed).')
            self.assertEqual(self.api.deleteAndVacuum(), 'done')
            self.assertIsNone(json.loads(
                self.api.getSentMessageById(sent_msgid)))
        finally:
            self.assertEqual(self.api.deleteAddress(addr), 'success')

    def test_chan(self):
        """Testing chan creation/joining"""
        # Create chan with known address
        self.assertEqual(
            self.api.createChan(self._seed), sample_deterministic_addr4)
        # cleanup
        self.assertEqual(
            self.api.leaveChan(sample_deterministic_addr4), 'success')
        # Join chan with addresses of version 3 or 4
        for addr in (sample_deterministic_addr4, sample_deterministic_addr3):
            self.assertEqual(self.api.joinChan(self._seed, addr), 'success')
            self.assertEqual(self.api.leaveChan(addr), 'success')
        # Joining with wrong address should fail
        self.assertRegexpMatches(
            self.api.joinChan(self._seed, 'BM-2cWzSnwjJ7yRP3nLEW'),
            r'^API Error 0008:'
        )
