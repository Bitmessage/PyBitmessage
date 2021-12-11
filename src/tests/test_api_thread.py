import time
import unittest

from six.moves import queue, xmlrpc_client

from pybitmessage import pathmagic

from .samples import sample_statusbar_msg  # any


class TestAPIThread(unittest.TestCase):
    """Test case running the API thread"""

    @classmethod
    def setUpClass(cls):
        pathmagic.setup()  # need this because of import state in network ):

        import helper_sql
        import helper_startup
        import queues
        import state
        from bmconfigparser import BMConfigParser

        #  pylint: disable=too-few-public-methods
        class SqlReadyMock(object):
            """Mock helper_sql.sql_ready event with dummy class"""
            @staticmethod
            def wait():
                """Don't wait, return immediately"""
                return

        helper_sql.sql_ready = SqlReadyMock
        cls.state = state
        cls.queues = queues

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

    def test_statusbar(self):
        """Check UISignalQueue after issuing the 'statusBar' command"""
        self.queues.UISignalQueue.queue.clear()
        self.assertEqual(
            self.api.statusBar(sample_statusbar_msg), 'success')
        try:
            cmd, data = self.queues.UISignalQueue.get(block=False)
        except queue.Empty:
            self.fail('UISignalQueue is empty!')

        self.assertEqual(cmd, 'updateStatusBar')
        self.assertEqual(data, sample_statusbar_msg)

    @classmethod
    def tearDownClass(cls):
        cls.state.shutdown = 1
