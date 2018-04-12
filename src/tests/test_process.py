import unittest
import subprocess
import os
import signal
import tempfile
from time import sleep

import psutil


class TestProcessProto(unittest.TestCase):
    _process_cmd = ['pybitmessage', '-d']
    _threads_count = 14
    _files = ('keys.dat', 'debug.log', 'messages.dat', 'knownnodes.dat')

    @classmethod
    def setUpClass(cls):
        cls.home = os.environ['BITMESSAGE_HOME'] = tempfile.gettempdir()
        subprocess.call(cls._process_cmd)
        sleep(5)
        cls.pid = int(cls._get_readline('singleton.lock'))
        cls.process = psutil.Process(cls.pid)

    @classmethod
    def _get_readline(cls, pfile):
        pfile = os.path.join(cls.home, pfile)
        try:
            return open(pfile, 'rb').readline().strip()
        except (OSError, IOError):
            pass

    @classmethod
    def _cleanup_files(cls):
        for pfile in cls._files:
            try:
                os.remove(os.path.join(cls.home, pfile))
            except OSError:
                pass

    @classmethod
    def tearDownClass(cls):
        cls.process.send_signal(signal.SIGTERM)
        try:
            cls.process.wait(5)
        except psutil.TimeoutExpired:
            print(open(os.path.join(cls.home, 'debug.log'), 'rb').read())
            cls.process.kill()
        finally:
            cls._cleanup_files()

    def _test_threads(self):
        # only count for now
        # because of https://github.com/giampaolo/psutil/issues/613
        # PyBitmessage
        #   - addressGenerator
        #   - singleWorker
        #   - SQL
        #   - objectProcessor
        #   - singleCleaner
        #   - singleAPI
        #   - Asyncore
        #   - ReceiveQueue_0
        #   - ReceiveQueue_1
        #   - ReceiveQueue_2
        #   - Announcer
        #   - InvBroadcaster
        #   - AddrBroadcaster
        #   - Downloader
        self.assertEqual(
            len(self.process.threads()), self._threads_count)


class TestProcess(TestProcessProto):
    def test_process_name(self):
        """Check PyBitmessage process name"""
        self.assertEqual(self.process.name(), 'PyBitmessage')

    def test_files(self):
        """Check existence of PyBitmessage files"""
        for pfile in self._files:
            self.assertIsNot(
                self._get_readline(pfile), None,
                'Failed to read file %s' % pfile
            )

    def test_threads(self):
        """Testing PyBitmessage threads"""
        self._test_threads()
