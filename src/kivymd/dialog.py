# -*- coding: utf-8 -*-

from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, ListProperty
from kivy.metrics import dp
from kivy.uix.modalview import ModalView
from kivy.animation import Animation
from kivymd.theming import ThemableBehavior
from kivymd.elevationbehavior import ElevationBehavior
from kivymd.button import MDFlatButton

Builder.load_string('''
<MDDialog>:
    canvas:
        Color:
            rgba:     self.theme_cls.bg_light
        Rectangle:
            size:     self.size
            pos:     self.pos

    _container:        container
    _action_area:    action_area
    elevation:        12
    GridLayout:
        cols:            1

        GridLayout:
            cols: 1
            padding:        dp(24), dp(24), dp(24), 0
            spacing:        dp(20)
            MDLabel:
                text:                root.title
                font_style:            'Title'
                theme_text_color:    'Primary'
                halign:                'left'
                valign:                'middle'
                size_hint_y:        None
                text_size:            self.width, None
                height:                self.texture_size[1]

            BoxLayout:
                id:                    container

        AnchorLayout:
            anchor_x:            'right'
            anchor_y:            'center'
            size_hint:            1, None
            height:                dp(48)
            padding:            dp(8), dp(8)
            spacing:            dp(4)

            GridLayout:
                id:                action_area
                rows:            1
                size_hint:        None, None if len(root._action_buttons) > 0 else 1
                height:            dp(36) if len(root._action_buttons) > 0 else 0
                width:            self.minimum_width
''')


class MDDialog(ThemableBehavior, ElevationBehavior, ModalView):
    title = StringProperty('')

    content = ObjectProperty(None)

    background_color = ListProperty([0, 0, 0, .2])

    _container = ObjectProperty()
    _action_buttons = ListProperty([])
    _action_area = ObjectProperty()

    def __init__(self, **kwargs):
        super(MDDialog, self).__init__(**kwargs)
        self.bind(_action_buttons=self._update_action_buttons,
                  auto_dismiss=lambda *x: setattr(self.shadow, 'on_release',
                                                  self.shadow.dismiss if self.auto_dismiss else None))

    def add_action_button(self, text, action=None):
        """Add an :class:`FlatButton` to the right of the action area.

        :param icon: Unicode character for the icon
        :type icon: str or None
        :param action: Function set to trigger when on_release fires
        :type action: function or None
        """
        button = MDFlatButton(text=text,
                              size_hint=(None, None),
                              height=dp(36))
        if action:
            button.bind(on_release=action)
        button.text_color = self.theme_cls.primary_color
        button.background_color = self.theme_cls.bg_light
        self._action_buttons.append(button)

    def add_widget(self, widget):
        if self._container:
            if self.content:
                raise PopupException(
                    'Popup can have only one widget as content')
            self.content = widget
        else:
            super(MDDialog, self).add_widget(widget)

    def open(self, *largs):
        '''Show the view window from the :attr:`attach_to` widget. If set, it
        will attach to the nearest window. If the widget is not attached to any
        window, the view will attach to the global
        :class:`~kivy.core.window.Window`.
        '''
        if self._window is not None:
            Logger.warning('ModalView: you can only open once.')
            return self
        # search window
        self._window = self._search_window()
        if not self._window:
            Logger.warning('ModalView: cannot open view, no window found.')
            return self
        self._window.add_widget(self)
        self._window.bind(on_resize=self._align_center,
                          on_keyboard=self._handle_keyboard)
        self.center = self._window.center
        self.bind(size=self._align_center)
        a = Animation(_anim_alpha=1., d=self._anim_duration)
        a.bind(on_complete=lambda *x: self.dispatch('on_open'))
        a.start(self)
        return self

    def dismiss(self, *largs, **kwargs):
        '''Close the view if it is open. If you really want to close the
        view, whatever the on_dismiss event returns, you can use the *force*
        argument:
        ::

            view = ModalView(...)
            view.dismiss(force=True)

        When the view is dismissed, it will be faded out before being
        removed from the parent. If you don't want animation, use::

            view.dismiss(animation=False)

        '''
        if self._window is None:
            return self
        if self.dispatch('on_dismiss') is True:
            if kwargs.get('force', False) is not True:
                return self
        if kwargs.get('animation', True):
            Animation(_anim_alpha=0., d=self._anim_duration).start(self)
        else:
            self._anim_alpha = 0
            self._real_remove_widget()
        return self

    def on_content(self, instance, value):
        if self._container:
            self._container.clear_widgets()
            self._container.add_widget(value)

    def on__container(self, instance, value):
        if value is None or self.content is None:
            return
        self._container.clear_widgets()
        self._container.add_widget(self.content)

    def on_touch_down(self, touch):
        if self.disabled and self.collide_point(*touch.pos):
            return True
        return super(MDDialog, self).on_touch_down(touch)

    def _update_action_buttons(self, *args):
        self._action_area.clear_widgets()
        for btn in self._action_buttons:
            btn.ids._label.texture_update()
            btn.width = btn.ids._label.texture_size[0] + dp(16)
            self._action_area.add_widget(btn)
