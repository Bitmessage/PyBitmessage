# -*- coding: utf-8 -*-

from kivy.lang import Builder
from kivy.properties import StringProperty, ListProperty, OptionProperty
from kivy.utils import get_color_from_hex
from kivymd.color_definitions import colors
from kivymd.theming import ThemableBehavior
from kivy.uix.accordion import Accordion, AccordionItem
from kivymd.backgroundcolorbehavior import BackgroundColorBehavior
from kivy.uix.boxlayout import BoxLayout


class MDAccordionItemTitleLayout(ThemableBehavior, BackgroundColorBehavior, BoxLayout):
    pass


class MDAccordion(ThemableBehavior, BackgroundColorBehavior, Accordion):
    pass


class MDAccordionItem(ThemableBehavior, AccordionItem):
    title_theme_color = OptionProperty(None, allownone=True,
                                       options=['Primary', 'Secondary', 'Hint',
                                                'Error', 'Custom'])
    ''' Color theme for title text and  icon '''

    title_color = ListProperty(None, allownone=True)
    ''' Color for title text and icon if `title_theme_color` is Custom '''
    
    background_color = ListProperty(None, allownone=True)
    ''' Color for the background of the accordian item title in rgba format. 
    '''
    
    divider_color = ListProperty(None, allownone=True)
    ''' Color for dividers between different titles in rgba format 
    To remove the divider set a color with an alpha of 0. 
    '''

    indicator_color = ListProperty(None, allownone=True)
    ''' Color for the indicator on the side of the active item in rgba format 
    To remove the indicator set a color with an alpha of 0. 
    '''
    
    font_style = OptionProperty(
        'Subhead', options=['Body1', 'Body2', 'Caption', 'Subhead', 'Title',
                          'Headline', 'Display1', 'Display2', 'Display3',
                          'Display4', 'Button', 'Icon'])
    ''' Font style to use for the title text '''

    title_template = StringProperty('MDAccordionItemTitle')
    ''' Template to use for the title '''
    
    icon = StringProperty(None,allownone=True)
    ''' Icon name to use when this item is expanded  '''
    
    icon_expanded = StringProperty('chevron-up')
    ''' Icon name to use when this item is expanded  '''
    
    icon_collapsed = StringProperty('chevron-down')
    ''' Icon name to use when this item is collapsed  '''
 
 
Builder.load_string('''
#:import MDLabel kivymd.label.MDLabel
#:import md_icons kivymd.icon_definitions.md_icons


<MDAccordionItem>:
    canvas.before:
        Color:
            rgba: self.background_color or self.theme_cls.primary_color
        Rectangle:
            size:self.size
            pos:self.pos
        
        PushMatrix
        Translate:
            xy: (dp(2),0) if self.orientation == 'vertical' else (0,dp(2))
    canvas.after:
        PopMatrix
        Color:
            rgba: self.divider_color or self.theme_cls.divider_color   
        Rectangle:
            size:(dp(1),self.height) if self.orientation == 'horizontal' else (self.width,dp(1)) 
            pos:self.pos
        Color:
            rgba: [0,0,0,0] if self.collapse else (self.indicator_color or self.theme_cls.accent_color)   
        Rectangle:
            size:(dp(2),self.height) if self.orientation == 'vertical' else (self.width,dp(2)) 
            pos:self.pos

[MDAccordionItemTitle@MDAccordionItemTitleLayout]:
    padding: '12dp'
    spacing: '12dp'
    orientation: 'horizontal' if ctx.item.orientation=='vertical' else 'vertical'
    canvas:
        PushMatrix
        Translate:
            xy: (-dp(2),0) if ctx.item.orientation == 'vertical' else (0,-dp(2))
            
        Color:
            rgba: self.background_color or self.theme_cls.primary_color
        Rectangle:
            size:self.size
            pos:self.pos
        
    canvas.after:
        Color:
            rgba: [0,0,0,0] if ctx.item.collapse else (ctx.item.indicator_color or self.theme_cls.accent_color)   
        Rectangle:
            size:(dp(2),self.height) if ctx.item.orientation == 'vertical' else (self.width,dp(2)) 
            pos:self.pos
        PopMatrix
    MDLabel:
        id:_icon
        theme_text_color:ctx.item.title_theme_color if ctx.item.icon else 'Custom'
        text_color:ctx.item.title_color if ctx.item.icon else [0,0,0,0]
        text: md_icons[ctx.item.icon if ctx.item.icon else 'menu']
        font_style:'Icon'
        size_hint: (None,1) if ctx.item.orientation == 'vertical' else (1,None)
        size: ((self.texture_size[0],1) if ctx.item.orientation == 'vertical' else (1,self.texture_size[1])) \
            if ctx.item.icon else (0,0)
        text_size: (self.width, None) if ctx.item.orientation=='vertical' else (None,self.width)
        canvas.before:
            PushMatrix
            Rotate:
                angle: 90 if ctx.item.orientation == 'horizontal' else 0
                origin: self.center
        canvas.after:
            PopMatrix
    MDLabel:
        id:_label
        theme_text_color:ctx.item.title_theme_color
        text_color:ctx.item.title_color
        text: ctx.item.title
        font_style:ctx.item.font_style
        text_size: (self.width, None) if ctx.item.orientation=='vertical' else (None,self.width)
        canvas.before:
            PushMatrix
            Rotate:
                angle: 90 if ctx.item.orientation == 'horizontal' else 0
                origin: self.center
        canvas.after:
            PopMatrix
        
    MDLabel:
        id:_expand_icon
        theme_text_color:ctx.item.title_theme_color
        text_color:ctx.item.title_color
        font_style:'Icon'
        size_hint: (None,1) if ctx.item.orientation == 'vertical' else (1,None)
        size: (self.texture_size[0],1) if ctx.item.orientation == 'vertical' else (1,self.texture_size[1])
        text:md_icons[ctx.item.icon_collapsed if ctx.item.collapse else ctx.item.icon_expanded]
        halign: 'right' if ctx.item.orientation=='vertical' else 'center'
        #valign: 'middle' if ctx.item.orientation=='vertical' else 'bottom'
        canvas.before:
            PushMatrix
            Rotate:
                angle: 90 if ctx.item.orientation == 'horizontal' else 0
                origin:self.center
        canvas.after:
            PopMatrix
    
''')           
    
if __name__ == '__main__':
    from kivy.app import App
    from kivymd.theming import ThemeManager
    
    class AccordionApp(App):
        theme_cls = ThemeManager()

        def build(self):
            # self.theme_cls.primary_palette = 'Indigo'
            return Builder.load_string("""
#:import MDLabel kivymd.label.MDLabel
#:import MDList kivymd.list.MDList
#:import OneLineListItem kivymd.list.OneLineListItem
BoxLayout:
    spacing: '64dp'
    MDAccordion:
        orientation:'vertical'
        MDAccordionItem:
            title:'Item 1'
            icon: 'home'
            ScrollView:
                MDList:
                    OneLineListItem:
                        text: "Subitem 1"
                        theme_text_color: 'Custom'
                        text_color: [1,1,1,1]
                    OneLineListItem:
                        text: "Subitem 2"
                        theme_text_color: 'Custom'
                        text_color: [1,1,1,1]
                    OneLineListItem:
                        text: "Subitem 3"
                        theme_text_color: 'Custom'
                        text_color: [1,1,1,1]
        MDAccordionItem:
            title:'Item 2'
            icon: 'globe'
            ScrollView:
                MDList:
                    OneLineListItem:
                        text: "Subitem 4"
                        theme_text_color: 'Custom'
                        text_color: [1,1,1,1]
                    OneLineListItem:
                        text: "Subitem 5"
                        theme_text_color: 'Custom'
                        text_color: [1,1,1,1]
                    OneLineListItem:
                        text: "Subitem 6"
                        theme_text_color: 'Custom'
                        text_color: [1,1,1,1]
        MDAccordionItem:
            title:'Item 3'
            ScrollView:
                MDList:
                    OneLineListItem:
                        text: "Subitem 7"
                        theme_text_color: 'Custom'
                        text_color: [1,1,1,1]
                    OneLineListItem:
                        text: "Subitem 8"
                        theme_text_color: 'Custom'
                        text_color: [1,1,1,1]
                    OneLineListItem:
                        text: "Subitem 9"
                        theme_text_color: 'Custom'
                        text_color: [1,1,1,1]
    MDAccordion:
        orientation:'horizontal'
        MDAccordionItem:
            title:'Item 1'
            icon: 'home'
            MDLabel:
                text:'Content 1'
                theme_text_color:'Primary'
        MDAccordionItem:
            title:'Item 2'
            MDLabel:
                text:'Content 2'
                theme_text_color:'Primary'
        MDAccordionItem:
            title:'Item 3'
            MDLabel:
                text:'Content 3'
                theme_text_color:'Primary'
""")
            

    AccordionApp().run()
