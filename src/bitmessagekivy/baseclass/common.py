# pylint: disable=no-name-in-module, attribute-defined-outside-init, import-error
"""
    All Common widgets of kivy are managed here.
"""

from datetime import datetime

from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.properties import (
    NumericProperty,
    StringProperty
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

from bitmessagekivy.get_platform import platform


ThemeClsColor = [0.12, 0.58, 0.95, 1]


data_screens = {
    "MailDetail": {
        "kv_string": "maildetail",
        "Factory": "MailDetail()",
        "name_screen": "mailDetail",
        "object": 0,
        "Import": "from bitmessagekivy.baseclass.maildetail import MailDetail",
    },
}


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
    return max_msg_count if total_msg > 99 else str(total_msg)


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
    display_data = (
        action_time.strftime("%d/%m/%Y")
        if duration.days >= 365
        else action_time.strftime("%I:%M %p").lstrip("0")
        if duration.days == 0 and crnt_date.strftime("%d/%m/%Y") == action_time.strftime("%d/%m/%Y")
        else action_time.strftime("%d %b")
    )
    return display_data


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
    kivy_running_app = App.get_running_app()
    kivy_state = kivy_running_app.kivy_state_obj
    content = MDLabel(
        font_style='Caption',
        theme_text_color='Primary',
        text=no_search_res_found if kivy_state.searching_text else label_str,
        halign='center',
        size_hint_y=None,
        valign='top')
    return content


def set_mail_details(mail):
    """Return mail details"""
    secondary_txt_len = 10
    third_txt_len = 25
    dot_str = '...........'
    dot_str2 = '...!'
    third_text = mail[3].replace('\n', ' ')

    mail_details_data = {
        'text': mail[1].strip(),
        'secondary_text': mail[2][:secondary_txt_len] + dot_str if len(mail[2]) > secondary_txt_len
        else mail[2] + '\n' + " " + (third_text[:third_txt_len] + dot_str2)
        if len(third_text) > third_txt_len else third_text,
        'ackdata': mail[5], 'senttime': mail[6]
    }
    return mail_details_data


def mdlist_message_content(queryreturn, data):
    """Set Mails details in MD_list"""
    for mail in queryreturn:
        mdlist_data = set_mail_details(mail)
        data.append(mdlist_data)
