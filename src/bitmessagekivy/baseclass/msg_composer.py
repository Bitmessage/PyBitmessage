# pylint: disable=unused-argument, consider-using-f-string, too-many-ancestors
# pylint: disable=no-member, no-name-in-module, too-few-public-methods, no-name-in-module
"""
    Message composer screen UI
"""

import logging

from kivy.app import App
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
)
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.screenmanager import Screen

from kivymd.uix.textfield import MDTextField

from pybitmessage import state
from pybitmessage.bitmessagekivy.get_platform import platform
from pybitmessage.bitmessagekivy.baseclass.common import (
    toast, kivy_state_variables, composer_common_dialog
)

logger = logging.getLogger('default')


class Create(Screen):
    """Creates Screen class for kivy Ui"""

    def __init__(self, **kwargs):
        """Getting Labels and address from addressbook"""
        super(Create, self).__init__(**kwargs)
        self.kivy_running_app = App.get_running_app()
        self.kivy_state = kivy_state_variables()
        self.dropdown_widget = DropDownWidget()
        self.dropdown_widget.ids.txt_input.starting_no = 2
        self.add_widget(self.dropdown_widget)
        self.children[0].ids.id_scroll.bind(scroll_y=self.check_scroll_y)

    def check_scroll_y(self, instance, somethingelse):  # pylint: disable=unused-argument
        """show data on scroll down"""
        if self.children[1].ids.composer_dropdown.is_open:
            self.children[1].ids.composer_dropdown.is_open = False


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

    def __init__(self, **kwargs):
        super(DropDownWidget, self).__init__(**kwargs)
        self.kivy_running_app = App.get_running_app()
        self.kivy_state = kivy_state_variables()

    @staticmethod
    def callback_for_msgsend(dt=0):  # pylint: disable=unused-argument
        """Callback method for messagesend"""
        state.kivyapp.root.ids.id_create.children[0].active = False
        state.in_sent_method = True
        state.kivyapp.back_press()
        toast("sent")

    def reset_composer(self):
        """Method will reset composer"""
        self.ids.ti.text = ""
        self.ids.composer_dropdown.text = "Select"
        self.ids.txt_input.text = ""
        self.ids.subject.text = ""
        self.ids.body.text = ""
        toast("Reset message")

    def auto_fill_fromaddr(self):
        """Fill the text automatically From Address"""
        self.ids.ti.text = self.ids.composer_dropdown.text
        self.ids.ti.focus = True

    def is_camara_attached(self):
        """Checks the camera availability in device"""
        self.parent.parent.parent.ids.id_scanscreen.check_camera()
        is_available = self.parent.parent.parent.ids.id_scanscreen.camera_available
        return is_available

    @staticmethod
    def camera_alert():
        """Show camera availability alert message"""
        feature_unavailable = 'Currently this feature is not available!'
        cam_not_available = 'Camera is not available!'
        alert_text = feature_unavailable if platform == 'android' else cam_not_available
        composer_common_dialog(alert_text)


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
        max_recipient_len = 10
        box_height = 250
        box_max_height = 400

        matches = [self.word_list[i] for i in range(
            len(self.word_list)) if self.word_list[
                i][:self.starting_no] == value[:self.starting_no]]
        display_data = []
        for i in matches:
            display_data.append({'text': i})
        self.parent.parent.parent.parent.parent.ids.rv.data = display_data
        if len(matches) <= max_recipient_len:
            self.parent.height = (box_height + (len(matches) * 20))
        else:
            self.parent.height = box_max_height

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """Keyboard on key Down"""
        if self.suggestion_text and keycode[1] == 'tab' and modifiers is None:
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
            logger.debug("selection changed to %s", rv.data[index])
            rv.parent.txt_input.text = rv.parent.txt_input.text.replace(
                rv.parent.txt_input.text, rv.data[index]["text"]
            )
