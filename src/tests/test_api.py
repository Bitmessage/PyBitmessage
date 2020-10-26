"""
Tests using API.
"""

import base64
import json
import time
import xmlrpclib  # nosec

from test_process import TestProcessProto, TestProcessShutdown


class TestAPIProto(TestProcessProto):
    """Test case logic for testing API"""
    _process_cmd = ['pybitmessage', '-t']

    @classmethod
    def setUpClass(cls):
        """Setup XMLRPC proxy for pybitmessage API"""
        super(TestAPIProto, cls).setUpClass()
        cls.addresses = []
        cls.api = xmlrpclib.ServerProxy(
            "http://username:password@127.0.0.1:8442/")
        for _ in range(5):
            if cls._get_readline('.api_started'):
                return
            time.sleep(1)


class TestAPIShutdown(TestAPIProto, TestProcessShutdown):
    """Separate test case for API command 'shutdown'"""
    def test_shutdown(self):
        """Shutdown the pybitmessage"""
        self.assertEqual(self.api.shutdown(), 'done')
        for _ in range(5):
            if not self.process.is_running():
                break
            time.sleep(2)
        else:
            self.fail(
                '%s has not stopped in 10 sec' % ' '.join(self._process_cmd))


# TODO: uncovered API commands
# getAllInboxMessages
# getAllInboxMessageIds
# getInboxMessageById
# getInboxMessagesByReceiver
# trashMessage
# trashInboxMessage
# addSubscription
# disseminatePreEncryptedMsg
# disseminatePubkey
# getMessageDataByDestinationHash
# statusBar

class TestAPI(TestAPIProto):
    """Main API test case"""
    _seed = base64.encodestring(
        'TIGER, tiger, burning bright. In the forests of the night'
    )

    def _add_random_address(self, label):
        return self.api.createRandomAddress(base64.encodestring(label))

    def test_user_password(self):
        """Trying to connect with wrong username/password"""
        api_wrong = xmlrpclib.ServerProxy("http://test:wrong@127.0.0.1:8442/")
        with self.assertRaises(xmlrpclib.ProtocolError):
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
            self.api.decodeAddress('BM-2cWzSnwjJ7yRP3nLEWUV5LisTZyREWSzUK'))
        self.assertEqual(result.get('status'), 'success')
        self.assertEqual(result['addressVersion'], 4)
        self.assertEqual(result['streamNumber'], 1)

    def test_create_deterministic_addresses(self):
        """Test creation of deterministic addresses"""
        self.assertEqual(
            self.api.getDeterministicAddress(self._seed, 4, 1),
            'BM-2cWzSnwjJ7yRP3nLEWUV5LisTZyREWSzUK')
        self.assertEqual(
            self.api.getDeterministicAddress(self._seed, 3, 1),
            'BM-2DBPTgeSawWYZceFD69AbDT5q4iUWtj1ZN')
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
        self.assertEqual(addresses[0], 'BM-2cWzSnwjJ7yRP3nLEWUV5LisTZyREWSzUK')
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
            'BM-2cWzSnwjJ7yRP3nLEWUV5LisTZyREWSzUK',
            base64.encodestring('tiger_4')
        )
        # Check addressbook entry
        entries = json.loads(
            self.api.listAddressBookEntries()).get('addresses')[0]
        self.assertEqual(
            entries['address'], 'BM-2cWzSnwjJ7yRP3nLEWUV5LisTZyREWSzUK')
        self.assertEqual(
            base64.decodestring(entries['label']), 'tiger_4')
        # Remove known address
        self.api.deleteAddressBookEntry(
            'BM-2cWzSnwjJ7yRP3nLEWUV5LisTZyREWSzUK')
        # Addressbook should be empty again
        self.assertEqual(
            json.loads(self.api.listAddressBookEntries()).get('addresses'),
            []
        )

    def test_subscriptions(self):
        """Testing the API commands related to subscriptions"""
        for s in json.loads(self.api.listSubscriptions())['subscriptions']:
            # special address, added when sqlThread starts
            if s['address'] == 'BM-GtovgYdgs7qXPkoYaRgrLFuFKz1SFpsw':
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
            self.api.deleteSubscription('BM-GtovgYdgs7qXPkoYaRgrLFuFKz1SFpsw'),
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
            'BM-2cWzSnwjJ7yRP3nLEWUV5LisTZyREWSzUK', addr, msg_subject, msg)
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
            self.api.createChan(self._seed),
            'BM-2cWzSnwjJ7yRP3nLEWUV5LisTZyREWSzUK'
        )
        # cleanup
        self.assertEqual(
            self.api.leaveChan('BM-2cWzSnwjJ7yRP3nLEWUV5LisTZyREWSzUK'),
            'success'
        )
        # Join chan with addresses of version 3 or 4
        for addr in (
            'BM-2cWzSnwjJ7yRP3nLEWUV5LisTZyREWSzUK',
            'BM-2DBPTgeSawWYZceFD69AbDT5q4iUWtj1ZN'
        ):
            self.assertEqual(self.api.joinChan(self._seed, addr), 'success')
            self.assertEqual(self.api.leaveChan(addr), 'success')
        # Joining with wrong address should fail
        self.assertRegexpMatches(
            self.api.joinChan(self._seed, 'BM-2cWzSnwjJ7yRP3nLEW'),
            r'^API Error 0008:'
        )
