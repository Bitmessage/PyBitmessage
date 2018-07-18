# -*- coding: utf-8 -*-

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import (ListProperty, ObjectProperty, NumericProperty)
from kivy.properties import AliasProperty
from kivy.metrics import dp

Builder.load_string('''
<ElevationBehavior>
    canvas.before:
        Color:
            a: self._soft_shadow_a
        Rectangle:
            texture: self._soft_shadow_texture
            size: self._soft_shadow_size
            pos: self._soft_shadow_pos
        Color:
            a: self._hard_shadow_a
        Rectangle:
            texture: self._hard_shadow_texture
            size: self._hard_shadow_size
            pos: self._hard_shadow_pos
        Color:
            a: 1

<RoundElevationBehavior>
    canvas.before:
        Color:
            a: self._soft_shadow_a
        Rectangle:
            texture: self._soft_shadow_texture
            size: self._soft_shadow_size
            pos: self._soft_shadow_pos
        Color:
            a: self._hard_shadow_a
        Rectangle:
            texture: self._hard_shadow_texture
            size: self._hard_shadow_size
            pos: self._hard_shadow_pos
        Color:
            a: 1
''')


class ElevationBehavior(object):
    _elevation = NumericProperty(1)

    def _get_elevation(self):
        return self._elevation

    def _set_elevation(self, elevation):
        try:
            self._elevation = elevation
        except:
            self._elevation = 1

    elevation = AliasProperty(_get_elevation, _set_elevation,
                              bind=('_elevation',))

    _soft_shadow_texture = ObjectProperty()
    _soft_shadow_size = ListProperty([0, 0])
    _soft_shadow_pos = ListProperty([0, 0])
    _soft_shadow_a = NumericProperty(0)
    _hard_shadow_texture = ObjectProperty()
    _hard_shadow_size = ListProperty([0, 0])
    _hard_shadow_pos = ListProperty([0, 0])
    _hard_shadow_a = NumericProperty(0)

    def __init__(self, **kwargs):
        super(ElevationBehavior, self).__init__(**kwargs)
        self.bind(elevation=self._update_shadow,
                  pos=self._update_shadow,
                  size=self._update_shadow)

    def _update_shadow(self, *args):
        if self.elevation > 0:
            ratio = self.width / (self.height if self.height != 0 else 1)
            if ratio > -2 and ratio < 2:
                self._shadow = App.get_running_app().theme_cls.quad_shadow
                width = soft_width = self.width * 1.9
                height = soft_height = self.height * 1.9
            elif ratio <= -2:
                self._shadow = App.get_running_app().theme_cls.rec_st_shadow
                ratio = abs(ratio)
                if ratio > 5:
                    ratio = ratio * 22
                else:
                    ratio = ratio * 11.5

                width = soft_width = self.width * 1.9
                height = self.height + dp(ratio)
                soft_height = self.height + dp(ratio) + dp(self.elevation) * .5
            else:
                self._shadow = App.get_running_app().theme_cls.quad_shadow
                width = soft_width = self.width * 1.8
                height = soft_height = self.height * 1.8
                #                 self._shadow = App.get_running_app().theme_cls.rec_shadow
                #                 ratio = abs(ratio)
                #                 if ratio > 5:
                #                     ratio = ratio * 22
                #                 else:
                #                     ratio = ratio * 11.5
                #
                #                 width = self.width + dp(ratio)
                #                 soft_width = self.width + dp(ratio) + dp(self.elevation) * .9
                #                 height = soft_height = self.height * 1.9

            x = self.center_x - width / 2
            soft_x = self.center_x - soft_width / 2
            self._soft_shadow_size = (soft_width, soft_height)
            self._hard_shadow_size = (width, height)

            y = self.center_y - soft_height / 2 - dp(
                .1 * 1.5 ** self.elevation)
            self._soft_shadow_pos = (soft_x, y)
            self._soft_shadow_a = 0.1 * 1.1 ** self.elevation
            self._soft_shadow_texture = self._shadow.textures[
                str(int(round(self.elevation - 1)))]

            y = self.center_y - height / 2 - dp(.5 * 1.18 ** self.elevation)
            self._hard_shadow_pos = (x, y)
            self._hard_shadow_a = .4 * .9 ** self.elevation
            self._hard_shadow_texture = self._shadow.textures[
                str(int(round(self.elevation)))]

        else:
            self._soft_shadow_a = 0
            self._hard_shadow_a = 0


class RoundElevationBehavior(object):
    _elevation = NumericProperty(1)

    def _get_elevation(self):
        return self._elevation

    def _set_elevation(self, elevation):
        try:
            self._elevation = elevation
        except:
            self._elevation = 1

    elevation = AliasProperty(_get_elevation, _set_elevation,
                              bind=('_elevation',))

    _soft_shadow_texture = ObjectProperty()
    _soft_shadow_size = ListProperty([0, 0])
    _soft_shadow_pos = ListProperty([0, 0])
    _soft_shadow_a = NumericProperty(0)
    _hard_shadow_texture = ObjectProperty()
    _hard_shadow_size = ListProperty([0, 0])
    _hard_shadow_pos = ListProperty([0, 0])
    _hard_shadow_a = NumericProperty(0)

    def __init__(self, **kwargs):
        super(RoundElevationBehavior, self).__init__(**kwargs)
        self._shadow = App.get_running_app().theme_cls.round_shadow
        self.bind(elevation=self._update_shadow,
                  pos=self._update_shadow,
                  size=self._update_shadow)

    def _update_shadow(self, *args):
        if self.elevation > 0:
            width = self.width * 2
            height = self.height * 2

            x = self.center_x - width / 2
            self._soft_shadow_size = (width, height)

            self._hard_shadow_size = (width, height)

            y = self.center_y - height / 2 - dp(.1 * 1.5 ** self.elevation)
            self._soft_shadow_pos = (x, y)
            self._soft_shadow_a = 0.1 * 1.1 ** self.elevation
            self._soft_shadow_texture = self._shadow.textures[
                str(int(round(self.elevation)))]

            y = self.center_y - height / 2 - dp(.5 * 1.18 ** self.elevation)
            self._hard_shadow_pos = (x, y)
            self._hard_shadow_a = .4 * .9 ** self.elevation
            self._hard_shadow_texture = self._shadow.textures[
                str(int(round(self.elevation - 1)))]

        else:
            self._soft_shadow_a = 0
            self._hard_shadow_a = 0
