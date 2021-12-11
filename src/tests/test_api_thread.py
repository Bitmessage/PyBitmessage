import time
import unittest

from six.moves import xmlrpc_client

from pybitmessage import pathmagic


class TestAPIThread(unittest.TestCase):
    """Test case running the API thread"""

    @classmethod
    def setUpClass(cls):
        pathmagic.setup()  # need this because of import state in network ):

        import helper_sql
        import helper_startup
        import state
        from bmconfigparser import BMConfigParser

        class SqlReadyMock(object):
            @staticmethod
            def wait():
                return

        helper_sql.sql_ready = SqlReadyMock
        cls.state = state
        helper_startup.loadConfig()
        # helper_startup.fixSocket()
        config = BMConfigParser()

        config.set('bitmessagesettings', 'apiusername', 'username')
        config.set('bitmessagesettings', 'apipassword', 'password')
        config.set('inventory', 'storage', 'filesystem')

        import api
        cls.thread = api.singleAPI()
        cls.thread.daemon = True
        cls.thread.start()
        time.sleep(3)
        cls.api = xmlrpc_client.ServerProxy(
            "http://username:password@127.0.0.1:8442/")

    def test_connection(self):
        """API command 'helloWorld'"""
        self.assertEqual(
            self.api.helloWorld('hello', 'world'), 'hello-world')

    @classmethod
    def tearDownClass(cls):
        cls.state.shutdown = 1
