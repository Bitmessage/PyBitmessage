# -*- coding: utf-8 -*-

import os

from xdg import BaseDirectory, Menu, Exceptions


class DesktopXDG(object):
    """pyxdg Freedesktop desktop implementation"""
    def __init__(self):
        try:
            self.desktop = Menu.parse().getMenu('Office').getMenuEntry(
                'pybitmessage.desktop').DesktopEntry
        except Exceptions.ParsingError:
            raise TypeError  # TypeError disables startonlogon
        appimage = os.getenv('APPIMAGE')
        if appimage:
            self.desktop.set('Exec', appimage)

    def adjust_startonlogon(self, autostart=False):
        """Configure autostart according to settings"""
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
