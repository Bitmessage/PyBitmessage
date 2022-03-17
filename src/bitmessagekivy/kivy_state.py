# pylint: disable=too-many-instance-attributes, too-few-public-methods

"""
Kivy State variables are assigned here, they are separated from state.py
=================================
"""


class KivyStateVariables(object):
    """This Class hold all the kivy state variables"""

    def __init__(self):
        self.association = ''
        self.navinstance = None
        self.mail_id = 0
        self.myAddressObj = None
        self.detailPageType = None
        self.ackdata = None
        self.status = None
        self.screen_density = None
        self.msg_counter_objs = None
        self.check_sent_acc = None
        self.sent_count = 0
        self.inbox_count = 0
        self.trash_count = 0
        self.draft_count = 0
        self.all_count = 0
        self.searcing_text = ''
        self.search_screen = ''
        self.send_draft_mail = None
        self.is_allmail = False
        self.in_composer = False
        self.availabe_credit = 0
        self.in_sent_method = False
        self.in_search_mode = False
        self.imageDir = None
