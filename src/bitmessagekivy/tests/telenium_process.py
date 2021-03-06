import os
import psutil
import shutil
import tempfile
from telenium.tests import TeleniumTestCase
from bitmessagekivy.tests.test_process_data import TestProcessProto


_files = (
    'keys.dat', 'debug.log', 'messages.dat', 'knownnodes.dat',
    '.api_started', 'unittest.lock'
)

tmp_db_file = (
    'keys.dat', 'messages.dat'
)


def cleanup(home=None, files=_files):
    """Cleanup application files"""
    if not home:
        home = tempfile.gettempdir()
    for pfile in files:
        try:
            # import pdb;pdb.set_trace()
            os.remove(os.path.join(home, pfile))
            print(__file__,'.........................................(clean)', pfile)
        except OSError:
            print('error............................................')
            pass


def set_temp_data():
    for file in tmp_db_file:
        old_source_file = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), 'sampleData', file)
        new_destination_file =  os.path.join(os.environ['BITMESSAGE_HOME'], file)
        shutil.copyfile(old_source_file, new_destination_file)


class TeleniumTestProcess(TeleniumTestCase):
    """Setting Screen Functionality Testing"""
    cmd_entrypoint = ['/home/cis/py3porting/Chatroom/PyBitmessage/src/main.py']

    @classmethod
    def setUpClass(cls, is_login_screen=None):
        print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', is_login_screen)
        os.environ["BITMESSAGE_HOME"] = tempfile.gettempdir()
        if is_login_screen:
            cleanup()
        else:
            set_temp_data()
        super(TeleniumTestProcess, cls).setUpClass()

    # @classmethod
    # def tearDownClass(cls):
    #     """Ensures that pybitmessage stopped and removes files"""
    #     print('tearDownClass.........................................(pass)')
    #     try:
    #         if not cls._stop_process(1):
    #             processes = cls.process.children(recursive=True)
    #             processes.append(cls.process)
    #             for p in processes:
    #                 try:
    #                     p.kill()
    #                 except psutil.NoSuchProcess:
    #                     pass
    #     except psutil.NoSuchProcess:
    #         pass
    #     finally:
    #         # import pdb;pdb.set_trace()
    #         cleanup()
    #         # cls._cleanup_files()

    # @classmethod
    # def _stop_process(cls, timeout=5):
    #     print('_stop_process.........................................(pass)')
    #     import signal
    #     cls.process.send_signal(signal.SIGTERM)
    #     try:
    #         cls.process.wait(timeout)
    #     except psutil.TimeoutExpired:
    #         return False
    #     return True