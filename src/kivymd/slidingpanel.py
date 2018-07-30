# -*- coding: utf-8 -*-
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import OptionProperty, NumericProperty, StringProperty, \
    BooleanProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout

Builder.load_string("""
#: import Window kivy.core.window.Window
<SlidingPanel>
    orientation: 'vertical'
    size_hint_x: None
    width: dp(320)
    x: -1 * self.width if self.side == 'left' else Window.width

<PanelShadow>
    canvas:
        Color:
            rgba: root.color
        Rectangle:
            size: root.size
""")


class PanelShadow(BoxLayout):
    color = ListProperty([0, 0, 0, 0])


class SlidingPanel(BoxLayout):
    anim_length_close = NumericProperty(0.3)
    anim_length_open = NumericProperty(0.3)
    animation_t_open = StringProperty('out_sine')
    animation_t_close = StringProperty('out_sine')
    side = OptionProperty('left', options=['left', 'right'])

    _open = False

    def __init__(self, **kwargs):
        super(SlidingPanel, self).__init__(**kwargs)
        self.shadow = PanelShadow()
        Clock.schedule_once(lambda x: Window.add_widget(self.shadow,89), 0)
        Clock.schedule_once(lambda x: Window.add_widget(self,90), 0)

    def toggle(self):
        Animation.stop_all(self, 'x')
        Animation.stop_all(self.shadow, 'color')
        if self._open:
            if self.side == 'left':
                target_x = -1 * self.width
            else:
                target_x = Window.width

            sh_anim = Animation(duration=self.anim_length_open,
                                t=self.animation_t_open,
                                color=[0, 0, 0, 0])
            sh_anim.start(self.shadow)
            self._get_main_animation(duration=self.anim_length_close,
                                     t=self.animation_t_close,
                                     x=target_x,
                                     is_closing=True).start(self)
            self._open = False
        else:
            if self.side == 'left':
                target_x = 0
            else:
                target_x = Window.width - self.width
            Animation(duration=self.anim_length_open, t=self.animation_t_open,
                      color=[0, 0, 0, 0.5]).start(self.shadow)
            self._get_main_animation(duration=self.anim_length_open,
                                     t=self.animation_t_open,
                                     x=target_x,
                                     is_closing=False).start(self)
            self._open = True

    def _get_main_animation(self, duration, t, x, is_closing):
        return Animation(duration=duration, t=t, x=x)

    def on_touch_down(self, touch):
        # Prevents touch events from propagating to anything below the widget.
        super(SlidingPanel, self).on_touch_down(touch)
        if self.collide_point(*touch.pos) or self._open:
            return True

    def on_touch_up(self, touch):
        if not self.collide_point(touch.x, touch.y) and self._open:
            self.toggle()
            return True
        super(SlidingPanel, self).on_touch_up(touch)
