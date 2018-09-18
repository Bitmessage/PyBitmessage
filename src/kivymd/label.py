# -*- coding: utf-8 -*-
from kivy.lang import Builder
from kivy.metrics import sp
from kivy.properties import OptionProperty, DictProperty, ListProperty
from kivy.uix.label import Label
from kivymd.material_resources import DEVICE_TYPE
from kivymd.theming import ThemableBehavior

Builder.load_string('''
<MDLabel>
    disabled_color: self.theme_cls.disabled_hint_text_color
    text_size: (self.width, None)
''')


class MDLabel(ThemableBehavior, Label):
    font_style = OptionProperty(
        'Body1', options=['Body1', 'Body2', 'Caption', 'Subhead', 'Title',
                          'Headline', 'Display1', 'Display2', 'Display3',
                          'Display4', 'Button', 'Icon'])

    # Font, Bold, Mobile size, Desktop size (None if same as Mobile)
    _font_styles = DictProperty({'Body1': ['Roboto', False, 14, 13],
                                 'Body2': ['Roboto', True, 14, 13],
                                 'Caption': ['Roboto', False, 12, None],
                                 'Subhead': ['Roboto', False, 16, 15],
                                 'Title': ['Roboto', True, 20, None],
                                 'Headline': ['Roboto', False, 24, None],
                                 'Display1': ['Roboto', False, 34, None],
                                 'Display2': ['Roboto', False, 45, None],
                                 'Display3': ['Roboto', False, 56, None],
                                 'Display4': ['RobotoLight', False, 112, None],
                                 'Button': ['Roboto', True, 14, None],
                                 'Icon': ['Icons', False, 24, None]})

    theme_text_color = OptionProperty(None, allownone=True,
                                      options=['Primary', 'Secondary', 'Hint',
                                               'Error', 'Custom'])

    text_color = ListProperty(None, allownone=True)

    _currently_bound_property = {}

    def __init__(self, **kwargs):
        super(MDLabel, self).__init__(**kwargs)
        self.on_theme_text_color(None, self.theme_text_color)
        self.on_font_style(None, self.font_style)
        self.on_opposite_colors(None, self.opposite_colors)

    def on_font_style(self, instance, style):
        info = self._font_styles[style]
        self.font_name = info[0]
        self.bold = info[1]
        if DEVICE_TYPE == 'desktop' and info[3] is not None:
            self.font_size = sp(info[3])
        else:
            self.font_size = sp(info[2])

    def on_theme_text_color(self, instance, value):
        t = self.theme_cls
        op = self.opposite_colors
        setter = self.setter('color')
        t.unbind(**self._currently_bound_property)
        c = {}
        if value == 'Primary':
            c = {'text_color' if not op else 'opposite_text_color': setter}
            t.bind(**c)
            self.color = t.text_color if not op else t.opposite_text_color
        elif value == 'Secondary':
            c = {'secondary_text_color' if not op else
                 'opposite_secondary_text_color': setter}
            t.bind(**c)
            self.color = t.secondary_text_color if not op else \
                t.opposite_secondary_text_color
        elif value == 'Hint':
            c = {'disabled_hint_text_color' if not op else
                 'opposite_disabled_hint_text_color': setter}
            t.bind(**c)
            self.color = t.disabled_hint_text_color if not op else \
                t.opposite_disabled_hint_text_color
        elif value == 'Error':
            c = {'error_color': setter}
            t.bind(**c)
            self.color = t.error_color
        elif value == 'Custom':
            self.color = self.text_color if self.text_color else (0, 0, 0, 1)
        self._currently_bound_property = c

    def on_text_color(self, *args):
        if self.theme_text_color == 'Custom':
            self.color = self.text_color

    def on_opposite_colors(self, instance, value):
        self.on_theme_text_color(self, self.theme_text_color)
