import xmlrpclib
import base64
import json
from time import sleep

from test_process import TestProcessProto


class TestAPI(TestProcessProto):
    _process_cmd = ['pybitmessage', '-t']

    @classmethod
    def setUpClass(cls):
        super(TestAPI, cls).setUpClass()
        cls.addresses = []
        cls.api = xmlrpclib.ServerProxy(
            "http://username:password@127.0.0.1:8442/")
        for tick in range(0, 5):
            if cls._get_readline('.api_started'):
                print('API start detected!')
                return
            sleep(1)

    def _add_random_address(self, label):
        return self.api.createRandomAddress(base64.encodestring(label))

    def test_user_password(self):
        """Trying to connect with wrong username/password"""
        api_wrong = xmlrpclib.ServerProxy("http://test:wrong@127.0.0.1:8442/")
        self.assertEqual(
            api_wrong.clientStatus(),
            'RPC Username or password incorrect or HTTP header lacks'
            ' authentication at all.'
        )

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
        """API command 'getDeterministicAddress': with various params"""
        seed = base64.encodestring(
            'TIGER, tiger, burning bright. In the forests of the night')
        self.assertEqual(
            self.api.getDeterministicAddress(seed, 4, 1),
            'BM-2cWzSnwjJ7yRP3nLEWUV5LisTZyREWSzUK'
        )
        self.assertEqual(
            self.api.getDeterministicAddress(seed, 3, 1),
            'BM-2DBPTgeSawWYZceFD69AbDT5q4iUWtj1ZN'
        )
        self.assertRegexpMatches(
            self.api.getDeterministicAddress(seed, 2, 1),
            r'^API Error 0002:'
        )
        # This is here until the streams will be implemented
        self.assertRegexpMatches(
            self.api.getDeterministicAddress(seed, 3, 2),
            r'API Error 0003:'
        )

    def test_create_random_address(self):
        """API command 'createRandomAddress': basic BM-address validation"""
        addr = self._add_random_address('random_1')
        self.assertRegexpMatches(addr, r'^BM-')
        self.assertRegexpMatches(addr[3:], r'[a-zA-Z1-9]+$')
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

    def test_send_broadcast(self):
        """API command 'sendBroadcast': ensure it returns ackData"""
        addr = self._add_random_address('random_2')
        ack = self.api.sendBroadcast(
            addr, base64.encodestring('test_subject'),
            base64.encodestring('test message')
        )
        try:
            int(ack, 16)
        except ValueError:
            self.fail('sendBroadcast returned error or ackData is not hex')
        finally:
            self.assertEqual(self.api.deleteAddress(addr), 'success')
