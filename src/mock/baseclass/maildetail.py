# pylint: disable=import-error, no-name-in-module, unused-argument
# pylint: disable=import-outside-toplevel, too-many-function-args


"""
Kivy Mail Detail screen
"""

from datetime import datetime

from kivy.core.clipboard import Clipboard
from kivy.clock import Clock
from kivy.properties import (
    StringProperty,
    NumericProperty
)
from kivy.factory import Factory
from kivy.uix.screenmanager import Screen

from kivymd.uix.button import MDFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import (
    OneLineListItem,
    IRightBodyTouch
)

from pybitmessage import state
from pybitmessage import kivy_state

from .common import (
    toast, avatarImageFirstLetter, ShowTimeHistoy
)
from .popup import SenderDetailPopup


# from pybitmessage.get_platform import platform
platform = "linux"


class OneLineListTitle(OneLineListItem):
    """OneLineListTitle class for kivy Ui"""
    __events__ = ('on_long_press', )
    long_press_time = NumericProperty(1)

    def on_state(self, instance, value):
        """On state"""
        if value == 'down':
            lpt = self.long_press_time
            self._clockev = Clock.schedule_once(self._do_long_press, lpt)
        else:
            self._clockev.cancel()

    def _do_long_press(self, dt):
        """Do long press"""
        self.dispatch('on_long_press')

    def on_long_press(self, *largs):
        """On long press"""
        self.copymessageTitle(self.text)

    def copymessageTitle(self, title_text):
        """this method is for displaying dialog box"""
        self.title_text = title_text
        width = .8 if platform == 'android' else .55
        self.dialog_box = MDDialog(
            text=title_text,
            size_hint=(width, .25),
            buttons=[
                MDFlatButton(
                    text="Copy", on_release=self.callback_for_copy_title
                ),
                MDFlatButton(
                    text="Cancel", on_release=self.callback_for_copy_title,
                ),
            ],)
        self.dialog_box.open()

    def callback_for_copy_title(self, instance):
        """Callback of alert box"""
        if instance.text == 'Copy':
            Clipboard.copy(self.title_text)
        self.dialog_box.dismiss()
        toast(instance.text)


class IconRightSampleWidget(IRightBodyTouch, MDIconButton):
    """IconRightSampleWidget class for kivy Ui"""


class MailDetail(Screen):  # pylint: disable=too-many-instance-attributes
    """MailDetail Screen class for kivy Ui"""

    to_addr = StringProperty()
    from_addr = StringProperty()
    subject = StringProperty()
    message = StringProperty()
    status = StringProperty()
    page_type = StringProperty()
    time_tag = StringProperty()
    avatarImg = StringProperty()

    def __init__(self, *args, **kwargs):
        """Mail Details method"""
        super().__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method MailDetail mails"""
        self.page_type = state.detailPageType if kivy_state.detailPageType else ''
        try:
            # pylint: disable=consider-using-in
            if kivy_state.detailPageType == 'sent' or kivy_state.detailPageType == 'draft':
                data = []
                state.status = self
                state.ackdata = data[0][5]
                self.assign_mail_details(data)
                state.kivyapp.set_mail_detail_header()
            elif kivy_state.detailPageType == 'inbox':
                data = []
                self.assign_mail_details(data)
                state.kivyapp.set_mail_detail_header()
        except Exception as e:
            print('Something wents wrong!!')

    def assign_mail_details(self, data):
        """Assigning mail details"""
        subject = data[0][2].decode() if isinstance(data[0][2], bytes) else data[0][2]
        body = data[0][3].decode() if isinstance(data[0][2], bytes) else data[0][3]
        self.to_addr = data[0][0] if len(data[0][0]) > 4 else ' '
        self.from_addr = data[0][1]

        self.subject = subject.capitalize(
        ) if subject.capitalize() else '(no subject)'
        self.message = body
        if len(data[0]) == 7:
            self.status = data[0][4]
        self.time_tag = ShowTimeHistoy(data[0][4]) \
            if kivy_state.detailPageType == 'inbox' else ShowTimeHistoy(data[0][6])
        self.avatarImg = kivy_state.imageDir + '/avatar.png' if kivy_state.detailPageType == 'draft' else (
            kivy_state.imageDir + f'/text_images/{avatarImageFirstLetter(self.subject.strip(9))}.png')  # noqa:E999
        self.timeinseconds = data[0][4] if kivy_state.detailPageType == 'inbox' else data[0][6]

    def delete_mail(self):
        """Method for mail delete"""
        msg_count_objs = state.kivyapp.root.ids.content_drawer.ids
        kivy_state.searcing_text = ''
        self.children[0].children[0].active = True
        if kivy_state.detailPageType == 'sent':
            state.kivyapp.root.ids.sc4.ids.sent_search.ids.search_field.text = ''
            msg_count_objs.send_cnt.ids.badge_txt.text = str(int(kivy_state.sent_count) - 1)
            kivy_state.sent_count = str(int(kivy_state.sent_count) - 1)
            self.parent.screens[2].ids.ml.clear_widgets()
            self.parent.screens[2].loadSent(kivy_state.association)
        elif kivy_state.detailPageType == 'inbox':
            state.kivyapp.root.ids.sc1.ids.inbox_search.ids.search_field.text = ''
            msg_count_objs.inbox_cnt.ids.badge_txt.text = str(
                int(kivy_state.inbox_count) - 1)
            kivy_state.inbox_count = str(int(kivy_state.inbox_count) - 1)
            self.parent.screens[0].ids.ml.clear_widgets()
            self.parent.screens[0].loadMessagelist(kivy_state.association)

        elif kivy_state.detailPageType == 'draft':
            msg_count_objs.draft_cnt.ids.badge_txt.text = str(
                int(kivy_state.draft_count) - 1)
            kivy_state.draft_count = str(int(kivy_state.draft_count) - 1)
            self.parent.screens[13].clear_widgets()
            self.parent.screens[13].add_widget(Factory.Draft())

        if kivy_state.detailPageType != 'draft':
            msg_count_objs.trash_cnt.ids.badge_txt.text = str(
                int(kivy_state.trash_count) + 1)
            msg_count_objs.allmail_cnt.ids.badge_txt.text = str(
                int(kivy_state.all_count) - 1)
            kivy_state.trash_count = str(int(kivy_state.trash_count) + 1)
            kivy_state.all_count = str(int(kivy_state.all_count) - 1) if int(kivy_state.all_count) else '0'
            self.parent.screens[3].clear_widgets()
            self.parent.screens[3].add_widget(Factory.Trash())
            self.parent.screens[14].clear_widgets()
            self.parent.screens[14].add_widget(Factory.Allmails())
        Clock.schedule_once(self.callback_for_delete, 4)

    def callback_for_delete(self, dt=0):
        """Delete method from allmails"""
        if kivy_state.detailPageType:
            self.children[0].children[0].active = False
            state.kivyapp.set_common_header()
            self.parent.current = 'allmails' \
                if kivy_state.is_allmail else kivy_state.detailPageType
            kivy_state.detailPageType = ''
            toast('Deleted')

    def inbox_reply(self):
        """Reply inbox messages"""
        kivy_state.in_composer = True
        data = []
        composer_obj = self.parent.screens[1].children[1].ids
        composer_obj.ti.text = data[0][0]
        composer_obj.btn.text = data[0][0]
        composer_obj.txt_input.text = data[0][1]
        split_subject = data[0][2].split('Re:', 1)
        composer_obj.subject.text = 'Re: ' + (split_subject[1] if len(split_subject) > 1 else split_subject[0])
        time_obj = datetime.fromtimestamp(int(data[0][4]))
        time_tag = time_obj.strftime("%d %b %Y, %I:%M %p")
        # sender_name = BMConfigParser().get(data[0][1], 'label')
        sender_name = data[0][1]
        composer_obj.body.text = (
            '\n\n --------------On ' + time_tag + ', ' + sender_name + ' wrote:--------------\n' + data[0][3])
        composer_obj.body.focus = True
        composer_obj.body.cursor = (0, 0)
        state.kivyapp.root.ids.sc3.children[1].ids.rv.data = ''
        self.parent.current = 'create'
        state.kivyapp.set_navbar_for_composer()

    def write_msg(self, navApp):
        """Write on draft mail"""
        kivy_state.send_draft_mail = kivy_state.mail_id
        data = []
        composer_ids = (
            self.parent.parent.ids.sc3.children[1].ids)
        composer_ids.ti.text = data[0][1]
        composer_ids.btn.text = data[0][1]
        composer_ids.txt_input.text = data[0][0]
        composer_ids.subject.text = data[0][2] if data[0][2] != '(no subject)' else ''
        composer_ids.body.text = data[0][3]
        self.parent.current = 'create'
        navApp.set_navbar_for_composer()

    def detailedPopup(self):
        """Detailed popup"""
        obj = SenderDetailPopup()
        obj.open()
        arg = (self.to_addr, self.from_addr, self.timeinseconds)
        obj.assignDetail(*arg)

    @staticmethod
    def callback_for_menu_items(text_item, *arg):
        """Callback of alert box"""
        toast(text_item)
