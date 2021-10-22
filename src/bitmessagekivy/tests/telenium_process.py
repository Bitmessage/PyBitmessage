"""
    Base class for telenium test cases which run kivy app as background process
"""

import os
import shutil
import tempfile
from time import time, sleep

from telenium.tests import TeleniumTestCase
from telenium.client import TeleniumHttpException


_files = (
    'keys.dat', 'debug.log', 'messages.dat', 'knownnodes.dat',
    '.api_started', 'unittest.lock'
)

tmp_db_file = (
    'keys.dat', 'messages.dat'
)


def cleanup(files=_files):
    """Cleanup application files"""
    for pfile in files:
        try:
            os.remove(os.path.join(tempfile.gettempdir(), pfile))
        except OSError:
            pass


class TeleniumTestProcess(TeleniumTestCase):
    """Setting Screen Functionality Testing"""
    cmd_entrypoint = [os.path.join(os.path.abspath(os.getcwd()), 'src', 'mock', 'kivy_main.py')]

    @classmethod
    def setUpClass(cls):
        """Setupclass is for setting temp environment"""
        os.environ["BITMESSAGE_HOME"] = tempfile.gettempdir()
        cls.populate_test_data()
        super(TeleniumTestProcess, cls).setUpClass()

    @staticmethod
    def populate_test_data():
        """Set temp data in tmp directory"""
        for file_name in tmp_db_file:
            old_source_file = os.path.join(
                os.path.abspath(os.path.dirname(__file__)), 'sampleData', file_name)
            new_destination_file = os.path.join(os.environ['BITMESSAGE_HOME'], file_name)
            shutil.copyfile(old_source_file, new_destination_file)

    @classmethod
    def tearDownClass(cls):
        """Ensures that pybitmessage stopped and removes files"""
        # pylint: disable=no-member
        try:
            cls.cli.app_quit()
        except:
            pass

        try:
            cls.process.kill()
        except:
            pass
        cleanup()

    def assert_wait_no_except(self, selector, timeout=-1, value='inbox'):
        """This method is to check the application is launched."""
        start = time()
        deadline = start + timeout
        while time() < deadline:
            try:
                if self.cli.getattr(selector, 'current') == value:
                    self.assertTrue(selector, value)
                    break
            except TeleniumHttpException:
                sleep(0.1)
                continue
            finally:
                # Finally Sleep is used to make the menu button funcationlly available for the click process.
                # (because Transition is little bit slow)
                sleep(0.2)

    def drag(self, xpath1, xpath2):
        """this method is for dragging"""
        self.cli.drag(xpath1, xpath2, 1)
        self.cli.sleep(0.3)

    def assertCheckScrollDown(self, selector, timeout=-1):
        """this method is for checking scroll"""
        start = time()
        while True:
            scroll_distance = self.cli.getattr(selector, 'scroll_y')
            if scroll_distance > 0.0:
                self.assertGreaterEqual(scroll_distance, 0.0)
                return True
            if timeout == -1:
                return False
            if timeout > 0 and time() - start > timeout:
                raise Exception("Timeout")
            sleep(0.1)

    def assertCheckScrollUp(self, selector, timeout=-1):
        """this method is for checking scroll UP"""
        start = time()
        while True:
            scroll_distance = self.cli.getattr(selector, 'scroll_y')
            if scroll_distance < 1.0:
                self.assertGreaterEqual(scroll_distance, 0.0)
                return True
            if timeout == -1:
                return False
            if timeout > 0 and time() - start > timeout:
                raise Exception("Timeout")
            sleep(0.1)

    def open_side_navbar(self):
        """Common method for opening Side navbar (Side Drawer)"""
        # Checking the drawer is in 'closed' state
        self.assertExists('//MDNavigationDrawer[@status~=\"closed\"]', timeout=5)
        # This is for checking the menu button is appeared
        self.assertExists('//MDActionTopAppBarButton[@icon~=\"menu\"]', timeout=5)
        # this is for opening Nav drawer
        self.cli.wait_click('//MDActionTopAppBarButton[@icon=\"menu\"]', timeout=5)
        # checking state of Nav drawer
        self.assertExists("//MDNavigationDrawer[@state~=\"open\"]", timeout=5)
