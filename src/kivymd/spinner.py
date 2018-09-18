# -*- coding: utf-8 -*-

from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ListProperty, BooleanProperty
from kivy.animation import Animation
from kivymd.theming import ThemableBehavior
from kivy.clock import Clock

Builder.load_string('''
<MDSpinner>:
    canvas.before:
        PushMatrix
        Rotate:
            angle: self._rotation_angle
            origin: self.center
    canvas:
        Color:
            rgba: self.color
            a: self._alpha
        Line:
            circle: self.center_x, self.center_y, self.width / 2, \
            self._angle_start, self._angle_end
            cap: 'square'
            width: dp(2)
    canvas.after:
        PopMatrix

''')


class MDSpinner(ThemableBehavior, Widget):
    """:class:`MDSpinner` is an implementation of the circular progress
    indicator in Google's Material Design.

    It can be used either as an indeterminate indicator that loops while
    the user waits for something to happen, or as a determinate indicator.

    Set :attr:`determinate` to **True** to activate determinate mode, and
    :attr:`determinate_time` to set the duration of the animation.
    """

    determinate = BooleanProperty(False)
    """:attr:`determinate` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to False
    """

    determinate_time = NumericProperty(2)
    """:attr:`determinate_time` is a :class:`~kivy.properties.NumericProperty`
    and defaults to 2
    """

    active = BooleanProperty(True)
    """Use :attr:`active` to start or stop the spinner.

    :attr:`active` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to True
    """

    color = ListProperty([])
    """:attr:`color` is a :class:`~kivy.properties.ListProperty` and
    defaults to 'self.theme_cls.primary_color'
    """

    _alpha = NumericProperty(0)
    _rotation_angle = NumericProperty(360)
    _angle_start = NumericProperty(0)
    _angle_end = NumericProperty(8)

    def __init__(self, **kwargs):
        super(MDSpinner, self).__init__(**kwargs)
        Clock.schedule_interval(self._update_color, 5)
        self.color = self.theme_cls.primary_color
        self._alpha_anim_in = Animation(_alpha=1, duration=.8, t='out_quad')
        self._alpha_anim_out = Animation(_alpha=0, duration=.3, t='out_quad')
        self._alpha_anim_out.bind(on_complete=self._reset)

        if self.determinate:
            self._start_determinate()
        else:
            self._start_loop()

    def _update_color(self, *args):
        self.color = self.theme_cls.primary_color

    def _start_determinate(self, *args):
        self._alpha_anim_in.start(self)

        _rot_anim = Animation(_rotation_angle=0,
                              duration=self.determinate_time * .7,
                              t='out_quad')
        _rot_anim.start(self)

        _angle_start_anim = Animation(_angle_end=360,
                                      duration=self.determinate_time,
                                      t='in_out_quad')
        _angle_start_anim.bind(on_complete=lambda *x: \
            self._alpha_anim_out.start(self))

        _angle_start_anim.start(self)

    def _start_loop(self, *args):
        if self._alpha == 0:
            _rot_anim = Animation(_rotation_angle=0,
                                  duration=2,
                                  t='linear')
            _rot_anim.start(self)

        self._alpha = 1
        self._alpha_anim_in.start(self)
        _angle_start_anim = Animation(_angle_end=self._angle_end + 270,
                                      duration=.6,
                                      t='in_out_cubic')
        _angle_start_anim.bind(on_complete=self._anim_back)
        _angle_start_anim.start(self)

    def _anim_back(self, *args):
        _angle_back_anim = Animation(_angle_start=self._angle_end - 8,
                                     duration=.6,
                                     t='in_out_cubic')
        _angle_back_anim.bind(on_complete=self._start_loop)

        _angle_back_anim.start(self)

    def on__rotation_angle(self, *args):
        if self._rotation_angle == 0:
            self._rotation_angle = 360
            if not self.determinate:
                _rot_anim = Animation(_rotation_angle=0,
                                      duration=2)
                _rot_anim.start(self)

    def _reset(self, *args):
        Animation.cancel_all(self, '_angle_start', '_rotation_angle',
                             '_angle_end', '_alpha')
        self._angle_start = 0
        self._angle_end = 8
        self._rotation_angle = 360
        self._alpha = 0
        self.active = False

    def on_active(self, *args):
        if not self.active:
            self._reset()
        else:
            if self.determinate:
                self._start_determinate()
            else:
                self._start_loop()
