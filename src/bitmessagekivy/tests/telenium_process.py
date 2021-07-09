import os
import shutil
import tempfile

from telenium.tests import TeleniumTestCase

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
            os.remove(os.path.join(home, pfile))
        except OSError:
            pass


def set_temp_data():
    """Set temp data in tmp directory"""
    for file in tmp_db_file:
        old_source_file = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), 'sampleData', file)
        new_destination_file = os.path.join(os.environ['BITMESSAGE_HOME'], file)
        shutil.copyfile(old_source_file, new_destination_file)


class TeleniumTestProcess(TeleniumTestCase):
    """Setting Screen Functionality Testing"""
    cmd_entrypoint = [os.path.join(os.path.abspath(os.getcwd()), 'src', 'main_test.py')]

    @classmethod
    def setUpClass(cls):
        """Setupclass is for setting temp environment"""
        os.environ["BITMESSAGE_HOME"] = tempfile.gettempdir()
        set_temp_data()
        super(TeleniumTestProcess, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        """Ensures that pybitmessage stopped and removes files"""
        cleanup()
        cls.cli.app_quit()
        cls.process.kill()

    def click_on(self, xpath, seconds=0.3):
        """this methos is used for on_click event with time"""
        self.cli.click_on(xpath)
        self.cli.sleep(seconds)

    def drag(self, xpath1, xpath2):
        self.cli.drag(xpath1, xpath2, 1)
        self.cli.sleep(0.3)
