import os
import kivy_helper_search
import queues
import random
import shutdown
import time

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import BooleanProperty
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.listview import ListItemButton
from navigationdrawer import NavigationDrawer
from kivy.properties import ObjectProperty, StringProperty, ListProperty, NumericProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivymd.theming import ThemeManager
from kivymd.toolbar import Toolbar
from kivy.uix.widget import Widget
from bmconfigparser import BMConfigParser
from helper_ackPayload import genAckPayload
from addresses import decodeAddress, addBMIfNotPresent
from helper_sql import sqlExecute, sqlQuery
statusIconColor = 'red'
avatarlist = os.listdir("images/ngletteravatar")
global belonging
belonging = ''


class NavigateApp(App, TextInput):
    theme_cls = ThemeManager()
    nav_drawer = ObjectProperty()

    def build(self):
        global main_widget
        main_widget = Builder.load_file(
            os.path.join(os.path.dirname(__file__), 'main.kv'))
        self.nav_drawer = Navigator()
        return main_widget

    def getCurrentAccountData(self, text):
        global belonging
        belonging = text
        main_widget.ids.sc1.clear_widgets()
        main_widget.ids.sc2.clear_widgets()
        main_widget.ids.sc1.add_widget(Inbox())
        main_widget.ids.sc2.add_widget(Sent())
        Inbox()
        Sent()

    def say_exit(self):
        print("**************************EXITING FROM APPLICATION*****************************")
        App.get_running_app().stop()
        shutdown.doCleanShutdown()

    def showmeaddresses(self, name="text"):
        if name == "text":
            return BMConfigParser().addresses()[0]
        elif name == "values":
            return BMConfigParser().addresses()


class Navigator(NavigationDrawer):
    image_source = StringProperty('images/qidenticon_two.png')
    title = StringProperty('Navigation')


class Inbox(Screen):
    def __init__(self, *args, **kwargs):
        super(Inbox, self).__init__(*args, **kwargs)
        global belonging
        if belonging == '':
            belonging = Navigator().ids.btn.text
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        global belonging
        self.orientation = "vertical"
        self.inboxaccounts(self.ids.box_share)

    def inboxaccounts(self, box_share):
        account = belonging
        folder = 'inbox'
        self.loadinboxlist(account, folder, box_share, 'All', '')

    def loadinboxlist(self, account, folder, box_share, where="", what="", unreadOnly=False):
        top_logo_share = 1.01
        top_button_share = 1.1
        top_label_share = 1.4
        xAddress = "toaddress"

        queryreturn = kivy_helper_search.search_sql(xAddress, account, folder, where, what, unreadOnly)
        if queryreturn:
            for row in queryreturn:
                msgfolder, msgid, toAddress, fromAddress, subject, received, read = row
                top_logo_share -= .4
                top_button_share -= .4
                top_label_share -= .4
                logo_share = \
                    Image(source='images/ngletteravatar/{}'.format(self.getletterimage(avatarlist, subject)),
                          pos_hint={"center_x": .05, "top": top_logo_share},
                          size_hint_y=None, height=25)
                button_share = \
                    Button(pos_hint={"x": 0, "top": top_button_share},
                           size_hint_y=None, height=40, text=subject, multiline=True, background_color=NavigateApp.theme_cls.primary_dark)
                button_share.bind(on_press=self.getInboxMessageDetail)
                fl = FloatLayout(size_hint_y=None, height=25)
                fl.add_widget(button_share)
                fl.add_widget(logo_share)
                box_share.add_widget(fl)
        else:
            label_share = \
                Label(text="yet you dont have any emails received", pos_hint={"x": 0, "top": top_label_share},
                      size_hint_y=None)
            box_share.add_widget(label_share)

    def getletterimage(self, ran, subject):
        limit = 5
        for x in subject[:limit]:
            if '{}.png'.format(x.lower()) in ran:
                return '{}.png'.format(x.lower())
            elif '{}.jpg'.format(x.lower()) in ran:
                return '{}.jpg'.format(x.lower())
            if x == limit:
                random.shuffle(ran)
                return ran[0]
                break

    def getInboxMessageDetail(self, instance):
        try:
            self.manager.current = 'page'
        except AttributeError:
            self.parent.manager.current = 'page'
        print('I am {}'.format(instance.text))


class Page(Screen):
    pass


class AddressSuccessful(Screen):
    pass


class Sent(Screen):
    def __init__(self, *args, **kwargs):
        super(Sent, self).__init__(*args, **kwargs)
        global belonging
        if belonging == '':
            belonging = Navigator().ids.btn.text
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        global belonging
        self.orientation = "vertical"
        self.sentaccounts(self.ids.box_share)

    def sentaccounts(self, box_share):
        account = belonging
        folder = 'inbox'
        self.loadSent(account, box_share, 'All', '')

    def loadSent(self, account, box_share, where="", what=""):
        top_logo_share = 1.01
        top_button_share = 1.1
        top_label_share = 1.4
        xAddress = 'fromaddress'
        queryreturn = kivy_helper_search.search_sql(xAddress, account, "sent", where, what, False)
        if queryreturn:
            for row in queryreturn:
                toAddress, fromAddress, subject, status, ackdata, lastactiontime = row
                top_logo_share -= .4
                top_button_share -= .4
                top_label_share -= .4
                logo_share = \
                    Image(source='images/ngletteravatar/{}'.format(self.getletterimage(avatarlist, subject)),
                          pos_hint={"center_x": .05, "top": top_logo_share},
                          size_hint_y=None, height=25)
                button_share = \
                    Button(pos_hint={"x": 0, "top": top_button_share},
                           size_hint_y=None, height=40, text=subject, multiline=True, background_color=NavigateApp.theme_cls.primary_dark)
                button_share.bind(on_press=self.getSentMessageDetail)
                fl = FloatLayout(size_hint_y=None, height=25)
                fl.add_widget(button_share)
                fl.add_widget(logo_share)
                box_share.add_widget(fl)
        else:
            label_share = \
                Label(text="yet you dont have any emails received", pos_hint={"x": 0, "top": top_label_share},
                      size_hint_y=None)
            box_share.add_widget(label_share)

    def getletterimage(self, ran, subject):
        limit = 5
        for x in subject[:limit]:
            if '{}.png'.format(x.lower()) in ran:
                return '{}.png'.format(x.lower())
            elif '{}.jpg'.format(x.lower()) in ran:
                return '{}.jpg'.format(x.lower())
            if x == limit:
                random.shuffle(ran)
                return ran[0]
                break

    def getSentMessageDetail(self, instance):
        try:
            self.manager.current = 'page'
        except AttributeError:
            self.parent.manager.current = 'page'
        print('I am {}'.format(instance.text))


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


class Create(Screen):

    def __init__(self, *args, **kwargs):
        super(Create, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        pass

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
    checked = StringProperty("")

    def generateaddress(self):
        if self.checked == 'use a random number generator to make an address':
            queues.apiAddressGeneratorReturnQueue.queue.clear()
            streamNumberForAddress = 1
            label = self.ids.label.text
            eighteenByteRipe = False
            nonceTrialsPerByte = 1000
            payloadLengthExtraBytes = 1000
            queues.addressGeneratorQueue.put((
                'createRandomAddress', 4, streamNumberForAddress, label, 1, "", eighteenByteRipe, nonceTrialsPerByte, payloadLengthExtraBytes)
            )
            self.manager.current = 'add_sucess'

if __name__ == '__main__':
    NavigateApp().run()
