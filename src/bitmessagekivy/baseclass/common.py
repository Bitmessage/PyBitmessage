# pylint: disable=no-name-in-module, attribute-defined-outside-init, import-error, unused-argument
"""
    All Common widgets of kivy are managed here.
"""

import os
from datetime import datetime

from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.properties import (
    NumericProperty,
    StringProperty,
    ListProperty
)
from kivy.app import App

from kivymd.uix.list import (
    ILeftBody,
    IRightBodyTouch,
)
from kivymd.uix.label import MDLabel
from kivymd.toast import kivytoast
from kivymd.uix.card import MDCardSwipe
from kivymd.uix.chip import MDChip
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

from pybitmessage.bitmessagekivy.get_platform import platform
from pybitmessage.bmconfigparser import config

ThemeClsColor = [0.12, 0.58, 0.95, 1]


data_screens = {
    "MailDetail": {
        "kv_string": "maildetail",
        "Factory": "MailDetail()",
        "name_screen": "mailDetail",
        "object": 0,
        "Import": "from pybitmessage.bitmessagekivy.baseclass.maildetail import MailDetail",
    },
}


def load_image_path():
    """Return the path of kivy images"""
    image_path = os.path.abspath(os.path.join('pybitmessage', 'images', 'kivy'))
    return image_path


def get_identity_list():
    """Get list of identities and access 'identity_list' variable in .kv file"""
    identity_list = ListProperty(
        addr for addr in config.addresses() if config.getboolean(str(addr), 'enabled')
    )
    return identity_list


def kivy_state_variables():
    """Return kivy_state variable"""
    kivy_running_app = App.get_running_app()
    kivy_state = kivy_running_app.kivy_state_obj
    return kivy_state


def chip_tag(text):
    """Create a new ChipTag"""
    obj = MDChip()
    # obj.size_hint = (None, None)
    obj.size_hint = (0.16 if platform == "android" else 0.08, None)
    obj.text = text
    obj.icon = ""
    obj.pos_hint = {
        "center_x": 0.91 if platform == "android" else 0.94,
        "center_y": 0.3
    }
    obj.height = dp(18)
    obj.text_color = (1, 1, 1, 1)
    obj.radius = [8]
    return obj


def toast(text):
    """Method will display the toast message"""
    kivytoast.toast(text)


def show_limited_cnt(total_msg):
    """This method set the total count limit in badge_text"""
    max_msg_count = '99+'
    total_msg_limit = 99
    return max_msg_count if total_msg > total_msg_limit else str(total_msg)


def avatar_image_first_letter(letter_string):
    """Returns first letter for the avatar image"""
    try:
        image_letter = letter_string.title()[0]
        if image_letter.isalnum():
            return image_letter
        return '!'
    except IndexError:
        return '!'


def add_time_widget(time):  # pylint: disable=redefined-outer-name, W0201
    """This method is used to create TimeWidget"""
    action_time = TimeTagRightSampleWidget(
        text=str(show_time_history(time)),
        font_style="Caption",
        size=[120, 140] if platform == "android" else [64, 80],
    )
    action_time.font_size = "11sp"
    return action_time


def show_time_history(act_time):
    """This method is used to return the message sent or receive time"""
    action_time = datetime.fromtimestamp(int(act_time))
    crnt_date = datetime.now()
    duration = crnt_date - action_time
    if duration.days < 1:
        return action_time.strftime("%I:%M %p")
    if duration.days < 365:
        return action_time.strftime("%d %b")
    return action_time.strftime("%d/%m/%Y")


# pylint: disable=too-few-public-methods
class AvatarSampleWidget(ILeftBody, Image):
    """AvatarSampleWidget class for kivy Ui"""


class TimeTagRightSampleWidget(IRightBodyTouch, MDLabel):
    """TimeTagRightSampleWidget class for Ui"""


class SwipeToDeleteItem(MDCardSwipe):
    """Swipe delete class for App UI"""
    text = StringProperty()
    cla = Window.size[0] / 2
    # cla = 800
    swipe_distance = NumericProperty(cla)
    opening_time = NumericProperty(0.5)


class CustomSwipeToDeleteItem(MDCardSwipe):
    """Custom swipe delete class for App UI"""
    text = StringProperty()
    cla = Window.size[0] / 2
    swipe_distance = NumericProperty(cla)
    opening_time = NumericProperty(0.5)


def empty_screen_label(label_str=None, no_search_res_found=None):
    """Returns default text on screen when no address is there."""
    kivy_state = kivy_state_variables()
    content = MDLabel(
        font_style='Caption',
        theme_text_color='Primary',
        text=no_search_res_found if kivy_state.searching_text else label_str,
        halign='center',
        size_hint_y=None,
        valign='top')
    return content


def retrieve_secondary_text(mail):
    """Retriving mail details"""
    secondary_txt_len = 10
    third_txt_len = 25
    dot_str = '...........'
    dot_str2 = '...!'
    third_text = mail[3].replace('\n', ' ')

    if len(third_text) > third_txt_len:
        if len(mail[2]) > secondary_txt_len:  # pylint: disable=no-else-return
            return mail[2][:secondary_txt_len] + dot_str
        else:
            return mail[2] + '\n' + " " + (third_text[:third_txt_len] + dot_str2)
    else:
        return third_text


def set_mail_details(mail):
    """Setting mail details"""
    mail_details_data = {
        'text': mail[1].strip(),
        'secondary_text': retrieve_secondary_text(mail),
        'ackdata': mail[5],
        'senttime': mail[6]
    }
    return mail_details_data


def mdlist_message_content(queryreturn, data):
    """Set Mails details in MD_list"""
    for mail in queryreturn:
        mdlist_data = set_mail_details(mail)
        data.append(mdlist_data)


def msg_content_length(body, subject, max_length=50):
    """This function concatinate body and subject if len(subject) > 50"""
    continue_str = '........'
    if len(subject) >= max_length:
        subject = subject[:max_length] + continue_str
    else:
        subject = ((subject + ',' + body)[0:50] + continue_str).replace('\t', '').replace('  ', '')
    return subject


def composer_common_dialog(alert_msg):
    """Common alert popup for message composer"""
    is_android_width = .8
    other_platform_width = .55
    dialog_height = .25
    width = is_android_width if platform == 'android' else other_platform_width

    dialog_box = MDDialog(
        text=alert_msg,
        size_hint=(width, dialog_height),
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
