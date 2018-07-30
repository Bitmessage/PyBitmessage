# -*- coding: utf-8 -*-
'''
Buttons
=======

`Material Design spec, Buttons page <https://www.google.com/design/spec/components/buttons.html>`_

`Material Design spec, Buttons: Floating Action Button page <https://www.google.com/design/spec/components/buttons-floating-action-button.html>`_

TO-DO: DOCUMENT MODULE
'''
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.properties import StringProperty, BoundedNumericProperty, \
    ListProperty, AliasProperty, BooleanProperty, NumericProperty, \
    OptionProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.animation import Animation
from kivymd.backgroundcolorbehavior import BackgroundColorBehavior
from kivymd.ripplebehavior import CircularRippleBehavior, \
    RectangularRippleBehavior
from kivymd.elevationbehavior import ElevationBehavior, \
    RoundElevationBehavior
from kivymd.theming import ThemableBehavior
from kivymd.color_definitions import colors

Builder.load_string('''
#:import md_icons kivymd.icon_definitions.md_icons
#:import colors kivymd.color_definitions.colors
#:import MDLabel kivymd.label.MDLabel
<MDIconButton>
    size_hint: (None, None)
    size: (dp(48), dp(48))
    padding: dp(12)
    theme_text_color: 'Primary'
    MDLabel:
        id: _label
        font_style: 'Icon'
        text: u"{}".format(md_icons[root.icon])
        halign: 'center'
        theme_text_color: root.theme_text_color
        text_color: root.text_color
        opposite_colors: root.opposite_colors
        valign: 'middle'

<MDFlatButton>
    canvas:
        Color:
            #rgba: self.background_color if self.state == 'normal' else self._bg_color_down
            rgba: self._current_button_color
        Rectangle:
            size: self.size
            pos: self.pos
    size_hint: (None, None)
    height: dp(36)
    width: _label.texture_size[0] + dp(16)
    padding: (dp(8), 0)
    theme_text_color: 'Custom'
    text_color: root.theme_cls.primary_color
    MDLabel:
        id: _label
        text: root._text
        font_style: 'Button'
        size_hint_x: None
        text_size: (None, root.height)
        height: self.texture_size[1]
        theme_text_color: root.theme_text_color
        text_color: root.text_color
        valign: 'middle'
        halign: 'center'
        opposite_colors: root.opposite_colors

<MDRaisedButton>:
    canvas:
        Clear
        Color:
            rgba: self.background_color_disabled if self.disabled else \
            (self.background_color if self.state == 'normal' else self.background_color_down)
        Rectangle:
            size: self.size
            pos: self.pos

    anchor_x: 'center'
    anchor_y: 'center'
    background_color: root.theme_cls.primary_color
    background_color_down: root.theme_cls.primary_dark
    background_color_disabled: root.theme_cls.divider_color
    theme_text_color: 'Primary'
    MDLabel:
        id: label
        font_style:         'Button'
        text:                root._text
        size_hint:            None, None
        width:                root.width
        text_size:            self.width, None
        height:                self.texture_size[1]
        theme_text_color:    root.theme_text_color
        text_color:         root.text_color
        opposite_colors:    root.opposite_colors
        disabled:            root.disabled
        halign:                'center'
        valign:                'middle'

<MDFloatingActionButton>:
    canvas:
        Clear
        Color:
            rgba: self.background_color_disabled if self.disabled else \
            (self.background_color if self.state == 'normal' else self.background_color_down)
        Ellipse:
            size: self.size
            pos: self.pos

    anchor_x:            'center'
    anchor_y:            'center'
    background_color: root.theme_cls.accent_color
    background_color_down: root.theme_cls.accent_dark
    background_color_disabled: root.theme_cls.divider_color
    theme_text_color: 'Primary'
    MDLabel:
        id: label
        font_style:         'Icon'
        text:                 u"{}".format(md_icons[root.icon])
        size_hint:            None, None
        size:                dp(24), dp(24)
        text_size:            self.size
        theme_text_color:    root.theme_text_color
        text_color:         root.text_color
        opposite_colors:    root.opposite_colors
        disabled:            root.disabled
        halign:                'center'
        valign:                'middle'
''')


class MDIconButton(CircularRippleBehavior, ButtonBehavior, BoxLayout):
    icon = StringProperty('circle')
    theme_text_color = OptionProperty(None, allownone=True,
                                      options=['Primary', 'Secondary', 'Hint',
                                               'Error', 'Custom'])
    text_color = ListProperty(None, allownone=True)
    opposite_colors = BooleanProperty(False)


class MDFlatButton(ThemableBehavior, RectangularRippleBehavior,
                   ButtonBehavior, BackgroundColorBehavior, AnchorLayout):
    width = BoundedNumericProperty(dp(64), min=dp(64), max=None,
                                   errorhandler=lambda x: dp(64))

    text_color = ListProperty()

    text = StringProperty('')
    theme_text_color = OptionProperty(None, allownone=True,
                                      options=['Primary', 'Secondary', 'Hint',
                                               'Error', 'Custom'])
    text_color = ListProperty(None, allownone=True)

    _text = StringProperty('')
    _bg_color_down = ListProperty([0, 0, 0, 0])
    _current_button_color = ListProperty([0, 0, 0, 0])

    def __init__(self, **kwargs):
        super(MDFlatButton, self).__init__(**kwargs)
        self._current_button_color = self.background_color
        self._bg_color_down = get_color_from_hex(
            colors[self.theme_cls.theme_style]['FlatButtonDown'])

        Clock.schedule_once(lambda x: self.ids._label.bind(
            texture_size=self.update_width_on_label_texture))

    def update_width_on_label_texture(self, instance, value):
        self.ids._label.width = value[0]

    def on_text(self, instance, value):
        self._text = value.upper()

    def on_touch_down(self, touch):
        if touch.is_mouse_scrolling:
            return False
        elif not self.collide_point(touch.x, touch.y):
            return False
        elif self in touch.ud:
            return False
        elif self.disabled:
            return False
        else:
            self.fade_bg = Animation(duration=.2, _current_button_color=get_color_from_hex(
                                     colors[self.theme_cls.theme_style]['FlatButtonDown']))
            self.fade_bg.start(self)
            return super(MDFlatButton, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            self.fade_bg.stop_property(self, '_current_button_color')
            Animation(duration=.05, _current_button_color=self.background_color).start(self)
        return super(MDFlatButton, self).on_touch_up(touch)


class MDRaisedButton(ThemableBehavior, RectangularRippleBehavior,
                     ElevationBehavior, ButtonBehavior,
                     AnchorLayout):
    _bg_color_down = ListProperty([])
    background_color = ListProperty()
    background_color_down = ListProperty()
    background_color_disabled = ListProperty()
    theme_text_color = OptionProperty(None, allownone=True,
                                      options=['Primary', 'Secondary', 'Hint',
                                               'Error', 'Custom'])
    text_color = ListProperty(None, allownone=True)

    def _get_bg_color_down(self):
        return self._bg_color_down

    def _set_bg_color_down(self, color, alpha=None):
        if len(color) == 2:
            self._bg_color_down = get_color_from_hex(
                colors[color[0]][color[1]])
            if alpha:
                self._bg_color_down[3] = alpha
        elif len(color) == 4:
            self._bg_color_down = color

    background_color_down = AliasProperty(_get_bg_color_down,
                                          _set_bg_color_down,
                                          bind=('_bg_color_down',))

    _bg_color_disabled = ListProperty([])

    def _get_bg_color_disabled(self):
        return self._bg_color_disabled

    def _set_bg_color_disabled(self, color, alpha=None):
        if len(color) == 2:
            self._bg_color_disabled = get_color_from_hex(
                colors[color[0]][color[1]])
            if alpha:
                self._bg_color_disabled[3] = alpha
        elif len(color) == 4:
            self._bg_color_disabled = color

    background_color_disabled = AliasProperty(_get_bg_color_disabled,
                                              _set_bg_color_disabled,
                                              bind=('_bg_color_disabled',))

    _elev_norm = NumericProperty(2)

    def _get_elev_norm(self):
        return self._elev_norm

    def _set_elev_norm(self, value):
        self._elev_norm = value if value <= 12 else 12
        self._elev_raised = (value + 6) if value + 6 <= 12 else 12
        self.elevation = self._elev_norm

    elevation_normal = AliasProperty(_get_elev_norm, _set_elev_norm,
                                     bind=('_elev_norm',))

    _elev_raised = NumericProperty(8)

    def _get_elev_raised(self):
        return self._elev_raised

    def _set_elev_raised(self, value):
        self._elev_raised = value if value + self._elev_norm <= 12 else 12

    elevation_raised = AliasProperty(_get_elev_raised, _set_elev_raised,
                                     bind=('_elev_raised',))

    text = StringProperty()

    _text = StringProperty()

    def __init__(self, **kwargs):
        super(MDRaisedButton, self).__init__(**kwargs)
        self.elevation_press_anim = Animation(elevation=self.elevation_raised,
                                              duration=.2, t='out_quad')
        self.elevation_release_anim = Animation(
            elevation=self.elevation_normal, duration=.2, t='out_quad')

    def on_disabled(self, instance, value):
        if value:
            self.elevation = 0
        else:
            self.elevation = self.elevation_normal
        super(MDRaisedButton, self).on_disabled(instance, value)

    def on_touch_down(self, touch):
        if not self.disabled:
            if touch.is_mouse_scrolling:
                return False
            if not self.collide_point(touch.x, touch.y):
                return False
            if self in touch.ud:
                return False
            Animation.cancel_all(self, 'elevation')
            self.elevation_press_anim.start(self)
        return super(MDRaisedButton, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if not self.disabled:
            if touch.grab_current is not self:
                return super(ButtonBehavior, self).on_touch_up(touch)
            Animation.cancel_all(self, 'elevation')
            self.elevation_release_anim.start(self)
        else:
            Animation.cancel_all(self, 'elevation')
            self.elevation = 0
        return super(MDRaisedButton, self).on_touch_up(touch)

    def on_text(self, instance, text):
        self._text = text.upper()

    def on__elev_norm(self, instance, value):
        self.elevation_release_anim = Animation(elevation=value,
                                                duration=.2, t='out_quad')

    def on__elev_raised(self, instance, value):
        self.elevation_press_anim = Animation(elevation=value,
                                              duration=.2, t='out_quad')


class MDFloatingActionButton(ThemableBehavior, CircularRippleBehavior,
                             RoundElevationBehavior, ButtonBehavior,
                             AnchorLayout):
    _bg_color_down = ListProperty([])
    background_color = ListProperty()
    background_color_down = ListProperty()
    background_color_disabled = ListProperty()
    theme_text_color = OptionProperty(None, allownone=True,
                                      options=['Primary', 'Secondary', 'Hint',
                                               'Error', 'Custom'])
    text_color = ListProperty(None, allownone=True)

    def _get_bg_color_down(self):
        return self._bg_color_down

    def _set_bg_color_down(self, color, alpha=None):
        if len(color) == 2:
            self._bg_color_down = get_color_from_hex(
                colors[color[0]][color[1]])
            if alpha:
                self._bg_color_down[3] = alpha
        elif len(color) == 4:
            self._bg_color_down = color

    background_color_down = AliasProperty(_get_bg_color_down,
                                          _set_bg_color_down,
                                          bind=('_bg_color_down',))

    _bg_color_disabled = ListProperty([])

    def _get_bg_color_disabled(self):
        return self._bg_color_disabled

    def _set_bg_color_disabled(self, color, alpha=None):
        if len(color) == 2:
            self._bg_color_disabled = get_color_from_hex(
                colors[color[0]][color[1]])
            if alpha:
                self._bg_color_disabled[3] = alpha
        elif len(color) == 4:
            self._bg_color_disabled = color

    background_color_disabled = AliasProperty(_get_bg_color_disabled,
                                              _set_bg_color_disabled,
                                              bind=('_bg_color_disabled',))
    icon = StringProperty('android')

    _elev_norm = NumericProperty(6)

    def _get_elev_norm(self):
        return self._elev_norm

    def _set_elev_norm(self, value):
        self._elev_norm = value if value <= 12 else 12
        self._elev_raised = (value + 6) if value + 6 <= 12 else 12
        self.elevation = self._elev_norm

    elevation_normal = AliasProperty(_get_elev_norm, _set_elev_norm,
                                     bind=('_elev_norm',))

    # _elev_raised = NumericProperty(12)
    _elev_raised = NumericProperty(6)

    def _get_elev_raised(self):
        return self._elev_raised

    def _set_elev_raised(self, value):
        self._elev_raised = value if value + self._elev_norm <= 12 else 12

    elevation_raised = AliasProperty(_get_elev_raised, _set_elev_raised,
                                     bind=('_elev_raised',))

    def __init__(self, **kwargs):
        if self.elevation_raised == 0 and self.elevation_normal + 6 <= 12:
            self.elevation_raised = self.elevation_normal + 6
        elif self.elevation_raised == 0:
            self.elevation_raised = 12

        super(MDFloatingActionButton, self).__init__(**kwargs)

        self.elevation_press_anim = Animation(elevation=self.elevation_raised,
                                              duration=.2, t='out_quad')
        self.elevation_release_anim = Animation(
            elevation=self.elevation_normal, duration=.2, t='out_quad')

    def _set_ellipse(self, instance, value):
        ellipse = self.ellipse
        ripple_rad = self.ripple_rad

        ellipse.size = (ripple_rad, ripple_rad)
        ellipse.pos = (self.center_x - ripple_rad / 2.,
                       self.center_y - ripple_rad / 2.)

    def on_disabled(self, instance, value):
        super(MDFloatingActionButton, self).on_disabled(instance, value)
        if self.disabled:
            self.elevation = 0
        else:
            self.elevation = self.elevation_normal

    def on_touch_down(self, touch):
        if not self.disabled:
            if touch.is_mouse_scrolling:
                return False
            if not self.collide_point(touch.x, touch.y):
                return False
            if self in touch.ud:
                return False
            self.elevation_press_anim.stop(self)
            self.elevation_press_anim.start(self)
        return super(MDFloatingActionButton, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if not self.disabled:
            if touch.grab_current is not self:
                return super(ButtonBehavior, self).on_touch_up(touch)
            self.elevation_release_anim.stop(self)
            self.elevation_release_anim.start(self)
        return super(MDFloatingActionButton, self).on_touch_up(touch)

    def on_elevation_normal(self, instance, value):
        self.elevation = value

    def on_elevation_raised(self, instance, value):
        if self.elevation_raised == 0 and self.elevation_normal + 6 <= 12:
            self.elevation_raised = self.elevation_normal + 6
        elif self.elevation_raised == 0:
            self.elevation_raised = 12
