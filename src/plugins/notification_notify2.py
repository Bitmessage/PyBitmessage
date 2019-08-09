# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *
import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify

Notify.init('pybitmessage')

def connect_plugin(title, subtitle, category, label, icon):
    if not icon:
        icon = 'mail-message-new' if category == 2 else 'pybitmessage'
    connect_plugin.notification.update(title, subtitle, icon)
    connect_plugin.notification.show()

connect_plugin.notification = Notify.Notification.new("Init", "Init")
