import os
import queues
import shutdown
import time

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty
from kivy.clock import Clock
from kivy.uix.label import Label
from navigationdrawer import NavigationDrawer
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivymd.theming import ThemeManager
from kivymd.toolbar import Toolbar
from kivy.uix.widget import Widget
from bmconfigparser import BMConfigParser
from helper_ackPayload import genAckPayload
from addresses import decodeAddress, addBMIfNotPresent
from helper_sql import sqlExecute
statusIconColor = 'red'


class NavigateApp(App, TextInput):
    theme_cls = ThemeManager()
    nav_drawer = ObjectProperty()

    def build(self):
        main_widget = Builder.load_file(
            os.path.join(os.path.dirname(__file__), 'main.kv'))
        self.nav_drawer = Navigator()
        return main_widget

    def say_exit(self):
        print("**************************EXITING FROM APPLICATION*****************************")
        App.get_running_app().stop()
        shutdown.doCleanShutdown()


class Navigator(NavigationDrawer):
    image_source = StringProperty('images/me.jpg')
    title = StringProperty('Navigation')


class Inbox(Screen):
    def __init__(self, **kwargs):
        super(Inbox, self).__init__(**kwargs)
        val_y = .1
        val_z = 0
        my_box1 = BoxLayout(orientation='vertical')
        for i in range(1, 5):
            my_box1.add_widget(Label(text="I am in inbox", size_hint=(.3, .1), pos_hint={
                               'x': val_z, 'top': val_y}, color=(0, 0, 0, 1), background_color=(0, 0, 0, 0)))
            val_y += .1
        self.add_widget(my_box1)


class Sent(Screen):
    def __init__(self, **kwargs):
        super(Sent, self).__init__(**kwargs)
        val_y = .1
        val_z = 0
        my_box1 = BoxLayout(orientation='vertical')
        for i in range(1, 5):
            my_box1.add_widget(Label(text="I am in sent", size_hint=(.3, .1), pos_hint={
                               'x': val_z, 'top': val_y}, color=(0, 0, 0, 1), background_color=(0, 0, 0, 0)))
            val_y += .1
        self.add_widget(my_box1)


class Trash(Screen):
    def __init__(self, **kwargs):
        super(Trash, self).__init__(**kwargs)
        val_y = .1
        val_z = 0
        my_box1 = BoxLayout(orientation='vertical')
        for i in range(1, 5):
            my_box1.add_widget(Label(text="I am in trash", size_hint=(.3, .1), pos_hint={
                               'x': val_z, 'top': val_y}, color=(0, 0, 0, 1), background_color=(0, 0, 0, 0)))
            val_y += .1
        self.add_widget(my_box1)


class Dialog(Screen):
    pass


class Test(Screen):
    pass


class Create(Screen, Widget):

    def __init__(self, *args, **kwargs):
        super(Create, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        # self.ids['recipent'].bind(text=self.on_text)
        pass

    def showmeaddresses(self):
        return BMConfigParser().addresses()

    def send(self):
        # toAddress = self.ids.recipent.text
        fromAddress = self.ids.spinner_id.text
        # For now we are using static address i.e we are not using recipent field value.
        toAddress = "BM-2cWyUfBdY2FbgyuCb7abFZ49JYxSzUhNFe"
        message = self.ids.message.text
        subject = self.ids.subject.text
        encoding = 3
        print("message: ", self.ids.message.text)
        sendMessageToPeople = True
        if sendMessageToPeople:
            if toAddress != '':
                status, addressVersionNumber, streamNumber, ripe = decodeAddress(
                    toAddress)
                if status == 'success':
                    toAddress = addBMIfNotPresent(toAddress)

                    if addressVersionNumber > 4 or addressVersionNumber <= 1:
                        print("addressVersionNumber > 4 or addressVersionNumber <= 1")
                    if streamNumber > 1 or streamNumber == 0:
                        print("streamNumber > 1 or streamNumber == 0")
                    if statusIconColor == 'red':
                        print("shared.statusIconColor == 'red'")
                    stealthLevel = BMConfigParser().safeGetInt(
                        'bitmessagesettings', 'ackstealthlevel')
                    ackdata = genAckPayload(streamNumber, stealthLevel)
                    t = ()
                    sqlExecute(
                        '''INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                        '',
                        toAddress,
                        ripe,
                        fromAddress,
                        subject,
                        message,
                        ackdata,
                        int(time.time()),
                        int(time.time()),
                        0,
                        'msgqueued',
                        0,
                        'sent',
                        encoding,
                        BMConfigParser().getint('bitmessagesettings', 'ttl'))
                    toLabel = ''
                    queues.workerQueue.put(('sendmessage', toAddress))
                    print("sqlExecute successfully #####    ##################")
                    self.ids.message.text = ''
                    self.ids.spinner_id.text = '<select>'
                    self.ids.subject.text = ''
                    self.ids.recipent.text = ''
                    return None

    def cancel(self):
        self.ids.message.text = ''
        self.ids.spinner_id.text = '<select>'
        self.ids.subject.text = ''
        self.ids.recipent.text = ''
        return None


class NewIdentity(Screen):
    is_active = BooleanProperty(False)


if __name__ == '__main__':
    NavigateApp().run()
