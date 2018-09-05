import kivy_helper_search
import os
import queues
import shutdown
import state
import time

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import BooleanProperty
from kivy.clock import Clock
from navigationdrawer import NavigationDrawer
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivymd.theming import ThemeManager
from kivymd.toolbar import Toolbar
from bmconfigparser import BMConfigParser
from helper_ackPayload import genAckPayload
from addresses import decodeAddress, addBMIfNotPresent
from helper_sql import sqlExecute
from kivy.core.window import Window
from kivy.uix.actionbar import ActionItem

statusIconColor = 'red'


class NavigateApp(App, TextInput):
    """Application uses kivy in which base Class of Navigate App inherits from the App class."""

    theme_cls = ThemeManager()
    nav_drawer = ObjectProperty()

    def build(self):
        """Return a main_widget as a root widget.

        An application can be built if you return a widget on build(), or if you set
        self.root.
        """
        main_widget = Builder.load_file(
            os.path.join(os.path.dirname(__file__), 'main.kv'))
        self.nav_drawer = Navigator()
        Window.bind(on_keyboard=self._key_handler)
        return main_widget

    def _key_handler(self, instance, key, *args):
        """Escape key manages previous screen on back."""
        if key is 27:
            print(args)
            print(instance)
            self.set_previous_screen()
            return True

    def set_previous_screen(self):
        """Set previous screen based on back."""
        if self.root.ids.scr_mngr.current != 'inbox':
            self.root.ids.scr_mngr.transition.direction = 'left'
            self.root.ids.scr_mngr.current = 'inbox'

    def getCurrentAccountData(self, text):
        """Get Current Address Account Data."""
        state.association = text
        self.root.ids.sc1.clear_widgets()
        self.root.ids.sc2.clear_widgets()
        self.root.ids.sc3.clear_widgets()
        self.root.ids.sc1.add_widget(Inbox())
        self.root.ids.sc2.add_widget(Sent())
        self.root.ids.sc3.add_widget(Trash())
        self.root.ids.toolbar.title = BMConfigParser().get(
            state.association, 'label') + '({})'.format(state.association)
        Inbox()
        Sent()
        Trash()

    def say_exit(self):
        """Exit the application as uses shutdown PyBitmessage."""
        print("**************************EXITING FROM APPLICATION*****************************")
        App.get_running_app().stop()
        shutdown.doCleanShutdown()

    @staticmethod
    def showmeaddresses(name="text"):
        """Show the addresses in spinner to make as dropdown."""
        if name == "text":
            return BMConfigParser().addresses()[0]
        elif name == "values":
            return BMConfigParser().addresses()

    def update_index(self, data_index, index):
        """Update index after archieve message to trash."""
        if self.root.ids.scr_mngr.current == 'inbox':
            self.root.ids.sc1.data[data_index]['index'] = index
        elif self.root.ids.scr_mngr.current == 'sent':
            self.root.ids.sc2.data[data_index]['index'] = index
        elif self.root.ids.scr_mngr.current == 'trash':
            self.root.ids.sc3.data[data_index]['index'] = index

    def delete(self, data_index):
        """It will make delete using remove function."""
        print("delete {}".format(data_index))
        self._remove(data_index)

    def archive(self, data_index):
        """It will make archieve using remove function."""
        print("archive {}".format(data_index))
        self._remove(data_index)

    def _remove(self, data_index):
        """It will remove message by resetting the values in recycleview data."""
        if self.root.ids.scr_mngr.current == 'inbox':
            self.root.ids.sc1.data.pop(data_index)
            self.root.ids.sc1.data = [{
                'data_index': i,
                'index': d['index'],
                'height': d['height'],
                'text': d['text']}
                for i, d in enumerate(self.root.ids.sc1.data)
            ]
        elif self.root.ids.scr_mngr.current == 'sent':
            self.root.ids.sc2.data.pop(data_index)
            self.root.ids.sc2.data = [{
                'data_index': i,
                'index': d['index'],
                'height': d['height'],
                'text': d['text']}
                for i, d in enumerate(self.root.ids.sc2.data)
            ]
        elif self.root.ids.scr_mngr.current == 'trash':
            self.root.ids.sc3.data.pop(data_index)
            self.root.ids.sc3.data = [{
                'data_index': i,
                'index': d['index'],
                'height': d['height'],
                'text': d['text']}
                for i, d in enumerate(self.root.ids.sc3.data)
            ]

    def getInboxMessageDetail(self, instance):
        """It will get message detail after make selected message description."""
        try:
            self.root.ids.scr_mngr.current = 'page'
        except AttributeError:
            self.parent.manager.current = 'page'
        print('Message Clicked {}'.format(instance))

    @staticmethod
    def getCurrentAccount():
        """It uses to get current account label."""
        return BMConfigParser().get(state.association, 'label') + '({})'.format(state.association)


class Navigator(NavigationDrawer):
    """Navigator class uses NavigationDrawer.

    It is an UI panel that shows our app's main navigation menu
    It is hidden when not in use, but appears when the user swipes
    a finger from the left edge of the screen or, when at the top
    level of the app, the user touches the drawer icon in the app bar
    """

    image_source = StringProperty('images/qidenticon_two.png')
    title = StringProperty('Navigation')


class Inbox(Screen):
    """Inbox Screen uses screen to show widgets of screens."""

    data = ListProperty()

    def __init__(self, *args, **kwargs):
        super(Inbox, self).__init__(*args, **kwargs)
        if state.association == '':
            state.association = Navigator().ids.btn.text
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
        """Load Inbox list for inbox messages."""
        xAddress = "toaddress"
        queryreturn = kivy_helper_search.search_sql(
            xAddress, account, 'inbox', where, what, False)
        if queryreturn:
            self.data = [{
                'data_index': i,
                'index': 1,
                'height': 48,
                'text': row[4]}
                for i, row in enumerate(queryreturn)
            ]
        else:
            self.data = [{
                'data_index': 1,
                'index': 1,
                'height': 48,
                'text': "yet no message for this account!!!!!!!!!!!!!"}
            ]


class Page(Screen):
    pass


class AddressSuccessful(Screen):
    pass


class Sent(Screen):
    """Sent Screen uses screen to show widgets of screens."""

    data = ListProperty()

    def __init__(self, *args, **kwargs):
        super(Sent, self).__init__(*args, **kwargs)
        if state.association == '':
            state.association = Navigator().ids.btn.text
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
        if queryreturn:
            self.data = [{
                'data_index': i,
                'index': 1,
                'height': 48,
                'text': row[2]}
                for i, row in enumerate(queryreturn)
            ]
        else:
            self.data = [{
                'data_index': 1,
                'index': 1,
                'height': 48,
                'text': "yet no message for this account!!!!!!!!!!!!!"}
            ]


class Trash(Screen):
    """Trash Screen uses screen to show widgets of screens."""

    data = ListProperty()

    def __init__(self, *args, **kwargs):
        super(Trash, self).__init__(*args, **kwargs)
        if state.association == '':
            state.association = Navigator().ids.btn.text
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method inbox accounts."""
        self.inboxaccounts()
        print(dt)

    def inboxaccounts(self):
        """Load inbox accounts."""
        account = state.association
        self.loadTrashlist(account, 'All', '')

    def loadTrashlist(self, account, where="", what=""):
        """Load Trash list for trashed messages."""
        xAddress = "toaddress"
        queryreturn = kivy_helper_search.search_sql(
            xAddress, account, 'trash', where, what, False)
        if queryreturn:
            self.data = [{
                'data_index': i,
                'index': 1,
                'height': 48,
                'text': row[4]}
                for i, row in enumerate(queryreturn)
            ]
        else:
            self.data = [{
                'data_index': 1,
                'index': 1,
                'height': 48,
                'text': "yet no message for this account!!!!!!!!!!!!!"}
            ]


class Dialog(Screen):
    """Dialog Screen uses screen to show widgets of screens."""

    pass


class Test(Screen):
    """Test Screen uses screen to show widgets of screens."""

    pass


class Create(Screen):
    """Create Screen uses screen to show widgets of screens."""

    def __init__(self, *args, **kwargs):
        super(Create, self).__init__(*args, **kwargs)

    def send(self):
        """Send message from one address to another."""
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
        """Reset values for send message."""
        self.ids.message.text = ''
        self.ids.spinner_id.text = '<select>'
        self.ids.subject.text = ''
        self.ids.recipent.text = ''
        return None


class NewIdentity(Screen):
    """Create new address for PyBitmessage."""

    is_active = BooleanProperty(False)
    checked = StringProperty("")
    # self.manager.parent.ids.create.children[0].source = 'images/plus-4-xxl.png'

    def generateaddress(self):
        """Generate new address."""
        if self.checked == 'use a random number generator to make an address':
            queues.apiAddressGeneratorReturnQueue.queue.clear()
            streamNumberForAddress = 1
            label = self.ids.label.text
            eighteenByteRipe = False
            nonceTrialsPerByte = 1000
            payloadLengthExtraBytes = 1000

            queues.addressGeneratorQueue.put((
                'createRandomAddress',
                4, streamNumberForAddress,
                label, 1, "", eighteenByteRipe,
                nonceTrialsPerByte,
                payloadLengthExtraBytes)
            )
            self.manager.current = 'add_sucess'


class SearchBar(TextInput, ActionItem):
    """Create SearchBar for PyBitmessage."""

    def __init__(self, *args, **kwargs):
        """Initailizes SearchBar with hint text."""
        super(SearchBar, self).__init__(*args, **kwargs)
        self.hint_text = 'Search'

    def search(self):
        """Search for message request."""
        request = self.text
        return str(request)


if __name__ == '__main__':
    NavigateApp().run()
