import unittest
import subprocess
import xmlrpclib
import base64
import json
import os
import tempfile
from time import sleep


class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.call(['pybitmessage', '-t'])
        cls.addresses = []
        cls.api = xmlrpclib.ServerProxy(
            "http://username:password@127.0.0.1:8442/")
        for tick in range(0, 10):
            sleep(1)
            if os.path.isfile(os.path.join(
                    tempfile.gettempdir(), '.api_started')):
                print('API start detected!')
                return

    def _add_random_address(self, label):
        return self.api.createRandomAddress(base64.encodestring(label))

    def test_user_password(self):
        api_wrong = xmlrpclib.ServerProxy("http://test:wrong@127.0.0.1:8442/")
        self.assertEqual(
            api_wrong.clientStatus(),
            'RPC Username or password incorrect or HTTP header lacks'
            ' authentication at all.'
        )

    def test_connection(self):
        self.assertEqual(
            self.api.helloWorld('hello', 'world'),
            'hello-world'
        )

    def test_arithmetic(self):
        """add API command"""
        self.assertEqual(self.api.add(69, 42), 111)

    def test_invalid_method(self):
        self.assertEqual(
            self.api.test(),
            'API Error 0020: Invalid method: test'
        )

    def test_list_addresses(self):
        self.assertEqual(
            json.loads(self.api.listAddresses()).get('addresses'),
            self.addresses
        )

    def test_decode_address(self):
        result = json.loads(
            self.api.decodeAddress('BM-2cWzSnwjJ7yRP3nLEWUV5LisTZyREWSzUK'))
        self.assertEqual(result.get('status'), 'success')
        self.assertEqual(result['addressVersion'], 4)
        self.assertEqual(result['streamNumber'], 1)

    def test_create_deterministic_addresses(self):
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
        # The following for version 2:
        # "API Error 0021: Unexpected API Failure -
        #  cannot concatenate 'str' and 'int' objects"

    def test_create_random_address(self):
        addr = self._add_random_address('random_1')
        self.assertRegexpMatches(addr, r'^BM-')
        self.assertRegexpMatches(addr[3:], r'[a-zA-Z1-9]+$')
        self.assertEqual(self.api.deleteAddress(addr), 'success')

    def test_addressbook(self):
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

    # def test_send_broadcast(self):
    #     addr = self._add_random_address('random_2')
        
