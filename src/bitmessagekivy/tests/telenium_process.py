import os
import tempfile
from telenium.tests import TeleniumTestCase
from bitmessagekivy.tests.test_process_data import TestProcessProto

class TeleniumTestProcess(TestProcessProto, TeleniumTestCase):
    """Setting Screen Functionality Testing"""
    cmd_entrypoint = ['/home/cis/py3porting/Chatroom/PyBitmessage/src/main.py']

    @classmethod
    def setUpClass(cls):
        print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
        os.environ["BITMESSAGE_HOME"] = tempfile.gettempdir()
        TeleniumTestCase.start_process()
        super(TeleniumTestProcess, cls).setUpClass()
