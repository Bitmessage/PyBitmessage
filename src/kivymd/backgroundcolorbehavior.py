# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *
from kivy.lang import Builder
from kivy.properties import BoundedNumericProperty, ReferenceListProperty
from kivy.uix.widget import Widget

Builder.load_string('''
<BackgroundColorBehavior>
    canvas:
        Color:
            rgba: self.background_color
        Rectangle:
            size: self.size
            pos: self.pos
''')


class BackgroundColorBehavior(Widget):
    r = BoundedNumericProperty(1., min=0., max=1.)
    g = BoundedNumericProperty(1., min=0., max=1.)
    b = BoundedNumericProperty(1., min=0., max=1.)
    a = BoundedNumericProperty(0., min=0., max=1.)

    background_color = ReferenceListProperty(r, g, b, a)
