from datetime import datetime
from kivy.core.window import Window
from kivy.metrics import dp
from kivymd.uix.list import (
    ILeftBody,
    IRightBodyTouch,
)
from kivy.uix.image import Image
from kivymd.uix.label import MDLabel
from kivymd.toast import kivytoast
from kivymd.uix.card import MDCardSwipe
from kivymd.uix.chip import MDChip
from kivy.properties import (
    NumericProperty,
    StringProperty
)
# from pybitmessage.get_platform import platform
platform = "linux"


ThemeClsColor = [0.12, 0.58, 0.95, 1]


data_screens = {
    "MailDetail": {
        "kv_string": "maildetail",
        "Factory": "MailDetail()",
        "name_screen": "mailDetail",
        "object": 0,
        "Import": "from pybitmessage.baseclass.maildetail import MailDetail",
    },
}


def chipTag(text):
    """This method is used for showing chip tag"""
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


def showLimitedCnt(total_msg):
    """This method set the total count limit in badge_text"""
    return "99+" if total_msg > 99 else str(total_msg)


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


class CutsomSwipeToDeleteItem(MDCardSwipe):
    """Custom swipe delete class for App UI"""
    text = StringProperty()
    cla = Window.size[0] / 2
    swipe_distance = NumericProperty(cla)
    opening_time = NumericProperty(0.5)
