# pylint: disable=import-error, no-name-in-module, simplifiable-if-expression, no-self-use

"""
Kivy Trash Box screen
"""

from kivy.clock import Clock
from kivy.properties import (
    ListProperty,
    StringProperty
)
from kivy.uix.screenmanager import Screen

from baseclass.common import showLimitedCnt


from kivymd.uix.label import MDLabel

from pybitmessage import state
from pybitmessage import kivy_state


class Trash(Screen):
    """Trash Screen class for kivy Ui"""

    trash_messages = ListProperty()
    has_refreshed = True
    delete_index = None
    table_name = StringProperty()

    def __init__(self, *args, **kwargs):
        """Trash method, delete sent message and add in Trash"""
        super(Trash, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self):
        """Clock Schdule for method trash screen"""
        if state.association == '':
            if state.kivyapp.variable_1:
                state.association = state.kivyapp.variable_1[0]
        self.ids.tag_label.text = ''
        if len(self.trash_messages):
            self.ids.ml.clear_widgets()
            self.ids.tag_label.text = 'Trash'
            # src_mng_obj = state.kivyapp.root.children[2].children[0].ids
            # src_mng_obj.trash_cnt.badge_text = state.trash_count
            self.set_TrashCnt(kivy_state.trash_count)
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

    def set_TrashCnt(self, Count):
        """This method is used to set trash message count"""
        trashCnt_obj = state.kivyapp.root.ids.content_drawer.ids.trash_cnt
        trashCnt_obj.ids.badge_txt.text = showLimitedCnt(int(Count))

    def set_mdList(self):
        """This method is used to create the mdlist"""
        total_trash_msg = len(self.ids.ml.children)
        self.has_refreshed = True if total_trash_msg != len(
            self.ids.ml.children) else False

    def on_swipe_complete(self, instance):
        """call on swipe left"""
        instance.ids.delete_msg.disabled = bool(instance.state == 'closed')

    def check_scroll_y(self):
        """Load data on scroll"""
        if self.ids.scroll_y.scroll_y <= -0.0 and self.has_refreshed:
            self.ids.scroll_y.scroll_y = 0.06
