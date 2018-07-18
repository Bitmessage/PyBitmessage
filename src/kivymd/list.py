# -*- coding: utf-8 -*-
'''
Lists
=====

`Material Design spec, Lists page <https://www.google.com/design/spec/components/lists.html>`_

`Material Design spec, Lists: Controls page <https://www.google.com/design/spec/components/lists-controls.html>`_

The class :class:`MDList` in combination with a ListItem like
:class:`OneLineListItem` will create a list that expands as items are added to
it, working nicely with Kivy's :class:`~kivy.uix.scrollview.ScrollView`.


Simple examples
---------------

Kv Lang:

.. code-block:: python

    ScrollView:
        do_scroll_x: False  # Important for MD compliance
        MDList:
            OneLineListItem:
                text: "Single-line item"
            TwoLineListItem:
                text: "Two-line item"
                secondary_text: "Secondary text here"
            ThreeLineListItem:
                text: "Three-line item"
                secondary_text: "This is a multi-line label where you can fit more text than usual"


Python:

.. code-block:: python

    # Sets up ScrollView with MDList, as normally used in Android:
    sv = ScrollView()
    ml = MDList()
    sv.add_widget(ml)

    contacts = ["Paula", "John", "Kate", "Vlad"]
    for c in contacts:
        ml.add_widget(
            OneLineListItem(
                text=c
            )
        )

Advanced usage
--------------

Due to the variety in sizes and controls in the MD spec, this module suffers
from a certain level of complexity to keep the widgets compliant, flexible
and performant.

For this KivyMD provides ListItems that try to cover the most common usecases,
when those are insufficient, there's a base class called :class:`ListItem`
which you can use to create your own ListItems. This documentation will only
cover the provided ones, for custom implementations please refer to this
module's source code.

Text only ListItems
-------------------

- :class:`~OneLineListItem`
- :class:`~TwoLineListItem`
- :class:`~ThreeLineListItem`

These are the simplest ones. The :attr:`~ListItem.text` attribute changes the
text in the most prominent line, while :attr:`~ListItem.secondary_text`
changes the second and third line.

If there are only two lines, :attr:`~ListItem.secondary_text` will shorten
the text to fit in case it is too long; if a third line is available, it will
instead wrap the text to make use of it.

ListItems with widget containers
--------------------------------

- :class:`~OneLineAvatarListItem`
- :class:`~TwoLineAvatarListItem`
- :class:`~ThreeLineAvatarListItem`
- :class:`~OneLineIconListItem`
- :class:`~TwoLineIconListItem`
- :class:`~ThreeLineIconListItem`
- :class:`~OneLineAvatarIconListItem`
- :class:`~TwoLineAvatarIconListItem`
- :class:`~ThreeLineAvatarIconListItem`

These widgets will take other widgets that inherit from :class:`~ILeftBody`,
:class:`ILeftBodyTouch`, :class:`~IRightBody` or :class:`~IRightBodyTouch` and
put them in their corresponding container.

As the name implies, :class:`~ILeftBody` and :class:`~IRightBody` will signal
that the widget goes into the left or right container, respectively.

:class:`~ILeftBodyTouch` and :class:`~IRightBodyTouch` do the same thing,
except these widgets will also receive touch events that occur within their
surfaces.

Python example:

.. code-block:: python

    class ContactPhoto(ILeftBody, AsyncImage):
        pass

    class MessageButton(IRightBodyTouch, MDIconButton):
        phone_number = StringProperty()

        def on_release(self):
            # sample code:
            Dialer.send_sms(phone_number, "Hey! What's up?")
            pass

    # Sets up ScrollView with MDList, as normally used in Android:
    sv = ScrollView()
    ml = MDList()
    sv.add_widget(ml)

    contacts = [
        ["Annie", "555-24235", "http://myphotos.com/annie.png"],
        ["Bob", "555-15423", "http://myphotos.com/bob.png"],
        ["Claire", "555-66098", "http://myphotos.com/claire.png"]
    ]

    for c in contacts:
        item = TwoLineAvatarIconListItem(
            text=c[0],
            secondary_text=c[1]
        )
        item.add_widget(ContactPhoto(source=c[2]))
        item.add_widget(MessageButton(phone_number=c[1])
        ml.add_widget(item)

API
---
'''

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, \
    ListProperty, OptionProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
import kivymd.material_resources as m_res
from kivymd.ripplebehavior import RectangularRippleBehavior
from kivymd.theming import ThemableBehavior

Builder.load_string('''
#:import m_res kivymd.material_resources
<MDList>
    cols: 1
    size_hint_y: None
    height: self._min_list_height
    padding: 0, self._list_vertical_padding

<BaseListItem>
    size_hint_y: None
    canvas:
        Color:
            rgba: self.theme_cls.divider_color
        Line:
            points: root.x,root.y, root.x+self.width,root.y
    BoxLayout:
        id: _text_container
        orientation: 'vertical'
        pos: root.pos
        padding: root._txt_left_pad, root._txt_top_pad, root._txt_right_pad, root._txt_bot_pad
        MDLabel:
            id: _lbl_primary
            text: root.text
            font_style: root.font_style
            theme_text_color: root.theme_text_color
            text_color: root.text_color
            size_hint_y: None
            height: self.texture_size[1]
        MDLabel:
            id: _lbl_secondary
            text: '' if root._num_lines == 1 else root.secondary_text
            font_style: root.secondary_font_style
            theme_text_color: root.secondary_theme_text_color
            text_color: root.secondary_text_color
            size_hint_y: None
            height: 0 if root._num_lines == 1 else self.texture_size[1]
            shorten: True if root._num_lines == 2 else False

<OneLineAvatarListItem>
    BoxLayout:
        id: _left_container
        size_hint: None, None
        x: root.x + dp(16)
        y: root.y + root.height/2 - self.height/2
        size: dp(40), dp(40)

<ThreeLineAvatarListItem>
    BoxLayout:
        id: _left_container
        size_hint: None, None
        x: root.x + dp(16)
        y: root.y + root.height - root._txt_top_pad - self.height - dp(5)
        size: dp(40), dp(40)

<OneLineIconListItem>
    BoxLayout:
        id: _left_container
        size_hint: None, None
        x: root.x + dp(16)
        y: root.y + root.height/2 - self.height/2
        size: dp(48), dp(48)

<ThreeLineIconListItem>
    BoxLayout:
        id: _left_container
        size_hint: None, None
        x: root.x + dp(16)
        y: root.y + root.height - root._txt_top_pad - self.height - dp(5)
        size: dp(48), dp(48)

<OneLineRightIconListItem>
    BoxLayout:
        id: _right_container
        size_hint: None, None
        x: root.x + root.width - m_res.HORIZ_MARGINS - self.width
        y: root.y + root.height/2 - self.height/2
        size: dp(48), dp(48)

<ThreeLineRightIconListItem>
    BoxLayout:
        id: _right_container
        size_hint: None, None
        x: root.x + root.width - m_res.HORIZ_MARGINS - self.width
        y: root.y + root.height/2 - self.height/2
        size: dp(48), dp(48)

<OneLineAvatarIconListItem>
    BoxLayout:
        id: _right_container
        size_hint: None, None
        x: root.x + root.width - m_res.HORIZ_MARGINS - self.width
        y: root.y + root.height/2 - self.height/2
        size: dp(48), dp(48)

<TwoLineAvatarIconListItem>
    BoxLayout:
        id: _right_container
        size_hint: None, None
        x: root.x + root.width - m_res.HORIZ_MARGINS - self.width
        y: root.y + root.height/2 - self.height/2
        size: dp(48), dp(48)

<ThreeLineAvatarIconListItem>
    BoxLayout:
        id: _right_container
        size_hint: None, None
        x: root.x + root.width - m_res.HORIZ_MARGINS - self.width
        y: root.y + root.height - root._txt_top_pad - self.height - dp(5)
        size: dp(48), dp(48)
''')


class MDList(GridLayout):
    '''ListItem container. Best used in conjunction with a
    :class:`kivy.uix.ScrollView`.

    When adding (or removing) a widget, it will resize itself to fit its
    children, plus top and bottom paddings as described by the MD spec.
    '''
    selected = ObjectProperty()
    _min_list_height = dp(16)
    _list_vertical_padding = dp(8)

    icon = StringProperty()

    def add_widget(self, widget, index=0):
        super(MDList, self).add_widget(widget, index)
        self.height += widget.height

    def remove_widget(self, widget):
        super(MDList, self).remove_widget(widget)
        self.height -= widget.height


class BaseListItem(ThemableBehavior, RectangularRippleBehavior,
                   ButtonBehavior, FloatLayout):
    '''Base class to all ListItems. Not supposed to be instantiated on its own.
    '''

    text = StringProperty()
    '''Text shown in the first line.

    :attr:`text` is a :class:`~kivy.properties.StringProperty` and defaults
    to "".
    '''
    
    text_color = ListProperty(None)
    ''' Text color used if theme_text_color is set to 'Custom' '''

    font_style = OptionProperty(
        'Subhead', options=['Body1', 'Body2', 'Caption', 'Subhead', 'Title',
                            'Headline', 'Display1', 'Display2', 'Display3',
                            'Display4', 'Button', 'Icon'])
    
    theme_text_color = StringProperty('Primary',allownone=True)
    ''' Theme text color for primary text '''

    secondary_text = StringProperty()
    '''Text shown in the second and potentially third line.

    The text will wrap into the third line if the ListItem's type is set to
    \'one-line\'. It can be forced into the third line by adding a \\n
    escape sequence.

    :attr:`secondary_text` is a :class:`~kivy.properties.StringProperty` and
    defaults to "".
    '''
    
    secondary_text_color = ListProperty(None)
    ''' Text color used for secondary text if secondary_theme_text_color 
    is set to 'Custom' '''
    
    secondary_theme_text_color = StringProperty('Secondary',allownone=True)
    ''' Theme text color for secondary primary text '''
    
    secondary_font_style = OptionProperty(
        'Body1', options=['Body1', 'Body2', 'Caption', 'Subhead', 'Title',
                          'Headline', 'Display1', 'Display2', 'Display3',
                          'Display4', 'Button', 'Icon'])

    _txt_left_pad = NumericProperty(dp(16))
    _txt_top_pad = NumericProperty()
    _txt_bot_pad = NumericProperty()
    _txt_right_pad = NumericProperty(m_res.HORIZ_MARGINS)
    _num_lines = 2


class ILeftBody:
    '''Pseudo-interface for widgets that go in the left container for
    ListItems that support it.

    Implements nothing and requires no implementation, for annotation only.
    '''
    pass


class ILeftBodyTouch:
    '''Same as :class:`~ILeftBody`, but allows the widget to receive touch
    events instead of triggering the ListItem's ripple effect
    '''
    pass


class IRightBody:
    '''Pseudo-interface for widgets that go in the right container for
    ListItems that support it.

    Implements nothing and requires no implementation, for annotation only.
    '''
    pass


class IRightBodyTouch:
    '''Same as :class:`~IRightBody`, but allows the widget to receive touch
    events instead of triggering the ListItem's ripple effect
    '''
    pass


class ContainerSupport:
    '''Overrides add_widget in a ListItem to include support for I*Body
    widgets when the appropiate containers are present.
    '''
    _touchable_widgets = ListProperty()

    def add_widget(self, widget, index=0):
        if issubclass(widget.__class__, ILeftBody):
            self.ids['_left_container'].add_widget(widget)
        elif issubclass(widget.__class__, ILeftBodyTouch):
            self.ids['_left_container'].add_widget(widget)
            self._touchable_widgets.append(widget)
        elif issubclass(widget.__class__, IRightBody):
            self.ids['_right_container'].add_widget(widget)
        elif issubclass(widget.__class__, IRightBodyTouch):
            self.ids['_right_container'].add_widget(widget)
            self._touchable_widgets.append(widget)
        else:
            return super(BaseListItem, self).add_widget(widget,index)

    def remove_widget(self, widget):
        super(BaseListItem, self).remove_widget(widget)
        if widget in self._touchable_widgets:
            self._touchable_widgets.remove(widget)

    def on_touch_down(self, touch):
        if self.propagate_touch_to_touchable_widgets(touch, 'down'):
            return
        super(BaseListItem, self).on_touch_down(touch)

    def on_touch_move(self, touch, *args):
        if self.propagate_touch_to_touchable_widgets(touch, 'move', *args):
            return
        super(BaseListItem, self).on_touch_move(touch, *args)

    def on_touch_up(self, touch):
        if self.propagate_touch_to_touchable_widgets(touch, 'up'):
            return
        super(BaseListItem, self).on_touch_up(touch)

    def propagate_touch_to_touchable_widgets(self, touch, touch_event, *args):
        triggered = False
        for i in self._touchable_widgets:
            if i.collide_point(touch.x, touch.y):
                triggered = True
                if touch_event == 'down':
                    i.on_touch_down(touch)
                elif touch_event == 'move':
                    i.on_touch_move(touch, *args)
                elif touch_event == 'up':
                    i.on_touch_up(touch)
        return triggered


class OneLineListItem(BaseListItem):
    _txt_top_pad = NumericProperty(dp(16))
    _txt_bot_pad = NumericProperty(dp(15))  # dp(20) - dp(5)
    _num_lines = 1

    def __init__(self, **kwargs):
        super(OneLineListItem, self).__init__(**kwargs)
        self.height = dp(48)


class TwoLineListItem(BaseListItem):
    _txt_top_pad = NumericProperty(dp(20))
    _txt_bot_pad = NumericProperty(dp(15))  # dp(20) - dp(5)

    def __init__(self, **kwargs):
        super(TwoLineListItem, self).__init__(**kwargs)
        self.height = dp(72)


class ThreeLineListItem(BaseListItem):
    _txt_top_pad = NumericProperty(dp(16))
    _txt_bot_pad = NumericProperty(dp(15))  # dp(20) - dp(5)
    _num_lines = 3

    def __init__(self, **kwargs):
        super(ThreeLineListItem, self).__init__(**kwargs)
        self.height = dp(88)


class OneLineAvatarListItem(ContainerSupport, BaseListItem):
    _txt_left_pad = NumericProperty(dp(72))
    _txt_top_pad = NumericProperty(dp(20))
    _txt_bot_pad = NumericProperty(dp(19))  # dp(24) - dp(5)
    _num_lines = 1

    def __init__(self, **kwargs):
        super(OneLineAvatarListItem, self).__init__(**kwargs)
        self.height = dp(56)


class TwoLineAvatarListItem(OneLineAvatarListItem):
    _txt_top_pad = NumericProperty(dp(20))
    _txt_bot_pad = NumericProperty(dp(15))  # dp(20) - dp(5)
    _num_lines = 2

    def __init__(self, **kwargs):
        super(BaseListItem, self).__init__(**kwargs)
        self.height = dp(72)


class ThreeLineAvatarListItem(ContainerSupport, ThreeLineListItem):
    _txt_left_pad = NumericProperty(dp(72))


class OneLineIconListItem(ContainerSupport, OneLineListItem):
    _txt_left_pad = NumericProperty(dp(72))


class TwoLineIconListItem(OneLineIconListItem):
    _txt_top_pad = NumericProperty(dp(20))
    _txt_bot_pad = NumericProperty(dp(15))  # dp(20) - dp(5)
    _num_lines = 2

    def __init__(self, **kwargs):
        super(BaseListItem, self).__init__(**kwargs)
        self.height = dp(72)


class ThreeLineIconListItem(ContainerSupport, ThreeLineListItem):
    _txt_left_pad = NumericProperty(dp(72))


class OneLineRightIconListItem(ContainerSupport, OneLineListItem):
    # dp(40) = dp(16) + dp(24):
    _txt_right_pad = NumericProperty(dp(40) + m_res.HORIZ_MARGINS)


class TwoLineRightIconListItem(OneLineRightIconListItem):
    _txt_top_pad = NumericProperty(dp(20))
    _txt_bot_pad = NumericProperty(dp(15))  # dp(20) - dp(5)
    _num_lines = 2

    def __init__(self, **kwargs):
        super(BaseListItem, self).__init__(**kwargs)
        self.height = dp(72)


class ThreeLineRightIconListitem(ContainerSupport, ThreeLineListItem):
    # dp(40) = dp(16) + dp(24):
    _txt_right_pad = NumericProperty(dp(40) + m_res.HORIZ_MARGINS)


class OneLineAvatarIconListItem(OneLineAvatarListItem):
    # dp(40) = dp(16) + dp(24):
    _txt_right_pad = NumericProperty(dp(40) + m_res.HORIZ_MARGINS)


class TwoLineAvatarIconListItem(TwoLineAvatarListItem):
    # dp(40) = dp(16) + dp(24):
    _txt_right_pad = NumericProperty(dp(40) + m_res.HORIZ_MARGINS)


class ThreeLineAvatarIconListItem(ThreeLineAvatarListItem):
    # dp(40) = dp(16) + dp(24):
    _txt_right_pad = NumericProperty(dp(40) + m_res.HORIZ_MARGINS)
