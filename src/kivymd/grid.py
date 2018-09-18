# coding=utf-8
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, \
    NumericProperty, ListProperty, OptionProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivymd.ripplebehavior import RectangularRippleBehavior
from kivymd.theming import ThemableBehavior

Builder.load_string("""
<SmartTile>
    _img_widget: img
    _img_overlay: img_overlay
    _box_overlay: box
    AsyncImage:
        id: img
        allow_stretch: root.allow_stretch
        anim_delay: root.anim_delay
        anim_loop: root.anim_loop
        color: root.img_color
        keep_ratio: root.keep_ratio
        mipmap: root.mipmap
        source: root.source
        size_hint_y: 1 if root.overlap else None
        x: root.x
        y: root.y if root.overlap or root.box_position == 'header' else box.top
    BoxLayout:
        id: img_overlay
        size_hint: img.size_hint
        size: img.size
        pos: img.pos
    BoxLayout:
        canvas:
            Color:
                rgba: root.box_color
            Rectangle:
                pos: self.pos
                size: self.size
        id: box
        size_hint_y: None
        height: dp(68) if root.lines == 2 else dp(48)
        x: root.x
        y: root.y if root.box_position == 'footer' else root.y + root.height - self.height

<SmartTileWithLabel>
    _img_widget: img
    _img_overlay: img_overlay
    _box_overlay: box
    _box_label: boxlabel
    AsyncImage:
        id: img
        allow_stretch: root.allow_stretch
        anim_delay: root.anim_delay
        anim_loop: root.anim_loop
        color: root.img_color
        keep_ratio: root.keep_ratio
        mipmap: root.mipmap
        source: root.source
        size_hint_y: 1 if root.overlap else None
        x: root.x
        y: root.y if root.overlap or root.box_position == 'header' else box.top
    BoxLayout:
        id: img_overlay
        size_hint: img.size_hint
        size: img.size
        pos: img.pos
    BoxLayout:
        canvas:
            Color:
                rgba: root.box_color
            Rectangle:
                pos: self.pos
                size: self.size
        id: box
        size_hint_y: None
        height: dp(68) if root.lines == 2 else dp(48)
        x: root.x
        y: root.y if root.box_position == 'footer' else root.y + root.height - self.height
        MDLabel:
            id: boxlabel
            font_style: "Caption"
            halign: "center"
            text: root.text
""")


class Tile(ThemableBehavior, RectangularRippleBehavior, ButtonBehavior,
           BoxLayout):
    """A simple tile. It does nothing special, just inherits the right behaviors
    to work as a building block.
    """
    pass


class SmartTile(ThemableBehavior, RectangularRippleBehavior, ButtonBehavior,
                FloatLayout):
    """A tile for more complex needs.

    Includes an image, a container to place overlays and a box that can act
    as a header or a footer, as described in the Material Design specs.
    """

    box_color = ListProperty([0, 0, 0, 0.5])
    """Sets the color and opacity for the information box."""

    box_position = OptionProperty('footer', options=['footer', 'header'])
    """Determines wether the information box acts as a header or footer to the
    image.
    """

    lines = OptionProperty(1, options=[1, 2])
    """Number of lines in the header/footer.

    As per Material Design specs, only 1 and 2 are valid values.
    """

    overlap = BooleanProperty(True)
    """Determines if the header/footer overlaps on top of the image or not"""

    # Img properties
    allow_stretch = BooleanProperty(True)
    anim_delay = NumericProperty(0.25)
    anim_loop = NumericProperty(0)
    img_color = ListProperty([1, 1, 1, 1])
    keep_ratio = BooleanProperty(False)
    mipmap = BooleanProperty(False)
    source = StringProperty()

    _img_widget = ObjectProperty()
    _img_overlay = ObjectProperty()
    _box_overlay = ObjectProperty()
    _box_label = ObjectProperty()

    def reload(self):
        self._img_widget.reload()

    def add_widget(self, widget, index=0):
        if issubclass(widget.__class__, IOverlay):
            self._img_overlay.add_widget(widget, index)
        elif issubclass(widget.__class__, IBoxOverlay):
            self._box_overlay.add_widget(widget, index)
        else:
            super(SmartTile, self).add_widget(widget, index)


class SmartTileWithLabel(SmartTile):
    _box_label = ObjectProperty()

    # MDLabel properties
    font_style = StringProperty("Caption")
    theme_text_color = StringProperty("")
    text = StringProperty("")
    """Determines the text for the box footer/header"""


class IBoxOverlay():
    """An interface to specify widgets that belong to to the image overlay
    in the :class:`SmartTile` widget when added as a child.
    """
    pass


class IOverlay():
    """An interface to specify widgets that belong to to the image overlay
    in the :class:`SmartTile` widget when added as a child.
    """
    pass
