# -*- coding: utf-8 -*-
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.garden.recycleview import RecycleView
from kivy.metrics import dp
from kivy.properties import NumericProperty, ListProperty, OptionProperty, \
    StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
import kivymd.material_resources as m_res
from kivymd.theming import ThemableBehavior

Builder.load_string('''
#:import STD_INC kivymd.material_resources.STANDARD_INCREMENT
<MDMenuItem>
    size_hint_y: None
    height: dp(48)
    padding: dp(16), 0
    on_release: root.parent.parent.parent.parent.dismiss()  # Horrible, but hey it works
    MDLabel:
        text: root.text
        theme_text_color: 'Primary'

<MDMenu>
    size_hint: None, None
    width: root.width_mult * STD_INC
    key_viewclass: 'viewclass'
    key_size: 'height'

<MDDropdownMenu>
    FloatLayout:
        id: fl
        MDMenu:
            id: md_menu
            data: root.items
            width_mult: root.width_mult
            size_hint: None, None
            size: 0,0
            canvas.before:
                Color:
                    rgba: root.theme_cls.bg_light
                Rectangle:
                    size: self.size
                    pos: self.pos
''')


class MDMenuItem(ButtonBehavior, BoxLayout):
    text = StringProperty()


class MDMenu(RecycleView):
    width_mult = NumericProperty(1)


class MDDropdownMenu(ThemableBehavior, BoxLayout):
    items = ListProperty()
    '''See :attr:`~kivy.garden.recycleview.RecycleView.data`
    '''

    width_mult = NumericProperty(1)
    '''This number multiplied by the standard increment (56dp on mobile,
    64dp on desktop, determines the width of the menu items.

    If the resulting number were to be too big for the application Window,
    the multiplier will be adjusted for the biggest possible one.
    '''

    max_height = NumericProperty()
    '''The menu will grow no bigger than this number.

    Set to 0 for no limit. Defaults to 0.
    '''

    border_margin = NumericProperty(dp(4))
    '''Margin between Window border and menu
    '''

    ver_growth = OptionProperty(None, allownone=True,
                                options=['up', 'down'])
    '''Where the menu will grow vertically to when opening

    Set to None to let the widget pick for you. Defaults to None.
    '''

    hor_growth = OptionProperty(None, allownone=True,
                                options=['left', 'right'])
    '''Where the menu will grow horizontally to when opening

    Set to None to let the widget pick for you. Defaults to None.
    '''

    def open(self, *largs):
        Window.add_widget(self)
        Clock.schedule_once(lambda x: self.display_menu(largs[0]), -1)

    def display_menu(self, caller):
        # We need to pick a starting point, see how big we need to be,
        # and where to grow to.

        c = caller.to_window(caller.center_x,
                             caller.center_y)  # Starting coords

        # ---ESTABLISH INITIAL TARGET SIZE ESTIMATE---
        target_width = self.width_mult * m_res.STANDARD_INCREMENT
        # If we're wider than the Window...
        if target_width > Window.width:
            # ...reduce our multiplier to max allowed.
            target_width = int(
                Window.width / m_res.STANDARD_INCREMENT) * m_res.STANDARD_INCREMENT

        target_height = sum([dp(48) for i in self.items])
        # If we're over max_height...
        if 0 < self.max_height < target_height:
            target_height = self.max_height

        # ---ESTABLISH VERTICAL GROWTH DIRECTION---
        if self.ver_growth is not None:
            ver_growth = self.ver_growth
        else:
            # If there's enough space below us:
            if target_height <= c[1] - self.border_margin:
                ver_growth = 'down'
            # if there's enough space above us:
            elif target_height < Window.height - c[1] - self.border_margin:
                ver_growth = 'up'
            # otherwise, let's pick the one with more space and adjust ourselves
            else:
                # if there's more space below us:
                if c[1] >= Window.height - c[1]:
                    ver_growth = 'down'
                    target_height = c[1] - self.border_margin
                # if there's more space above us:
                else:
                    ver_growth = 'up'
                    target_height = Window.height - c[1] - self.border_margin

        if self.hor_growth is not None:
            hor_growth = self.hor_growth
        else:
            # If there's enough space to the right:
            if target_width <= Window.width - c[0] - self.border_margin:
                hor_growth = 'right'
            # if there's enough space to the left:
            elif target_width < c[0] - self.border_margin:
                hor_growth = 'left'
            # otherwise, let's pick the one with more space and adjust ourselves
            else:
                # if there's more space to the right:
                if Window.width - c[0] >= c[0]:
                    hor_growth = 'right'
                    target_width = Window.width - c[0] - self.border_margin
                # if there's more space to the left:
                else:
                    hor_growth = 'left'
                    target_width = c[0] - self.border_margin

        if ver_growth == 'down':
            tar_y = c[1] - target_height
        else:  # should always be 'up'
            tar_y = c[1]

        if hor_growth == 'right':
            tar_x = c[0]
        else:  # should always be 'left'
            tar_x = c[0] - target_width
        anim = Animation(x=tar_x, y=tar_y,
                         width=target_width, height=target_height,
                         duration=.3, transition='out_quint')
        menu = self.ids['md_menu']
        menu.pos = c
        anim.start(menu)

    def on_touch_down(self, touch):
        if not self.ids['md_menu'].collide_point(*touch.pos):
            self.dismiss()
            return True
        super(MDDropdownMenu, self).on_touch_down(touch)
        return True

    def on_touch_move(self, touch):
        super(MDDropdownMenu, self).on_touch_move(touch)
        return True

    def on_touch_up(self, touch):
        super(MDDropdownMenu, self).on_touch_up(touch)
        return True

    def dismiss(self):
        Window.remove_widget(self)
