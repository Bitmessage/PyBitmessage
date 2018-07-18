# Created on Jul 8, 2016
#
# The default kivy tab implementation seems like a stupid design to me. The
# ScreenManager is much better.
#
# @author: jrm

from kivy.properties import StringProperty, DictProperty, ListProperty, \
    ObjectProperty, OptionProperty, BoundedNumericProperty
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivymd.theming import ThemableBehavior
from kivymd.backgroundcolorbehavior import BackgroundColorBehavior
from kivymd.button import MDFlatButton

Builder.load_string("""
<MDTabbedPanel>:
    id: panel
    orientation: 'vertical' if panel.tab_orientation in ['top','bottom'] else 'horizontal'
    ScrollView:
        id: scroll_view
        size_hint_y: None
        height: panel._tab_display_height[panel.tab_display_mode]
        MDTabBar:
            id: tab_bar
            size_hint_y: None
            height: panel._tab_display_height[panel.tab_display_mode]
            background_color: panel.tab_color or panel.theme_cls.primary_color
            canvas:
                # Draw bottom border
                Color:
                    rgba: (panel.tab_border_color or panel.tab_color or panel.theme_cls.primary_dark)
                Rectangle:
                    size: (self.width,dp(2))
    ScreenManager:
        id: tab_manager
        current: root.current
        screens: root.tabs
            

<MDTabHeader>:
    canvas:
        Color:
            rgba: self.panel.tab_color or self.panel.theme_cls.primary_color
        Rectangle:
            size: self.size
            pos: self.pos
            
        # Draw indicator
        Color:
            rgba: (self.panel.tab_indicator_color or self.panel.theme_cls.accent_color) if self.tab \
                and self.tab.manager and self.tab.manager.current==self.tab.name else (self.panel.tab_border_color  \
                or self.panel.tab_color or self.panel.theme_cls.primary_dark)
        Rectangle:
            size: (self.width,dp(2))
            pos: self.pos
            
    size_hint: (None,None) #(1, None)  if self.panel.tab_width_mode=='fixed' else (None,None)
    width: (_label.texture_size[0] + dp(16))
    padding: (dp(12), 0)
    theme_text_color: 'Custom'
    text_color: (self.panel.tab_text_color_active or app.theme_cls.bg_light if app.theme_cls.theme_style == "Light" \
            else app.theme_cls.opposite_bg_light) if self.tab and self.tab.manager \
            and self.tab.manager.current==self.tab.name else (self.panel.tab_text_color \
            or self.panel.theme_cls.primary_light)
    on_press: 
        self.tab.dispatch('on_tab_press') 
        # self.tab.manager.current = self.tab.name
    on_release: self.tab.dispatch('on_tab_release')
    on_touch_down: self.tab.dispatch('on_tab_touch_down',*args)
    on_touch_move: self.tab.dispatch('on_tab_touch_move',*args)
    on_touch_up: self.tab.dispatch('on_tab_touch_up',*args)
    
    
    MDLabel:
        id: _label
        text: root.tab.text if root.panel.tab_display_mode == 'text' else u"{}".format(md_icons[root.tab.icon])
        font_style: 'Button' if root.panel.tab_display_mode == 'text' else 'Icon'
        size_hint_x: None# if root.panel.tab_width_mode=='fixed' else 1
        text_size: (None, root.height)
        height: self.texture_size[1]
        theme_text_color: root.theme_text_color
        text_color: root.text_color
        valign: 'middle'
        halign: 'center'
        opposite_colors: root.opposite_colors
""")


class MDTabBar(ThemableBehavior, BackgroundColorBehavior, BoxLayout):
    pass


class MDTabHeader(MDFlatButton):
    """ Internal widget for headers based on MDFlatButton"""
    
    width = BoundedNumericProperty(dp(None), min=dp(72), max=dp(264), errorhandler=lambda x: dp(72))
    tab = ObjectProperty(None)
    panel = ObjectProperty(None)


class MDTab(Screen):
    """ A tab is simply a screen with meta information
        that defines the content that goes in the tab header.
    """
    __events__ = ('on_tab_touch_down', 'on_tab_touch_move', 'on_tab_touch_up', 'on_tab_press', 'on_tab_release')
    
    # Tab header text
    text = StringProperty("")
    
    # Tab header icon
    icon = StringProperty("circle")
    
    # Tab dropdown menu items
    menu_items = ListProperty()
    
    # Tab dropdown menu (if you want to customize it)
    menu = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(MDTab, self).__init__(**kwargs)
        self.index = 0
        self.parent_widget = None
        self.register_event_type('on_tab_touch_down')
        self.register_event_type('on_tab_touch_move')
        self.register_event_type('on_tab_touch_up')
        self.register_event_type('on_tab_press')
        self.register_event_type('on_tab_release')

    def on_leave(self, *args):
        self.parent_widget.ids.tab_manager.transition.direction = self.parent_widget.prev_dir
        
    def on_tab_touch_down(self, *args):
        pass
    
    def on_tab_touch_move(self, *args):
        pass
    
    def on_tab_touch_up(self, *args):
        pass

    def on_tab_press(self, *args):
        par = self.parent_widget
        if par.previous_tab is not self:
            par.prev_dir = str(par.ids.tab_manager.transition.direction)
            if par.previous_tab.index > self.index:
                par.ids.tab_manager.transition.direction = "right"
            elif par.previous_tab.index < self.index:
                par.ids.tab_manager.transition.direction = "left"
            par.ids.tab_manager.current = self.name
            par.previous_tab = self
    
    def on_tab_release(self, *args):
        pass
    
    def __repr__(self):
        return "<MDTab name='{}', text='{}'>".format(self.name, self.text)
    

class MDTabbedPanel(ThemableBehavior, BackgroundColorBehavior, BoxLayout):
    """ A tab panel that is implemented by delegating all tabs
        to a ScreenManager.
    """
    # If tabs should fill space
    tab_width_mode = OptionProperty('stacked', options=['stacked', 'fixed'])
    
    # Where the tabs go
    tab_orientation = OptionProperty('top', options=['top'])  # ,'left','bottom','right'])
    
    # How tabs are displayed
    tab_display_mode = OptionProperty('text', options=['text', 'icons'])  # ,'both'])
    _tab_display_height = DictProperty({'text': dp(46), 'icons': dp(46), 'both': dp(72)})
    
    # Tab background color (leave empty for theme color)
    tab_color = ListProperty([])
    
    # Tab text color in normal state (leave empty for theme color)
    tab_text_color = ListProperty([])
    
    # Tab text color in active state (leave empty for theme color)
    tab_text_color_active = ListProperty([])
    
    # Tab indicator color  (leave empty for theme color)
    tab_indicator_color = ListProperty([])
    
    # Tab bar bottom border color (leave empty for theme color)
    tab_border_color = ListProperty([])
        
    # List of all the tabs so you can dynamically change them
    tabs = ListProperty([])
    
    # Current tab name
    current = StringProperty(None)
    
    def __init__(self, **kwargs):
        super(MDTabbedPanel, self).__init__(**kwargs)
        self.previous_tab = None
        self.prev_dir = None
        self.index = 0
        self._refresh_tabs()
        
    def on_tab_width_mode(self, *args):
        self._refresh_tabs()
    
    def on_tab_display_mode(self, *args):
        self._refresh_tabs()
    
    def _refresh_tabs(self):
        """ Refresh all tabs """
        # if fixed width, use a box layout
        if not self.ids:
            return
        tab_bar = self.ids.tab_bar
        tab_bar.clear_widgets()
        tab_manager = self.ids.tab_manager
        for tab in tab_manager.screens:
            tab_header = MDTabHeader(tab=tab,
                                     panel=self,
                                     height=tab_bar.height,
                                     )
            tab_bar.add_widget(tab_header)
        
    def add_widget(self, widget, **kwargs):
        """ Add tabs to the screen or the layout.
        :param widget: The widget to add.
        """
        d = {}
        if isinstance(widget, MDTab):
            self.index += 1
            if self.index == 1:
                self.previous_tab = widget
            widget.index = self.index
            widget.parent_widget = self
            self.ids.tab_manager.add_widget(widget)
            self._refresh_tabs()
        else:
            super(MDTabbedPanel, self).add_widget(widget)
        
    def remove_widget(self, widget):
        """ Remove tabs from the screen or the layout.
        :param widget: The widget to remove.
        """
        self.index -= 1
        if isinstance(widget, MDTab):
            self.ids.tab_manager.remove_widget(widget)
            self._refresh_tabs()
        else:
            super(MDTabbedPanel, self).remove_widget(widget)

        
if __name__ == '__main__':
    from kivy.app import App
    from kivymd.theming import ThemeManager
    
    class TabsApp(App):
        theme_cls = ThemeManager()

        def build(self):
            from kivy.core.window import Window
            Window.size = (540, 720)
            # self.theme_cls.theme_style = 'Dark'

            return Builder.load_string("""
#:import Toolbar kivymd.toolbar.Toolbar
BoxLayout:
    orientation:'vertical'
    Toolbar:
        id: toolbar
        title: 'Page title'
        background_color: app.theme_cls.primary_color
        left_action_items: [['menu', lambda x: '']]
        right_action_items: [['search', lambda x: ''],['more-vert',lambda x:'']]
    MDTabbedPanel:
        id: tab_mgr
        tab_display_mode:'icons'
        
        MDTab:
            name: 'music' 
            text: "Music" # Why are these not set!!!
            icon: "playlist-audio"
            MDLabel:
                font_style: 'Body1'
                theme_text_color: 'Primary'
                text: "Here is my music list :)"
                halign: 'center'
        MDTab:
            name: 'movies'
            text: 'Movies'
            icon: "movie"
             
            MDLabel:
                font_style: 'Body1'
                theme_text_color: 'Primary'
                text: "Show movies here :)"
                halign: 'center'
     
        
""")
            

    TabsApp().run()
