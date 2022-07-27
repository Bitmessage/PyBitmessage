# pylint: disable=import-error, no-name-in-module
# pylint: disable=import-outside-toplevel, too-many-function-args

"""
Kivy My Address Book screen
"""

from pybitmessage.get_platform import platform
from functools import partial
from pybitmessage.bmconfigparser import BMConfigParser
from kivy.clock import Clock
from kivy.properties import (
    ListProperty,
    StringProperty
)
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.list import (
    IRightBodyTouch,
    TwoLineAvatarIconListItem,
)
from kivymd.uix.selectioncontrol import MDSwitch
from kivy.uix.screenmanager import Screen

from pybitmessage import state

from baseclass.common import (
    avatarImageFirstLetter, AvatarSampleWidget, ThemeClsColor,
    toast
)
from baseclass.popup import MyaddDetailPopup


class ToggleBtn(IRightBodyTouch, MDSwitch):
    """ToggleBtn class for kivy Ui"""


class CustomTwoLineAvatarIconListItem(TwoLineAvatarIconListItem):
    """CustomTwoLineAvatarIconListItem class for kivy Ui"""


class BadgeText(IRightBodyTouch, MDLabel):
    """BadgeText class for kivy Ui"""


class MyAddress(Screen):
    """MyAddress screen class for kivy Ui"""

    address_label = StringProperty()
    text_address = StringProperty()
    addresses_list = ListProperty()
    has_refreshed = True
    is_add_created = False

    def __init__(self, *args, **kwargs):
        """Clock schdule for method Myaddress accounts"""
        super().__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock schdule for method Myaddress accounts"""
        # pylint: disable=unnecessary-lambda
        self.addresses_list = BMConfigParser().addresses()
        if state.searcing_text:
            self.ids.refresh_layout.scroll_y = 1.0
            filtered_list = [
                x for x in BMConfigParser().addresses()
                if self.filter_address(x)
            ]
            self.addresses_list = filtered_list
        self.addresses_list = list(reversed(self.addresses_list))
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
            # meny._txt_right_pad = dp(70)
            try:
                meny.canvas.children[3].rgba = [0, 0, 0, 0] if is_enable == 'true' else [0.5, 0.5, 0.5, 0.5]
            except Exception:
                pass
            meny.add_widget(AvatarSampleWidget(
                source=state.imageDir + f'/text_images/{avatarImageFirstLetter(item["text"].strip())}.png'))  # noqa:E999
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

    def myadd_detail(self, fromaddress, label, *args):
        """Load myaddresses details"""
        if BMConfigParser().get(fromaddress, 'enabled') == 'true':
            obj = MyaddDetailPopup()
            self.address_label = obj.address_label = label
            self.text_address = obj.address = fromaddress
            width = .9 if platform == 'android' else .6
            self.myadddetail_popup = MDDialog(
                type="custom",
                size_hint=(width, .25),
                content_cls=obj,
            )
            # self.myadddetail_popup.set_normal_height()
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
            # self.tick = 0
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
        instance.parent.parent.canvas.children[3].rgba = [0.5, 0.5, 0.5, 0.5]
        # try:
        #     instance.parent.parent.canvas.children[6].rgba = [0.5, 0.5, 0.5, 0.5]
        # except Exception:
        #     instance.parent.parent.canvas.children[9].rgba = [0.5, 0.5, 0.5, 0.5]
        toast('Address disabled')
        Clock.schedule_once(self.address_permision_callback, 0)

    def enableAddress(self, address, instance):
        """This method is use for enabling address"""
        BMConfigParser().set(address, 'enabled', 'true')
        BMConfigParser().save()
        instance.parent.parent.theme_text_color = 'Custom'
        instance.parent.parent.canvas.children[3].rgba = [0, 0, 0, 0]
        # try:
        #     instance.parent.parent.canvas.children[6].rgba = [0, 0, 0, 0]
        # except Exception:
        #     instance.parent.parent.canvas.children[9].rgba = [0, 0, 0, 0]
        toast('Address Enabled')
        Clock.schedule_once(self.address_permision_callback, 0)

    def address_permision_callback(self, dt=0):
        """callback for enable or disable addresses"""
        addresses = [addr for addr in BMConfigParser().addresses()
                     if BMConfigParser().get(str(addr), 'enabled') == 'true']
        self.parent.parent.ids.content_drawer.ids.btn.values = addresses
        self.parent.parent.ids.sc3.children[1].ids.btn.values = addresses
        state.kivyapp.variable_1 = addresses

    def toggleAction(self, instance):
        """This method is used for enable or disable address"""
        addr = instance.parent.parent.secondary_text
        if instance.active:
            self.enableAddress(addr, instance)
        else:
            self.disableAddress(addr, instance)
