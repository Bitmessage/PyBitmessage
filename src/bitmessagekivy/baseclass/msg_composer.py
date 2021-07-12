import time

from bitmessagekivy.get_platform import platform
from bmconfigparser import BMConfigParser
from helper_sql import sqlExecute, sqlQuery
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
)
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput

import state
import queues

from addresses import decodeAddress, addBMIfNotPresent
from bitmessagekivy.baseclass.common import (
    toast, showLimitedCnt
)
from kivymd.uix.textfield import MDTextField


class Create(Screen):
    """Creates Screen class for kivy Ui"""

    def __init__(self, **kwargs):
        """Getting Labels and address from addressbook"""
        super(Create, self).__init__(**kwargs)
        Window.softinput_mode = "below_target"
        widget_1 = DropDownWidget()
        widget_1.ids.txt_input.word_list = [
            addr[1] for addr in sqlQuery(
                "SELECT label, address from addressbook")]
        widget_1.ids.txt_input.starting_no = 2
        self.add_widget(widget_1)
        self.children[0].ids.id_scroll.bind(scroll_y=self.check_scroll_y)

    def check_scroll_y(self, instance, somethingelse):  # pylint: disable=unused-argument
        """show data on scroll down"""
        if self.children[1].ids.btn.is_open:
            self.children[1].ids.btn.is_open = False


class RV(RecycleView):
    """Recycling View class for kivy Ui"""

    def __init__(self, **kwargs):
        """Recycling Method"""
        super(RV, self).__init__(**kwargs)


class SelectableRecycleBoxLayout(
    FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout
):
    """Adds selection and focus behaviour to the view"""

    # pylint: disable = duplicate-bases


class DropDownWidget(BoxLayout):
    """DropDownWidget class for kivy Ui"""

    # pylint: disable=too-many-statements

    txt_input = ObjectProperty()
    rv = ObjectProperty()

    def send(self, navApp):
        """Send message from one address to another"""
        fromAddress = self.ids.ti.text.strip()
        toAddress = self.ids.txt_input.text.strip()
        subject = self.ids.subject.text.strip()
        message = self.ids.body.text.strip()
        print("message: ", self.ids.body.text)
        if toAddress != "" and subject and message:
            status, addressVersionNumber, streamNumber, ripe = decodeAddress(
                toAddress
            )
            if status == "success":
                navApp.root.ids.sc3.children[0].active = True
                if state.detailPageType == "draft" and state.send_draft_mail:
                    sqlExecute(
                        "UPDATE sent SET toaddress = ?"
                        ", fromaddress = ? , subject = ?"
                        ", message = ?, folder = 'sent'"
                        ", senttime = ?, lastactiontime = ?"
                        " WHERE ackdata = ?;",
                        toAddress,
                        fromAddress,
                        subject,
                        message,
                        int(time.time()),
                        int(time.time()),
                        state.send_draft_mail)
                    self.parent.parent.screens[13].clear_widgets()
                    self.parent.parent.screens[13].add_widget(Factory.Draft())
                    # state.detailPageType = ''
                    # state.send_draft_mail = None
                else:
                    # toAddress = addBMIfNotPresent(toAddress)
                    if (addressVersionNumber > 4) or (
                            addressVersionNumber <= 1):
                        print(
                            "addressVersionNumber > 4"
                            " or addressVersionNumber <= 1")
                    if streamNumber > 1 or streamNumber == 0:
                        print("streamNumber > 1 or streamNumber == 0")
                    stealthLevel = BMConfigParser().safeGetInt(
                        'bitmessagesettings', 'ackstealthlevel')
                    from helper_ackPayload import genAckPayload
                    # ackdata = genAckPayload(streamNumber, stealthLevel)
                    # t = ()
                    sqlExecute(
                        '''INSERT INTO sent VALUES
                        (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                        '',
                        addBMIfNotPresent(toAddress),
                        ripe,
                        fromAddress,
                        subject,
                        message,
                        genAckPayload(streamNumber, stealthLevel),  #ackdata
                        int(time.time()),
                        int(time.time()),
                        0,
                        'msgqueued',
                        0,
                        'sent',
                        3,  #encoding
                        BMConfigParser().safeGetInt(
                            'bitmessagesettings', 'ttl'))
                state.check_sent_acc = fromAddress
                # state.msg_counter_objs = self.parent.parent.parent.parent\
                #     .parent.parent.children[2].children[0].ids
                if state.detailPageType == 'draft' \
                        and state.send_draft_mail:
                    state.draft_count = str(int(state.draft_count) - 1)
                    # state.msg_counter_objs.draft_cnt.badge_text = (
                    #     state.draft_count)
                    state.detailPageType = ''
                    state.send_draft_mail = None
                self.parent.parent.parent.ids.sc4.update_sent_messagelist()
                allmailCnt_obj = state.kivyapp.root.ids.content_drawer.ids.allmail_cnt
                allmailCnt_obj.ids.badge_txt.text = showLimitedCnt(int(state.all_count) + 1)
                state.all_count = str(int(state.all_count) + 1)
                Clock.schedule_once(self.callback_for_msgsend, 3)
                queues.workerQueue.put(('sendmessage', addBMIfNotPresent(toAddress)))
                print("sqlExecute successfully #######################")
                state.in_composer = True
                return
            else:
                msg = 'Enter a valid recipients address'
        elif not toAddress:
            msg = 'Please fill the form completely'
        else:
            msg = 'Please fill the form completely'
        self.address_error_message(msg)

    @staticmethod
    def callback_for_msgsend(dt=0):  # pylint: disable=unused-argument
        """Callback method for messagesend"""
        state.kivyapp.root.ids.sc3.children[0].active = False
        state.in_sent_method = True
        state.kivyapp.back_press()
        toast("sent")

    @staticmethod
    def address_error_message(msg):
        """Generates error message"""
        width = .8 if platform == 'android' else .55
        dialog_box = MDDialog(
            text=msg,
            size_hint=(width, .25),
            buttons=[
                MDFlatButton(
                    text="Ok", on_release=lambda x: callback_for_menu_items("Ok")
                ),
            ],)
        dialog_box.open()

        def callback_for_menu_items(text_item, *arg):
            """Callback of alert box"""
            dialog_box.dismiss()
            toast(text_item)

    def reset_composer(self):
        """Method will reset composer"""
        self.ids.ti.text = ""
        self.ids.btn.text = "Select"
        self.ids.txt_input.text = ""
        self.ids.subject.text = ""
        self.ids.body.text = ""
        toast("Reset message")

    def auto_fill_fromaddr(self):
        """Fill the text automatically From Address"""
        self.ids.ti.text = self.ids.btn.text
        self.ids.ti.focus = True

    def is_camara_attached(self):
        """Checks the camera availability in device"""
        self.parent.parent.parent.ids.sc23.check_camera()
        is_available = self.parent.parent.parent.ids.sc23.camera_avaialbe
        return is_available

    @staticmethod
    def camera_alert():
        """Show camera availability alert message"""
        width = .8 if platform == 'android' else .55
        altet_txt = 'Currently this feature is not avaialbe!'if platform == 'android' else 'Camera is not available!'
        dialog_box = MDDialog(
            text=altet_txt,
            size_hint=(width, .25),
            buttons=[
                MDFlatButton(
                    text="Ok", on_release=lambda x: callback_for_menu_items("Ok")
                ),
            ],
        )
        dialog_box.open()

        def callback_for_menu_items(text_item, *arg):
            """Callback of alert box"""
            dialog_box.dismiss()
            toast(text_item)


class MyTextInput(MDTextField):
    """MyTextInput class for kivy Ui"""

    txt_input = ObjectProperty()
    flt_list = ObjectProperty()
    word_list = ListProperty()
    starting_no = NumericProperty(3)
    suggestion_text = ''

    def __init__(self, **kwargs):
        """Getting Text Input."""
        super(MyTextInput, self).__init__(**kwargs)
        self.__lineBreak__ = 0

    def on_text(self, instance, value):  # pylint: disable=unused-argument
        """Find all the occurrence of the word"""
        self.parent.parent.parent.parent.parent.ids.rv.data = []
        matches = [self.word_list[i] for i in range(
            len(self.word_list)) if self.word_list[
                i][:self.starting_no] == value[:self.starting_no]]
        display_data = []
        for i in matches:
            display_data.append({'text': i})
        self.parent.parent.parent.parent.parent.ids.rv.data = display_data
        if len(matches) <= 10:
            self.parent.height = (250 + (len(matches) * 20))
        else:
            self.parent.height = 400

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """Keyboard on key Down"""
        if self.suggestion_text and keycode[1] == 'tab':
            self.insert_text(self.suggestion_text + ' ')
            return True
        return super(MyTextInput, self).keyboard_on_key_down(
            window, keycode, text, modifiers)


class SelectableLabel(RecycleDataViewBehavior, Label):
    """Add selection support to the Label"""

    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        """Catch and handle the view changes"""
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):  # pylint: disable=inconsistent-return-statements
        """Add selection on touch down"""
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """Respond to the selection of items in the view"""
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
            rv.parent.txt_input.text = rv.parent.txt_input.text.replace(
                rv.parent.txt_input.text, rv.data[index]["text"]
            )
