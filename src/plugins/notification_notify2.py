# -*- coding: utf-8 -*-
"""
src/plugins/notification_notify2.py
===================================
"""
# pylint: disable=import-error

import gi
from gi.repository import Notify

gi.require_version('Notify', '0.7')

Notify.init('pybitmessage')


def connect_plugin(title, subtitle, category, label, icon):
    """Plugin for notify2"""
    # pylint: disable=unused-argument
    if not icon:
        icon = 'mail-message-new' if category == 2 else 'pybitmessage'
    connect_plugin.notification.update(title, subtitle, icon)
    connect_plugin.notification.show()


connect_plugin.notification = Notify.Notification.new("Init", "Init")
