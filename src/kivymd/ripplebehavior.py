# -*- coding: utf-8 -*-
from kivy.properties import ListProperty, NumericProperty, StringProperty, \
    BooleanProperty
from kivy.animation import Animation
from kivy.graphics import Color, Ellipse, StencilPush, StencilPop, \
    StencilUse, StencilUnUse, Rectangle


class CommonRipple(object):
    ripple_rad = NumericProperty()
    ripple_rad_default = NumericProperty(1)
    ripple_post = ListProperty()
    ripple_color = ListProperty()
    ripple_alpha = NumericProperty(.5)
    ripple_scale = NumericProperty(None)
    ripple_duration_in_fast = NumericProperty(.3)
    # FIXME: These speeds should be calculated based on widget size in dp
    ripple_duration_in_slow = NumericProperty(2)
    ripple_duration_out = NumericProperty(.3)
    ripple_func_in = StringProperty('out_quad')
    ripple_func_out = StringProperty('out_quad')

    doing_ripple = BooleanProperty(False)
    finishing_ripple = BooleanProperty(False)
    fading_out = BooleanProperty(False)

    def on_touch_down(self, touch):
        if touch.is_mouse_scrolling:
            return False
        if not self.collide_point(touch.x, touch.y):
            return False

        if not self.disabled:
            if self.doing_ripple:
                Animation.cancel_all(self, 'ripple_rad', 'ripple_color',
                                     'rect_color')
                self.anim_complete()
            self.ripple_rad = self.ripple_rad_default
            self.ripple_pos = (touch.x, touch.y)

            if self.ripple_color != []:
                pass
            elif hasattr(self, 'theme_cls'):
                self.ripple_color = self.theme_cls.ripple_color
            else:
                # If no theme, set Grey 300
                self.ripple_color = [0.8784313725490196, 0.8784313725490196,
                                     0.8784313725490196, self.ripple_alpha]
            self.ripple_color[3] = self.ripple_alpha

            self.lay_canvas_instructions()
            self.finish_rad = max(self.width, self.height) * self.ripple_scale
            self.start_ripple()
        return super(CommonRipple, self).on_touch_down(touch)

    def lay_canvas_instructions(self):
        raise NotImplementedError

    def on_touch_move(self, touch, *args):
        if not self.collide_point(touch.x, touch.y):
            if not self.finishing_ripple and self.doing_ripple:
                self.finish_ripple()
        return super(CommonRipple, self).on_touch_move(touch, *args)

    def on_touch_up(self, touch):
        if self.collide_point(touch.x, touch.y) and self.doing_ripple:
            self.finish_ripple()
        return super(CommonRipple, self).on_touch_up(touch)

    def start_ripple(self):
        if not self.doing_ripple:
            anim = Animation(
                ripple_rad=self.finish_rad,
                t='linear',
                duration=self.ripple_duration_in_slow)
            anim.bind(on_complete=self.fade_out)
            self.doing_ripple = True
            anim.start(self)

    def _set_ellipse(self, instance, value):
        self.ellipse.size = (self.ripple_rad, self.ripple_rad)

    # Adjust ellipse pos here

    def _set_color(self, instance, value):
        self.col_instruction.a = value[3]

    def finish_ripple(self):
        if self.doing_ripple and not self.finishing_ripple:
            Animation.cancel_all(self, 'ripple_rad')
            anim = Animation(ripple_rad=self.finish_rad,
                             t=self.ripple_func_in,
                             duration=self.ripple_duration_in_fast)
            anim.bind(on_complete=self.fade_out)
            self.finishing_ripple = True
            anim.start(self)

    def fade_out(self, *args):
        rc = self.ripple_color
        if not self.fading_out:
            Animation.cancel_all(self, 'ripple_color')
            anim = Animation(ripple_color=[rc[0], rc[1], rc[2], 0.],
                             t=self.ripple_func_out,
                             duration=self.ripple_duration_out)
            anim.bind(on_complete=self.anim_complete)
            self.fading_out = True
            anim.start(self)

    def anim_complete(self, *args):
        self.doing_ripple = False
        self.finishing_ripple = False
        self.fading_out = False
        self.canvas.after.clear()


class RectangularRippleBehavior(CommonRipple):
    ripple_scale = NumericProperty(2.75)

    def lay_canvas_instructions(self):
        with self.canvas.after:
            StencilPush()
            Rectangle(pos=self.pos, size=self.size)
            StencilUse()
            self.col_instruction = Color(rgba=self.ripple_color)
            self.ellipse = \
                Ellipse(size=(self.ripple_rad, self.ripple_rad),
                        pos=(self.ripple_pos[0] - self.ripple_rad / 2.,
                             self.ripple_pos[1] - self.ripple_rad / 2.))
            StencilUnUse()
            Rectangle(pos=self.pos, size=self.size)
            StencilPop()
        self.bind(ripple_color=self._set_color,
                  ripple_rad=self._set_ellipse)

    def _set_ellipse(self, instance, value):
        super(RectangularRippleBehavior, self)._set_ellipse(instance, value)
        self.ellipse.pos = (self.ripple_pos[0] - self.ripple_rad / 2.,
                            self.ripple_pos[1] - self.ripple_rad / 2.)


class CircularRippleBehavior(CommonRipple):
    ripple_scale = NumericProperty(1)

    def lay_canvas_instructions(self):
        with self.canvas.after:
            StencilPush()
            self.stencil = Ellipse(size=(self.width * self.ripple_scale,
                                         self.height * self.ripple_scale),
                                   pos=(self.center_x - (
                                       self.width * self.ripple_scale) / 2,
                                        self.center_y - (
                                            self.height * self.ripple_scale) / 2))
            StencilUse()
            self.col_instruction = Color(rgba=self.ripple_color)
            self.ellipse = Ellipse(size=(self.ripple_rad, self.ripple_rad),
                                   pos=(self.center_x - self.ripple_rad / 2.,
                                        self.center_y - self.ripple_rad / 2.))
            StencilUnUse()
            Ellipse(pos=self.pos, size=self.size)
            StencilPop()
            self.bind(ripple_color=self._set_color,
                      ripple_rad=self._set_ellipse)

    def _set_ellipse(self, instance, value):
        super(CircularRippleBehavior, self)._set_ellipse(instance, value)
        if self.ellipse.size[0] > self.width * .6 and not self.fading_out:
            self.fade_out()
        self.ellipse.pos = (self.center_x - self.ripple_rad / 2.,
                            self.center_y - self.ripple_rad / 2.)
