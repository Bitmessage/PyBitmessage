# -*- coding: utf-8 -*-

import os

from xdg import BaseDirectory, Menu


class DesktopXDG(object):
    """pyxdg Freedesktop desktop implementation"""
    def __init__(self):
        menu_entry = Menu.parse().getMenu('Office').getMenuEntry(
            'pybitmessage.desktop')
        self.desktop = menu_entry.DesktopEntry if menu_entry else None

    def adjust_startonlogon(self, autostart=False):
        """Configure autostart according to settings"""
        if not self.desktop:
            return

        autostart_path = os.path.join(
            BaseDirectory.xdg_config_home, 'autostart', 'pybitmessage.desktop')
        if autostart:
            self.desktop.write(autostart_path)
        else:
            try:
                os.remove(autostart_path)
            except OSError:
                pass


connect_plugin = DesktopXDG
