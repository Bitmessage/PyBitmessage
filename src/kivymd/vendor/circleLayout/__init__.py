#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CircularLayout
==============

CircularLayout is a special layout that places widgets around a circle.

size_hint
---------

size_hint_x is used as an angle-quota hint (widget with higher
size_hint_x will be farther from each other, and vice versa), while
size_hint_y is used as a widget size hint (widgets with a higher size
hint will be bigger).size_hint_x cannot be None.

Widgets are all squares, unless you set size_hint_y to None (in that
case you'll be able to specify your own size), and their size is the
difference between the outer and the inner circle's radii. To make the
widgets bigger you can just decrease inner_radius_hint.
"""

from kivy.uix.layout import Layout
from kivy.properties import NumericProperty, ReferenceListProperty, OptionProperty, \
                            BoundedNumericProperty, VariableListProperty, AliasProperty
from math import sin, cos, pi, radians

__all__ = ('CircularLayout')

try:
    xrange(1, 2)
except NameError:
    def xrange(first, second, third=None):
        if third:
            return range(first, second, third)
        else:
            return range(first, second)


class CircularLayout(Layout):
    '''
    Circular layout class. See module documentation for more information.
    '''

    padding = VariableListProperty([0, 0, 0, 0])
    '''Padding between the layout box and it's children: [padding_left,
    padding_top, padding_right, padding_bottom].

    padding also accepts a two argument form [padding_horizontal,
    padding_vertical] and a one argument form [padding].

    .. version changed:: 1.7.0
        Replaced NumericProperty with VariableListProperty.

    :attr:`padding` is a :class:`~kivy.properties.VariableListProperty` and
    defaults to [0, 0, 0, 0].
    '''

    start_angle = NumericProperty(0)
    '''Angle (in degrees) at which the first widget will be placed.
    Start counting angles from the X axis, going counterclockwise.

    :attr:`start_angle` is a :class:`~kivy.properties.NumericProperty` and
    defaults to 0 (start from the right).
    '''

    circle_quota = BoundedNumericProperty(360, min=0, max=360)
    '''Size (in degrees) of the part of the circumference that will actually
    be used to place widgets.

    :attr:`circle_quota` is a :class:`~kivy.properties.BoundedNumericProperty`
    and defaults to 360 (all the circumference).
    '''

    direction = OptionProperty("ccw", options=("cw", "ccw"))
    '''Direction of widgets in the circle.

    :attr:`direction` is an :class:`~kivy.properties.OptionProperty` and
    defaults to 'ccw'. Can be 'ccw' (counterclockwise) or 'cw' (clockwise).
    '''

    outer_radius_hint = NumericProperty(1)
    '''Sets the size of the outer circle. A number greater than 1 will make the
    widgets larger than the actual widget, a number smaller than 1 will leave
    a gap.

    :attr:`outer_radius_hint` is a :class:`~kivy.properties.NumericProperty` and
    defaults to 1.
    '''

    inner_radius_hint = NumericProperty(.6)
    '''Sets the size of the inner circle. A number greater than
    :attr:`outer_radius_hint` will cause glitches. The closest it is to
    :attr:`outer_radius_hint`, the smallest will be the widget in the layout.

    :attr:`outer_radius_hint` is a :class:`~kivy.properties.NumericProperty` and
    defaults to 1.
    '''

    radius_hint = ReferenceListProperty(inner_radius_hint, outer_radius_hint)
    '''Combined :attr:`outer_radius_hint` and :attr:`inner_radius_hint` in a list
    for convenience. See their documentation for more details.

    :attr:`radius_hint` is a :class:`~kivy.properties.ReferenceListProperty`.
    '''

    def _get_delta_radii(self):
        radius = min(self.width-self.padding[0]-self.padding[2], self.height-self.padding[1]-self.padding[3]) / 2.
        outer_r = radius * self.outer_radius_hint
        inner_r = radius * self.inner_radius_hint
        return outer_r - inner_r
    delta_radii = AliasProperty(_get_delta_radii, None, bind=("radius_hint", "padding", "size"))

    def __init__(self, **kwargs):
        super(CircularLayout, self).__init__(**kwargs)

        self.bind(
            start_angle=self._trigger_layout,
            parent=self._trigger_layout,
            # padding=self._trigger_layout,
            children=self._trigger_layout,
            size=self._trigger_layout,
            radius_hint=self._trigger_layout,
            pos=self._trigger_layout)

    def do_layout(self, *largs):
        # optimize layout by preventing looking at the same attribute in a loop
        len_children = len(self.children)
        if len_children == 0:
            return
        selfcx = self.center_x
        selfcy = self.center_y
        direction = self.direction
        cquota = radians(self.circle_quota)
        start_angle_r = radians(self.start_angle)
        padding_left = self.padding[0]
        padding_top = self.padding[1]
        padding_right = self.padding[2]
        padding_bottom = self.padding[3]
        padding_x = padding_left + padding_right
        padding_y = padding_top + padding_bottom

        radius = min(self.width-padding_x, self.height-padding_y) / 2.
        outer_r = radius * self.outer_radius_hint
        inner_r = radius * self.inner_radius_hint
        middle_r = radius * sum(self.radius_hint) / 2.
        delta_r = outer_r - inner_r

        stretch_weight_angle = 0.
        for w in self.children:
            sha = w.size_hint_x
            if sha is None:
                raise ValueError("size_hint_x cannot be None in a CircularLayout")
            else:
                stretch_weight_angle += sha

        sign = +1.
        angle_offset = start_angle_r
        if direction == 'cw':
            angle_offset = 2 * pi - start_angle_r
            sign = -1.

        for c in reversed(self.children):
            sha = c.size_hint_x
            shs = c.size_hint_y

            angle_quota = cquota / stretch_weight_angle * sha
            angle = angle_offset + (sign * angle_quota / 2)
            angle_offset += sign * angle_quota

            # kived: looking it up, yes. x = cos(angle) * radius + centerx; y = sin(angle) * radius + centery
            ccx = cos(angle) * middle_r + selfcx + padding_left - padding_right
            ccy = sin(angle) * middle_r + selfcy + padding_bottom - padding_top

            c.center_x = ccx
            c.center_y = ccy
            if shs:
                s = delta_r * shs
                c.width = s
                c.height = s

if __name__ == "__main__":
    from kivy.app import App
    from kivy.uix.button import Button

    class CircLayoutApp(App):
        def build(self):
            cly = CircularLayout(direction="cw", start_angle=-75, inner_radius_hint=.7, padding="20dp")

            for i in xrange(1, 13):
                cly.add_widget(Button(text=str(i), font_size="30dp"))

            return cly

    CircLayoutApp().run()
