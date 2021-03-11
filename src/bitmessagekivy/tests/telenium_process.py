import os, signal 
import psutil
import shutil
import tempfile
from telenium.tests import TeleniumTestCase
from threads import addressGenerator, sqlThread


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
            # print('error............................................')
            pass


def set_temp_data():
    for file in tmp_db_file:
        old_source_file = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), 'sampleData', file)
        new_destination_file =  os.path.join(os.environ['BITMESSAGE_HOME'], file)
        shutil.copyfile(old_source_file, new_destination_file)


class TeleniumTestProcess(TeleniumTestCase):
    """Setting Screen Functionality Testing"""
    cmd_entrypoint = [os.path.join(os.path.abspath(os.getcwd()), 'main_mock_test.py')]

    @classmethod
    def setUpClass(cls):
        print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', __file__)
        os.environ["BITMESSAGE_HOME"] = tempfile.gettempdir()
        set_temp_data()
        super(TeleniumTestProcess, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        """Ensures that pybitmessage stopped and removes files"""
        # super(TeleniumTestProcess, cls).tearDownClass()
        print('tearDownClass.........................................(pass)', os.getpid())
        cleanup()
        pid = os.getpid()
        os.kill(int(pid), signal.SIGKILL)
        # import pdb;pdb.set_trace()

    #     # os.kill()
    #     # import psutil
    #     # cnt = 0
    #     # # print('total count=========================================', len(psutil.process_iter()))
    #     # for proc in psutil.process_iter():
    #     #     print('line...................................62', proc.name(), proc.pid)
    #     #     cnt = cnt +1
    #     #     if proc.name() == 'python':
    #     #         print('line........................69', proc.pid)
    #     #         # os.kill(int(pid), signal.SIGKILL)
    #     #         print('total cnt.............................', cnt)
    #     #         # cleanup()
    #     #         proc.kill()
    #     #         # os.kill(int(proc.pid), signal.SIGKILL)

    @classmethod
    def setUp(self):
        # self.widget = Widget('The widget')
        print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&7setup')

    @classmethod
    def tearDown(self):
        print('###############################################tearDown')
        # self.widget.dispose()
