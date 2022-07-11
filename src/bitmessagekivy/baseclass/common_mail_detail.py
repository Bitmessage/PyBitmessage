# pylint: disable=no-name-in-module, attribute-defined-outside-init, import-error
"""
    All Common widgets of kivy are managed here.
"""

from bitmessagekivy.baseclass.maildetail import MailDetail
from bitmessagekivy.baseclass.common import kivy_state_variables


def mail_detail_screen(screen_name, msg_id, instance, folder, *args):  # pylint: disable=unused-argument
    """Common function for all screens to open Mail detail."""
    kivy_state = kivy_state_variables()
    if instance.open_progress == 0.0:
        kivy_state.detailPageType = folder
        kivy_state.mail_id = msg_id
        if screen_name.manager:
            src_mng_obj = screen_name.manager
        else:
            src_mng_obj = screen_name.parent.parent
        src_mng_obj.screens[11].clear_widgets()
        src_mng_obj.screens[11].add_widget(MailDetail())
        src_mng_obj.current = "mailDetail"
