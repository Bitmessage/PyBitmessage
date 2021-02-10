
# pylint: disable=too-many-lines,import-error,no-name-in-module,unused-argument
# pylint: disable=too-many-ancestors,too-many-locals,useless-super-delegation
# pylint: disable=protected-access
# pylint: disable=import-outside-toplevel,ungrouped-imports,wrong-import-order,unused-import,arguments-differ
# pylint: disable=invalid-name,unnecessary-comprehension,broad-except,simplifiable-if-expression,no-member
# pylint: disable=too-many-return-statements

"""
Bitmessage android(mobile) interface
"""


from bitmessagekivy.get_platform import platform
import os
import time
from bitmessagekivy import identiconGeneration
from bitmessagekivy import kivy_helper_search
from bitmessagekivy.uikivysignaler import UIkivySignaler
from bmconfigparser import BMConfigParser
from functools import partial
from helper_sql import sqlExecute, sqlQuery
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty
)
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.carousel import Carousel
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.screenmanager import Screen
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivymd.uix.button import MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.list import (
    ILeftBody,
    ILeftBodyTouch,
    IRightBodyTouch,
    TwoLineAvatarIconListItem,
    OneLineIconListItem,
    OneLineAvatarIconListItem,
    OneLineListItem
)

# from kivymd.uix.navigationdrawer import (
#     MDNavigationDrawer,
#     NavigationDrawerHeaderBase
# )
from kivymd.uix.selectioncontrol import MDCheckbox, MDSwitch
from kivymd.uix.chip import MDChip
from kivy.uix.screenmanager import RiseInTransition, SlideTransition, FallOutTransition

import queues
from semaphores import kivyuisignaler

import state
from addresses import decodeAddress
from datetime import datetime
from kivymd.uix.behaviors.elevation import RectangularElevationBehavior
from kivymd.uix.bottomsheet import MDCustomBottomSheet
from kivy.effects.dampedscroll import DampedScrollEffect
from kivymd.uix.menu import MDDropdownMenu

from kivy.lang import Observable
import gettext
import l10n
import locale
from debug import logger

if platform != "android":
    from kivy.config import Config
    from kivy_garden.zbarcam import ZBarCam
    from pyzbar.pyzbar import ZBarSymbol

    Config.set("input", "mouse", "mouse, multitouch_on_demand")
elif platform == "android":
    from jnius import autoclass, cast
    from android.runnable import run_on_ui_thread
    from android import python_act as PythonActivity

    Toast = autoclass("android.widget.Toast")
    String = autoclass("java.lang.String")
    CharSequence = autoclass("java.lang.CharSequence")
    context = PythonActivity.mActivity

    @run_on_ui_thread
    def show_toast(text, length):
        """Its showing toast on screen"""
        t = Toast.makeText(context, text, length)
        t.show()

# pylint: disable=too-few-public-methods,too-many-arguments,attribute-defined-outside-init

KVFILES = [
    "settings",
    "popup",
    "allmails",
    "draft",
    "maildetail",
    "common_widgets",
    "addressbook",
    "myaddress",
    "composer",
    "payment",
    "sent",
    "network",
    "login",
    "credits",
    "trash",
    "inbox",
    "chat_room",
    "chat_list"
]

ThemeClsColor = [0.12, 0.58, 0.95, 1]


def toast(text):
    """Method will display the toast message"""
    # pylint: disable=redefined-outer-name
    from kivymd.toast.kivytoast import toast

    toast(text)
    return None


def showLimitedCnt(total_msg):
    """This method set the total count limit in badge_text"""
    return "99+" if total_msg > 99 else str(total_msg)


def ShowTimeHistoy(act_time):
    """This method is used to return the message sent or receive time"""
    action_time = datetime.fromtimestamp(int(act_time))
    crnt_date = datetime.now()
    duration = crnt_date - action_time
    display_data = (
        action_time.strftime("%d/%m/%Y")
        if duration.days >= 365
        else action_time.strftime("%I:%M %p").lstrip("0")
        if duration.days == 0 and crnt_date.strftime("%d/%m/%Y") == action_time.strftime("%d/%m/%Y")
        else action_time.strftime("%d %b")
    )
    return display_data


def AddTimeWidget(time):  # pylint: disable=redefined-outer-name
    """This method is used to create TimeWidget"""
    action_time = TimeTagRightSampleWidget(
        text=str(ShowTimeHistoy(time)),
        font_style="Caption",
        size=[120, 140] if platform == "android" else [64, 80],
    )
    action_time.font_size = "11sp"
    return action_time


def chipTag(text):
    """This method is used for showing chip tag"""
    obj = MDChip()
    # obj.size_hint = (None, None)
    obj.size_hint = (0.16 if platform == "android" else 0.07, None)
    obj.label = text
    obj.icon = ""
    obj.pos_hint = {
        "center_x": 0.91 if platform == "android" else 0.94,
        "center_y": 0.3
    }
    obj.height = dp(18)
    obj.radius = 8
    return obj


class Lang(Observable):
    observers = []
    lang = None

    def __init__(self, defaultlang):
        super(Lang, self).__init__()
        self.ugettext = None
        self.lang = defaultlang
        self.switch_lang(self.lang)

    def _(self, text):
        return self.ugettext(text)

    def fbind(self, name, func, args, **kwargs):
        if name == "_":
            self.observers.append((func, args, kwargs))
        else:
            return super(Lang, self).fbind(name, func, *largs, **kwargs)

    def funbind(self, name, func, args, **kwargs):
        if name == "_":
            key = (func, args, kwargs)
            if key in self.observers:
                self.observers.remove(key)
        else:
            return super(Lang, self).funbind(name, func, *args, **kwargs)

    def switch_lang(self, lang):
        # get the right locales directory, and instanciate a gettext
        locale_dir = os.path.join(os.path.dirname(__file__), 'translations', 'mo', 'locales')
        locales = gettext.translation('langapp', locale_dir, languages=[lang])
        self.ugettext = locales.gettext

        # update all the kv rules attached to this text
        for func, largs, kwargs in self.observers:
            func(largs, None, None)


class Inbox(Screen):
    """Inbox Screen class for kivy Ui"""

    queryreturn = ListProperty()
    has_refreshed = True
    account = StringProperty()

    def __init__(self, *args, **kwargs):
        """Method Parsing the address"""
        super(Inbox, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    @staticmethod
    def set_defaultAddress():
        """This method set's default address"""
        if state.association == "":
            if BMConfigParser().addresses():
                state.association = BMConfigParser().addresses()[0]

    def init_ui(self, dt=0):
        """Clock schdule for method inbox accounts"""
        self.loadMessagelist()

    def loadMessagelist(self, where="", what=""):
        """Load Inbox list for Inbox messages"""
        self.set_defaultAddress()
        self.account = state.association
        if state.searcing_text:
            # self.children[2].children[0].children[0].scroll_y = 1.0
            self.ids.scroll_y.scroll_y = 1.0
            where = ["subject", "message"]
            what = state.searcing_text
        xAddress = "toaddress"
        data = []
        self.ids.tag_label.text = ""
        self.inboxDataQuery(xAddress, where, what)
        self.ids.tag_label.text = ""
        if self.queryreturn:
            self.ids.tag_label.text = "Inbox"
            state.kivyapp.get_inbox_count()
            self.set_inboxCount(state.inbox_count)
            for mail in self.queryreturn:
                # third_text = mail[3].replace('\n', ' ')
                body = mail[3].decode() if isinstance(mail[3], bytes) else mail[3]
                subject = mail[5].decode() if isinstance(mail[5], bytes) else mail[5]
                data.append(
                    {
                        "text": mail[4].strip(),
                        "secondary_text": (
                            subject[:50] + "........"
                            if len(subject) >= 50
                            else (subject + "," + body)[0:50] + "........"
                        )
                        .replace("\t", "")
                        .replace("  ", ""),
                        "msgid": mail[1],
                        "received": mail[6]
                    }
                )

            self.has_refreshed = True
            self.set_mdList(data)
            self.ids.scroll_y.bind(scroll_y=self.check_scroll_y)
        else:
            self.set_inboxCount("0")
            content = MDLabel(
                font_style="Caption",
                theme_text_color="Primary",
                text="No message found!"
                if state.searcing_text
                else "yet no message for this account!!!!!!!!!!!!!",
                halign="center",
                size_hint_y=None,
                valign="top"
            )
            self.ids.ml.add_widget(content)

    def set_inboxCount(self, msgCnt):  # pylint: disable=no-self-use
        """This method is used to sent inbox message count"""
        src_mng_obj = state.kivyapp.root.ids.content_drawer.ids
        src_mng_obj.inbox_cnt.ids.badge_txt.text = showLimitedCnt(int(msgCnt))
        state.kivyapp.get_sent_count()
        state.all_count = str(
            int(state.sent_count) + int(state.inbox_count))
        src_mng_obj.allmail_cnt.ids.badge_txt.text = showLimitedCnt(int(state.all_count))

    def inboxDataQuery(self, xAddress, where, what, start_indx=0, end_indx=20):
        """This method is used for retrieving inbox data"""
        self.queryreturn = kivy_helper_search.search_sql(
            xAddress, self.account, "inbox", where, what, False, start_indx, end_indx
        )

    def set_mdList(self, data):
        """This method is used to create the mdList"""
        total_message = len(self.ids.ml.children)
        for item in data:
            meny = TwoLineAvatarIconListItem(
                text=item["text"],
                secondary_text=item["secondary_text"],
                theme_text_color="Custom",
                text_color=NavigateApp().theme_cls.primary_color
            )
            meny._txt_right_pad = dp(70)
            meny.add_widget(
                AvatarSampleWidget(
                    source=state.imageDir + "/text_images/{}.png".format(
                        avatarImageFirstLetter(item["secondary_text"].strip())
                    )
                )
            )
            meny.bind(on_press=partial(self.inbox_detail, item["msgid"]))
            meny.add_widget(AddTimeWidget(item["received"]))
            carousel = Carousel(direction="right")
            carousel.height = meny.height
            carousel.size_hint_y = None
            carousel.ignore_perpendicular_swipes = True
            carousel.data_index = 0
            carousel.min_move = 0.2
            del_btn = Button(text="Delete")
            del_btn.background_normal = ""
            del_btn.background_color = (1, 0, 0, 1)
            del_btn.bind(on_press=partial(self.delete, item["msgid"]))
            carousel.add_widget(del_btn)
            carousel.add_widget(meny)
            # ach_btn = Button(text='Achieve')
            # ach_btn.background_color = (0, 1, 0, 1)
            # ach_btn.bind(on_press=partial(self.archive, item['msgid']))
            # carousel.add_widget(ach_btn)
            carousel.index = 1
            self.ids.ml.add_widget(carousel)
        update_message = len(self.ids.ml.children)
        self.has_refreshed = True if total_message != update_message else False

    def check_scroll_y(self, instance, somethingelse):
        """Loads data on scroll"""
        if self.ids.scroll_y.scroll_y <= -0.0 and self.has_refreshed:
            self.ids.scroll_y.scroll_y = 0.06
            total_message = len(self.ids.ml.children)
            self.update_inbox_screen_on_scroll(total_message)

    def update_inbox_screen_on_scroll(self, total_message, where="", what=""):
        """This method is used to load more data on scroll down"""
        data = []
        if state.searcing_text:
            where = ["subject", "message"]
            what = state.searcing_text
        self.inboxDataQuery("toaddress", where, what, total_message, 5)
        for mail in self.queryreturn:
            # third_text = mail[3].replace('\n', ' ')
            subject = mail[3].decode() if isinstance(mail[3], bytes) else mail[3]
            body = mail[5].decode() if isinstance(mail[5], bytes) else mail[5]
            data.append(
                {
                    "text": mail[4].strip(),
                    "secondary_text": body[:50] + "........"
                    if len(body) >= 50
                    else (body + "," + subject.replace("\n", ""))[0:50] + "........",
                    "msgid": mail[1],
                    "received": mail[6]
                }
            )
        self.set_mdList(data)

    def inbox_detail(self, msg_id, *args):
        """Load inbox page details"""
        state.detailPageType = "inbox"
        state.mail_id = msg_id
        if self.manager:
            src_mng_obj = self.manager
        else:
            src_mng_obj = self.parent.parent
        src_mng_obj.screens[13].clear_widgets()
        src_mng_obj.screens[13].add_widget(MailDetail())
        src_mng_obj.current = "mailDetail"

    def delete(self, data_index, instance, *args):
        """Delete inbox mail from inbox listing"""
        sqlExecute("UPDATE inbox SET folder = 'trash' WHERE msgid = ?;", data_index)
        msg_count_objs = self.parent.parent.ids.content_drawer.ids
        if int(state.inbox_count) > 0:
            msg_count_objs.inbox_cnt.ids.badge_txt.text = showLimitedCnt(
                int(state.inbox_count) - 1
            )
            msg_count_objs.trash_cnt.ids.badge_txt.text = showLimitedCnt(
                int(state.trash_count) + 1
            )
            state.inbox_count = str(int(state.inbox_count) - 1)
            state.trash_count = str(int(state.trash_count) + 1)
            if int(state.all_count) > 0:
                msg_count_objs.allmail_cnt.ids.badge_txt.text = showLimitedCnt(
                    int(state.all_count) - 1
                )
                state.all_count = str(int(state.all_count) - 1)

            if int(state.inbox_count) <= 0:
                # self.ids.identi_tag.children[0].text = ''
                self.ids.tag_label.text = ''
        self.ids.ml.remove_widget(
            instance.parent.parent)
        toast('Deleted')
        self.update_trash()

    def archive(self, data_index, instance, *args):
        """Archive inbox mail from inbox listing"""
        sqlExecute("UPDATE inbox SET folder = 'trash' WHERE msgid = ?;", data_index)
        self.ids.ml.remove_widget(instance.parent.parent)
        self.update_trash()

    def update_trash(self):
        """Update trash screen mails which is deleted from inbox"""
        try:
            self.parent.screens[4].clear_widgets()
            self.parent.screens[4].add_widget(Trash())
        except Exception:
            self.parent.parent.screens[4].clear_widgets()
            self.parent.parent.screens[4].add_widget(Trash())

    def refresh_callback(self, *args):
        """Method updates the state of application,
        While the spinner remains on the screen"""

        def refresh_callback(interval):
            """Method used for loading the inbox screen data"""
            state.searcing_text = ""
            self.children[2].children[1].ids.search_field.text = ""
            self.ids.ml.clear_widgets()
            self.loadMessagelist(state.association)
            self.has_refreshed = True
            self.ids.refresh_layout.refresh_done()
            self.tick = 0

        Clock.schedule_once(refresh_callback, 1)


class CustomTwoLineAvatarIconListItem(TwoLineAvatarIconListItem):
    """CustomTwoLineAvatarIconListItem class for kivy Ui"""


class MyAddress(Screen):
    """MyAddress screen class for kivy Ui"""

    address_label = StringProperty()
    text_address = StringProperty()
    addresses_list = ListProperty()
    has_refreshed = True
    is_add_created = False

    def __init__(self, *args, **kwargs):
        """Clock schdule for method Myaddress accounts"""
        super(MyAddress, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock schdule for method Myaddress accounts"""
        # pylint: disable=unnecessary-lambda, deprecated-lambda
        # self.addresses_list = state.kivyapp.variable_1
        self.addresses_list = BMConfigParser().addresses()
        if state.searcing_text:
            self.ids.refresh_layout.scroll_y = 1.0
            filtered_list = [
                x for x in BMConfigParser().addresses()
                if self.filter_address(x)
            ]
            self.addresses_list = filtered_list
        self.addresses_list = [obj for obj in reversed(self.addresses_list)]
        self.ids.tag_label.text = ''
        if self.addresses_list:
            self.ids.tag_label.text = 'My Addresses'
            self.has_refreshed = True
            self.set_mdList(0, 15)
            self.ids.refresh_layout.bind(scroll_y=self.check_scroll_y)
        else:
            content = MDLabel(
                font_style='Caption',
                theme_text_color='Primary',
                text="No address found!" if state.searcing_text
                else "yet no address is created by user!!!!!!!!!!!!!",
                halign='center',
                size_hint_y=None,
                valign='top')
            self.ids.ml.add_widget(content)
            if not state.searcing_text and not self.is_add_created:
                try:
                    self.manager.current = 'login'
                except Exception:
                    pass

    def set_mdList(self, first_index, last_index):
        """Creating the mdlist"""
        data = []
        for address in self.addresses_list[first_index:last_index]:
            data.append({
                'text': BMConfigParser().get(address, 'label'),
                'secondary_text': address})
        for item in data:
            is_enable = BMConfigParser().get(item['secondary_text'], 'enabled')
            meny = CustomTwoLineAvatarIconListItem(
                text=item['text'], secondary_text=item['secondary_text'],
                theme_text_color='Custom' if is_enable == 'true' else 'Primary',
                text_color=ThemeClsColor,)
            meny._txt_right_pad = dp(70)
            try:
                meny.canvas.children[6].rgba = [0, 0, 0, 0] if is_enable == 'true' else [0.5, 0.5, 0.5, 0.5]
            except Exception:
                try:
                    meny.canvas.children[9].rgba = [0, 0, 0, 0] if is_enable == 'true' else [0.5, 0.5, 0.5, 0.5]
                except Exception as e:
                    print('Exception: ', e)
            meny.add_widget(AvatarSampleWidget(
                source=state.imageDir + '/text_images/{}.png'.format(
                    avatarImageFirstLetter(item['text'].strip()))))
            meny.bind(on_press=partial(
                self.myadd_detail, item['secondary_text'], item['text']))
            if state.association == item['secondary_text'] and is_enable == 'true':
                badge_obj = BadgeText(
                    size_hint=(None, None),
                    size=[90 if platform == 'android' else 50, 60],
                    text='Active', halign='center',
                    font_style='Body1', theme_text_color='Custom',
                    text_color=ThemeClsColor
                )
                badge_obj.font_size = '13sp'
                meny.add_widget(badge_obj)
            else:
                meny.add_widget(ToggleBtn(active=True if is_enable == 'true' else False))
            self.ids.ml.add_widget(meny)

    def check_scroll_y(self, instance, somethingelse):
        """Load data on scroll down"""
        if self.ids.refresh_layout.scroll_y <= -0.0 and self.has_refreshed:
            self.ids.refresh_layout.scroll_y = 0.06
            my_addresses = len(self.ids.ml.children)
            if my_addresses != len(self.addresses_list):
                self.update_addressBook_on_scroll(my_addresses)
            self.has_refreshed = (
                True if my_addresses != len(self.addresses_list) else False
            )

    def update_addressBook_on_scroll(self, my_addresses):
        """Loads more data on scroll down"""
        self.set_mdList(my_addresses, my_addresses + 20)

    # @staticmethod
    def myadd_detail(self, fromaddress, label, *args):
        """Load myaddresses details"""
        if BMConfigParser().get(fromaddress, 'enabled') == 'true':
            obj = MyaddDetailPopup()
            self.address_label = obj.address_label = label
            self.text_address = obj.address = fromaddress
            width = .9 if platform == 'android' else .8
            self.myadddetail_popup = MDDialog(
                type="custom",
                size_hint=(width, .25),
                content_cls=obj,
            )
            self.myadddetail_popup.set_normal_height()
            self.myadddetail_popup.auto_dismiss = False
            self.myadddetail_popup.open()
            # p.set_address(fromaddress, label)
        else:
            width = .8 if platform == 'android' else .55
            dialog_box = MDDialog(
                text='Address is not currently active. Please click on Toggle button to active it.',
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

    # @staticmethod
    # def callback_for_menu_items(text_item, *arg):
    #     """Callback of alert box"""
    #     toast(text_item)

    def refresh_callback(self, *args):
        """Method updates the state of application,
        While the spinner remains on the screen"""
        def refresh_callback(interval):
            """Method used for loading the myaddress screen data"""
            state.searcing_text = ''
            # state.kivyapp.root.ids.sc10.children[2].active = False
            self.ids.search_bar.ids.search_field.text = ''
            self.has_refreshed = True
            self.ids.ml.clear_widgets()
            self.init_ui()
            self.ids.refresh_layout.refresh_done()
            self.tick = 0
            Clock.schedule_once(self.address_permision_callback, 0)
        Clock.schedule_once(refresh_callback, 1)

    @staticmethod
    def filter_address(address):
        """Method will filter the my address list data"""
        if [
                x for x in [
                    BMConfigParser().get(address, 'label').lower(),
                    address.lower()
                ]
                if (state.searcing_text).lower() in x
        ]:
            return True
        return False

    def disableAddress(self, address, instance):
        """This method is use for disabling address"""
        BMConfigParser().set(str(address), 'enabled', 'false')
        BMConfigParser().save()
        instance.parent.parent.theme_text_color = 'Primary'
        try:
            instance.parent.parent.canvas.children[6].rgba = [0.5, 0.5, 0.5, 0.5]
        except Exception:
            instance.parent.parent.canvas.children[9].rgba = [0.5, 0.5, 0.5, 0.5]
        toast('Address disabled')
        Clock.schedule_once(self.address_permision_callback, 0)

    def enableAddress(self, address, instance):
        """This method is use for enabling address"""
        BMConfigParser().set(address, 'enabled', 'true')
        BMConfigParser().save()
        instance.parent.parent.theme_text_color = 'Custom'
        try:
            instance.parent.parent.canvas.children[6].rgba = [0, 0, 0, 0]
        except Exception:
            instance.parent.parent.canvas.children[9].rgba = [0, 0, 0, 0]
        toast('Address Enabled')
        Clock.schedule_once(self.address_permision_callback, 0)

    def address_permision_callback(self, dt=0):
        """callback for enable or disable addresses"""
        addresses = [addr for addr in BMConfigParser().addresses()
                     if BMConfigParser().get(str(addr), 'enabled') == 'true']
        self.parent.parent.ids.content_drawer.ids.btn.values = addresses
        self.parent.parent.ids.sc3.children[1].ids.btn.values = addresses

    def toggleAction(self, instance):
        """This method is used for enable or disable address"""
        addr = instance.parent.parent.secondary_text
        if instance.active:
            self.enableAddress(addr, instance)
        else:
            self.disableAddress(addr, instance)


class AddressBook(Screen):
    """AddressBook Screen class for kivy Ui"""

    queryreturn = ListProperty()
    has_refreshed = True
    address_label = StringProperty()
    address = StringProperty()

    def __init__(self, *args, **kwargs):
        """Getting AddressBook Details"""
        super(AddressBook, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method AddressBook"""
        self.loadAddresslist(None, 'All', '')
        print(dt)

    def loadAddresslist(self, account, where="", what=""):
        """Clock Schdule for method AddressBook"""
        if state.searcing_text:
            self.ids.scroll_y.scroll_y = 1.0
            where = ['label', 'address']
            what = state.searcing_text
        xAddress = ''
        self.ids.tag_label.text = ''
        self.queryreturn = kivy_helper_search.search_sql(
            xAddress, account, "addressbook", where, what, False)
        self.queryreturn = [obj for obj in reversed(self.queryreturn)]
        if self.queryreturn:
            self.ids.tag_label.text = 'Address Book'
            self.has_refreshed = True
            self.set_mdList(0, 20)
            self.ids.scroll_y.bind(scroll_y=self.check_scroll_y)
        else:
            content = MDLabel(
                font_style='Caption',
                theme_text_color='Primary',
                text="No contact found!" if state.searcing_text
                else "No contact found yet...... ",
                halign='center',
                size_hint_y=None,
                valign='top')
            self.ids.ml.add_widget(content)

    def set_mdList(self, start_index, end_index):
        """Creating the mdList"""
        for item in self.queryreturn[start_index:end_index]:
            meny = TwoLineAvatarIconListItem(
                text=item[0], secondary_text=item[1], theme_text_color='Custom',
                text_color=ThemeClsColor)
            meny.add_widget(AvatarSampleWidget(
                source=state.imageDir + '/text_images/{}.png'.format(
                    avatarImageFirstLetter(item[0].strip()))))
            meny.bind(on_press=partial(
                self.addBook_detail, item[1], item[0]))
            carousel = Carousel(direction='right')
            carousel.height = meny.height
            carousel.size_hint_y = None
            carousel.ignore_perpendicular_swipes = True
            carousel.data_index = 0
            carousel.min_move = 0.2
            del_btn = Button(text='Delete')
            del_btn.background_normal = ''
            del_btn.background_color = (1, 0, 0, 1)
            del_btn.bind(on_press=partial(self.delete_address, item[1]))
            carousel.add_widget(del_btn)
            carousel.add_widget(meny)
            carousel.index = 1
            self.ids.ml.add_widget(carousel)

    def check_scroll_y(self, instance, somethingelse):
        """Load data on scroll"""
        if self.ids.scroll_y.scroll_y <= -0.0 and self.has_refreshed:
            self.ids.scroll_y.scroll_y = 0.06
            exist_addresses = len(self.ids.ml.children)
            if exist_addresses != len(self.queryreturn):
                self.update_addressBook_on_scroll(exist_addresses)
            self.has_refreshed = (
                True if exist_addresses != len(self.queryreturn) else False
            )

    def update_addressBook_on_scroll(self, exist_addresses):
        """Load more data on scroll down"""
        self.set_mdList(exist_addresses, exist_addresses + 5)

    @staticmethod
    def refreshs(*args):
        """Refresh the Widget"""
        # state.navinstance.ids.sc11.ids.ml.clear_widgets()
        # state.navinstance.ids.sc11.loadAddresslist(None, 'All', '')

    # @staticmethod
    def addBook_detail(self, address, label, *args):
        """Addressbook details"""
        obj = AddbookDetailPopup()
        self.address_label = obj.address_label = label
        self.address = obj.address = address
        width = .9 if platform == 'android' else .8
        self.addbook_popup = MDDialog(
            type="custom",
            size_hint=(width, .25),
            content_cls=obj,
            buttons=[
                MDRaisedButton(
                    text="Send message to",
                    text_color=state.kivyapp.theme_cls.primary_color,
                    on_release=self.send_message_to,
                ),
                MDRaisedButton(
                    text="Save", text_color=state.kivyapp.theme_cls.primary_color,
                    on_release=self.update_addbook_label,
                ),
                MDRaisedButton(
                    text="Cancel", text_color=state.kivyapp.theme_cls.primary_color,
                    on_release=self.close_pop,
                ),
            ],
        )
        self.addbook_popup.set_normal_height()
        self.addbook_popup.auto_dismiss = False
        self.addbook_popup.open()

    def delete_address(self, address, instance, *args):
        """Delete inbox mail from inbox listing"""
        self.ids.ml.remove_widget(instance.parent.parent)
        # if len(self.ids.ml.children) == 0:
        if self.ids.ml.children is not None:
            self.ids.tag_label.text = ''
        sqlExecute(
            "DELETE FROM  addressbook WHERE address = '{}';".format(address))

    def close_pop(self, instance):
        """Pop is Canceled"""
        self.addbook_popup.dismiss()
        toast('Canceled')

    def update_addbook_label(self, instance):
        """Updating the label of address book address"""
        address_list = kivy_helper_search.search_sql(folder="addressbook")
        stored_labels = [labels[0] for labels in address_list]
        add_dict = dict(address_list)
        label = str(self.addbook_popup.content_cls.ids.add_label.text)
        if label in stored_labels and self.address == add_dict[label]:
            stored_labels.remove(label)
        if label and label not in stored_labels:
            sqlExecute(
                "UPDATE addressbook SET label = '{}' WHERE"
                " address = '{}';".format(
                    label, self.addbook_popup.content_cls.address))
            state.kivyapp.root.ids.sc11.ids.ml.clear_widgets()
            state.kivyapp.root.ids.sc11.loadAddresslist(None, 'All', '')
            self.addbook_popup.dismiss()
            toast('Saved')

    def send_message_to(self, instance):
        """Method used to fill to_address of composer autofield"""
        state.kivyapp.set_navbar_for_composer()
        window_obj = state.kivyapp.root.ids
        window_obj.sc3.children[1].ids.txt_input.text = self.address
        window_obj.sc3.children[1].ids.ti.text = ''
        window_obj.sc3.children[1].ids.btn.text = 'Select'
        window_obj.sc3.children[1].ids.subject.text = ''
        window_obj.sc3.children[1].ids.body.text = ''
        window_obj.scr_mngr.current = 'create'
        self.addbook_popup.dismiss()


class SelectableRecycleBoxLayout(
    FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout
):
    """Adds selection and focus behaviour to the view"""

    # pylint: disable = duplicate-bases


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


class RV(RecycleView):
    """Recycling View class for kivy Ui"""

    def __init__(self, **kwargs):
        """Recycling Method"""
        super(RV, self).__init__(**kwargs)


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
        encoding = 3
        print("message: ", self.ids.body.text)
        sendMessageToPeople = True
        if sendMessageToPeople:
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
                        self.parent.parent.screens[15].clear_widgets()
                        self.parent.parent.screens[15].add_widget(Draft())
                        # state.detailPageType = ''
                        # state.send_draft_mail = None
                    else:
                        from addresses import addBMIfNotPresent
                        toAddress = addBMIfNotPresent(toAddress)
                        statusIconColor = 'red'
                        if (addressVersionNumber > 4) or (
                                addressVersionNumber <= 1):
                            print(
                                "addressVersionNumber > 4"
                                " or addressVersionNumber <= 1")
                        if streamNumber > 1 or streamNumber == 0:
                            print("streamNumber > 1 or streamNumber == 0")
                        if statusIconColor == 'red':
                            print("shared.statusIconColor == 'red'")
                        stealthLevel = BMConfigParser().safeGetInt(
                            'bitmessagesettings', 'ackstealthlevel')
                        from helper_ackPayload import genAckPayload
                        ackdata = genAckPayload(streamNumber, stealthLevel)
                        # t = ()
                        sqlExecute(
                            '''INSERT INTO sent VALUES
                            (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                            '',
                            toAddress,
                            ripe,
                            fromAddress,
                            subject,
                            message,
                            ackdata,
                            int(time.time()),
                            int(time.time()),
                            0,
                            'msgqueued',
                            0,
                            'sent',
                            encoding,
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
                    queues.workerQueue.put(('sendmessage', toAddress))
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
    def callback_for_msgsend(dt=0):
        """Callback method for messagesend"""
        state.kivyapp.root.ids.sc3.children[0].active = False
        state.in_sent_method = True
        state.kivyapp.back_press()
        toast("sent")

    def address_error_message(self, msg):
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
        self.parent.parent.parent.ids.sc23.check_camera()
        is_available = self.parent.parent.parent.ids.sc23.camera_avaialbe
        return is_available

    def camera_alert(self):
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


class ScanScreen(Screen):
    camera_avaialbe = BooleanProperty(False)
    previous_open_screen = StringProperty()
    pop_up_instance = ObjectProperty()

    def __init__(self, *args, **kwargs):
        """Getting AddressBook Details"""
        super(ScanScreen, self).__init__(*args, **kwargs)
        self.check_camera()

    def check_camera(self):
        """This method is used for checking camera avaibility"""
        if platform != "android":
            import cv2
            cap = cv2.VideoCapture(0)
            while(cap.isOpened()):
                print('Camera is available!')
                self.camera_avaialbe = True
                break
            else:
                print("Camera is not available!")
                self.camera_avaialbe = False

    def get_screen(self, screen_name, instance=None):
        """This method is used for getting previous screen name"""
        self.previous_open_screen = screen_name
        if screen_name != 'composer':
            self.pop_up_instance = instance

    def on_pre_enter(self):
        """
       on_pre_enter works little better on android
       It affects screen transition on linux
       """
        if not self.children:
            tmp = Builder.load_file(
                os.path.join(os.path.dirname(__file__), "kv/{}.kv").format("scanner")
            )
            self.add_widget(tmp)
        if platform == "android":
            Clock.schedule_once(self.start_camera, 0)

    def on_enter(self):
        """
       on_enter works better on linux
       It creates a black screen on android until camera gets loaded
       """
        # print(self.children)
        if platform != "android":
            # pass
            Clock.schedule_once(self.start_camera, 0)

    def on_leave(self):
        # pass
        Clock.schedule_once(self.stop_camera, 0)

    def start_camera(self, *args):
        """Its used for starting camera for scanning qrcode"""
        self.xcam = self.children[0].ids.zbarcam.ids.xcamera
        if platform == "android":
            self.xcam.play = True

        else:
            Clock.schedule_once(self.open_cam, 0)

    def stop_camera(self, *args):
        """Its used for stop the camera"""
        self.xcam.play = False
        if platform != "android":
            self.xcam._camera._device.release()

    def open_cam(self, *args):
        """It will open up the camera"""
        if not self.xcam._camera._device.isOpened():
            self.xcam._camera._device.open(self.xcam._camera._index)
        self.xcam.play = True


class MyTextInput(TextInput):
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

    def on_text(self, instance, value):
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


class Payment(Screen):
    """Payment Screen class for kivy Ui"""

    def get_free_credits(self, instance):
        """Get the available credits"""
        # pylint: disable=no-self-use
        state.availabe_credit = instance.parent.children[1].text
        existing_credits = state.kivyapp.root.ids.sc18.ids.cred.text
        if float(existing_credits.split()[1]) > 0:
            toast(
                'We already have added free coins'
                ' for the subscription to your account!')
        else:
            toast('Coins added to your account!')
            state.kivyapp.root.ids.sc18.ids.cred.text = '{0}'.format(
                state.availabe_credit)

    def create_hidden_payment_address(self, instance):
        """This is basically used for creating hidden address used in payment for purchasing credits"""
        if BMConfigParser().paymentaddress():
            toast('hidden payment address already exist for buying subscription...')
        else:
            streamNumberForAddress = 1
            eighteenByteRipe = False
            nonceTrialsPerByte = 1000
            payloadLengthExtraBytes = 1000
            queues.addressGeneratorQueue.put((
                'createPaymentAddress', 4, streamNumberForAddress, '', 1,
                "", eighteenByteRipe, nonceTrialsPerByte,
                payloadLengthExtraBytes))
            toast('hidden payment address Creating for buying subscription....')


class Category(BoxLayout, RectangularElevationBehavior):
    """Category class for kivy Ui"""
    elevation_normal = .01


class ProductLayout(BoxLayout, RectangularElevationBehavior):
    """ProductLayout class for kivy Ui"""
    elevation_normal = .01


class PaymentMethodLayout(BoxLayout):
    """PaymentMethodLayout class for kivy Ui"""


class ListItemWithLabel(OneLineAvatarIconListItem):
    """ListItemWithLabel class for kivy Ui"""


class RightLabel(IRightBodyTouch, MDLabel):
    """RightLabel class for kivy Ui"""


class HomeScreen(Screen):
    """HomeScreen class for kivy Ui"""


class Credits(Screen):
    """Credits Screen class for kivy Ui"""

    available_credits = StringProperty('{0}'.format('€ 0'))


class Login(Screen):
    """Login Screeen class for kivy Ui"""
    log_text1 = (
        'You may generate addresses by using either random numbers'
        ' or by using a passphrase If you use a passphrase, the address'
        ' is called a deterministic; address The Random Number option is'
        ' selected by default but deterministic addresses have several pros'
        ' and cons:')
    log_text2 = ('If talk about pros You can recreate your addresses on any computer'
                 ' from memory, You need-not worry about backing up your keys.dat file'
                 ' as long as you can remember your passphrase and aside talk about cons'
                 ' You must remember (or write down) your  You must remember the address'
                 ' version number and the stream number along with your passphrase If you'
                 ' choose a weak passphrase and someone on the Internet can brute-force it,'
                 ' they can read your messages and send messages as you')


class NetworkStat(Screen):
    """NetworkStat class for kivy Ui"""

    text_variable_1 = StringProperty(
        '{0}::{1}'.format('Total Connections', '0'))
    text_variable_2 = StringProperty(
        'Processed {0} per-to-per messages'.format('0'))
    text_variable_3 = StringProperty(
        'Processed {0} brodcast messages'.format('0'))
    text_variable_4 = StringProperty(
        'Processed {0} public keys'.format('0'))
    text_variable_5 = StringProperty(
        'Processed {0} object to be synced'.format('0'))

    def __init__(self, *args, **kwargs):
        """Init method for network stat"""
        super(NetworkStat, self).__init__(*args, **kwargs)
        Clock.schedule_interval(self.init_ui, 1)

    def init_ui(self, dt=0):
        """Clock Schdule for method networkstat screen"""
        import network.stats
        from network import objectracker
        self.text_variable_1 = '{0} :: {1}'.format(
            'Total Connections', str(len(network.stats.connectedHostsList())))
        self.text_variable_2 = 'Processed {0} per-to-per messages'.format(
            str(state.numberOfMessagesProcessed))
        self.text_variable_3 = 'Processed {0} brodcast messages'.format(
            str(state.numberOfBroadcastsProcessed))
        self.text_variable_4 = 'Processed {0} public keys'.format(
            str(state.numberOfPubkeysProcessed))
        self.text_variable_5 = '{0} object to be synced'.format(
            len(objectracker.missingObjects))


class ContentNavigationDrawer(BoxLayout):
    """ContentNavigationDrawer class for kivy Uir"""

    def __init__(self, *args, **kwargs):
        """Method used for contentNavigationDrawer"""
        super(ContentNavigationDrawer, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for class contentNavigationDrawer"""
        self.ids.scroll_y.bind(scroll_y=self.check_scroll_y)

    def check_scroll_y(self, instance, somethingelse):
        """show data on scroll down"""
        if self.ids.btn.is_open:
            self.ids.btn.is_open = False


class Random(Screen):
    """Random Screen class for Ui"""

    is_active = BooleanProperty(False)
    checked = StringProperty("")

    def generateaddress(self, navApp):
        """Method for Address Generator"""
        # entered_label = str(self.ids.lab.text).strip()
        entered_label = str(self.ids.add_random_bx.children[0].ids.lab.text).strip()
        if not entered_label:
            self.ids.add_random_bx.children[0].ids.lab.focus = True
        streamNumberForAddress = 1
        eighteenByteRipe = False
        nonceTrialsPerByte = 1000
        payloadLengthExtraBytes = 1000
        lables = [BMConfigParser().get(obj, 'label')
                  for obj in BMConfigParser().addresses()]
        if entered_label and entered_label not in lables:
            toast('Address Creating...')
            queues.addressGeneratorQueue.put((
                'createRandomAddress', 4, streamNumberForAddress, entered_label, 1,
                "", eighteenByteRipe, nonceTrialsPerByte,
                payloadLengthExtraBytes))
            self.parent.parent.ids.toolbar.opacity = 1
            self.parent.parent.ids.toolbar.disabled = False
            state.kivyapp.loadMyAddressScreen(True)
            self.manager.current = 'myaddress'
            Clock.schedule_once(self.address_created_callback, 6)

    def address_created_callback(self, dt=0):
        """New address created"""
        state.kivyapp.loadMyAddressScreen(False)
        state.kivyapp.root.ids.sc10.ids.ml.clear_widgets()
        state.kivyapp.root.ids.sc10.is_add_created = True
        state.kivyapp.root.ids.sc10.init_ui()
        self.reset_address_spinner()
        toast('New address created')

    def reset_address_spinner(self):
        """reseting spinner address and UI"""
        addresses = [addr for addr in BMConfigParser().addresses()
                     if BMConfigParser().get(str(addr), 'enabled') == 'true']
        self.manager.parent.ids.content_drawer.ids.btn.values = []
        self.manager.parent.ids.sc3.children[1].ids.btn.values = []
        self.manager.parent.ids.content_drawer.ids.btn.values = addresses
        self.manager.parent.ids.sc3.children[1].ids.btn.values = addresses

    @staticmethod
    def add_validation(instance):
        """Checking validation at address creation time"""
        entered_label = str(instance.text.strip())
        lables = [BMConfigParser().get(obj, 'label')
                  for obj in BMConfigParser().addresses()]
        if entered_label in lables:
            instance.error = True
            instance.helper_text = 'it is already exist you'\
                ' can try this Ex. ( {0}_1, {0}_2 )'.format(
                    entered_label)
        elif entered_label:
            instance.error = False
        else:
            instance.error = False
            instance.helper_text = 'This field is required'

    def reset_address_label(self, n):
        """Resetting address labels"""
        if not self.ids.add_random_bx.children:
            self.ids.add_random_bx.add_widget(RandomBoxlayout())


class Sent(Screen):
    """Sent Screen class for kivy Ui"""

    queryreturn = ListProperty()
    has_refreshed = True
    account = StringProperty()

    def __init__(self, *args, **kwargs):
        """Association with the screen"""
        super(Sent, self).__init__(*args, **kwargs)
        if state.association == '':
            if BMConfigParser().addresses():
                state.association = BMConfigParser().addresses()[0]
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method sent accounts"""
        self.loadSent()
        print(dt)

    def loadSent(self, where="", what=""):
        """Load Sent list for Sent messages"""
        self.account = state.association
        if state.searcing_text:
            self.ids.scroll_y.scroll_y = 1.0
            where = ['subject', 'message']
            what = state.searcing_text
        xAddress = 'fromaddress'
        data = []
        self.ids.tag_label.text = ''
        self.sentDataQuery(xAddress, where, what)
        if self.queryreturn:
            self.ids.tag_label.text = 'Sent'
            self.set_sentCount(state.sent_count)
            for mail in self.queryreturn:
                data.append({
                    'text': mail[1].strip(),
                    'secondary_text': (mail[2][:50] + '........' if len(
                        mail[2]) >= 50 else (mail[2] + ',' + mail[3])[0:50] + '........').replace(
                            '\t', '').replace('  ', ''),
                    'ackdata': mail[5], 'senttime': mail[6]},)
            self.set_mdlist(data, 0)
            self.has_refreshed = True
            self.ids.scroll_y.bind(scroll_y=self.check_scroll_y)
        else:
            self.set_sentCount('0')
            content = MDLabel(
                font_style='Caption',
                theme_text_color='Primary',
                text="No message found!" if state.searcing_text
                else "yet no message for this account!!!!!!!!!!!!!",
                halign='center',
                size_hint_y=None,
                valign='top')
            self.ids.ml.add_widget(content)

    def sentDataQuery(self, xAddress, where, what, start_indx=0, end_indx=20):
        """This method is used to retrieving data from sent table"""
        self.queryreturn = kivy_helper_search.search_sql(
            xAddress,
            self.account,
            'sent',
            where,
            what,
            False,
            start_indx,
            end_indx)

    def set_mdlist(self, data, set_index=0):
        """This method is used to create the mdList"""
        total_sent_msg = len(self.ids.ml.children)
        for item in data:
            meny = TwoLineAvatarIconListItem(
                text=item['text'], secondary_text=item['secondary_text'],
                theme_text_color='Custom',
                text_color=ThemeClsColor)
            meny._txt_right_pad = dp(70)
            meny.add_widget(AvatarSampleWidget(
                source=state.imageDir + '/text_images/{}.png'.format(
                    avatarImageFirstLetter(item['secondary_text'].strip()))))
            meny.bind(on_press=partial(self.sent_detail, item['ackdata']))
            meny.add_widget(AddTimeWidget(item['senttime']))
            carousel = Carousel(direction='right')
            carousel.height = meny.height
            carousel.size_hint_y = None
            carousel.ignore_perpendicular_swipes = True
            carousel.data_index = 0
            carousel.min_move = 0.2
            del_btn = Button(text='Delete')
            del_btn.background_normal = ''
            del_btn.background_color = (1, 0, 0, 1)
            del_btn.bind(on_press=partial(self.delete, item['ackdata']))
            carousel.add_widget(del_btn)
            carousel.add_widget(meny)
            # ach_btn = Button(text='Achieve')
            # ach_btn.background_color = (0, 1, 0, 1)
            # ach_btn.bind(on_press=partial(self.archive, item['ackdata']))
            # carousel.add_widget(ach_btn)
            carousel.index = 1
            self.ids.ml.add_widget(carousel, index=set_index)
        updated_msgs = len(self.ids.ml.children)
        self.has_refreshed = True if total_sent_msg != updated_msgs else False

    def update_sent_messagelist(self):
        """This method is used to update screen when new mail is sent"""
        self.account = state.association
        if len(self.ids.ml.children) < 3:
            self.ids.ml.clear_widgets()
            self.loadSent()
            if state.association == state.check_sent_acc:
                total_sent = int(state.sent_count) + 1
                state.sent_count = str(int(state.sent_count) + 1)
                self.set_sentCount(total_sent)
            else:
                total_sent = int(state.sent_count)
        else:
            data = []
            self.sentDataQuery('fromaddress', '', '', 0, 1)
            if state.association == state.check_sent_acc:
                total_sent = int(state.sent_count) + 1
                state.sent_count = str(int(state.sent_count) + 1)
                self.set_sentCount(total_sent)
            else:
                total_sent = int(state.sent_count)
            for mail in self.queryreturn:
                data.append({
                    'text': mail[1].strip(),
                    'secondary_text': (mail[2][:50] + '........' if len(
                        mail[2]) >= 50 else (mail[2] + ',' + mail[3])[0:50] + '........').replace(
                            '\t', '').replace('  ', ''),
                    'ackdata': mail[5], 'senttime': mail[6]})
            self.set_mdlist(data, total_sent - 1)
        if state.msg_counter_objs and state.association == (
                state.check_sent_acc):
            state.all_count = str(int(state.all_count) + 1)
            state.msg_counter_objs.allmail_cnt.badge_text = state.all_count
            state.check_sent_acc = None

    def check_scroll_y(self, instance, somethingelse):
        """Load data on scroll down"""
        if self.ids.scroll_y.scroll_y <= -0.0 and self.has_refreshed:
            self.ids.scroll_y.scroll_y = 0.06
            total_sent_msg = len(self.ids.ml.children)
            self.update_sent_screen_on_scroll(total_sent_msg)

    def update_sent_screen_on_scroll(self, total_sent_msg, where="", what=""):
        """This method is used to load more data on scroll down"""
        if state.searcing_text:
            where = ['subject', 'message']
            what = state.searcing_text
        self.sentDataQuery('fromaddress', where, what, total_sent_msg, 5)
        data = []
        for mail in self.queryreturn:
            data.append({
                'text': mail[1].strip(),
                'secondary_text': mail[2][:50] + '........' if len(
                    mail[2]) >= 50 else (mail[2] + ',' + mail[3].replace(
                        '\n', ''))[0:50] + '........',
                'ackdata': mail[5], 'senttime': mail[6]})
        self.set_mdlist(data, 0)

    @staticmethod
    def set_sentCount(total_sent):
        """Set the total no. of sent message count"""
        src_mng_obj = state.kivyapp.root.ids.content_drawer.ids.send_cnt
        state.kivyapp.root.ids.content_drawer.ids.send_cnt.ids.badge_txt.text
        if state.association:
            src_mng_obj.ids.badge_txt.text = showLimitedCnt(int(total_sent))
        else:
            src_mng_obj.ids.badge_txt.text = '0'

    def sent_detail(self, ackdata, *args):
        """Load sent mail details"""
        state.detailPageType = 'sent'
        state.mail_id = ackdata
        if self.manager:
            src_mng_obj = self.manager
        else:
            src_mng_obj = self.parent.parent
        src_mng_obj.screens[13].clear_widgets()
        src_mng_obj.screens[13].add_widget(MailDetail())
        src_mng_obj.current = 'mailDetail'

    def delete(self, data_index, instance, *args):
        """Delete sent mail from sent mail listing"""
        msg_count_objs = self.parent.parent.ids.content_drawer.ids
        if int(state.sent_count) > 0:
            msg_count_objs.send_cnt.ids.badge_txt.text = showLimitedCnt(int(state.sent_count) - 1)
            msg_count_objs.trash_cnt.ids.badge_txt.text = showLimitedCnt(int(state.trash_count) + 1)
            msg_count_objs.allmail_cnt.ids.badge_txt.text = showLimitedCnt(int(state.all_count) - 1)
            state.sent_count = str(int(state.sent_count) - 1)
            state.trash_count = str(int(state.trash_count) + 1)
            state.all_count = str(int(state.all_count) - 1)
            if int(state.sent_count) <= 0:
                self.ids.tag_label.text = ''
        sqlExecute(
            "UPDATE sent SET folder = 'trash'"
            " WHERE ackdata = ?;", data_index)
        self.ids.ml.remove_widget(instance.parent.parent)
        toast('Deleted')
        self.update_trash()

    def archive(self, data_index, instance, *args):
        """Archive sent mail from sent mail listing"""
        sqlExecute(
            "UPDATE sent SET folder = 'trash'"
            " WHERE ackdata = ?;", data_index)
        self.ids.ml.remove_widget(instance.parent.parent)
        self.update_trash()

    def update_trash(self):
        """Update trash screen mails which is deleted from inbox"""
        try:
            self.parent.screens[4].clear_widgets()
            self.parent.screens[4].add_widget(Trash())
            self.parent.screens[16].clear_widgets()
            self.parent.screens[16].add_widget(Allmails())
        except Exception:
            self.parent.parent.screens[4].clear_widgets()
            self.parent.parent.screens[4].add_widget(Trash())
            self.parent.parent.screens[16].clear_widgets()
            self.parent.parent.screens[16].add_widget(Allmails())


class Trash(Screen):
    """Trash Screen class for kivy Ui"""

    trash_messages = ListProperty()
    has_refreshed = True
    # delete_index = StringProperty()
    table_name = StringProperty()

    def __init__(self, *args, **kwargs):
        """Trash method, delete sent message and add in Trash"""
        super(Trash, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method trash screen"""
        if state.association == '':
            if BMConfigParser().addresses():
                state.association = BMConfigParser().addresses()[0]
        self.ids.tag_label.text = ''
        self.trashDataQuery(0, 20)
        if self.trash_messages:
            self.ids.tag_label.text = 'Trash'
            # src_mng_obj = state.kivyapp.root.children[2].children[0].ids
            # src_mng_obj.trash_cnt.badge_text = state.trash_count
            self.set_TrashCnt(state.trash_count)
            self.set_mdList()
            self.ids.scroll_y.bind(scroll_y=self.check_scroll_y)
        else:
            self.set_TrashCnt('0')
            content = MDLabel(
                font_style='Caption',
                theme_text_color='Primary',
                text="yet no trashed message for this account!!!!!!!!!!!!!",
                halign='center',
                size_hint_y=None,
                valign='top')
            self.ids.ml.add_widget(content)

    def trashDataQuery(self, start_indx, end_indx):
        """Trash message query"""
        self.trash_messages = sqlQuery(
            "SELECT toaddress, fromaddress, subject, message,"
            " folder ||',' || 'sent' as  folder, ackdata As"
            " id, DATE(senttime) As actionTime, senttime as msgtime FROM sent"
            " WHERE folder = 'trash'  and fromaddress = '{0}' UNION"
            " SELECT toaddress, fromaddress, subject, message,"
            " folder ||',' || 'inbox' as  folder, msgid As id,"
            " DATE(received) As actionTime, received as msgtime FROM inbox"
            " WHERE folder = 'trash' and toaddress = '{0}'"
            " ORDER BY actionTime DESC limit {1}, {2}".format(
                state.association, start_indx, end_indx))

    def set_TrashCnt(self, Count):  # pylint: disable=no-self-use
        """This method is used to set trash message count"""
        trashCnt_obj = state.kivyapp.root.ids.content_drawer.ids.trash_cnt
        trashCnt_obj.ids.badge_txt.text = showLimitedCnt(int(Count))

    def set_mdList(self):
        """This method is used to create the mdlist"""
        total_trash_msg = len(self.ids.ml.children)
        for item in self.trash_messages:
            subject = item[2].decode() if isinstance(item[2], bytes) else item[2]
            body = item[3].decode() if isinstance(item[3], bytes) else item[3]
            meny = TwoLineAvatarIconListItem(
                text=item[1],
                secondary_text=(item[2][:50] + '........' if len(
                    subject) >= 50 else (subject + ',' + body)[0:50] + '........').replace('\t', '').replace('  ', ''),
                theme_text_color='Custom',
                text_color=ThemeClsColor)
            meny._txt_right_pad = dp(70)
            img_latter = state.imageDir + '/text_images/{}.png'.format(
                subject[0].upper() if (subject[0].upper() >= 'A' and subject[0].upper() <= 'Z') else '!')
            meny.add_widget(AvatarSampleWidget(source=img_latter))
            meny.add_widget(AddTimeWidget(item[7]))
            meny.add_widget(chipTag('inbox 'if 'inbox' in item[4] else 'sent'))
            carousel = Carousel(direction='right')
            carousel.height = meny.height
            carousel.size_hint_y = None
            carousel.ignore_perpendicular_swipes = True
            carousel.data_index = 0
            carousel.min_move = 0.2
            del_btn = Button(text='Delete')
            del_btn.background_normal = ''
            del_btn.background_color = (1, 0, 0, 1)
            del_btn.bind(on_press=partial(
                self.delete_permanently, item[5], item[4]))
            carousel.add_widget(del_btn)
            carousel.add_widget(meny)
            carousel.index = 1
            self.ids.ml.add_widget(carousel)
        self.has_refreshed = True if total_trash_msg != len(
            self.ids.ml.children) else False

    def check_scroll_y(self, instance, somethingelse):
        """Load data on scroll"""
        if self.ids.scroll_y.scroll_y <= -0.0 and self.has_refreshed:
            self.ids.scroll_y.scroll_y = 0.06
            total_trash_msg = len(self.ids.ml.children)
            self.update_trash_screen_on_scroll(total_trash_msg)

    def update_trash_screen_on_scroll(self, total_trash_msg):
        """Load more data on scroll down"""
        self.trashDataQuery(total_trash_msg, 5)
        self.set_mdList()

    def delete_permanently(self, data_index, folder, instance, *args):
        """Deleting trash mail permanently"""
        self.table_name = folder.split(',')[1]
        self.delete_index = data_index
        self.delete_confirmation()

    def callback_for_screen_load(self, dt=0):
        """This methos is for loading screen"""
        self.ids.ml.clear_widgets()
        self.init_ui(0)
        self.children[1].active = False
        toast('Message is permanently deleted')

    def delete_confirmation(self):
        """Show confirmation delete popup"""
        width = .8 if platform == 'android' else .55
        dialog_box = MDDialog(
            text='Are you sure you want to delete this'
            ' message permanently from trash?',
            size_hint=(width, .25),
            buttons=[
                MDFlatButton(
                    text="Yes", on_release=lambda x: callback_for_delete_msg("Yes")
                ),
                MDFlatButton(
                    text="No", on_release=lambda x: callback_for_delete_msg("No"),
                ),
            ],)
        dialog_box.open()

        def callback_for_delete_msg(text_item, *arg):
            """Getting the callback of alert box"""
            if text_item == 'Yes':
                self.delete_message_from_trash()
            else:
                toast(text_item)
            dialog_box.dismiss()

    # def callback_for_delete_msg(self, text_item, *arg):
    #     """Getting the callback of alert box"""
    #     if text_item == 'Yes':
    #         self.delete_message_from_trash()
    #     else:
    #         toast(text_item)

    def delete_message_from_trash(self):
        """Deleting message from trash"""
        self.children[1].active = True
        if self.table_name == 'inbox':
            sqlExecute(
                "DELETE FROM inbox WHERE msgid = ?;", self.delete_index)
        elif self.table_name == 'sent':
            sqlExecute(
                "DELETE FROM sent WHERE ackdata = ?;", self.delete_index)
        if int(state.trash_count) > 0:
            # msg_count_objs.trash_cnt.badge_text = str(
            #     int(state.trash_count) - 1)
            self.set_TrashCnt(int(state.trash_count) - 1)
            state.trash_count = str(int(state.trash_count) - 1)
            Clock.schedule_once(self.callback_for_screen_load, 1)


class Page(Screen):
    """Page Screen class for kivy Ui"""


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

    def check_scroll_y(self, instance, somethingelse):
        """show data on scroll down"""
        if self.children[1].ids.btn.is_open:
            self.children[1].ids.btn.is_open = False


class Setting(Screen):
    """Setting Screen for kivy Ui"""
    exp_text = "By default, if you send a message to someone and he is offline for more than two days, Bitmessage will\
                send the message again after an additional two days. This will be continued with exponential backoff\
                forever; messages will be resent after 5, 10, 20 days ect. until the receiver acknowledges them.\
                Here you may change that behavior by having Bitmessage give up after a certain number of days \
                or months."

    languages = {
        'ar': 'Arabic',
        'cs': 'Czech',
        'da': 'Danish',
        'de': 'German',
        'en': 'English',
        'eo': 'Esperanto',
        'fr': 'French',
        'it': 'Italian',
        'ja': 'Japanese',
        'nl': 'Dutch',
        'no': 'Norwegian',
        'pl': 'Polish',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'sk': 'Slovak',
        'zh': 'Chinese',
    }
    newlocale = None

    def __init__(self, *args, **kwargs):
        """Trash method, delete sent message and add in Trash"""
        super(Setting, self).__init__(*args, **kwargs)
        if self.newlocale is None:
            self.newlocale = l10n.getTranslationLanguage()
        lang = locale.normalize(l10n.getTranslationLanguage())
        langs = [
            lang.split(".")[0] + "." + l10n.encoding,
            lang.split(".")[0] + "." + 'UTF-8',
            lang
        ]
        if 'win32' in platform or 'win64' in platform:
            langs = [l10n.getWindowsLocale(lang)]
        for lang in langs:
            try:
                l10n.setlocale(locale.LC_ALL, lang)
                if 'win32' not in platform and 'win64' not in platform:
                    l10n.encoding = locale.nl_langinfo(locale.CODESET)
                else:
                    l10n.encoding = locale.getlocale()[1]
                logger.info("Successfully set locale to %s", lang)
                break
            except:
                logger.error("Failed to set locale to %s", lang, exc_info=True)

        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Initialization for Ui"""
        if self.newlocale is None:
            self.newlocale = l10n.getTranslationLanguage()
        # state.kivyapp.tr = Lang(self.newlocale)
        state.kivyapp.tr = Lang(self.newlocale)
        menu_items = [{"text": f"{i}"} for i in self.languages.values()]
        self.menu = MDDropdownMenu(
            caller=self,
            items=menu_items,
            position="auto",
            callback=self.set_item,
            width_mult=3.5,
            # use_icon_item=False,
        )

    def set_caller(self):
        """set_caller module"""
        self.menu.caller = self.ids.drop_item
        self.menu.target_height = 150

    def set_item(self, instance):
        """set_item module for menu selection"""
        self.ids.drop_item.set_item(instance.text)
        self.menu.dismiss()

    def change_language(self):
        lang = self.ids.drop_item.current_item
        for k, v in self.languages.items():
            if v == lang:
                BMConfigParser().set('bitmessagesettings', 'userlocale', k)
                BMConfigParser().save()
                state.kivyapp.tr = Lang(k)
                self.children[0].active = True
                Clock.schedule_once(partial(self.language_callback, k), 1)

    def language_callback(self, lang, dt=0):
        self.children[0].active = False
        state.kivyapp.tr = Lang(lang)
        toast('Language changed')


class NavigateApp(MDApp):
    """Navigation Layout of class"""
    # pylint: disable=too-many-public-methods,inconsistent-return-statements

    # theme_cls = ThemeManager()
    previous_date = ObjectProperty()
    obj_1 = ObjectProperty()
    variable_1 = ListProperty(addr for addr in BMConfigParser().addresses()
                              if BMConfigParser().get(str(addr), 'enabled') == 'true')
    nav_drawer = ObjectProperty()
    state.screen_density = Window.size
    window_size = state.screen_density
    app_platform = platform
    title = "PyBitmessage"
    imgstatus = False
    count = 0
    manager_open = False
    file_manager = None
    state.imageDir = os.path.join('./images', 'kivy')
    image_path = state.imageDir
    tr = Lang("en")  # for changing in franch replace en with fr

    def build(self):
        """Method builds the widget"""
        for kv_file in KVFILES:
            Builder.load_file(os.path.join(os.path.dirname(__file__), "kv/{}.kv").format(kv_file))
        self.obj_1 = AddressBook()
        kivysignalthread = UIkivySignaler()
        kivysignalthread.daemon = True
        kivysignalthread.start()
        Window.bind(on_keyboard=self.on_key, on_request_close=self.on_request_close)
        return Builder.load_file(
            os.path.join(os.path.dirname(__file__), 'main.kv'))

    def run(self):
        """Running the widgets"""
        kivyuisignaler.release()
        super(NavigateApp, self).run()

    @staticmethod
    def showmeaddresses(name="text"):
        """Show the addresses in spinner to make as dropdown"""
        if name == "text":
            if BMConfigParser().addresses():
                return BMConfigParser().addresses()[0][:16] + '..'
            return "textdemo"
        elif name == "values":
            if BMConfigParser().addresses():
                return [address[:16] + '..'
                        for address in BMConfigParser().addresses()]
            return "valuesdemo"

    def getCurrentAccountData(self, text):
        """Get Current Address Account Data"""
        if text != '':
            if os.path.exists(state.imageDir + '/default_identicon/{}.png'.format(text)):
                self.load_selected_Image(text)
            else:
                self.set_identicon(text)
                self.root.ids.content_drawer.ids.reset_image.opacity = 0
                self.root.ids.content_drawer.ids.reset_image.disabled = True
            address_label = self.current_address_label(
                BMConfigParser().get(text, 'label'), text)
            self.root_window.children[1].ids.toolbar.title = address_label
            state.association = text
            state.searcing_text = ''
            LoadingPopup().open()
            self.set_message_count()
            for nav_obj in self.root.ids.content_drawer.children[
                    0].children[0].children[0].children:
                nav_obj.active = True if nav_obj.text == 'Inbox' else False
            self.fileManagerSetting()
            Clock.schedule_once(self.setCurrentAccountData, 0.5)

    def fileManagerSetting(self):
        """This method is for file manager setting"""
        if not self.root.ids.content_drawer.ids.file_manager.opacity and \
                self.root.ids.content_drawer.ids.file_manager.disabled:
            self.root.ids.content_drawer.ids.file_manager.opacity = 1
            self.root.ids.content_drawer.ids.file_manager.disabled = False

    def setCurrentAccountData(self, dt=0):
        """This method set the current accout data on all the screens"""
        self.root.ids.sc1.ids.ml.clear_widgets()
        self.root.ids.sc1.loadMessagelist(state.association)

        self.root.ids.sc4.ids.ml.clear_widgets()
        self.root.ids.sc4.children[2].children[2].ids.search_field.text = ''
        self.root.ids.sc4.loadSent(state.association)

        self.root.ids.sc16.clear_widgets()
        self.root.ids.sc16.add_widget(Draft())

        self.root.ids.sc5.clear_widgets()
        self.root.ids.sc5.add_widget(Trash())

        self.root.ids.sc17.clear_widgets()
        self.root.ids.sc17.add_widget(Allmails())

        self.root.ids.sc10.ids.ml.clear_widgets()
        self.root.ids.sc10.init_ui()

        self.root.ids.scr_mngr.current = 'inbox'

    @staticmethod
    def getCurrentAccount():
        """It uses to get current account label"""
        if state.association:
            return state.association
        return "Bitmessage Login"

    # @staticmethod
    def addingtoaddressbook(self):
        """Adding to address Book"""
        width = .85 if platform == 'android' else .8
        self.add_popup = MDDialog(
            title='add contact\'s',
            type="custom",
            size_hint=(width, .25),
            content_cls=GrashofPopup(),
            buttons=[
                MDRaisedButton(
                    text="Save",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.savecontact,
                ),
                MDRaisedButton(
                    text="Cancel", text_color=self.theme_cls.primary_color,
                    on_release=self.close_pop,
                ),
                MDRaisedButton(
                    text="Scan QR code", text_color=self.theme_cls.primary_color,
                    on_release=self.scan_qr_code,
                ),
            ],
        )
        self.add_popup.set_normal_height()
        self.add_popup.auto_dismiss = False
        self.add_popup.open()
        # p = GrashofPopup()
        # p.open()

    def scan_qr_code(self, instance):
        """this method is used for showing QR code scanner"""
        if self.is_camara_attached():
            self.add_popup.dismiss()
            self.root.ids.sc23.get_screen(self.root.ids.scr_mngr.current, self.add_popup)
            self.root.ids.scr_mngr.current = 'scanscreen'
        else:
            altet_txt = (
                'Currently this feature is not avaialbe!' if platform == 'android' else 'Camera is not available!')
            self.add_popup.dismiss()
            toast(altet_txt)

    def is_camara_attached(self):
        """This method is for checking is camera available or not"""
        self.root.ids.sc23.check_camera()
        is_available = self.root.ids.sc23.camera_avaialbe
        return is_available

    def savecontact(self, instance):
        """Method is used for saving contacts"""
        pupup_obj = self.add_popup.content_cls
        label = pupup_obj.ids.label.text.strip()
        address = pupup_obj.ids.address.text.strip()
        if label == '' and address == '':
            pupup_obj.ids.label.focus = True
            pupup_obj.ids.address.focus = True
        elif address == '':
            pupup_obj.ids.address.focus = True
        elif label == '':
            pupup_obj.ids.label.focus = True
        else:
            pupup_obj.ids.address.focus = True
            # pupup_obj.ids.label.focus = True

        stored_address = [addr[1] for addr in kivy_helper_search.search_sql(
            folder="addressbook")]
        stored_labels = [labels[0] for labels in kivy_helper_search.search_sql(
            folder="addressbook")]
        if label and address and address not in stored_address \
                and label not in stored_labels and pupup_obj.valid:
            # state.navinstance = self.parent.children[1]
            queues.UISignalQueue.put(('rerenderAddressBook', ''))
            self.add_popup.dismiss()
            sqlExecute("INSERT INTO addressbook VALUES(?,?)", label, address)
            self.root.ids.sc11.ids.ml.clear_widgets()
            self.root.ids.sc11.loadAddresslist(None, 'All', '')
            self.root.ids.scr_mngr.current = 'addressbook'
            toast('Saved')

    def close_pop(self, instance):
        """Pop is Canceled"""
        self.add_popup.dismiss()
        toast('Canceled')

    def getDefaultAccData(self, instance):
        """Getting Default Account Data"""
        if BMConfigParser().addresses():
            first_addr = BMConfigParser().addresses()[0]
            if BMConfigParser().get(str(first_addr), 'enabled') == 'true':
                img = identiconGeneration.generate(first_addr)
                # self.createFolder(state.imageDir + '/default_identicon/')
                # if platform == 'android':
                #     # android_path = os.path.expanduser
                #     # ("~/user/0/org.test.bitapp/files/app/")
                #     if not os.path.exists(state.imageDir + '/default_identicon/{}.png'.format(
                #             BMConfigParser().addresses()[0])):
                #         android_path = os.path.join(
                #             os.environ['ANDROID_PRIVATE'] + '/app/')
                #         img.texture.save('{1}/images/kivy/default_identicon/{0}.png'.format(
                #             BMConfigParser().addresses()[0], android_path))
                # else:
                #     if not os.path.exists(state.imageDir + '/default_identicon/{}.png'.format(
                #             BMConfigParser().addresses()[0])):
                #         img.texture.save(state.imageDir + '/default_identicon/{}.png'.format(
                #             BMConfigParser().addresses()[0]))
                instance.parent.parent.parent.parent.parent.ids.top_box.children[0].texture = (
                    img.texture)
                return first_addr
        return 'Select Address'

    @staticmethod
    def createFolder(directory):
        """Create directory when app starts"""
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            print('Error: Creating directory. ' + directory)

    @staticmethod
    def get_default_image():
        """Getting default image on address"""
        if BMConfigParser().addresses():
            return state.imageDir + '/default_identicon/{}.png'.format(
                BMConfigParser().addresses()[0])
        return state.imageDir + '/no_identicons.png'

    @staticmethod
    def get_default_logo():
        """Getting default logo image"""
        if BMConfigParser().addresses():
            first_addr = BMConfigParser().addresses()[0]
            if BMConfigParser().get(str(first_addr), 'enabled') == 'true':
                return state.imageDir + '/default_identicon/{}.png'.format(
                    first_addr)
        return state.imageDir + '/drawer_logo1.png'

    @staticmethod
    def addressexist():
        """Checking address existence"""
        if BMConfigParser().addresses():
            return True
        return False

    def on_key(self, window, key, *args):
        # pylint: disable=inconsistent-return-statements, too-many-branches
        """Method is used for going on previous screen"""
        if key == 27:
            if state.in_search_mode and self.root.ids.scr_mngr.current not in [
                    "mailDetail", "create"]:
                self.closeSearchScreen()
            elif self.root.ids.scr_mngr.current == "mailDetail":
                self.root.ids.scr_mngr.current = 'sent'\
                    if state.detailPageType == 'sent' else 'inbox' \
                    if state.detailPageType == 'inbox' else 'draft'
                self.back_press()
                if state.in_search_mode and state.searcing_text:
                    toolbar_obj = self.root.ids.toolbar
                    toolbar_obj.left_action_items = [
                        ['arrow-left', lambda x: self.closeSearchScreen()]]
                    toolbar_obj.right_action_items = []
                    self.root.ids.toolbar.title = ''
            elif self.root.ids.scr_mngr.current == "create":
                self.save_draft()
                self.set_common_header()
                state.in_composer = False
                self.root.ids.scr_mngr.current = 'inbox'
            elif self.root.ids.scr_mngr.current == "showqrcode":
                self.root.ids.scr_mngr.current = 'myaddress'
            elif self.root.ids.scr_mngr.current == "random":
                self.root.ids.scr_mngr.current = 'login'
            elif self.root.ids.scr_mngr.current == 'pay-options':
                self.set_common_header()
                self.root.ids.scr_mngr.current = 'payment'
            elif self.root.ids.scr_mngr.current == 'chroom':
                if state.association:
                    address_label = self.current_address_label(
                        BMConfigParser().get(
                            state.association, 'label'), state.association)
                    self.root.ids.toolbar.title = address_label
                self.set_common_header()
                self.root.ids.scr_mngr.transition = FallOutTransition()
                self.root.ids.scr_mngr.current = 'chlist'
                self.root.ids.scr_mngr.transition = SlideTransition()
            else:
                if state.kivyapp.variable_1:
                    self.root.ids.scr_mngr.current = 'inbox'
            self.root.ids.scr_mngr.transition.direction = 'right'
            self.root.ids.scr_mngr.transition.bind(on_complete=self.reset)
            return True
        elif key == 13 and state.searcing_text and not state.in_composer:
            if state.search_screen == 'inbox':
                self.root.ids.sc1.children[1].active = True
                Clock.schedule_once(self.search_callback, 0.5)
            elif state.search_screen == 'addressbook':
                self.root.ids.sc11.children[1].active = True
                Clock.schedule_once(self.search_callback, 0.5)
            elif state.search_screen == 'myaddress':
                self.loadMyAddressScreen(True)
                Clock.schedule_once(self.search_callback, 0.5)
            elif state.search_screen == 'sent':
                self.root.ids.sc4.children[1].active = True
                Clock.schedule_once(self.search_callback, 0.5)

    def search_callback(self, dt=0):
        """Show data after loader is loaded"""
        if state.search_screen == 'inbox':
            self.root.ids.sc1.ids.ml.clear_widgets()
            self.root.ids.sc1.loadMessagelist(state.association)
            self.root.ids.sc1.children[1].active = False
        elif state.search_screen == 'addressbook':
            self.root.ids.sc11.ids.ml.clear_widgets()
            self.root.ids.sc11.loadAddresslist(None, 'All', '')
            self.root.ids.sc11.children[1].active = False
        elif state.search_screen == 'myaddress':
            self.root.ids.sc10.ids.ml.clear_widgets()
            self.root.ids.sc10.init_ui()
            self.loadMyAddressScreen(False)
        else:
            self.root.ids.sc4.ids.ml.clear_widgets()
            self.root.ids.sc4.loadSent(state.association)
            self.root.ids.sc4.children[1].active = False
        self.root.ids.scr_mngr.current = state.search_screen

    def loadMyAddressScreen(self, action):
        """loadMyAddressScreen method spin the loader"""
        if len(self.root.ids.sc10.children) <= 2:
            self.root.ids.sc10.children[0].active = action
        else:
            self.root.ids.sc10.children[1].active = action

    def save_draft(self):
        """Saving drafts messages"""
        composer_objs = self.root
        from_addr = str(self.root.ids.sc3.children[1].ids.ti.text)
        # to_addr = str(self.root.ids.sc3.children[1].ids.txt_input.text)
        if from_addr and state.detailPageType != 'draft' \
                and not state.in_sent_method:
            Draft().draft_msg(composer_objs)
        return

    def reset(self, *args):
        """Set transition direction"""
        self.root.ids.scr_mngr.transition.direction = 'left'
        self.root.ids.scr_mngr.transition.unbind(on_complete=self.reset)

    @staticmethod
    def status_dispatching(data):
        """Dispatching Status acknowledgment"""
        ackData, message = data
        if state.ackdata == ackData:
            state.status.status = message

    def clear_composer(self):
        """If slow down, the new composer edit screen"""
        self.set_navbar_for_composer()
        composer_obj = self.root.ids.sc3.children[1].ids
        composer_obj.ti.text = ''
        composer_obj.btn.text = 'Select'
        composer_obj.txt_input.text = ''
        composer_obj.subject.text = ''
        composer_obj.body.text = ''
        state.in_composer = True
        state.in_sent_method = False

    def set_navbar_for_composer(self):
        """Clearing toolbar data when composer open"""
        self.root.ids.toolbar.left_action_items = [
            ['arrow-left', lambda x: self.back_press()]]
        self.root.ids.toolbar.right_action_items = [
            ['refresh',
             lambda x: self.root.ids.sc3.children[1].reset_composer()],
            ['send',
             lambda x: self.root.ids.sc3.children[1].send(self)]]

    def set_toolbar_for_QrCode(self):
        """This method is use for setting Qr code toolbar."""
        self.root.ids.toolbar.left_action_items = [
            ['arrow-left', lambda x: self.back_press()]]
        self.root.ids.toolbar.right_action_items = []

    def set_common_header(self):
        """Common header for all window"""
        self.root.ids.toolbar.right_action_items = [
            ['account-plus', lambda x: self.addingtoaddressbook()]]
        # self.root.ids.toolbar.left_action_items = [
        #     ['menu', lambda x: self.root.toggle_nav_drawer()]]
        self.root.ids.toolbar.left_action_items = [
            ['menu', lambda x: self.root.ids.nav_drawer.set_state("toggle")]]
        return

    def back_press(self):
        """Method for, reverting composer to previous page"""
        if self.root.ids.scr_mngr.current == 'create':
            self.save_draft()
        if self.root.ids.scr_mngr.current == \
                'mailDetail' and state.in_search_mode:
            toolbar_obj = self.root.ids.toolbar
            toolbar_obj.left_action_items = [
                ['arrow-left', lambda x: self.closeSearchScreen()]]
            toolbar_obj.right_action_items = []
            self.root.ids.toolbar.title = ''
        else:
            self.set_common_header()
            if self.root.ids.scr_mngr.current == 'chroom' and state.association:
                self.root.ids.scr_mngr.transition = FallOutTransition()
                address_label = self.current_address_label(
                    BMConfigParser().get(
                        state.association, 'label'), state.association)
                self.root.ids.toolbar.title = address_label
        self.root.ids.scr_mngr.current = 'inbox' \
            if state.in_composer else 'allmails'\
            if state.is_allmail else state.detailPageType\
            if state.detailPageType else 'myaddress'\
            if self.root.ids.scr_mngr.current == 'showqrcode' else 'payment'\
            if self.root.ids.scr_mngr.current == 'pay-options' else 'chlist'\
            if self.root.ids.scr_mngr.current == 'chroom' else 'inbox'
        if self.root.ids.scr_mngr.current == 'chlist':
            self.root.ids.scr_mngr.transition = SlideTransition()
        self.root.ids.scr_mngr.transition.direction = 'right'
        self.root.ids.scr_mngr.transition.bind(on_complete=self.reset)
        if state.is_allmail or state.detailPageType == 'draft':
            state.is_allmail = False
        state.detailPageType = ''
        state.in_composer = False

    @staticmethod
    def get_inbox_count():
        """Getting inbox count"""
        state.inbox_count = str(sqlQuery(
            "SELECT COUNT(*) FROM inbox WHERE toaddress = '{}' and"
            " folder = 'inbox' ;".format(state.association))[0][0])

    @staticmethod
    def get_sent_count():
        """Getting sent count"""
        state.sent_count = str(sqlQuery(
            "SELECT COUNT(*) FROM sent WHERE fromaddress = '{}' and"
            " folder = 'sent' ;".format(state.association))[0][0])

    def set_message_count(self):
        """Setting message count"""
        msg_counter_objs = state.kivyapp.root.children[0].children[0].ids
        # try:
        #     msg_counter_objs = (
        #         self.root_window.children[0].children[2].children[0].ids)
        # except Exception:
        #     msg_counter_objs = (
        #         self.root_window.children[2].children[2].children[0].ids)
        self.get_inbox_count()
        self.get_sent_count()
        state.trash_count = str(sqlQuery(
            "SELECT (SELECT count(*) FROM  sent"
            " where fromaddress = '{0}' and  folder = 'trash' )"
            "+(SELECT count(*) FROM inbox where toaddress = '{0}' and"
            " folder = 'trash') AS SumCount".format(state.association))[0][0])
        state.draft_count = str(sqlQuery(
            "SELECT COUNT(*) FROM sent WHERE fromaddress = '{}' and"
            " folder = 'draft' ;".format(state.association))[0][0])
        state.all_count = str(int(state.sent_count) + int(state.inbox_count))
        if msg_counter_objs:
            msg_counter_objs.send_cnt.badge_text = state.sent_count
            msg_counter_objs.inbox_cnt.badge_text = state.inbox_count
            msg_counter_objs.trash_cnt.badge_text = state.trash_count
            msg_counter_objs.draft_cnt.badge_text = state.draft_count
            msg_counter_objs.allmail_cnt.badge_text = state.all_count

    def on_start(self):
        """Setting message count"""
        self.set_message_count()

    # @staticmethod
    # def on_stop():
    #     """On stop methos is used for stoping the runing script"""
    #     print("*******************EXITING FROM APPLICATION*******************")
    #     import shutdown
    #     shutdown.doCleanShutdown()

    @staticmethod
    def current_address_label(current_add_label=None, current_addr=None):
        """Getting current address labels"""
        if BMConfigParser().addresses():
            if current_add_label:
                first_name = current_add_label
                addr = current_addr
            else:
                addr = BMConfigParser().addresses()[0]
                first_name = BMConfigParser().get(addr, 'label')
                if BMConfigParser().get(addr, 'enabled') != 'true':
                    return ''
            f_name = first_name.split()
            label = f_name[0][:14].capitalize() + '...' if len(
                f_name[0]) > 15 else f_name[0].capitalize()
            address = ' (' + addr + ')'
            return label + address
        return ''

    def searchQuery(self, instance):
        """Showing searched mails"""
        state.search_screen = self.root.ids.scr_mngr.current
        state.searcing_text = str(instance.text).strip()
        if instance.focus and state.searcing_text:
            toolbar_obj = self.root.ids.toolbar
            toolbar_obj.left_action_items = [
                ['arrow-left', lambda x: self.closeSearchScreen()]]
            toolbar_obj.right_action_items = []
            self.root.ids.toolbar.title = ''
            state.in_search_mode = True

    def closeSearchScreen(self):
        """Function for close search screen"""
        self.set_common_header()
        if state.association:
            address_label = self.current_address_label(
                BMConfigParser().get(
                    state.association, 'label'), state.association)
            self.root.ids.toolbar.title = address_label
        state.searcing_text = ''
        self.refreshScreen()
        state.in_search_mode = False

    def refreshScreen(self):
        """Method show search button only on inbox or sent screen"""
        # pylint: disable=unused-variable
        state.searcing_text = ''
        if state.search_screen == 'inbox':
            self.root.ids.sc1.ids.inbox_search.ids.search_field.text = ''
            # try:
            #     self.root.ids.sc1.children[
            #         3].children[2].ids.search_field.text = ''
            # except Exception:
            #     self.root.ids.sc1.children[
            #         2].children[2].ids.search_field.text = ''
            self.root.ids.sc1.children[1].active = True
            Clock.schedule_once(self.search_callback, 0.5)
        elif state.search_screen == 'addressbook':
            self.root.ids.sc11.ids.address_search.ids.search_field.text = ''
            # self.root.ids.sc11.children[
            #     2].children[2].ids.search_field.text = ''
            self.root.ids.sc11.children[
                1].active = True
            Clock.schedule_once(self.search_callback, 0.5)
        elif state.search_screen == 'myaddress':
            self.root.ids.sc10.ids.search_bar.ids.search_field.text = ''
            # try:
            #     self.root.ids.sc10.children[
            #         1].children[2].ids.search_field.text = ''
            # except Exception:
            #     self.root.ids.sc10.children[
            #         2].children[2].ids.search_field.text = ''
            self.loadMyAddressScreen(True)
            Clock.schedule_once(self.search_callback, 0.5)
        else:
            self.root.ids.sc4.ids.sent_search.ids.search_field.text = ''
            # self.root.ids.sc4.children[
            #     2].children[2].ids.search_field.text = ''
            self.root.ids.sc4.children[1].active = True
            Clock.schedule_once(self.search_callback, 0.5)
        return

    def set_identicon(self, text):
        """Show identicon in address spinner"""
        img = identiconGeneration.generate(text)
        # self.root.children[0].children[0].ids.btn.children[1].texture = (img.texture)
        # below line is for displaing logo
        self.root.ids.content_drawer.ids.top_box.children[0].texture = (img.texture)

    def set_mail_detail_header(self):
        """Setting the details of the page"""
        if state.association and state.in_search_mode:
            address_label = self.current_address_label(
                BMConfigParser().get(
                    state.association, 'label'), state.association)
            self.root.ids.toolbar.title = address_label
        toolbar_obj = self.root.ids.toolbar
        toolbar_obj.left_action_items = [
            ['arrow-left', lambda x: self.back_press()]]
        delete_btn = ['delete-forever',
                      lambda x: self.root.ids.sc14.delete_mail()]
        dynamic_list = []
        if state.detailPageType == 'inbox':
            dynamic_list = [
                ['reply', lambda x: self.root.ids.sc14.inbox_reply()],
                delete_btn]
        elif state.detailPageType == 'sent':
            dynamic_list = [delete_btn]
        elif state.detailPageType == 'draft':
            dynamic_list = [
                ['pencil', lambda x: self.root.ids.sc14.write_msg(self)],
                delete_btn]
        toolbar_obj.right_action_items = dynamic_list

    def load_screen(self, instance):
        """This method is used for loading screen on every click"""
        if instance.text == 'Inbox':
            self.root.ids.scr_mngr.current = 'inbox'
            self.root.ids.sc1.children[1].active = True
        elif instance.text == 'All Mails':
            self.root.ids.scr_mngr.current = 'allmails'
            try:
                self.root.ids.sc17.children[1].active = True
            except Exception:
                self.root.ids.sc17.children[0].children[1].active = True
        Clock.schedule_once(partial(self.load_screen_callback, instance), 1)

    def load_screen_callback(self, instance, dt=0):
        """This method is rotating loader for few seconds"""
        if instance.text == 'Inbox':
            self.root.ids.sc1.ids.ml.clear_widgets()
            self.root.ids.sc1.loadMessagelist(state.association)
            self.root.ids.sc1.children[1].active = False
        elif instance.text == 'All Mails':
            # if len(self.root.ids.sc17.ids.ml.children) <= 2:
            #     self.root.ids.sc17.clear_widgets()
            #     self.root.ids.sc17.add_widget(Allmails())
            # else:
            #     self.root.ids.sc17.ids.ml.clear_widgets()
            #     self.root.ids.sc17.loadMessagelist()
            self.root.ids.sc17.clear_widgets()
            self.root.ids.sc17.add_widget(Allmails())
            try:
                self.root.ids.sc17.children[1].active = False
            except Exception:
                self.root.ids.sc17.children[0].children[1].active = False

    def on_request_close(self, *args):  # pylint: disable=no-self-use
        """This method is for app closing request"""
        AppClosingPopup().open()
        return True

    def file_manager_open(self):
        """This method open the file manager of local system"""
        from kivymd.uix.filemanager import MDFileManager

        if not self.file_manager:
            self.file_manager = MDFileManager(
                exit_manager=self.exit_manager,
                select_path=self.select_path,
                ext=['.png', '.jpg']
            )
        self.file_manager.previous = False
        self.file_manager.current_path = '/'
        if platform == 'android':
            from android.permissions import request_permissions, Permission, check_permission
            if check_permission(Permission.WRITE_EXTERNAL_STORAGE) and \
                    check_permission(Permission.READ_EXTERNAL_STORAGE):
                self.file_manager.show(os.getenv('EXTERNAL_STORAGE'))
                self.manager_open = True
            else:
                request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
        else:
            self.file_manager.show(os.environ["HOME"])
            self.manager_open = True

    def select_path(self, path):
        """This method is used to save the select image"""
        try:
            from PIL import Image as PilImage
            newImg = PilImage.open(path).resize((300, 300))
            if platform == 'android':
                android_path = os.path.join(
                    os.environ['ANDROID_PRIVATE'] + '/app/')
                newImg.save('{1}/images/kivy/default_identicon/{0}.png'.format(
                    state.association, android_path))
            else:
                if not os.path.exists(state.imageDir + '/default_identicon/'):
                    os.makedirs(state.imageDir + '/default_identicon/')
                newImg.save(state.imageDir + '/default_identicon/{0}.png'.format(state.association))
            self.load_selected_Image(state.association)
            toast('Image changed')
        except Exception:
            toast('Exit')
        self.exit_manager()

    def exit_manager(self, *args):
        """Called when the user reaches the root of the directory tree."""
        self.manager_open = False
        self.file_manager.close()

    def load_selected_Image(self, curerentAddr):
        """This method load the selected image on screen"""
        top_box_obj = self.root.ids.content_drawer.ids.top_box.children[0]
        # spinner_img_obj = self.root.ids.content_drawer.ids.btn.children[1]
        # spinner_img_obj.source = top_box_obj.source ='./images/default_identicon/{0}.png'.format(curerentAddr)
        top_box_obj.source = state.imageDir + '/default_identicon/{0}.png'.format(curerentAddr)
        self.root.ids.content_drawer.ids.reset_image.opacity = 1
        self.root.ids.content_drawer.ids.reset_image.disabled = False
        top_box_obj.reload()
        # spinner_img_obj.reload()

    def rest_default_avatar_img(self):
        """set default avatar generated image"""
        self.set_identicon(state.association)
        img_path = state.imageDir + '/default_identicon/{}.png'.format(state.association)
        try:
            if os.path.exists(img_path):
                os.remove(img_path)
                self.root.ids.content_drawer.ids.reset_image.opacity = 0
                self.root.ids.content_drawer.ids.reset_image.disabled = True
        except Exception as e:
            pass
        toast('Avatar reset')

    def copy_composer_text(self, text):  # pylint: disable=no-self-use
        """Copy the data from mail detail page"""
        Clipboard.copy(text)
        toast('Copied')

    def reset_login_screen(self):
        """This method is used for clearing random screen"""
        if self.root.ids.sc7.ids.add_random_bx.children:
            self.root.ids.sc7.ids.add_random_bx.clear_widgets()

    def open_payment_layout(self, sku):
        """It basically open up a payment layout for kivy Ui"""
        pml = PaymentMethodLayout()
        self.product_id = sku
        self.custom_sheet = MDCustomBottomSheet(screen=pml)
        self.custom_sheet.open()

    def initiate_purchase(self, method_name):
        """initiate_purchase module"""
        print("Purchasing {} through {}".format(self.product_id, method_name))

    def _after_scan(self, text):
        if platform == 'android':
            text = cast(CharSequence, String(text))
            show_toast(text, Toast.LENGTH_SHORT)
        elif self.root.ids.sc23.previous_open_screen == 'composer':
            self.root.ids.sc3.children[1].ids.txt_input.text = text
            self.root.ids.scr_mngr.current = 'create'
        elif self.root.ids.sc23.previous_open_screen:
            back_screen = self.root.ids.sc23.previous_open_screen
            self.root.ids.scr_mngr.current = 'inbox' if back_screen == 'scanscreen' else back_screen
            add_obj = self.root.ids.sc23.pop_up_instance
            add_obj.content_cls.ids.address.text = text
            Clock.schedule_once(partial(self.open_popup, add_obj), .5)

    def open_popup(self, instance, dt):
        """This method is used for opening popup"""
        instance.open()


class GrashofPopup(BoxLayout):
    """GrashofPopup class for kivy Ui"""

    valid = False

    def __init__(self, **kwargs):
        """Grash of pop screen settings"""
        super(GrashofPopup, self).__init__(**kwargs)

    def checkAddress_valid(self, instance):
        """Checking address is valid or not"""
        my_addresses = (
            state.kivyapp.root.ids.content_drawer.ids.btn.values)
        add_book = [addr[1] for addr in kivy_helper_search.search_sql(
            folder="addressbook")]
        entered_text = str(instance.text).strip()
        if entered_text in add_book:
            text = 'Address is already in the addressbook.'
        elif entered_text in my_addresses:
            text = 'You can not save your own address.'
        elif entered_text:
            text = self.addressChanged(entered_text)

        if entered_text in my_addresses or entered_text in add_book:
            self.ids.address.error = True
            self.ids.address.helper_text = text
        elif entered_text and self.valid:
            self.ids.address.error = False
        elif entered_text:
            self.ids.address.error = True
            self.ids.address.helper_text = text
        else:
            self.ids.address.error = False
            self.ids.address.helper_text = 'This field is required'

    def checkLabel_valid(self, instance):
        """Checking address label is unique or not"""
        entered_label = instance.text.strip()
        addr_labels = [labels[0] for labels in kivy_helper_search.search_sql(
            folder="addressbook")]
        if entered_label in addr_labels:
            self.ids.label.error = True
            self.ids.label.helper_text = 'label name already exists.'
        elif entered_label:
            self.ids.label.error = False
        else:
            self.ids.label.error = False
            self.ids.label.helper_text = 'This field is required'

    def _onSuccess(self, addressVersion, streamNumber, ripe):
        pass

    def addressChanged(self, addr):
        """Address validation callback, performs validation and gives feedback"""
        status, addressVersion, streamNumber, ripe = decodeAddress(
            str(addr))
        self.valid = status == 'success'
        if self.valid:
            text = "Address is valid."
            self._onSuccess(addressVersion, streamNumber, ripe)
        elif status == 'missingbm':
            text = "The address should start with ''BM-''"
        elif status == 'checksumfailed':
            text = (
                "The address is not typed or copied correctly"
                # " (the checksum failed)."
            )
        elif status == 'versiontoohigh':
            text = (
                "The version number of this address is higher than this"
                " software can support. Please upgrade Bitmessage.")
        elif status == 'invalidcharacters':
            text = "The address contains invalid characters."
        elif status == 'ripetooshort':
            text = "Some data encoded in the address is too short."
        elif status == 'ripetoolong':
            text = "Some data encoded in the address is too long."
        elif status == 'varintmalformed':
            text = "Some data encoded in the address is malformed."
        return text


class InfoLayout(BoxLayout, RectangularElevationBehavior):
    """InfoLayout class for kivy Ui"""


class AvatarSampleWidget(ILeftBody, Image):
    """AvatarSampleWidget class for kivy Ui"""


class IconLeftSampleWidget(ILeftBodyTouch, MDIconButton):
    """IconLeftSampleWidget class for kivy Ui"""


class IconRightSampleWidget(IRightBodyTouch, MDIconButton):
    """IconRightSampleWidget class for kivy Ui"""


class TimeTagRightSampleWidget(IRightBodyTouch, MDLabel):
    """TimeTagRightSampleWidget class for Ui"""


class ToggleBtn(IRightBodyTouch, MDSwitch):
    """ToggleBtn class for kivy Ui"""


class CheckboxLeftSampleWidget(ILeftBodyTouch, MDCheckbox):
    """CheckboxLeftSampleWidget class for kivy Ui"""


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
        super(MailDetail, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method MailDetail mails"""
        self.page_type = state.detailPageType if state.detailPageType else ''
        if state.detailPageType == 'sent' or state.detailPageType == 'draft':
            data = sqlQuery(
                "select toaddress, fromaddress, subject, message, status,"
                " ackdata, senttime from sent where ackdata = ?;", state.mail_id)
            state.status = self
            state.ackdata = data[0][5]
            self.assign_mail_details(data)
            state.kivyapp.set_mail_detail_header()
        elif state.detailPageType == 'inbox':
            data = sqlQuery(
                "select toaddress, fromaddress, subject, message, received from inbox"
                " where msgid = ?;", state.mail_id)
            self.assign_mail_details(data)
            state.kivyapp.set_mail_detail_header()

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
        self.time_tag = ShowTimeHistoy(data[0][4]) if state.detailPageType == 'inbox' else ShowTimeHistoy(data[0][6])
        self.avatarImg = state.imageDir + '/avatar.png' if state.detailPageType == 'draft' else (
            state.imageDir + '/text_images/{0}.png'.format(avatarImageFirstLetter(self.subject.strip())))
        self.timeinseconds = data[0][4] if state.detailPageType == 'inbox' else data[0][6]

    def delete_mail(self):
        """Method for mail delete"""
        msg_count_objs = state.kivyapp.root.ids.content_drawer.ids
        state.searcing_text = ''
        self.children[0].children[0].active = True
        if state.detailPageType == 'sent':
            state.kivyapp.root.ids.sc4.ids.sent_search.ids.search_field.text = ''
            sqlExecute(
                "UPDATE sent SET folder = 'trash' WHERE"
                " ackdata = ?;", state.mail_id)
            msg_count_objs.send_cnt.ids.badge_txt.text = str(int(state.sent_count) - 1)
            state.sent_count = str(int(state.sent_count) - 1)
            self.parent.screens[3].ids.ml.clear_widgets()
            self.parent.screens[3].loadSent(state.association)
        elif state.detailPageType == 'inbox':
            state.kivyapp.root.ids.sc1.ids.inbox_search.ids.search_field.text = ''
            sqlExecute(
                "UPDATE inbox SET folder = 'trash' WHERE"
                " msgid = ?;", state.mail_id)
            msg_count_objs.inbox_cnt.ids.badge_txt.text = str(
                int(state.inbox_count) - 1)
            state.inbox_count = str(int(state.inbox_count) - 1)
            self.parent.screens[0].ids.ml.clear_widgets()
            self.parent.screens[0].loadMessagelist(state.association)

        elif state.detailPageType == 'draft':
            sqlExecute("DELETE FROM sent WHERE ackdata = ?;", state.mail_id)
            msg_count_objs.draft_cnt.ids.badge_txt.text = str(
                int(state.draft_count) - 1)
            state.draft_count = str(int(state.draft_count) - 1)
            self.parent.screens[15].clear_widgets()
            self.parent.screens[15].add_widget(Draft())

        if state.detailPageType != 'draft':
            msg_count_objs.trash_cnt.ids.badge_txt.text = str(
                int(state.trash_count) + 1)
            msg_count_objs.allmail_cnt.ids.badge_txt.text = str(
                int(state.all_count) - 1)
            state.trash_count = str(int(state.trash_count) + 1)
            state.all_count = str(int(state.all_count) - 1) if int(state.all_count) else '0'
            self.parent.screens[4].clear_widgets()
            self.parent.screens[4].add_widget(Trash())
            self.parent.screens[16].clear_widgets()
            self.parent.screens[16].add_widget(Allmails())
        Clock.schedule_once(self.callback_for_delete, 4)

    def callback_for_delete(self, dt=0):
        """Delete method from allmails"""
        if state.detailPageType:
            self.children[0].children[0].active = False
            state.kivyapp.set_common_header()
            self.parent.current = 'allmails' \
                if state.is_allmail else state.detailPageType
            state.detailPageType = ''
            toast('Deleted')

    def inbox_reply(self):
        """Reply inbox messages"""
        state.in_composer = True
        data = sqlQuery(
            "select toaddress, fromaddress, subject, message, received from inbox where"
            " msgid = ?;", state.mail_id)
        composer_obj = self.parent.screens[2].children[1].ids
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
        state.send_draft_mail = state.mail_id
        data = sqlQuery(
            "select toaddress, fromaddress, subject, message from sent where"
            " ackdata = ?;", state.mail_id)
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


class MyaddDetailPopup(BoxLayout):
    """MyaddDetailPopup class for kivy Ui"""

    address_label = StringProperty()
    address = StringProperty()

    def __init__(self, **kwargs):
        """My Address Details screen setting"""
        super(MyaddDetailPopup, self).__init__(**kwargs)

    def send_message_from(self):
        """Method used to fill from address of composer autofield"""
        state.kivyapp.set_navbar_for_composer()
        window_obj = state.kivyapp.root.ids
        window_obj.sc3.children[1].ids.ti.text = self.address
        window_obj.sc3.children[1].ids.btn.text = self.address
        window_obj.sc3.children[1].ids.txt_input.text = ''
        window_obj.sc3.children[1].ids.subject.text = ''
        window_obj.sc3.children[1].ids.body.text = ''
        window_obj.scr_mngr.current = 'create'
        self.parent.parent.parent.dismiss()

    # @staticmethod
    def close_pop(self):
        """Pop is Canceled"""
        self.parent.parent.parent.dismiss()
        toast('Canceled')


class AddbookDetailPopup(BoxLayout):
    """AddbookDetailPopup class for kivy Ui"""

    address_label = StringProperty()
    address = StringProperty()

    def __init__(self, **kwargs):
        """Set screen of address detail page"""
        super(AddbookDetailPopup, self).__init__(**kwargs)

    def checkLabel_valid(self, instance):
        """Checking address label is unique of not"""
        entered_label = str(instance.text.strip())
        address_list = kivy_helper_search.search_sql(folder="addressbook")
        addr_labels = [labels[0] for labels in address_list]
        add_dict = dict(address_list)
        if self.address and entered_label in addr_labels \
                and self.address != add_dict[entered_label]:
            self.ids.add_label.error = True
            self.ids.add_label.helper_text = 'label name already exists.'
        elif entered_label:
            self.ids.add_label.error = False
        else:
            self.ids.add_label.error = False
            self.ids.add_label.helper_text = 'This field is required'


class ShowQRCode(Screen):
    """ShowQRCode Screen class for kivy Ui"""
    address = StringProperty()

    def qrdisplay(self, instasnce, address):
        """Method used for showing QR Code"""
        self.ids.qr.clear_widgets()
        state.kivyapp.set_toolbar_for_QrCode()
        try:
            from kivy.garden.qrcode import QRCodeWidget
        except Exception:
            from kivy_garden.qrcode import QRCodeWidget
        self.address = address
        self.ids.qr.add_widget(QRCodeWidget(data=address))
        self.ids.qr.children[0].show_border = False
        instasnce.parent.parent.parent.dismiss()
        toast('Show QR code')


class Draft(Screen):
    """Draft screen class for kivy Ui"""

    data = ListProperty()
    account = StringProperty()
    queryreturn = ListProperty()
    has_refreshed = True

    def __init__(self, *args, **kwargs):
        """Method used for storing draft messages"""
        super(Draft, self).__init__(*args, **kwargs)
        if state.association == '':
            if BMConfigParser().addresses():
                state.association = BMConfigParser().addresses()[0]
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method draft accounts"""
        self.sentaccounts()
        print(dt)

    def sentaccounts(self):
        """Load draft accounts"""
        self.account = state.association
        self.loadDraft()

    def loadDraft(self, where="", what=""):
        """Load draft list for Draft messages"""
        xAddress = 'fromaddress'
        self.ids.tag_label.text = ''
        self.draftDataQuery(xAddress, where, what)
        # if state.msg_counter_objs:
        #     state.msg_counter_objs.draft_cnt.children[0].children[0].text = showLimitedCnt(len(self.queryreturn))
        if self.queryreturn:
            self.ids.tag_label.text = 'Draft'
            self.set_draftCnt(state.draft_count)
            self.set_mdList()
            self.ids.scroll_y.bind(scroll_y=self.check_scroll_y)
        else:
            self.set_draftCnt('0')
            content = MDLabel(
                font_style='Caption',
                theme_text_color='Primary',
                text="yet no message for this account!!!!!!!!!!!!!",
                halign='center',
                size_hint_y=None,
                valign='top')
            self.ids.ml.add_widget(content)

    def draftDataQuery(self, xAddress, where, what, start_indx=0, end_indx=20):
        """This methosd is for retrieving draft messages"""
        self.queryreturn = kivy_helper_search.search_sql(
            xAddress, self.account, "draft", where, what,
            False, start_indx, end_indx)

    def set_draftCnt(self, Count):  # pylint: disable=no-self-use
        """This method set the count of draft mails"""
        draftCnt_obj = state.kivyapp.root.ids.content_drawer.ids.draft_cnt
        draftCnt_obj.ids.badge_txt.text = showLimitedCnt(int(Count))

    def set_mdList(self):
        """This method is used to create mdlist"""
        data = []
        total_draft_msg = len(self.ids.ml.children)
        for mail in self.queryreturn:
            third_text = mail[3].replace('\n', ' ')
            data.append({
                'text': mail[1].strip(),
                'secondary_text': mail[2][:10] + '...........' if len(
                    mail[2]) > 10 else mail[2] + '\n' + " " + (
                        third_text[:25] + '...!') if len(
                            third_text) > 25 else third_text,
                'ackdata': mail[5], 'senttime': mail[6]})
        for item in data:
            meny = TwoLineAvatarIconListItem(
                text='Draft', secondary_text=item['text'],
                theme_text_color='Custom',
                text_color=ThemeClsColor)
            meny._txt_right_pad = dp(70)
            meny.add_widget(AvatarSampleWidget(
                source=state.imageDir + '/avatar.png'))
            meny.bind(on_press=partial(
                self.draft_detail, item['ackdata']))
            meny.add_widget(AddTimeWidget(item['senttime']))
            carousel = Carousel(direction='right')
            carousel.height = meny.height
            carousel.size_hint_y = None
            carousel.ignore_perpendicular_swipes = True
            carousel.data_index = 0
            carousel.min_move = 0.2
            del_btn = Button(text='Delete')
            del_btn.background_normal = ''
            del_btn.background_color = (1, 0, 0, 1)
            del_btn.bind(on_press=partial(self.delete_draft, item['ackdata']))
            carousel.add_widget(del_btn)
            carousel.add_widget(meny)
            carousel.index = 1
            self.ids.ml.add_widget(carousel)
        updated_msg = len(self.ids.ml.children)
        self.has_refreshed = True if total_draft_msg != updated_msg else False

    def check_scroll_y(self, instance, somethingelse):
        """Load data on scroll"""
        if self.ids.scroll_y.scroll_y <= -0.0 and self.has_refreshed:
            self.ids.scroll_y.scroll_y = 0.06
            total_draft_msg = len(self.ids.ml.children)
            self.update_draft_screen_on_scroll(total_draft_msg)

    def update_draft_screen_on_scroll(self, total_draft_msg, where='', what=''):
        """Load more data on scroll down"""
        self.draftDataQuery('fromaddress', where, what, total_draft_msg, 5)
        self.set_mdList()

    def draft_detail(self, ackdata, *args):
        """Show draft Details"""
        state.detailPageType = 'draft'
        state.mail_id = ackdata
        if self.manager:
            src_mng_obj = self.manager
        else:
            src_mng_obj = self.parent.parent
        src_mng_obj.screens[13].clear_widgets()
        src_mng_obj.screens[13].add_widget(MailDetail())
        src_mng_obj.current = 'mailDetail'

    def delete_draft(self, data_index, instance, *args):
        """Delete draft message permanently"""
        sqlExecute("DELETE FROM sent WHERE ackdata = ?;", data_index)
        if int(state.draft_count) > 0:
            state.draft_count = str(int(state.draft_count) - 1)
            self.set_draftCnt(state.draft_count)
            if int(state.draft_count) <= 0:
                # self.ids.identi_tag.children[0].text = ''
                self.ids.tag_label.text = ''
        self.ids.ml.remove_widget(instance.parent.parent)
        toast('Deleted')

    @staticmethod
    def draft_msg(src_object):
        """Save draft mails"""
        composer_object = state.kivyapp.root.ids.sc3.children[1].ids
        fromAddress = str(composer_object.ti.text)
        toAddress = str(composer_object.txt_input.text)
        subject = str(composer_object.subject.text)
        message = str(composer_object.body.text)
        encoding = 3
        sendMessageToPeople = True
        if sendMessageToPeople:
            streamNumber, ripe = decodeAddress(toAddress)[2:]
            from addresses import addBMIfNotPresent
            toAddress = addBMIfNotPresent(toAddress)
            stealthLevel = BMConfigParser().safeGetInt(
                'bitmessagesettings', 'ackstealthlevel')
            from helper_ackPayload import genAckPayload
            ackdata = genAckPayload(streamNumber, stealthLevel)
            sqlExecute(
                '''INSERT INTO sent VALUES
                (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                '',
                toAddress,
                ripe,
                fromAddress,
                subject,
                message,
                ackdata,
                int(time.time()),
                int(time.time()),
                0,
                'msgqueued',
                0,
                'draft',
                encoding,
                BMConfigParser().safeGetInt('bitmessagesettings', 'ttl'))
            state.msg_counter_objs = src_object.children[2].children[0].ids
            state.draft_count = str(int(state.draft_count) + 1) \
                if state.association == fromAddress else state.draft_count
            src_object.ids.sc16.clear_widgets()
            src_object.ids.sc16.add_widget(Draft())
            toast('Save draft')
        return


class CustomSpinner(Spinner):
    """CustomSpinner class for kivy Ui"""

    def __init__(self, *args, **kwargs):
        """Method used for setting size of spinner"""
        super(CustomSpinner, self).__init__(*args, **kwargs)
        self.dropdown_cls.max_height = Window.size[1] / 3
        self.values = list(addr for addr in BMConfigParser().addresses()
                           if BMConfigParser().get(str(addr), 'enabled') == 'true')


class Allmails(Screen):
    """Allmails Screen for kivy Ui"""

    data = ListProperty()
    has_refreshed = True
    all_mails = ListProperty()
    account = StringProperty()

    def __init__(self, *args, **kwargs):
        """Method Parsing the address"""
        super(Allmails, self).__init__(*args, **kwargs)
        if state.association == '':
            if BMConfigParser().addresses():
                state.association = BMConfigParser().addresses()[0]
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method all mails"""
        self.loadMessagelist()
        print(dt)

    def loadMessagelist(self):
        """Load Inbox, Sent anf Draft list of messages"""
        self.account = state.association
        self.ids.tag_label.text = ''
        self.allMessageQuery(0, 20)
        if self.all_mails:
            self.ids.tag_label.text = 'All Mails'
            state.kivyapp.get_inbox_count()
            state.kivyapp.get_sent_count()
            state.all_count = str(
                int(state.sent_count) + int(state.inbox_count))
            self.set_AllmailCnt(state.all_count)
            self.set_mdlist()
            # self.ids.refresh_layout.bind(scroll_y=self.check_scroll_y)
            self.ids.scroll_y.bind(scroll_y=self.check_scroll_y)
        else:
            self.set_AllmailCnt('0')
            content = MDLabel(
                font_style='Caption',
                theme_text_color='Primary',
                text="yet no message for this account!!!!!!!!!!!!!",
                halign='center',
                size_hint_y=None,
                valign='top')
            self.ids.ml.add_widget(content)

    def allMessageQuery(self, start_indx, end_indx):
        """Retrieving data from inbox or sent both tables"""
        self.all_mails = sqlQuery(
            "SELECT toaddress, fromaddress, subject, message, folder, ackdata"
            " As id, DATE(senttime) As actionTime, senttime as msgtime FROM sent WHERE"
            " folder = 'sent' and fromaddress = '{0}'"
            " UNION SELECT toaddress, fromaddress, subject, message, folder,"
            " msgid As id, DATE(received) As actionTime, received as msgtime FROM inbox"
            " WHERE folder = 'inbox' and toaddress = '{0}'"
            " ORDER BY actionTime DESC limit {1}, {2}".format(
                self.account, start_indx, end_indx))

    def set_AllmailCnt(self, Count):  # pylint: disable=no-self-use
        """This method is used to set allmails message count"""
        allmailCnt_obj = state.kivyapp.root.ids.content_drawer.ids.allmail_cnt
        allmailCnt_obj.ids.badge_txt.text = showLimitedCnt(int(Count))

    def set_mdlist(self):
        """This method is used to create mdList for allmaills"""
        data_exist = len(self.ids.ml.children)
        for item in self.all_mails:
            body = item[3].decode() if isinstance(item[3], bytes) else item[3]
            subject = item[2].decode() if isinstance(item[2], bytes) else item[2]
            meny = TwoLineAvatarIconListItem(
                text=item[1],
                secondary_text=(subject[:50] + '........' if len(
                    subject) >= 50 else (
                        subject + ',' + body)[0:50] + '........').replace('\t', '').replace('  ', ''),
                theme_text_color='Custom',
                text_color=ThemeClsColor)
            meny._txt_right_pad = dp(70)
            meny.add_widget(AvatarSampleWidget(
                source=state.imageDir + '/text_images/{}.png'.format(
                    avatarImageFirstLetter(body.strip()))))
            meny.bind(on_press=partial(
                self.mail_detail, item[5], item[4]))
            meny.add_widget(AddTimeWidget(item[7]))
            meny.add_widget(chipTag(item[4]))
            carousel = Carousel(direction='right')
            carousel.height = meny.height
            carousel.size_hint_y = None
            carousel.ignore_perpendicular_swipes = True
            carousel.data_index = 0
            carousel.min_move = 0.2
            del_btn = Button(text='Delete')
            del_btn.background_normal = ''
            del_btn.background_color = (1, 0, 0, 1)
            del_btn.bind(on_press=partial(
                self.swipe_delete, item[5], item[4]))
            carousel.add_widget(del_btn)
            carousel.add_widget(meny)
            carousel.index = 1
            self.ids.ml.add_widget(carousel)
        updated_data = len(self.ids.ml.children)
        self.has_refreshed = True if data_exist != updated_data else False

    def check_scroll_y(self, instance, somethingelse):
        """Scroll fixed length"""
        if self.ids.scroll_y.scroll_y <= -0.00 and self.has_refreshed:
            self.ids.scroll_y.scroll_y = .06
            load_more = len(self.ids.ml.children)
            self.updating_allmail(load_more)

    def updating_allmail(self, load_more):
        """This method is used to update the all mail
        listing value on the scroll of screen"""
        self.allMessageQuery(load_more, 5)
        self.set_mdlist()

    def mail_detail(self, unique_id, folder, *args):
        """Load sent and inbox mail details"""
        state.detailPageType = folder
        state.is_allmail = True
        state.mail_id = unique_id
        if self.manager:
            src_mng_obj = self.manager
        else:
            src_mng_obj = self.parent.parent
        src_mng_obj.screens[13].clear_widgets()
        src_mng_obj.screens[13].add_widget(MailDetail())
        src_mng_obj.current = 'mailDetail'

    def swipe_delete(self, unique_id, folder, instance, *args):
        """Delete inbox mail from all mail listing"""
        if folder == 'inbox':
            sqlExecute(
                "UPDATE inbox SET folder = 'trash' WHERE msgid = ?;",
                unique_id)
        else:
            sqlExecute(
                "UPDATE sent SET folder = 'trash' WHERE ackdata = ?;",
                unique_id)
        self.ids.ml.remove_widget(instance.parent.parent)
        try:
            msg_count_objs = self.parent.parent.ids.content_drawer.ids
            nav_lay_obj = self.parent.parent.ids
        except Exception:
            msg_count_objs = self.parent.parent.parent.ids.content_drawer.ids
            nav_lay_obj = self.parent.parent.parent.ids
        if folder == 'inbox':
            msg_count_objs.inbox_cnt.ids.badge_txt.text = showLimitedCnt(int(state.inbox_count) - 1)
            state.inbox_count = str(int(state.inbox_count) - 1)
            nav_lay_obj.sc1.ids.ml.clear_widgets()
            nav_lay_obj.sc1.loadMessagelist(state.association)
        else:
            msg_count_objs.send_cnt.ids.badge_txt.text = showLimitedCnt(int(state.sent_count) - 1)
            state.sent_count = str(int(state.sent_count) - 1)
            nav_lay_obj.sc4.ids.ml.clear_widgets()
            nav_lay_obj.sc4.loadSent(state.association)
        if folder != 'inbox':
            msg_count_objs.allmail_cnt.ids.badge_txt.text = showLimitedCnt(int(state.all_count) - 1)
            state.all_count = str(int(state.all_count) - 1)
        msg_count_objs.trash_cnt.ids.badge_txt.text = showLimitedCnt(int(state.trash_count) + 1)
        state.trash_count = str(int(state.trash_count) + 1)
        if int(state.all_count) <= 0:
            self.ids.tag_label.text = ''
        nav_lay_obj.sc5.clear_widgets()
        nav_lay_obj.sc5.add_widget(Trash())
        nav_lay_obj.sc17.remove_widget(instance.parent.parent)
        toast('Deleted')

    def refresh_callback(self, *args):
        """Method updates the state of application,
        While the spinner remains on the screen"""
        def refresh_callback(interval):
            """Load the allmails screen data"""
            self.ids.ml.clear_widgets()
            self.remove_widget(self.children[1])
            try:
                screens_obj = self.parent.screens[16]
            except Exception:
                screens_obj = self.parent.parent.screens[16]
            screens_obj.add_widget(Allmails())
            self.ids.refresh_layout.refresh_done()
            self.tick = 0
        Clock.schedule_once(refresh_callback, 1)


def avatarImageFirstLetter(letter_string):
    """This function is used to the first letter for the avatar image"""
    try:
        if letter_string[0].upper() >= 'A' and letter_string[0].upper() <= 'Z':
            img_latter = letter_string[0].upper()
        elif int(letter_string[0]) >= 0 and int(letter_string[0]) <= 9:
            img_latter = letter_string[0]
        else:
            img_latter = '!'
    except ValueError:
        img_latter = '!'
    return img_latter if img_latter else '!'


class Starred(Screen):
    """Starred Screen class for kivy Ui"""


class Archieve(Screen):
    """Archieve Screen class for kivy Ui"""


class Spam(Screen):
    """Spam Screen class for kivy Ui"""


class LoadingPopup(Popup):
    """LoadingPopup class for kivy Ui"""

    def __init__(self, **kwargs):
        super(LoadingPopup, self).__init__(**kwargs)
        # call dismiss_popup in 2 seconds
        Clock.schedule_once(self.dismiss_popup, 0.5)

    def dismiss_popup(self, dt):
        """Dismiss popups"""
        self.dismiss()


class AddressDropdown(OneLineIconListItem):
    """AddressDropdown class for kivy Ui"""


class BadgeText(IRightBodyTouch, MDLabel):
    """BadgeText class for kivy Ui"""


class NavigationItem(OneLineAvatarIconListItem):
    """NavigationItem class for kivy Ui"""
    badge_text = StringProperty()
    icon = StringProperty()
    active = BooleanProperty(False)

    def currentlyActive(self):
        """Currenly active"""
        for nav_obj in self.parent.children:
            nav_obj.active = False
        self.active = True


class NavigationDrawerDivider(OneLineListItem):
    """
    A small full-width divider that can be placed
    in the :class:`MDNavigationDrawer`
    """

    disabled = True
    divider = None
    _txt_top_pad = NumericProperty(dp(8))
    _txt_bot_pad = NumericProperty(dp(8))

    def __init__(self, **kwargs):
        # pylint: disable=bad-super-call
        super(OneLineListItem, self).__init__(**kwargs)
        self.height = dp(16)


class NavigationDrawerSubheader(OneLineListItem):
    """
    A subheader for separating content in :class:`MDNavigationDrawer`

    Works well alongside :class:`NavigationDrawerDivider`
    """

    disabled = True
    divider = None
    theme_text_color = 'Secondary'


class AppClosingPopup(Popup):
    """AppClosingPopup class for kivy Ui"""

    def __init__(self, **kwargs):
        super(AppClosingPopup, self).__init__(**kwargs)

    def closingAction(self, text):
        """Action on closing window"""
        if text == 'Yes':
            print("*******************EXITING FROM APPLICATION*******************")
            import shutdown
            shutdown.doCleanShutdown()
        else:
            self.dismiss()
            toast(text)


class SenderDetailPopup(Popup):
    """SenderDetailPopup class for kivy Ui"""

    to_addr = StringProperty()
    from_addr = StringProperty()
    time_tag = StringProperty()

    def __init__(self, **kwargs):
        """this metthod initialized the send message detial popup"""
        super(SenderDetailPopup, self).__init__(**kwargs)

    def assignDetail(self, to_addr, from_addr, timeinseconds):
        """Detailes assigned"""
        self.to_addr = to_addr
        self.from_addr = from_addr
        time_obj = datetime.fromtimestamp(int(timeinseconds))
        self.time_tag = time_obj.strftime("%d %b %Y, %I:%M %p")
        device_type = 2 if platform == 'android' else 1.5
        pop_height = device_type * (self.ids.sd_label.height + self.ids.dismiss_btn.height)
        if len(to_addr) > 3:
            self.height = 0
            self.height = pop_height
            self.ids.to_addId.size_hint_y = None
            self.ids.to_addId.height = 50
            self.ids.to_addtitle.add_widget(ToAddressTitle())
            frmaddbox = ToAddrBoxlayout()
            frmaddbox.set_toAddress(to_addr)
            self.ids.to_addId.add_widget(frmaddbox)
        else:
            self.ids.space_1.height = dp(0)
            self.ids.space_2.height = dp(0)
            self.ids.myadd_popup_box.spacing = dp(8 if platform == 'android' else 3)
            self.height = 0
            self.height = pop_height / 1.2


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


class ToAddrBoxlayout(BoxLayout):
    """ToAddrBoxlayout class for kivy Ui"""
    to_addr = StringProperty()

    def set_toAddress(self, to_addr):
        """This method is use to set to address"""
        self.to_addr = to_addr


class ToAddressTitle(BoxLayout):
    """ToAddressTitle class for BoxLayout behaviour"""


class RandomBoxlayout(BoxLayout):
    """RandomBoxlayout class for BoxLayout behaviour"""


def esc_markup(msg):
    """this method is for replacing some property"""
    return (msg.replace('&', '&amp;')
            .replace('[', '&bl;')
            .replace(']', '&br;'))


class ChatRoom(Screen):
    """ChatRoom Screen class for kivy Ui"""
    def send_msg(self):
        """This method is for sending message"""
        msg = self.ids.message.text
        if msg:
            self.ids.chat_logs.text += (
                '[b][color=2980b9]{}:[/color][/b] {}\n'
                    .format('Me', esc_markup(msg)))
            # obj = MDChip(label=msg, radius=7)
            # obj.icon = ''
            # self.ids.ml.add_widget(obj)
            self.ids.message.text = ''


class ChatList(Screen):
    """ChatList Screen class for kivy Ui"""
    queryreturn = ListProperty()
    has_refreshed = True

    def __init__(self, *args, **kwargs):
        """Getting ChatList Details"""
        super(ChatList, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method ChatList"""
        self.loadAddresslist(None, 'All', '')
        print(dt)

    def loadAddresslist(self, account="", where="", what=""):
        """Clock Schdule for method ChatList"""
        self.queryreturn = kivy_helper_search.search_sql(
            '', account, "addressbook", where, what, False)
        self.queryreturn = [obj for obj in reversed(self.queryreturn)]
        if self.queryreturn:
            self.set_mdList()
        else:
            content = MDLabel(
                font_style='Caption',
                theme_text_color='Primary',
                text="No contact found!",
                halign='center',
                size_hint_y=None,
                valign='top')
            self.ids.ml.add_widget(content)

    def set_mdList(self):
        """Creating the mdList"""
        for item in self.queryreturn:
            meny = TwoLineAvatarIconListItem(
                text=item[0], secondary_text=item[1], theme_text_color='Custom',
                text_color=ThemeClsColor)
            meny.add_widget(AvatarSampleWidget(
                source=state.imageDir + '/text_images/{}.png'.format(
                    avatarImageFirstLetter(item[0].strip()))))
            meny.bind(on_release=partial(
                self.redirect_to_chat, item[0], item[1]))
            self.ids.ml.add_widget(meny)

    def redirect_to_chat(self, label, addr, *args):
        """This method is redirecting on chatroom"""
        self.manager.transition = RiseInTransition()
        state.kivyapp.set_toolbar_for_QrCode()
        label = label[:14].capitalize() + '...' if len(label) > 15 else label.capitalize()
        addrs = ' (' + addr + ')'
        self.manager.parent.ids.toolbar.title = label + addrs
        self.manager.parent.ids.sc21.ids.chat_logs.text = ''
        self.manager.current = 'chroom'
