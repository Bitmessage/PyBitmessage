"""
Common reusable code for tests and tests for pybitmessage process.
"""

import os
import signal
import subprocess  # nosec
import sys
import tempfile
import time
import unittest

import psutil

from pybitmessage.paths import set_appdata_folder


def put_signal_file(path, filename):
    """Creates file, presence of which is a signal about some event."""
    with open(os.path.join(path, filename), 'wb') as outfile:
        outfile.write(str(time.time()))


class TestProcessProto(unittest.TestCase):
    """Test case implementing common logic for external testing:
    it starts pybitmessage in setUpClass() and stops it in tearDownClass()
    """
    _process_cmd = ['pybitmessage', '-d']
    _threads_count_min = 15
    _threads_count_max = 16
    _threads_names = [
        'PyBitmessage',
        'addressGenerato',
        'singleWorker',
        'SQL',
        'objectProcessor',
        'singleCleaner',
        'singleAPI',
        'Asyncore',
        'ReceiveQueue_0',
        'ReceiveQueue_1',
        'ReceiveQueue_2',
        'Announcer',
        'InvBroadcaster',
        'AddrBroadcaster',
        'Downloader',
        'Uploader'
    ]
    _files = (
        'keys.dat', 'debug.log', 'messages.dat', 'knownnodes.dat',
        '.api_started', 'unittest.lock'
    )

    @classmethod
    def setUpClass(cls):
        """Setup environment and start pybitmessage"""
        cls.home = set_appdata_folder(tempfile.gettempdir())
        cls._cleanup_files()
        put_signal_file(cls.home, 'unittest.lock')
        starttime = int(time.time())
        subprocess.call(cls._process_cmd)  # nosec
        timeout = starttime + 30
        while time.time() <= timeout:
            try:
                if os.path.exists(os.path.join(cls.home,
                                               'singleton.lock')):
                    pstat = os.stat(os.path.join(cls.home, 'singleton.lock'))
                    if starttime <= pstat.st_mtime and pstat.st_size > 0:
                        break
            except OSError:
                break
            time.sleep(1)
        if time.time() >= timeout:
            raise psutil.TimeoutExpired(
                "Timeout starting {}".format(cls._process_cmd))
        # wait a bit for the program to fully start
        # 10 sec should be enough
        time.sleep(10)
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
    def _stop_process(cls, timeout=5):
        cls.process.send_signal(signal.SIGTERM)
        try:
            cls.process.wait(timeout)
        except psutil.TimeoutExpired:
            return False
        return True

    @classmethod
    def _kill_process(cls, timeout=5):
        try:
            cls.process.send_signal(signal.SIGKILL)
            cls.process.wait(timeout)
        # Windows or already dead
        except (AttributeError, psutil.NoSuchProcess):
            return True
        # except psutil.TimeoutExpired propagates, it means something is very
        # wrong
        return True

    @classmethod
    def _cleanup_files(cls):
        for pfile in cls._files:
            try:
                os.remove(os.path.join(cls.home, pfile))
            except OSError:
                pass

    @classmethod
    def tearDownClass(cls):
        """Ensures that pybitmessage stopped and removes files"""
        try:
            if not cls._stop_process():
                cls.process.kill()
                cls.process.wait(5)
        except (psutil.TimeoutExpired, psutil.NoSuchProcess):
            pass
        finally:
            cls._cleanup_files()

    def _test_threads(self):
        """Test number and names of threads"""

        # pylint: disable=invalid-name
        self.longMessage = True

        try:
            # using ps for posix platforms
            # because of https://github.com/giampaolo/psutil/issues/613
            thread_names = subprocess.check_output([
                "ps", "-L", "-o", "comm=", "--pid",
                str(self.process.pid)
            ]).split()
        except:  # pylint: disable=bare-except
            thread_names = []

        running_threads = len(thread_names)
        if 0 < running_threads < 30:  # adequacy check
            extra_threads = []
            missing_threads = []
            for thread_name in thread_names:
                if thread_name not in self._threads_names:
                    extra_threads.append(thread_name)
            for thread_name in self._threads_names:
                if thread_name not in thread_names:
                    missing_threads.append(thread_name)

            msg = "Missing threads: {}, Extra threads: {}".format(
                ",".join(missing_threads), ",".join(extra_threads))
        else:
            running_threads = self.process.num_threads()
            if sys.platform.startswith('win'):
                running_threads -= 1  # one extra thread on Windows!
            msg = "Unexpected running thread count"

        self.assertGreaterEqual(
            running_threads,
            self._threads_count_min,
            msg)

        self.assertLessEqual(
            running_threads,
            self._threads_count_max,
            msg)


class TestProcessShutdown(TestProcessProto):
    """Separate test case for SIGTERM"""
    def test_shutdown(self):
        """Send to pybitmessage SIGTERM and ensure it stopped"""
        # longer wait time because it's not a benchmark
        self.assertTrue(
            self._stop_process(20),
            '%s has not stopped in 20 sec' % ' '.join(self._process_cmd))

    @classmethod
    def tearDownClass(cls):
        """Special teardown because pybitmessage is already stopped"""
        try:
            if cls.process.is_running():
                cls.process.kill()
                cls.process.wait(5)
        except (psutil.TimeoutExpired, psutil.NoSuchProcess):
            pass
        finally:
            cls._cleanup_files()


class TestProcess(TestProcessProto):
    """A test case for pybitmessage process"""
    def test_process_name(self):
        """Check PyBitmessage process name"""
        self.assertEqual(self.process.name(), 'PyBitmessage')

    def test_files(self):
        """Check existence of PyBitmessage files"""
        for pfile in self._files:
            if pfile.startswith('.'):
                continue
            self.assertIsNot(
                self._get_readline(pfile), None,
                'Failed to read file %s' % pfile
            )

    def test_threads(self):
        """Testing PyBitmessage threads"""
        self._test_threads()
