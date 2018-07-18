# -*- coding: utf-8 -*-

from kivy.lang import Builder
from kivy.uix.modalview import ModalView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivymd.button import MDFlatButton, MDIconButton
from kivymd.theming import ThemableBehavior
from kivymd.elevationbehavior import ElevationBehavior
from kivy.properties import ObjectProperty, ListProperty
from kivymd.label import MDLabel
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivymd.color_definitions import colors

Builder.load_string("""
#:import SingleLineTextField kivymd.textfields.SingleLineTextField
#:import MDTabbedPanel kivymd.tabs.MDTabbedPanel
#:import MDTab kivymd.tabs.MDTab
<MDThemePicker>:
    size_hint: (None, None)
    size: dp(260), dp(120)+dp(290)
    pos_hint: {'center_x': .5, 'center_y': .5}
    canvas:
        Color:
            rgb: app.theme_cls.primary_color
        Rectangle:
            size: dp(260), dp(120)
            pos: root.pos[0], root.pos[1] + root.height-dp(120)
        Color:
            rgb: app.theme_cls.bg_normal
        Rectangle:
            size: dp(260), dp(290)
            pos: root.pos[0], root.pos[1] + root.height-(dp(120)+dp(290))

    MDFlatButton:
        pos: root.pos[0]+root.size[0]-dp(72), root.pos[1] + dp(10)
        text: "Close"
        on_release: root.dismiss()
    MDLabel:
        font_style: "Headline"
        text: "Change theme"
        size_hint: (None, None)
        size: dp(160), dp(50)
        pos_hint: {'center_x': 0.5, 'center_y': 0.9}
    MDTabbedPanel:
        size_hint: (None, None)
        size: dp(260), root.height-dp(135)
        pos_hint: {'center_x': 0.5, 'center_y': 0.475}
        id: tab_panel
        tab_display_mode:'text'

        MDTab:
            name: 'color'
            text: "Theme Color"
            BoxLayout:
                spacing: dp(4)
                size_hint: (None, None)
                size: dp(270), root.height  # -dp(120)
                pos_hint: {'center_x': 0.532, 'center_y': 0.89}
                orientation: 'vertical'
                BoxLayout:
                    size_hint: (None, None)
                    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                    size: dp(230), dp(40)
                    pos: self.pos
                    halign: 'center'
                    orientation: 'horizontal'
                    BoxLayout:
                        MDIconButton:
                            size: dp(40), dp(40)
                            pos: self.pos
                            size_hint: (None, None)
                            canvas:
                                Color:
                                    rgba: root.rgb_hex('Red')
                                Ellipse:
                                    size: self.size
                                    pos: self.pos
                            on_release: app.theme_cls.primary_palette = 'Red'
                    BoxLayout:
                        MDIconButton:
                            size: dp(40), dp(40)
                            pos: self.pos
                            size_hint: (None, None)
                            canvas:
                                Color:
                                    rgba: root.rgb_hex('Pink')
                                Ellipse:
                                    size: self.size
                                    pos: self.pos
                            on_release: app.theme_cls.primary_palette = 'Pink'
                    BoxLayout:
                        MDIconButton:
                            size: dp(40), dp(40)
                            pos: self.pos
                            size_hint: (None, None)
                            canvas:
                                Color:
                                    rgba: root.rgb_hex('Purple')
                                Ellipse:
                                    size: self.size
                                    pos: self.pos
                            on_release: app.theme_cls.primary_palette = 'Purple'
                    BoxLayout:
                        MDIconButton:
                            size: dp(40), dp(40)
                            pos: self.pos
                            size_hint: (None, None)
                            canvas:
                                Color:
                                    rgba: root.rgb_hex('DeepPurple')
                                Ellipse:
                                    size: self.size
                                    pos: self.pos
                            on_release: app.theme_cls.primary_palette = 'DeepPurple'
                BoxLayout:
                    size_hint: (None, None)
                    pos_hint: {'center_x': .5, 'center_y': 0.5}
                    size: dp(230), dp(40)
                    pos: self.pos
                    halign: 'center'
                    orientation: 'horizontal'
                    BoxLayout:
                        MDIconButton:
                            size: dp(40), dp(40)
                            pos: self.pos
                            size_hint: (None, None)
                            canvas:
                                Color:
                                    rgba: root.rgb_hex('Indigo')
                                Ellipse:
                                    size: self.size
                                    pos: self.pos
                            on_release: app.theme_cls.primary_palette = 'Indigo'
                    BoxLayout:
                        MDIconButton:
                            size: dp(40), dp(40)
                            pos: self.pos
                            size_hint: (None, None)
                            canvas:
                                Color:
                                    rgba: root.rgb_hex('Blue')
                                Ellipse:
                                    size: self.size
                                    pos: self.pos
                            on_release: app.theme_cls.primary_palette = 'Blue'
                    BoxLayout:
                        MDIconButton:
                            size: dp(40), dp(40)
                            pos: self.pos
                            size_hint: (None, None)
                            canvas:
                                Color:
                                    rgba: root.rgb_hex('LightBlue')
                                Ellipse:
                                    size: self.size
                                    pos: self.pos
                            on_release: app.theme_cls.primary_palette = 'LightBlue'
                    BoxLayout:
                        MDIconButton:
                            size: dp(40), dp(40)
                            pos: self.pos
                            size_hint: (None, None)
                            canvas:
                                Color:
                                    rgba: root.rgb_hex('Cyan')
                                Ellipse:
                                    size: self.size
                                    pos: self.pos
                            on_release: app.theme_cls.primary_palette = 'Cyan'
                BoxLayout:
                    size_hint: (None, None)
                    pos_hint: {'center_x': .5, 'center_y': 0.5}
                    size: dp(230), dp(40)
                    pos: self.pos
                    halign: 'center'
                    orientation: 'horizontal'
                    padding: 0, 0, 0, dp(1)
                    BoxLayout:
                        MDIconButton:
                            size: dp(40), dp(40)
                            pos: self.pos
                            size_hint: (None, None)
                            canvas:
                                Color:
                                    rgba: root.rgb_hex('Teal')
                                Ellipse:
                                    size: self.size
                                    pos: self.pos
                            on_release: app.theme_cls.primary_palette = 'Teal'
                    BoxLayout:
                        MDIconButton:
                            size: dp(40), dp(40)
                            pos: self.pos
                            size_hint: (None, None)
                            canvas:
                                Color:
                                    rgba: root.rgb_hex('Green')
                                Ellipse:
                                    size: self.size
                                    pos: self.pos
                            on_release: app.theme_cls.primary_palette = 'Green'
                    BoxLayout:
                        MDIconButton:
                            size: dp(40), dp(40)
                            pos: self.pos
                            size_hint: (None, None)
                            canvas:
                                Color:
                                    rgba: root.rgb_hex('LightGreen')
                                Ellipse:
                                    size: self.size
                                    pos: self.pos
                            on_release: app.theme_cls.primary_palette = 'LightGreen'
                    BoxLayout:
                        MDIconButton:
                            size: dp(40), dp(40)
                            pos: self.pos
                            size_hint: (None, None)
                            canvas:
                                Color:
                                    rgba: root.rgb_hex('Lime')
                                Ellipse:
                                    size: self.size
                                    pos: self.pos
                            on_release: app.theme_cls.primary_palette = 'Lime'
                BoxLayout:
                    size_hint: (None, None)
                    pos_hint: {'center_x': .5, 'center_y': 0.5}
                    size: dp(230), dp(40)
                    pos: self.pos
                    orientation: 'horizontal'
                    halign: 'center'
                    padding: 0, 0, 0, dp(1)
                    BoxLayout:
                        MDIconButton:
                            size: dp(40), dp(40)
                            pos: self.pos
                            size_hint: (None, None)
                            canvas:
                                Color:
                                    rgba: root.rgb_hex('Yellow')
                                Ellipse:
                                    size: self.size
                                    pos: self.pos
                            on_release: app.theme_cls.primary_palette = 'Yellow'
                    BoxLayout:
                        MDIconButton:
                            size: dp(40), dp(40)
                            pos: self.pos
                            size_hint: (None, None)
                            canvas:
                                Color:
                                    rgba: root.rgb_hex('Amber')
                                Ellipse:
                                    size: self.size
                                    pos: self.pos
                            on_release: app.theme_cls.primary_palette = 'Amber'
                    BoxLayout:
                        MDIconButton:
                            size: dp(40), dp(40)
                            pos: self.pos
                            size_hint: (None, None)
                            canvas:
                                Color:
                                    rgba: root.rgb_hex('Orange')
                                Ellipse:
                                    size: self.size
                                    pos: self.pos
                            on_release: app.theme_cls.primary_palette = 'Orange'
                    BoxLayout:
                        MDIconButton:
                            size: dp(40), dp(40)
                            pos: self.pos
                            size_hint: (None, None)
                            canvas:
                                Color:
                                    rgba: root.rgb_hex('DeepOrange')
                                Ellipse:
                                    size: self.size
                                    pos: self.pos
                            on_release: app.theme_cls.primary_palette = 'DeepOrange'
                BoxLayout:
                    size_hint: (None, None)
                    pos_hint: {'center_x': .5, 'center_y': 0.5}
                    size: dp(230), dp(40)
                    #pos: self.pos
                    orientation: 'horizontal'
                    padding: 0, 0, 0, dp(1)
                    BoxLayout:
                        MDIconButton:
                            size: dp(40), dp(40)
                            size_hint: (None, None)
                            canvas:
                                Color:
                                    rgba: root.rgb_hex('Brown')
                                Ellipse:
                                    size: self.size
                                    pos: self.pos
                            on_release: app.theme_cls.primary_palette = 'Brown'
                    BoxLayout:
                        MDIconButton:
                            size: dp(40), dp(40)
                            pos: self.pos
                            size_hint: (None, None)
                            canvas:
                                Color:
                                    rgba: root.rgb_hex('Grey')
                                Ellipse:
                                    size: self.size
                                    pos: self.pos
                            on_release: app.theme_cls.primary_palette = 'Grey'
                    BoxLayout:
                        MDIconButton:
                            size: dp(40), dp(40)
                            #pos: self.pos
                            size_hint: (None, None)
                            canvas:
                                Color:
                                    rgba: root.rgb_hex('BlueGrey')
                                Ellipse:
                                    size: self.size
                                    pos: self.pos
                            on_release: app.theme_cls.primary_palette = 'BlueGrey'
                    BoxLayout:
                        MDIconButton:
                            size: dp(40), dp(40)
                            size_hint: (None, None)
                            canvas:
                                Color:
                                    rgba: app.theme_cls.bg_normal
                                Ellipse:
                                    size: self.size
                                    pos: self.pos
                            disabled: True

        MDTab:
            name: 'style'
            text: "Theme Style"
            BoxLayout:
                size_hint: (None, None)
                pos_hint: {'center_x': .3, 'center_y': 0.5}
                size: self.size
                pos: self.pos
                halign: 'center'
                spacing: dp(10)
                BoxLayout:
                    halign: 'center'
                    size_hint: (None, None)
                    size: dp(100), dp(100)
                    pos: self.pos
                    pos_hint: {'center_x': .3, 'center_y': 0.5}
                    MDIconButton:
                        size: dp(100), dp(100)
                        pos: self.pos
                        size_hint: (None, None)
                        canvas:
                            Color:
                                rgba: 1, 1, 1, 1
                            Ellipse:
                                size: self.size
                                pos: self.pos
                            Color:
                                rgba: 0, 0, 0, 1
                            Line:
                                width: 1.
                                circle: (self.center_x, self.center_y, 50)
                        on_release: app.theme_cls.theme_style = 'Light'
                BoxLayout:
                    halign: 'center'
                    size_hint: (None, None)
                    size: dp(100), dp(100)
                    MDIconButton:
                        size: dp(100), dp(100)
                        pos: self.pos
                        size_hint: (None, None)
                        canvas:
                            Color:
                                rgba: 0, 0, 0, 1
                            Ellipse:
                                size: self.size
                                pos: self.pos
                        on_release: app.theme_cls.theme_style = 'Dark'
""")


class MDThemePicker(ThemableBehavior, FloatLayout, ModalView, ElevationBehavior):
    # background_color = ListProperty([0, 0, 0, 0])
    time = ObjectProperty()

    def __init__(self, **kwargs):
        super(MDThemePicker, self).__init__(**kwargs)

    def rgb_hex(self, col):
        return get_color_from_hex(colors[col][self.theme_cls.accent_hue])


if __name__ == "__main__":
    from kivy.app import App
    from kivymd.theming import ThemeManager

    class ThemePickerApp(App):
        theme_cls = ThemeManager()

        def build(self):
            main_widget = Builder.load_string("""
#:import MDRaisedButton kivymd.button.MDRaisedButton
#:import MDThemePicker kivymd.theme_picker.MDThemePicker
FloatLayout:
    MDRaisedButton:
        size_hint: None, None
        pos_hint: {'center_x': .5, 'center_y': .5}
        size: 3 * dp(48), dp(48)
        center_x: self.parent.center_x
        text: 'Open theme picker'
        on_release: MDThemePicker().open()
        opposite_colors: True
""")
            return main_widget

    ThemePickerApp().run()
