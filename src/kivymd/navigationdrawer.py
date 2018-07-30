# -*- coding: utf-8 -*-
from kivy.animation import Animation
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty
from kivymd.elevationbehavior import ElevationBehavior
from kivymd.icon_definitions import md_icons
from kivymd.label import MDLabel
from kivymd.list import OneLineIconListItem, ILeftBody, BaseListItem
from kivymd.slidingpanel import SlidingPanel
from kivymd.theming import ThemableBehavior

Builder.load_string('''
<NavDrawerToolbar@Toolbar>
    canvas:
        Color:
            rgba: root.theme_cls.divider_color
        Line:
            points: self.x, self.y, self.x+self.width,self.y

<NavigationDrawer>
    _list: list
    elevation: 0
    canvas:
        Color:
            rgba: root.theme_cls.bg_light
        Rectangle:
            size: root.size
            pos: root.pos
    NavDrawerToolbar:
        title: root.title
        opposite_colors: False
        title_theme_color: 'Secondary'
        background_color: root.theme_cls.bg_light
        elevation: 0
    ScrollView:
        do_scroll_x: False
        MDList:
            id: ml
            id: list

<NavigationDrawerIconButton>
    NDIconLabel:
        id: _icon
        font_style: 'Icon'
        theme_text_color: 'Secondary'
''')


class NavigationDrawer(SlidingPanel, ThemableBehavior, ElevationBehavior):
    title = StringProperty()

    _list = ObjectProperty()

    def add_widget(self, widget, index=0):
        if issubclass(widget.__class__, BaseListItem):
            self._list.add_widget(widget, index)
            widget.bind(on_release=lambda x: self.toggle())
        else:
            super(NavigationDrawer, self).add_widget(widget, index)

    def _get_main_animation(self, duration, t, x, is_closing):
        a = super(NavigationDrawer, self)._get_main_animation(duration, t, x,
                                                              is_closing)
        a &= Animation(elevation=0 if is_closing else 5, t=t, duration=duration)
        return a


class NDIconLabel(ILeftBody, MDLabel):
    pass


class NavigationDrawerIconButton(OneLineIconListItem):
    icon = StringProperty()

    def on_icon(self, instance, value):
        self.ids['_icon'].text = u"{}".format(md_icons[value])
