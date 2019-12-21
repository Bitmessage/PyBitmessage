# -*- coding: utf-8 -*-
"""
Indicator plugin using libmessaging
"""

import gi
gi.require_version('MessagingMenu', '1.0')  # noqa:E402
from gi.repository import MessagingMenu

from pybitmessage.bitmessageqt.utils import str_broadcast_subscribers
from pybitmessage.tr import _translate


class IndicatorLibmessaging(object):
    """Plugin for libmessage indicator"""
    def __init__(self, form):
        try:
            self.app = MessagingMenu.App(desktop_id='pybitmessage.desktop')
            self.app.register()
            self.app.connect('activate-source', self.activate)
        except:
            self.app = None
            return

        self._menu = {
            'send': unicode(_translate('MainWindow', 'Send')),
            'messages': unicode(_translate('MainWindow', 'Messages')),
            'subscriptions': unicode(_translate('MainWindow', 'Subscriptions'))
        }

        self.new_message_item = self.new_broadcast_item = None
        self.form = form
        self.show_unread()

    def __del__(self):
        if self.app:
            self.app.unregister()

    def activate(self, app, source):  # pylint: disable=unused-argument
        """Activate the libmessaging indicator plugin"""
        self.form.appIndicatorInbox(
            self.new_message_item if source == 'messages'
            else self.new_broadcast_item
        )

    def show_unread(self, draw_attention=False):
        """
        show the number of unread messages and subscriptions
        on the messaging menu
        """
        for source, count in zip(
                ('messages', 'subscriptions'),
                self.form.getUnread()
        ):
            if count > 0:
                if self.app.has_source(source):
                    self.app.set_source_count(source, count)
                else:
                    self.app.append_source_with_count(
                        source, None, self._menu[source], count)
                if draw_attention:
                    self.app.draw_attention(source)

    # update the Ubuntu messaging menu
    def __call__(self, draw_attention, item=None, to_label=None):
        if not self.app:
            return
        # remember this item to that the activate() can find it
        if item:
            if to_label == str_broadcast_subscribers:
                self.new_broadcast_item = item
            else:
                self.new_message_item = item

        self.show_unread(draw_attention)


connect_plugin = IndicatorLibmessaging
