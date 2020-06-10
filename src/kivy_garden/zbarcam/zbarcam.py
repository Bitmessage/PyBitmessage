import os
from collections import namedtuple

import PIL
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ListProperty, ObjectProperty, NumericProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.animation import Animation
from kivy.graphics import Color, Line
from pyzbar import pyzbar
from kivy.utils import platform
# from android.runnable import run_on_ui_thread

from .utils import fix_android_image

MODULE_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

from kivy.metrics import dp

class ZBarCam(BoxLayout):
    """
    Widget that use the Camera and zbar to detect qrcode.
    When found, the `codes` will be updated.
    """
    resolution = ListProperty([640, 480])
    qrwidth = dp(250) if platform=='android' else dp(600)
    # qrwidth= dp(500) #width of QR code scanner
    line_length= qrwidth/4 #width of boundary line (Focus Box)
    scanner_line_y_initial= NumericProperty(0)
    scanner_line_y_final= NumericProperty(0)
    scanner_line_y= NumericProperty(0)
    scanner_line_width= dp(2)
    sscanner_line_alpha=1
    border_line_alpha=0.4

    symbols = ListProperty([])
    Symbol = namedtuple('Symbol', ['type', 'data'])
    scan_callback= ObjectProperty(None)
    # checking all possible types by default
    code_types = ListProperty(set(pyzbar.ZBarSymbol))

    def __init__(self, **kwargs):
        # lazy loading the kv file rather than loading at module level,
        # that way the `XCamera` import doesn't happen too early
        Builder.load_file(os.path.join(MODULE_DIRECTORY, "zbarcam.kv"))
        super().__init__(**kwargs)
        Clock.schedule_once(lambda dt: self._setup())
        self.register_event_type("on_scan")

    def _setup(self):
        """
        Postpones some setup tasks that require self.ids dictionary.
        """
        self._remove_shoot_button()
        # `self.xcamera._camera` instance may not be available if e.g.
        # the `CAMERA` permission is not granted
        self.xcamera.bind(on_camera_ready=self._on_camera_ready)
        # camera may still be ready before we bind the event
        if self.xcamera._camera is not None:
            self._on_camera_ready(self.xcamera)

    def _on_camera_ready(self, xcamera):
        """
        Starts binding when the `xcamera._camera` instance is ready.
        """
        xcamera._camera.bind(on_texture=self._on_texture)
        #print((self.scanner_line_y_initial, self.scanner_line_y_final))
        #print(self.size[0])
        Clock.schedule_once(lambda dt: self.start_animation(1), 0)
        #start scanning animation
        #self.init_scanner_line(self.scanner_line_y_final)

    def _remove_shoot_button(self):
        """
        Removes the "shoot button", see:
        https://github.com/kivy-garden/garden.xcamera/pull/3
        """
        xcamera = self.xcamera
        shoot_button = xcamera.children[0]
        xcamera.remove_widget(shoot_button)

    def _on_texture(self, instance):
        #print((self.scanner_line_y_initial, self.scanner_line_y_final))
        #print(self.size[0])
        self.symbols = self._detect_qrcode_frame(
            texture=instance.texture, code_types=self.code_types)
        
        txt= ', '.join([symbol.data.decode("utf-8") for symbol in self.symbols])
        if txt:
            self.scanner_line_alpha=0
            self.dispatch("on_scan", txt)
        else: self.scanner_line_alpha=1
    
    def on_scan(self, text, *args):
        if self.scan_callback:
            self.scan_callback(text)
    
    def init_scanner_line(self, *args):
        self.scanner_line_y= self.scanner_line_y_initial
        Clock.schedule_once(lambda dt: self._update_canvas())
        self.update_scanner_line(self.scanner_line_y_final+self.scanner_line_width, self.scanner_line_y_initial-self.scanner_line_width)
    
    def update_scanner_line(self, val1, val2, *args):
        anim= Animation(
            d=1.5,
            scanner_line_y= val1,
        )
        anim += Animation(
            d=1.5,
            scanner_line_y= val2,
        )
        #anim.stop_all(self)
        anim.bind(on_complete=self._repeat_anim)
        anim.bind(on_progress=self._update_canvas)
        anim.start(self)
    
    def start_animation(self, val, *args):
        anim= Animation(
            d=.7,
            border_line_alpha=val
            )
        anim.bind(on_complete=self._repeat_anim)
        anim.bind(on_progress=self.update_border_line)
        anim.start(self)

    def _repeat_anim(self, inst, widget):
        inst.unbind(on_complete=self._repeat_anim)
        border_line_alpha = 0.4 if self.border_line_alpha==1 else 1
        self.start_animation(border_line_alpha)
        # self.update_scanner_line(self.scanner_line_y_final+self.scanner_line_width, self.scanner_line_y_initial-self.scanner_line_width)
    
    def _update_canvas(self, *args):
        self.canvas.remove_group("scanner_line")
        with self.canvas:
            Color(rgba=(0,1,0,self.scanner_line_alpha), group="scanner_line")
            Line(
            group="scanner_line",
            points= [
                self.size[0]/2-self.qrwidth/2+1, self.scanner_line_y,
                self.size[0]/2+self.qrwidth/2-1, self.scanner_line_y
                ],
            width=self.scanner_line_width,
            cap="none"
            )

    def update_border_line(self, *args):
        self.canvas.remove_group("qr_line")
        with self.canvas:
            Color(rgba=(1,1,1,self.border_line_alpha), group="qr_line")
            #top left
            Line(points=[\
                        self.size[0]/2-self.qrwidth/2, self.size[1]/2+self.qrwidth/2-self.line_length,\
                        self.size[0]/2-self.qrwidth/2, self.size[1]/2+self.qrwidth/2,\
                        self.size[0]/2-self.qrwidth/2+self.line_length, self.size[1]/2+self.qrwidth/2],  width=dp(2),cap= "none", group="qr_line")
            
            #top right
            Line(points=[\
                        self.size[0]/2+self.qrwidth/2, self.size[1]/2+self.qrwidth/2-self.line_length,\
                        self.size[0]/2+self.qrwidth/2, self.size[1]/2+self.qrwidth/2,\
                        self.size[0]/2+self.qrwidth/2-self.line_length, self.size[1]/2+self.qrwidth/2], width=dp(2),cap= "none", group="qr_line")
            
            #bottom right
            Line(points=[\
                        self.size[0]/2+self.qrwidth/2, self.size[1]/2-self.qrwidth/2+self.line_length,\
                        self.size[0]/2+self.qrwidth/2, self.size[1]/2-self.qrwidth/2,\
                        self.size[0]/2+self.qrwidth/2-self.line_length, self.size[1]/2-self.qrwidth/2], width= dp(2), cap="none", group="qr_line")
            
            #bottom left
            Line(points=[\
                        self.size[0]/2-self.qrwidth/2, self.size[1]/2-self.qrwidth/2+self.line_length,\
                        self.size[0]/2-self.qrwidth/2, self.size[1]/2-self.qrwidth/2,\
                        self.size[0]/2-self.qrwidth/2+self.line_length, self.size[1]/2-self.qrwidth/2],width= dp(2),cap= "none", group="qr_line")
            

    @classmethod
    def _detect_qrcode_frame(cls, texture, code_types):
        image_data = texture.pixels
        size = texture.size
        #print(cls.height.value, cls.width)
        #print(image_data)
        # Fix for mode mismatch between texture.colorfmt and data returned by
        # texture.pixels. texture.pixels always returns RGBA, so that should
        # be passed to PIL no matter what texture.colorfmt returns. refs:
        # https://github.com/AndreMiras/garden.zbarcam/issues/41
        pil_image = PIL.Image.frombytes(mode='RGBA', size=size,
                                        data=image_data)
        pil_image = fix_android_image(pil_image)
        pil_image.thumbnail(size, PIL.Image.ANTIALIAS)
        
        qrwidth= cls.qrwidth
        cropped_image = pil_image.crop((size[0]/2-qrwidth/4.5,size[1]/2-qrwidth/4.5,size[0]/2+qrwidth/4.5,size[1]/2+qrwidth/4.5))
        
        #print(pil_image.size)
        symbols = []
        codes = pyzbar.decode(cropped_image, symbols=code_types)
        for code in codes:
            symbol = ZBarCam.Symbol(type=code.type, data=code.data)
            symbols.append(symbol)
        
        return symbols
      
        

    @property
    def xcamera(self):
        return self.ids['xcamera']

    def start(self):
        self.xcamera.play = True

    def stop(self):
        self.xcamera.play = False
