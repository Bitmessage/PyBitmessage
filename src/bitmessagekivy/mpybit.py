# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivymd.bottomsheet import MDListBottomSheet, MDGridBottomSheet
from kivymd.button import MDIconButton
from kivymd.date_picker import MDDatePicker
from kivymd.dialog import MDDialog
from kivymd.label import MDLabel
from kivymd.list import ILeftBody, ILeftBodyTouch, IRightBodyTouch, BaseListItem
from kivymd.material_resources import DEVICE_TYPE
from kivymd.navigationdrawer import MDNavigationDrawer, NavigationDrawerHeaderBase
from kivymd.selectioncontrols import MDCheckbox
from kivymd.snackbar import Snackbar
from kivymd.theming import ThemeManager
from kivymd.time_picker import MDTimePicker
from kivymd.list import ThreeLineAvatarIconListItem, TwoLineAvatarIconListItem, TwoLineListItem
from kivy.properties import ListProperty, StringProperty, BooleanProperty
from kivy.clock import Clock
from bmconfigparser import BMConfigParser
import state
import queues
from kivy.uix.popup import Popup
from helper_sql import *
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, ListProperty, BooleanProperty, ObjectProperty
from kivy.uix.recycleview import RecycleView
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
import time
from uikivysignaler import UIkivySignaler
from semaphores import kivyuisignaler
from kivy.uix.button import Button
import kivy_helper_search
from kivy.core.window import Window
from functools import partial
from kivy.uix.carousel import Carousel


class Navigatorss(MDNavigationDrawer):
    image_source = StringProperty('images/qidenticon_two.png')
    title = StringProperty('Navigation')
    drawer_logo = StringProperty()


class Inbox(Screen):
    """Inbox Screen uses screen to show widgets of screens."""
    data = ListProperty()

    def __init__(self, *args, **kwargs):
        super(Inbox, self).__init__(*args, **kwargs)
        if state.association == '':
            if BMConfigParser().addresses():
                state.association = BMConfigParser().addresses()[0]
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method inbox accounts."""
        self.inboxaccounts()
        print(dt)

    def inboxaccounts(self):
        """Load inbox accounts."""
        account = state.association
        self.loadMessagelist(account, 'All', '')

    def loadMessagelist(self, account, where="", what=""):
        """Load Inbox list for Inbox messages."""
        xAddress = 'toaddress'
        data = []
        queryreturn = kivy_helper_search.search_sql(
            xAddress, account, "inbox", where, what, False)
        if queryreturn:
            for mail in queryreturn:
                third_text = mail[3].replace('\n', ' ')
                # ('inbox', 'j\xe5(M\xcfPbe\rl\x0f\xa3\r\xef>\xf0\x0b&\t\'}"RYg\x03\x80\x14\x82\xeb&,', 'BM-2cXpNNd7dhTjsv7LHNfmphfUabZk958sA3', 'hello', 'BM-2cWyUfBdY2FbgyuCb7abFZ49JYxSzUhNFe', 'test from peter', '1559121770', 0)
                data.append({'text': mail[4].strip(), 'secondary_text': mail[5][:10] + '...........' if len(mail[3]) > 10 else mail[3] + '\n' + " " + (third_text[:25] + '...!') if len(third_text) > 25 else third_text, 'receivedTime':  mail[6] })
            for item in data:
                meny = ThreeLineAvatarIconListItem(text=item['text'], secondary_text=item['secondary_text'], theme_text_color= 'Custom', text_color=NavigateApp().theme_cls.primary_color)
                meny.add_widget(AvatarSampleWidget(source='./images/avatar.png'))
                meny.bind(on_press = partial(self.inbox_detail, item['receivedTime']))
                carousel = Carousel(direction='right')
                carousel.height = 150
                carousel.size_hint_y = None
                carousel.ignore_perpendicular_swipes = True
                carousel.data_index = 0
                carousel.min_move = 0.2
                del_btn = Button(text='Delete')
                del_btn.background_color = (1, 0, 0, .5)
                del_btn.bind(on_press=partial(self.delete, item['receivedTime']))
                carousel.add_widget(del_btn)
                carousel.add_widget(meny)
                ach_btn = Button(text='Achieve')
                ach_btn.background_color = (0,1,0,1)
                ach_btn.bind(on_press=partial(self.archive, item['receivedTime']))
                carousel.add_widget(ach_btn)
                carousel.index=1
                self.ids.ml.add_widget(carousel)
        else:
            content = MDLabel(font_style='Body1',
                              theme_text_color='Primary',
                              text="yet no message for this account!!!!!!!!!!!!!",
                              halign='center',
                              bold=True,
                              size_hint_y=None,
                              valign='top')
            self.ids.ml.add_widget(content)

    def inbox_detail(self, receivedTime, *args):
        """Load inbox page details"""
        state.detailPageType = 'inbox'
        state.sentMailTime = receivedTime
        if self.manager:
            src_mng_obj = self.manager
        else:
            src_mng_obj = self.parent.parent
        src_mng_obj.screens[13].clear_widgets()
        src_mng_obj.screens[13].add_widget(MailDetail())
        src_mng_obj.current = 'mailDetail'

    def delete(self, data_index, instance, *args):
        """Delete inbox mail from inbox listing"""
        sqlExecute("UPDATE inbox SET folder = 'trash' WHERE received = {};".format(data_index))
        self.ids.ml.remove_widget(instance.parent.parent)
        self.update_trash()

    def archive(self, data_index, instance, *args):
        """Archive inbox mail from inbox listing"""
        sqlExecute("UPDATE inbox SET folder = 'trash' WHERE received = {};".format(data_index))
        self.ids.ml.remove_widget(instance.parent.parent)
        self.update_trash()

    def update_trash(self):
        """Update trash screen mails which is deleted from inbox"""
        try:
            self.parent.screens[4].clear_widgets()
            self.parent.screens[4].add_widget(Trash())
        except Exception as e:
            self.parent.parent.screens[4].clear_widgets()
            self.parent.parent.screens[4].add_widget(Trash())



class MyAddress(Screen):
    """MyAddress Screen uses screen to show widgets of screens."""
    def __init__(self, *args, **kwargs):
        super(MyAddress, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method inbox accounts."""
        if BMConfigParser().addresses() or ContentNavigationDrawer().ids.btn.values:
            data = []
            for address in ContentNavigationDrawer().ids.btn.values:
                data.append({'text': BMConfigParser().get(address, 'label'), 'secondary_text': address})
            for item in data:
                meny = TwoLineAvatarIconListItem(text=item['text'], secondary_text=item['secondary_text'], theme_text_color= 'Custom',text_color=NavigateApp().theme_cls.primary_color)
                meny.add_widget(AvatarSampleWidget(source='./images/avatar.png'))
                meny.bind(on_press = partial(self.myadd_detail, item['secondary_text']))
                self.ids.ml.add_widget(meny)
        else:
            content = MDLabel(font_style='Body1',
                              theme_text_color='Primary',
                              text="yet no address is created by user!!!!!!!!!!!!!",
                              halign='center',
                              bold=True,
                              size_hint_y=None,
                              valign='top')
            self.ids.ml.add_widget(content)
            try:
                self.manager.current = 'login'
            except Exception as e:
                pass

    def myadd_detail(self, fromaddress, *args):
        p = MyaddDetailPopup()
        p.open()
        p.get_address(fromaddress)


class AddressBook(Screen):
    """AddressBook Screen uses screen to show widgets of screens."""
    def __init__(self, *args, **kwargs):
        super(AddressBook, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method inbox accounts."""
        data = sqlQuery("SELECT label, address from addressbook")
        if data:
            for item in data:
                meny = TwoLineAvatarIconListItem(text=item[0], secondary_text=item[1], theme_text_color='Custom',text_color=NavigateApp().theme_cls.primary_color)
                meny.add_widget(AvatarSampleWidget(source='./images/avatar.png'))
                self.ids.ml.add_widget(meny)
        else:
            content = MDLabel(font_style='Body1',
                              theme_text_color='Primary',
                              text="No Contact Found yet...... ",
                              halign='center',
                              bold=True,
                              size_hint_y=None,
                              valign='top')
            self.ids.ml.add_widget(content)

    def refreshs(self, *args):
        state.navinstance.ids.sc11.clear_widgets()
        state.navinstance.ids.sc11.add_widget(AddressBook())


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''
    pass


class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
            rv.parent.txt_input.text = rv.parent.txt_input.text.replace(rv.parent.txt_input.text, rv.data[index]['text'])


class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)


class DropDownWidget(BoxLayout):
    txt_input = ObjectProperty()
    rv = ObjectProperty()

    def send(self):
        """Send message from one address to another."""
        fromAddress = str(self.ids.ti.text)
        toAddress = str(self.ids.txt_input.text)
        subject = str(self.ids.subject.text)
        message = str(self.ids.body.text)
        encoding = 3
        print("message: ", self.ids.body.text)
        sendMessageToPeople = True
        if sendMessageToPeople:
            if toAddress != '' and subject and message:
                from addresses import decodeAddress
                status, addressVersionNumber, streamNumber, ripe = decodeAddress(
                    toAddress)
                if status == 'success':
                    from addresses import *
                    toAddress = addBMIfNotPresent(toAddress)
                    statusIconColor = 'red'
                    if addressVersionNumber > 4 or addressVersionNumber <= 1:
                        print("addressVersionNumber > 4 or addressVersionNumber <= 1")
                    if streamNumber > 1 or streamNumber == 0:
                        print("streamNumber > 1 or streamNumber == 0")
                    if statusIconColor == 'red':
                        print("shared.statusIconColor == 'red'")
                    stealthLevel = BMConfigParser().safeGetInt(
                        'bitmessagesettings', 'ackstealthlevel')
                    from helper_ackPayload import genAckPayload
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
                    self.parent.parent.screens[3].clear_widgets()
                    self.parent.parent.screens[3].add_widget(Sent())
                    toLabel = ''
                    queues.workerQueue.put(('sendmessage', toAddress))
                    print("sqlExecute successfully #######################")
                    self.ids.body.text = ''
                    self.ids.ti.text = ''
                    self.ids.subject.text = ''
                    self.ids.txt_input.text = ''
                    self.parent.parent.current = 'sent'
                    self.ids.btn.text = 'select'
                    self.ids.ti.text = ''
                    return None
                else:
                    msg = 'Enter a valid recipients address'
            elif not toAddress:
                msg = 'Please fill the form'
            else:
                msg = 'Please fill the form'
            self.address_error_message(msg)

    def address_error_message(self, msg):
        self.box = FloatLayout()
        self.lab = (Label(text=msg, font_size=25,
                          size_hint=(None, None), pos_hint={'x': .25, 'y': .6}))
        self.box.add_widget(self.lab)
        self.but = (Button(text="dismiss", size_hint=(None, None),
                           width=200, height=50, pos_hint={'x': .3, 'y': 0}))
        self.box.add_widget(self.but)
        self.main_pop = Popup(title="Error", content=self.box,
                              size_hint=(None, None), size=(550, 400), auto_dismiss=False, title_size=30)
        self.but.bind(on_press=self.main_pop.dismiss)
        # self.main_pop.background = './images/popup.jpeg'
        self.main_pop.open()


class MyTextInput(TextInput):
    txt_input = ObjectProperty()
    flt_list = ObjectProperty()
    word_list = ListProperty()
    # this is the variable storing the number to which the look-up will start
    starting_no = NumericProperty(3)
    suggestion_text = ''

    def __init__(self, **kwargs):
        super(MyTextInput, self).__init__(**kwargs)

    def on_text(self, instance, value):
        # find all the occurrence of the word
        self.parent.parent.parent.parent.ids.rv.data = []
        matches = [self.word_list[i] for i in range(len(self.word_list)) if self.word_list[i][:self.starting_no] == value[:self.starting_no]]
        # display the data in the recycleview
        display_data = []
        for i in matches:
            display_data.append({'text': i})
        self.parent.parent.parent.parent.ids.rv.data = display_data
        # ensure the size is okay
        if len(matches) <= 10:
            self.parent.height = (250 + (len(matches) * 20))
        else:
            self.parent.height = 400

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if self.suggestion_text and keycode[1] == 'tab':
            self.insert_text(self.suggestion_text + ' ')
            return True
        return super(MyTextInput, self).keyboard_on_key_down(window, keycode, text, modifiers)


class Payment(Screen):
    pass


class Login(Screen):
    pass


class NetworkStat(Screen):
    text_variable_1 = StringProperty('{0}::{1}'.format('Total Connections', '0'))
    text_variable_2 = StringProperty('Processed {0} per-to-per messages'.format('0'))
    text_variable_3 = StringProperty('Processed {0} brodcast messages'.format('0'))
    text_variable_4 = StringProperty('Processed {0} public keys'.format('0'))
    text_variable_5 = StringProperty('Processed {0} object to be synced'.format('0'))

    def __init__(self, *args, **kwargs):
        super(NetworkStat, self).__init__(*args, **kwargs)
        Clock.schedule_interval(self.init_ui, 1)

    def init_ui(self, dt=0):
        """Clock Schdule for method inbox accounts."""
        import network.stats
        import shared
        from network import objectracker
        self.text_variable_1 = '{0} :: {1}'.format('Total Connections', str(len(network.stats.connectedHostsList())))
        self.text_variable_2 = 'Processed {0} per-to-per messages'.format(str(shared.numberOfMessagesProcessed))
        self.text_variable_3 = 'Processed {0} brodcast messages'.format(str(shared.numberOfBroadcastsProcessed))
        self.text_variable_4 = 'Processed {0} public keys'.format(str(shared.numberOfPubkeysProcessed))
        self.text_variable_5 = '{0} object to be synced'.format(len(objectracker.missingObjects))


class ContentNavigationDrawer(Navigatorss):
    pass


class Random(Screen):
    is_active = BooleanProperty(False)
    checked = StringProperty("")
    # self.manager.parent.ids.create.children[0].source = 'images/plus-4-xxl.png'

    def generateaddress(self):
        import queues
        # queues.apiAddressGeneratorReturnQueue.queue.clear()
        streamNumberForAddress = 1
        label = self.ids.label.text
        eighteenByteRipe = False
        nonceTrialsPerByte = 1000
        payloadLengthExtraBytes = 1000
        if self.ids.label.text:
            queues.addressGeneratorQueue.put((
                'createRandomAddress',
                4, streamNumberForAddress,
                label, 1, "", eighteenByteRipe,
                nonceTrialsPerByte,
                payloadLengthExtraBytes)
            )
            # self.manager.current = 'add_sucess'
            self.manager.current = 'myaddress'
            self.ids.label.text = ''
            self.parent.parent.parent.parent.ids.toolbar.opacity = 1
            self.parent.parent.parent.parent.ids.toolbar.disabled = False

            state.myAddressObj = self.parent.parent.parent.parent.ids.sc10
            # self.parent.parent.parent.parent.ids.sc10.clear_widgets()
            # self.parent.parent.parent.parent.ids.sc10.add_widget(MyAddress())
            

class AddressSuccessful(Screen):
    pass


class NavigationLayout():
    pass


class Sent(Screen):
    """Sent Screen uses screen to show widgets of screens."""
    data = ListProperty()

    def __init__(self, *args, **kwargs):
        super(Sent, self).__init__(*args, **kwargs)
        if state.association == '':
            if BMConfigParser().addresses():
                state.association = BMConfigParser().addresses()[0]
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method sent accounts."""
        self.sentaccounts()
        print(dt)

    def sentaccounts(self):
        """Load sent accounts."""
        account = state.association
        self.loadSent(account, 'All', '')

    def loadSent(self, account, where="", what=""):
        """Load Sent list for Sent messages."""
        xAddress = 'fromaddress'
        queryreturn = kivy_helper_search.search_sql(
            xAddress, account, "sent", where, what, False)
        state.totalSentMail = len(queryreturn)
        if queryreturn:
            for mail in queryreturn:
                third_text = mail[3].replace('\n', ' ')
                self.data.append({'text': mail[1].strip(), 'secondary_text': mail[2][:10] + '...........' if len(mail[2]) > 10 else mail[2] + '\n' + " " + (third_text[:25] + '...!') if len(third_text) > 25 else third_text, 'lastactiontime':  mail[6]})
            for item in self.data:
                meny = ThreeLineAvatarIconListItem(text=item['text'], secondary_text=item['secondary_text'], theme_text_color= 'Custom', text_color=NavigateApp().theme_cls.primary_color)
                meny.add_widget(AvatarSampleWidget(source='./images/avatar.png'))
                meny.bind(on_press = partial(self.sent_detail, item['lastactiontime']))
                carousel = Carousel(direction='right')
                carousel.height = 150
                carousel.size_hint_y = None
                carousel.ignore_perpendicular_swipes = True
                carousel.data_index = 0
                carousel.min_move = 0.2
                del_btn = Button(text='Delete')
                del_btn.background_color = (1, 0, 0, .5)
                del_btn.bind(on_press=partial(self.delete, item['lastactiontime']))
                carousel.add_widget(del_btn)
                carousel.add_widget(meny)
                ach_btn = Button(text='Achieve')
                ach_btn.background_color = (0,1,0,1)
                ach_btn.bind(on_press=partial(self.archive, item['lastactiontime']))
                carousel.add_widget(ach_btn)
                carousel.index=1
                self.ids.ml.add_widget(carousel)
                # self.ids.ml.add_widget(meny)
        else:
            content = MDLabel(font_style='Body1',
                              theme_text_color='Primary',
                              text="yet no message for this account!!!!!!!!!!!!!",
                              halign='center',
                              bold=True,
                              size_hint_y=None,
                              valign='top')
            self.ids.ml.add_widget(content)

    def sent_detail(self, lastsenttime, *args):
        """Load sent mail details"""
        state.detailPageType = 'sent'
        state.sentMailTime = lastsenttime
        if self.manager:
            src_mng_obj = self.manager
        else:
            src_mng_obj = self.parent.parent
        src_mng_obj.screens[13].clear_widgets()
        src_mng_obj.screens[13].add_widget(MailDetail())
        src_mng_obj.current = 'mailDetail'

    def delete(self, data_index, instance, *args):
        """delete sent mail from sent mail listing"""
        sqlExecute("UPDATE sent SET folder = 'trash' WHERE lastactiontime = {};".format(data_index))
        self.ids.ml.remove_widget(instance.parent.parent)
        self.update_trash()

    def archive(self, data_index, instance, *args):
        """archive sent mail from sent mail listing"""
        sqlExecute("UPDATE sent SET folder = 'trash' WHERE lastactiontime = {};".format(data_index))
        self.ids.ml.remove_widget(instance.parent.parent)
        self.update_trash()

    def update_trash(self):
        """Update trash screen mails which is deleted from inbox"""
        try:
            self.parent.screens[4].clear_widgets()
            self.parent.screens[4].add_widget(Trash())
        except Exception as e:
            self.parent.parent.screens[4].clear_widgets()
            self.parent.parent.screens[4].add_widget(Trash())


class Trash(Screen):
    """Trash Screen uses screen to show widgets of screens."""
    def __init__(self, *args, **kwargs):
        super(Trash, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method inbox accounts."""
        inbox = sqlQuery("SELECT toaddress, fromaddress, subject, message from inbox WHERE folder = 'trash';")
        sent = sqlQuery("SELECT toaddress, fromaddress, subject, message from sent WHERE folder = 'trash';")
        trash_data = inbox + sent
        for item in trash_data:
            meny = ThreeLineAvatarIconListItem(text=item[1], secondary_text=item[2], theme_text_color= 'Custom',text_color=NavigateApp().theme_cls.primary_color)
            meny.add_widget(AvatarSampleWidget(source='./images/avatar.png'))
            self.ids.ml.add_widget(meny)

class Page(Screen):
    pass


class Create(Screen):
    def __init__(self, **kwargs):
        super(Create, self).__init__(**kwargs)
        widget_1 = DropDownWidget()
        from helper_sql import *
        widget_1.ids.txt_input.word_list = [addr[1] for addr in sqlQuery("SELECT label, address from addressbook")]
        widget_1.ids.txt_input.starting_no = 2
        self.add_widget(widget_1)


class AddressSuccessful(Screen):
    pass


class Setting(Screen):
    pass


class NavigateApp(App):
    theme_cls = ThemeManager()
    previous_date = ObjectProperty()
    obj_1 = ObjectProperty()
    obj_2 = ObjectProperty()
    variable_1 = ListProperty(BMConfigParser().addresses())
    nav_drawer = ObjectProperty()
    total_sentmail = str(state.totalSentMail)
    scr_size = Window.size[0]
    title = "PyBitmessage"
    count = 0
    menu_items = [
        {'viewclass': 'MDMenuItem',
         'text': 'Example item'},
        {'viewclass': 'MDMenuItem',
         'text': 'Example item'},
        {'viewclass': 'MDMenuItem',
         'text': 'Example item'},
        {'viewclass': 'MDMenuItem',
         'text': 'Example item'},
        {'viewclass': 'MDMenuItem',
         'text': 'Example item'},
        {'viewclass': 'MDMenuItem',
         'text': 'Example item'},
        {'viewclass': 'MDMenuItem',
         'text': 'Example item'},
    ]

    def build(self):
        import os
        main_widget = Builder.load_file(
            os.path.join(os.path.dirname(__file__), 'main.kv'))
        self.nav_drawer = Navigatorss()
        self.obj_1 = AddressBook()
        self.obj_2 = MyAddress()
        kivysignalthread = UIkivySignaler()
        kivysignalthread.daemon = True
        kivysignalthread.start()
        Window.bind(on_keyboard=self.on_key)
        return main_widget

    def run(self):
        kivyuisignaler.release()
        super(NavigateApp, self).run()

    def say_exit(self):
        """Exit the application as uses shutdown PyBitmessage."""
        print("**************************EXITING FROM APPLICATION*****************************")
        App.get_running_app().stop()
        import shutdown
        shutdown.doCleanShutdown()

    def show_address_success(self):
        content = MDLabel(font_style='Body1',
                          theme_text_color='Secondary',
                          text="Successfully Saved your contact address. "
                               "That's pretty awesome right!",
                          size_hint_y=None,
                          valign='top')
        content.bind(texture_size=content.setter('size'))
        self.dialog.open()

    @staticmethod
    def showmeaddresses(name="text"):
        """Show the addresses in spinner to make as dropdown."""
        if name == "text":
            # return BMConfigParser().get(BMConfigParser().addresses()[0], 'label')[:12] + '..'
            if bmconfigparserigParser().addresses():
                return BMConfigParser().addresses()[0][:16] + '..'
            else:
                return "textdemo"
        elif name == "values":
            if BMConfigParser().addresses():
                return [address[:16] + '..' for address in BMConfigParser().addresses()]
            else:
                return "valuesdemo"

    def getCurrentAccountData(self, text):
        """Get Current Address Account Data."""
        state.association = text
        self.root.ids.sc1.clear_widgets()
        self.root.ids.sc4.clear_widgets()
        self.root.ids.sc5.clear_widgets()
        self.root.ids.sc1.add_widget(Inbox())
        self.root.ids.sc4.add_widget(Sent())
        self.root.ids.sc5.add_widget(Trash())
        self.root.ids.scr_mngr.current = 'inbox'

    def getInboxMessageDetail(self, instance):
        """It will get message detail after make selected message description."""
        try:
            self.root.ids._mngr.current = 'page'
        except AttributeError:
            self.parent.manager.current = 'page'
        print('Message Clicked {}'.format(instance))

    @staticmethod
    def getCurrentAccount():
        """It uses to get current account label."""
        if state.association:
            return state.association
        else:
            return "Bitmessage Login"

    def addingtoaddressbook(self):
        p = GrashofPopup()
        p.open()

    def getDefaultAccData(self):
        if BMConfigParser().addresses():
            return BMConfigParser().addresses()[0]
        return 'Select Address'

    def addressexist(self):
        if BMConfigParser().addresses():
            return True
        return False

    def limit_spinner(self):
        max = 2.8
        spinner_obj = ContentNavigationDrawer().ids.btn
        spinner_obj.dropdown_cls.max_height = spinner_obj.height* max + max * 4

    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            if self.root.ids.scr_mngr.current_screen.name == "mailDetail":
                self.root.ids.scr_mngr.current = 'sent'
                # this is for direction of the screen comesup
                # self.root.ids.scr_mngr.transition.direction = 'right'
                return True
            elif self.root.ids.scr_mngr.current_screen.name == "create":
                self.root.ids.scr_mngr.current = 'inbox'
                return True
            else:
                return True

    def status_dispatching(self, data):
        ackData, message = data
        if state.ackdata == ackData:
            state.status.status = message


class GrashofPopup(Popup):
    def __init__(self, **kwargs):
        super(GrashofPopup, self).__init__(**kwargs)
        self.size_hint_y = 0.7
        self.size_hint_x = 0.9

    def savecontact(self):
        label = self.ids.label.text
        address = self.ids.address.text
        if label and address:
            state.navinstance = self.parent.children[1]
            queues.UISignalQueue.put(('rerenderAddressBook', ''))
            self.dismiss()
            sqlExecute("INSERT INTO addressbook VALUES(?,?)", label, address)

    def show_error_message(self):
        content = MDLabel(font_style='Body1',
                          theme_text_color='Secondary',
                          text="Hey you are not allowed to save blank address contact. "
                               "That's wrong!",
                          size_hint_y=None,
                          valign='top')
        content.bind(texture_size=content.setter('size'))
        self.dialog = MDDialog(content=content,
                               size_hint=(.8, None),
                               height=dp(200),
                               auto_dismiss=False)

        self.dialog.add_action_button("ok",
                                      action=lambda *x: self.dialog.dismiss())
        self.dialog.open()


class AvatarSampleWidget(ILeftBody, Image):
    pass


class IconLeftSampleWidget(ILeftBodyTouch, MDIconButton):
    pass


class IconRightSampleWidget(IRightBodyTouch, MDCheckbox):

    pass


class NavigationDrawerTwoLineListItem(
        TwoLineListItem, NavigationDrawerHeaderBase):

    address_property = StringProperty()

    def __init__(self, **kwargs):
        super(NavigationDrawerTwoLineListItem, self).__init__(**kwargs)
        Clock.schedule_once(lambda dt: self.setup())

    def setup(self):
        """
        Binds Controller.current_account property.
        """
        pass

    def on_current_account(self, account):
        pass

    def _update_specific_text_color(self, instance, value):
        pass

    def _set_active(self, active, list):
        pass


class MailDetail(Screen):
    """MailDetail Screen uses to show the detail of mails."""
    to_addr = StringProperty()
    from_addr = StringProperty()
    subject = StringProperty()
    message = StringProperty()
    status = StringProperty()

    def __init__(self, *args, **kwargs):
        super(MailDetail, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method MailDetail mails."""
        if state.detailPageType == 'sent':
            data = sqlQuery("select toaddress, fromaddress, subject, message , status, ackdata from sent where lastactiontime = {};".format(state.sentMailTime))
            state.status = self
            state.ackdata = data[0][5]
            self.assign_mail_details(data)
        elif state.detailPageType == 'inbox':
            data = sqlQuery("select toaddress, fromaddress, subject, message from inbox where received = {};".format(state.sentMailTime))
            self.assign_mail_details(data)

    def assign_mail_details(self, data): 
        self.to_addr = data[0][0]
        self.from_addr = data[0][1]
        self.subject = data[0][2].upper()
        self.message = data[0][3]
        if len(data[0]) == 6:
            self.status = data[0][4]

    def delete_mail(self):
        if state.detailPageType == 'sent':
            sqlExecute("UPDATE sent SET folder = 'trash' WHERE lastactiontime = {};".format(state.sentMailTime))
            self.parent.parent.screens[3].clear_widgets()
            self.parent.parent.screens[3].add_widget(Sent())
            self.parent.parent.current = 'sent'
        self.parent.parent.screens[4].clear_widgets()
        self.parent.parent.screens[4].add_widget(Trash())


class MyaddDetailPopup(Popup):
    """MyaddDetailPopup pop is used for showing my address detail"""
    address_label = StringProperty()
    address = StringProperty()

    def __init__(self, **kwargs):
        super(MyaddDetailPopup, self).__init__(**kwargs)
        self.size_hint_y = 0.4
        self.size_hint_x = 0.9

    def get_address(self, address):
        """Getting address for displaying details on popup"""
        self.address_label = BMConfigParser().get(address, 'label') if BMConfigParser().get(address, 'label') else ''
        self.address = address