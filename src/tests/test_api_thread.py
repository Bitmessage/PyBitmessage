"""TestAPIThread class definition"""

import sys
import time

from six.moves import queue, xmlrpc_client

from .partial import TestPartialRun
from .samples import sample_statusbar_msg  # any


class TestAPIThread(TestPartialRun):
    """Test case running the API thread"""

    @classmethod
    def setUpClass(cls):
        super(TestAPIThread, cls).setUpClass()

        import helper_sql
        import queues

        #  pylint: disable=too-few-public-methods
        class SqlReadyMock(object):
            """Mock helper_sql.sql_ready event with dummy class"""
            @staticmethod
            def wait():
                """Don't wait, return immediately"""
                return

        helper_sql.sql_ready = SqlReadyMock
        cls.queues = queues

        cls.config.set('bitmessagesettings', 'apiusername', 'username')
        cls.config.set('bitmessagesettings', 'apipassword', 'password')
        cls.config.set('inventory', 'storage', 'filesystem')

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

    def test_client_status(self):
        """Ensure the reply of clientStatus corresponds to mock"""
        status = self.api.clientStatus()
        if sys.hexversion >= 0x3000000:
            self.assertEqual(status["networkConnections"], 4)
            self.assertEqual(status["pendingDownload"], 0)
