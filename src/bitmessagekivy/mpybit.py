"""
src/bitmessagekivy/mpybit.py
=================================
"""
# pylint: disable=relative-import, unused-variable, import-error, no-name-in-module, too-many-lines
import os
import time
from functools import partial
from bmconfigparser import BMConfigParser
from helper_sql import sqlExecute, sqlQuery
from kivy.app import App
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty)
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.carousel import Carousel
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.screenmanager import Screen
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.utils import platform
import kivy_helper_search
from kivymd.button import MDIconButton
from kivymd.dialog import MDDialog
from kivymd.label import MDLabel
from kivymd.list import (
    ILeftBody,
    ILeftBodyTouch,
    IRightBodyTouch,
    TwoLineAvatarIconListItem,
    TwoLineListItem)
from kivymd.navigationdrawer import (
    MDNavigationDrawer,
    NavigationDrawerHeaderBase)
from kivymd.selectioncontrols import MDCheckbox
from kivymd.theming import ThemeManager
import queues
from semaphores import kivyuisignaler
import state
from uikivysignaler import UIkivySignaler

import identiconGeneration
# pylint: disable=unused-argument, too-few-public-methods


def toast(text):
    """Method will display the toast message."""
    from kivymd.toast.kivytoast import toast    # pylint: disable=redefined-outer-name
    toast(text)
    return


class Navigatorss(MDNavigationDrawer):
    """Navigators class contains image, title and logo."""

    image_source = StringProperty('images/qidenticon_two.png')
    title = StringProperty('Navigation')
    drawer_logo = StringProperty()


class Inbox(Screen):
    """Inbox Screen uses screen to show widgets of screens."""

    def __init__(self, *args, **kwargs):
        """Method Parsing the address."""
        super(Inbox, self).__init__(*args, **kwargs)
        if state.association == '':
            if BMConfigParser().addresses():
                state.association = BMConfigParser().addresses()[0]
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method inbox accounts."""
        self.inboxaccounts()
        print dt

    def inboxaccounts(self):
        """Load inbox accounts."""
        account = state.association
        self.loadMessagelist(account, 'All', '')

    def loadMessagelist(self, account, where="", what=""):
        """Load Inbox list for Inbox messages."""
        # pylint: disable=too-many-locals
        if state.searcing_text:
            where = ['subject', 'message']
            what = state.searcing_text
        xAddress = 'toaddress'
        data = []
        queryreturn = kivy_helper_search.search_sql(
            xAddress, account, "inbox", where, what, False)
        if queryreturn:
            src_mng_obj = state.kivyapp.root.children[2].children[0].ids
            src_mng_obj.inbox_cnt.badge_text = str(len(queryreturn))
            state.inbox_count = str(len(queryreturn))
            state.kivyapp.root.ids.sc17.clear_widgets()
            state.kivyapp.root.ids.sc17.add_widget(Allmails())
            for mail in queryreturn:
                third_text = mail[3].replace('\n', ' ')
                data.append({
                    'text': mail[4].strip(),
                    'secondary_text': mail[5][:50] + '........' if len(
                        mail[5]) >= 50 else (
                            mail[5] + ',' + mail[3].replace('\n', ''))[0:50] + '........',
                    'msgid': mail[1]})
            for item in data:
                meny = TwoLineAvatarIconListItem(
                    text=item['text'],
                    secondary_text=item['secondary_text'],
                    theme_text_color='Custom',
                    text_color=NavigateApp().theme_cls.primary_color)
                meny.add_widget(AvatarSampleWidget(
                    source='./images/text_images/{}.png'.format(
                        avatarImageFirstLetter(item['secondary_text'].strip()))))
                meny.bind(on_press=partial(
                    self.inbox_detail, item['msgid']))
                carousel = Carousel(direction='right')
                carousel.height = meny.height
                carousel.size_hint_y = None
                carousel.ignore_perpendicular_swipes = True
                carousel.data_index = 0
                carousel.min_move = 0.2
                del_btn = Button(text='Delete')
                del_btn.background_normal = ''
                del_btn.background_color = (1, 0, 0, 1)
                del_btn.bind(on_press=partial(
                    self.delete, item['msgid']))
                carousel.add_widget(del_btn)
                carousel.add_widget(meny)
                ach_btn = Button(text='Achieve')
                ach_btn.background_color = (0, 1, 0, 1)
                ach_btn.bind(on_press=partial(
                    self.archive, item['msgid']))
                carousel.add_widget(ach_btn)
                carousel.index = 1
                self.ids.ml.add_widget(carousel)
        else:
            content = MDLabel(
                font_style='Body1',
                theme_text_color='Primary',
                text="No message found!" if state.searcing_text
                else "yet no message for this account!!!!!!!!!!!!!",
                halign='center',
                bold=True,
                size_hint_y=None,
                valign='top')
            self.ids.ml.add_widget(content)

    def inbox_detail(self, msg_id, *args):
        """Load inbox page details."""
        state.detailPageType = 'inbox'
        state.mail_id = msg_id
        if self.manager:
            src_mng_obj = self.manager
        else:
            src_mng_obj = self.parent.parent
        src_mng_obj.screens[13].clear_widgets()
        src_mng_obj.screens[13].add_widget(MailDetail())
        src_mng_obj.current = 'mailDetail'

    def delete(self, data_index, instance, *args):
        """Delete inbox mail from inbox listing."""
        sqlExecute(
            "UPDATE inbox SET folder = 'trash' WHERE msgid = ?;", str(
                data_index))
        try:
            msg_count_objs = \
                self.parent.parent.parent.parent.children[2].children[0].ids
        except Exception as e:
            msg_count_objs = \
                self.parent.parent.parent.parent.parent.children[2].children[0].ids
        if int(state.inbox_count) > 0:
            msg_count_objs.inbox_cnt.badge_text = str(
                int(state.inbox_count) - 1)
            msg_count_objs.trash_cnt.badge_text = str(
                int(state.trash_count) + 1)
            msg_count_objs.allmail_cnt.badge_text = str(
                int(state.all_count) - 1)
            state.inbox_count = str(
                int(state.inbox_count) - 1)
            state.trash_count = str(
                int(state.trash_count) + 1)
            state.all_count = str(
                int(state.all_count) - 1)
        self.ids.ml.remove_widget(
            instance.parent.parent)
        toast('Deleted')
        self.update_trash()

    def archive(self, data_index, instance, *args):
        """Archive inbox mail from inbox listing."""
        sqlExecute(
            "UPDATE inbox SET folder = 'trash' WHERE msgid = ?;", str(
                data_index))
        self.ids.ml.remove_widget(instance.parent.parent)
        self.update_trash()

    def update_trash(self):
        """Update trash screen mails which is deleted from inbox."""
        try:
            self.parent.screens[4].clear_widgets()
            self.parent.screens[4].add_widget(Trash())
        except Exception:
            self.parent.parent.screens[4].clear_widgets()
            self.parent.parent.screens[4].add_widget(Trash())

    # pylint: disable=attribute-defined-outside-init
    def refresh_callback(self, *args):
        """Method updates the state of application, While the spinner remains on the screen."""
        def refresh_callback(interval):
            """Method used for loading the inbox screen data."""
            state.searcing_text = ''
            self.children[2].children[1].ids.search_field.text = ''
            self.ids.ml.clear_widgets()
            self.loadMessagelist(state.association)
            self.ids.refresh_layout.refresh_done()
            self.tick = 0

        Clock.schedule_once(refresh_callback, 1)


class MyAddress(Screen):
    """MyAddress Screen uses screen to show widgets of screens."""

    def __init__(self, *args, **kwargs):
        """Clock Schdule for method inbox accounts."""
        super(MyAddress, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method inbox accounts."""
        # pylint: disable=unnecessary-lambda, deprecated-lambda
        addresses_list = state.kivyapp.variable_1
        if state.searcing_text:
            filtered_list = filter(
                lambda addr: self.filter_address(
                    addr), BMConfigParser().addresses())
            addresses_list = filtered_list
        if addresses_list:
            data = []
            for address in addresses_list:
                data.append({
                    'text': BMConfigParser().get(address, 'label'),
                    'secondary_text': address})
            for item in data:
                meny = TwoLineAvatarIconListItem(
                    text=item['text'],
                    secondary_text=item['secondary_text'],
                    theme_text_color='Custom',
                    text_color=NavigateApp().theme_cls.primary_color)
                meny.add_widget(AvatarSampleWidget(
                    source='./images/text_images/{}.png'.format(avatarImageFirstLetter(item['text'].strip()))))
                meny.bind(on_press=partial(
                    self.myadd_detail, item['secondary_text'], item['text']))
                self.ids.ml.add_widget(meny)
        else:
            content = MDLabel(
                font_style='Body1',
                theme_text_color='Primary',
                text="No address found!" if state.searcing_text
                else "yet no address is created by user!!!!!!!!!!!!!",
                halign='center',
                bold=True,
                size_hint_y=None,
                valign='top')
            self.ids.ml.add_widget(content)
            if not state.searcing_text:
                try:
                    self.manager.current = 'login'
                except Exception:
                    pass

    @staticmethod
    def myadd_detail(fromaddress, label, *args):
        """Myaddress Details."""
        p = MyaddDetailPopup()
        p.open()
        p.set_address(fromaddress, label)

    # pylint: disable=attribute-defined-outside-init
    def refresh_callback(self, *args):
        """Method updates the state of application, While the spinner remains on the screen."""
        def refresh_callback(interval):
            """Method used for loading the myaddress screen data."""
            state.searcing_text = ''
            self.children[2].children[1].ids.search_field.text = ''
            self.ids.ml.clear_widgets()
            self.init_ui()
            self.ids.refresh_layout.refresh_done()
            self.tick = 0
        Clock.schedule_once(refresh_callback, 1)

    @staticmethod
    def filter_address(address):
        """Method will filter the my address list data."""
        # pylint: disable=deprecated-lambda
        if filter(lambda x: (state.searcing_text).lower() in x, [
                BMConfigParser().get(
                    address, 'label').lower(), address.lower()]):
            return True
        return False


class AddressBook(Screen):
    """AddressBook Screen uses screen to show widgets of screens."""

    def __init__(self, *args, **kwargs):
        """Getting AddressBook Details."""
        super(AddressBook, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method AddressBook."""
        self.loadAddresslist(None, 'All', '')
        print dt

    def loadAddresslist(self, account, where="", what=""):
        """Clock Schdule for method AddressBook."""
        if state.searcing_text:
            where = ['label', 'address']
            what = state.searcing_text
        xAddress = ''
        queryreturn = kivy_helper_search.search_sql(
            xAddress, account, "addressbook", where, what, False)
        if queryreturn:
            for item in queryreturn:
                meny = TwoLineAvatarIconListItem(
                    text=item[0],
                    secondary_text=item[1],
                    theme_text_color='Custom',
                    text_color=NavigateApp().theme_cls.primary_color)
                meny.add_widget(AvatarSampleWidget(
                    source='./images/text_images/{}.png'.format(avatarImageFirstLetter(item[0].strip()))))
                meny.bind(on_press=partial(
                    self.addBook_detail, item[1], item[0]))
                carousel = Carousel(direction='right')
                carousel.height = meny.height
                carousel.size_hint_y = None
                carousel.ignore_perpendicular_swipes = True
                carousel.data_index = 0
                carousel.min_move = 0.2
                del_btn = Button(text='Delete')
                del_btn.background_normal = ''
                del_btn.background_color = (1, 0, 0, 1)
                del_btn.bind(on_press=partial(self.delete_address, item[1]))
                carousel.add_widget(del_btn)
                carousel.add_widget(meny)
                carousel.index = 1
                self.ids.ml.add_widget(carousel)
        else:
            content = MDLabel(
                font_style='Body1',
                theme_text_color='Primary',
                text="No contact found!" if state.searcing_text
                else "No contact found yet...... ",
                halign='center',
                bold=True,
                size_hint_y=None,
                valign='top')
            self.ids.ml.add_widget(content)

    @staticmethod
    def refreshs(*args):
        """Refresh the Widget."""
        # state.navinstance.ids.sc11.ids.ml.clear_widgets()
        # state.navinstance.ids.sc11.loadAddresslist(None, 'All', '')
        pass

    @staticmethod
    def addBook_detail(address, label, *args):
        """Addressbook Details."""
        p = AddbookDetailPopup()
        p.open()
        p.set_addbook_data(address, label)

    def delete_address(self, address, instance, *args):
        """Delete inbox mail from inbox listing."""
        self.ids.ml.remove_widget(instance.parent.parent)
        sqlExecute(
            "DELETE FROM  addressbook WHERE address = '{}';".format(address))


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    """Adds selection and focus behaviour to the view."""

    pass


class SelectableLabel(RecycleDataViewBehavior, Label):
    """Add selection support to the Label."""

    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        """Catch and handle the view changes."""
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    # pylint: disable=inconsistent-return-statements
    def on_touch_down(self, touch):
        """Add selection on touch down."""
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        """Respond to the selection of items in the view."""
        self.selected = is_selected
        if is_selected:
            print "selection changed to {0}".format(rv.data[index])
            rv.parent.txt_input.text = rv.parent.txt_input.text.replace(
                rv.parent.txt_input.text, rv.data[index]['text'])


class RV(RecycleView):
    """Recycling View."""

    def __init__(self, **kwargs):       # pylint: disable=useless-super-delegation
        """Recycling Method."""
        super(RV, self).__init__(**kwargs)


class DropDownWidget(BoxLayout):
    """Adding Dropdown Widget."""

    txt_input = ObjectProperty()
    rv = ObjectProperty()

    def send(self, navApp):     # pylint: disable=too-many-statements, inconsistent-return-statements
        """Send message from one address to another."""
        # pylint: disable=too-many-locals
        fromAddress = str(self.ids.ti.text)
        toAddress = str(self.ids.txt_input.text)
        subject = self.ids.subject.text.encode('utf-8').strip()
        message = self.ids.body.text.encode('utf-8').strip()
        encoding = 3
        print "message: ", self.ids.body.text
        sendMessageToPeople = True
        if sendMessageToPeople:
            if toAddress != '' and subject and message:
                from addresses import decodeAddress
                status, addressVersionNumber, streamNumber, ripe = \
                    decodeAddress(toAddress)
                if status == 'success':
                    if state.detailPageType == 'draft' and state.send_draft_mail:
                        sqlExecute(
                            "UPDATE sent SET toaddress = ? \
                            , fromaddress = ? , subject = ?\
                            , message = ?, folder = 'sent'\
                            WHERE ackdata = ?;",
                            toAddress,
                            fromAddress,
                            subject,
                            message,
                            str(state.send_draft_mail))
                        self.parent.parent.screens[15].clear_widgets()
                        self.parent.parent.screens[15].add_widget(Draft())
                        state.detailPageType = ''
                        state.send_draft_mail = None
                    else:
                        from addresses import addBMIfNotPresent
                        toAddress = addBMIfNotPresent(toAddress)
                        statusIconColor = 'red'
                        if addressVersionNumber > 4 or addressVersionNumber <= 1:
                            print "addressVersionNumber > 4 \
                            or addressVersionNumber <= 1"
                        if streamNumber > 1 or streamNumber == 0:
                            print "streamNumber > 1 or streamNumber == 0"
                        if statusIconColor == 'red':
                            print "shared.statusIconColor == 'red'"
                        stealthLevel = BMConfigParser().safeGetInt(
                            'bitmessagesettings', 'ackstealthlevel')
                        from helper_ackPayload import genAckPayload
                        ackdata = genAckPayload(streamNumber, stealthLevel)
                        t = ()
                        sqlExecute(
                            '''INSERT INTO sent VALUES
                            (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
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
                            BMConfigParser().getint(
                                'bitmessagesettings', 'ttl'))
                    state.check_sent_acc = fromAddress
                    state.msg_counter_objs = self.parent.parent.parent.parent\
                        .parent.parent.children[0].children[2].children[0].ids
                    self.parent.parent.screens[3].ids.ml.clear_widgets()
                    self.parent.parent.screens[3].loadSent(state.association)
                    self.parent.parent.screens[16].clear_widgets()
                    self.parent.parent.screens[16].add_widget(Allmails())
                    toLabel = ''

                    queues.workerQueue.put(('sendmessage', toAddress))
                    print "sqlExecute successfully #######################"
                    self.parent.parent.current = 'inbox'
                    state.in_composer = True
                    navApp.back_press()
                    toast('send')
                    return None
                else:
                    msg = 'Enter a valid recipients address'
            elif not toAddress:
                msg = 'Please fill the form'
            else:
                msg = 'Please fill the form'
            self.address_error_message(msg)

    # pylint: disable=attribute-defined-outside-init
    def address_error_message(self, msg):
        """Show Error Message."""
        msg_dialog = MDDialog(
            text=msg,
            title='', size_hint=(.8, .25), text_button_ok='Ok',
            events_callback=self.callback_for_menu_items)
        msg_dialog.open()

    @staticmethod
    def callback_for_menu_items(text_item):
        """Method is used for getting the callback of alert box"""
        toast(text_item)

    def reset_composer(self):
        """Method will reset composer."""
        self.ids.ti.text = ''
        self.ids.btn.text = 'Select'
        self.ids.txt_input.text = ''
        self.ids.subject.text = ''
        self.ids.body.text = ''
        toast("Reset message")

    def auto_fill_fromaddr(self):
        """Mehtod used to fill the text automatically From Address."""
        self.ids.ti.text = self.ids.btn.text
        self.ids.ti.focus = True


class MyTextInput(TextInput):
    """Takes the text input in the field."""

    txt_input = ObjectProperty()
    flt_list = ObjectProperty()
    word_list = ListProperty()
    starting_no = NumericProperty(3)
    suggestion_text = ''

    def __init__(self, **kwargs):       # pylint: disable=useless-super-delegation
        """Getting Text Input."""
        super(MyTextInput, self).__init__(**kwargs)

    def on_text(self, instance, value):
        """Find all the occurrence of the word."""
        self.parent.parent.parent.parent.ids.rv.data = []
        matches = [self.word_list[i] for i in range(
            len(self.word_list)) if self.word_list[
                i][:self.starting_no] == value[:self.starting_no]]
        display_data = []
        for i in matches:
            display_data.append({'text': i})
        self.parent.parent.parent.parent.ids.rv.data = display_data
        if len(matches) <= 10:
            self.parent.height = (250 + (len(matches) * 20))
        else:
            self.parent.height = 400

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        """Key Down."""
        if self.suggestion_text and keycode[1] == 'tab':
            self.insert_text(self.suggestion_text + ' ')
            return True
        return super(MyTextInput, self).keyboard_on_key_down(
            window, keycode, text, modifiers)


class Payment(Screen):
    """Payment Method."""

    def get_available_credits(self, instance):      # pylint: disable=no-self-use
        """Method helps to get the available credits"""
        state.availabe_credit = instance.parent.children[1].text
        existing_credits = state.kivyapp.root.ids.sc18.ids.ml.children[0].children[0].children[0].children[0].text
        if len(existing_credits.split(' ')) > 1:
            toast('We already have added free coins for the subscription to your account!')
        else:
            toast('Coins added to your account!')
            state.kivyapp.root.ids.sc18.ids.ml.children[0].children[0].children[
                0].children[0].text = '{0}'.format(state.availabe_credit)


class Credits(Screen):
    """Credits Method"""
    available_credits = StringProperty(
        '{0}'.format('0'))


class Login(Screen):
    """Login Screeen."""

    pass


class NetworkStat(Screen):
    """Method used to show network stat."""

    text_variable_1 = StringProperty(
        '{0}::{1}'.format('Total Connections', '0'))
    text_variable_2 = StringProperty(
        'Processed {0} per-to-per messages'.format('0'))
    text_variable_3 = StringProperty(
        'Processed {0} brodcast messages'.format('0'))
    text_variable_4 = StringProperty('Processed {0} public keys'.format('0'))
    text_variable_5 = StringProperty(
        'Processed {0} object to be synced'.format('0'))

    def __init__(self, *args, **kwargs):
        """Init method for network stat."""
        super(NetworkStat, self).__init__(*args, **kwargs)
        Clock.schedule_interval(self.init_ui, 1)

    def init_ui(self, dt=0):
        """Clock Schdule for method inbox accounts."""
        import network.stats
        import shared
        from network import objectracker
        self.text_variable_1 = '{0} :: {1}'.format(
            'Total Connections', str(len(network.stats.connectedHostsList())))
        self.text_variable_2 = 'Processed {0} per-to-per messages'.format(
            str(shared.numberOfMessagesProcessed))
        self.text_variable_3 = 'Processed {0} brodcast messages'.format(
            str(shared.numberOfBroadcastsProcessed))
        self.text_variable_4 = 'Processed {0} public keys'.format(
            str(shared.numberOfPubkeysProcessed))
        self.text_variable_5 = '{0} object to be synced'.format(
            len(objectracker.missingObjects))


class ContentNavigationDrawer(Navigatorss):
    """Navigate Content Drawer."""

    pass


class Random(Screen):
    """Generates Random Address."""

    is_active = BooleanProperty(False)
    checked = StringProperty("")

    def generateaddress(self, navApp):
        """Method for Address Generator."""
        streamNumberForAddress = 1
        label = self.ids.label.text
        eighteenByteRipe = False
        nonceTrialsPerByte = 1000
        payloadLengthExtraBytes = 1000
        if str(self.ids.label.text).strip():
            queues.addressGeneratorQueue.put((
                'createRandomAddress',
                4, streamNumberForAddress,
                label, 1, "", eighteenByteRipe,
                nonceTrialsPerByte,
                payloadLengthExtraBytes))
            self.ids.label.text = ''
            self.parent.parent.parent.parent.ids.toolbar.opacity = 1
            self.parent.parent.parent.parent.ids.toolbar.disabled = False
            self.parent.parent.parent.parent.ids.sc10.ids.ml.clear_widgets()
            self.manager.current = 'myaddress'
            self.parent.parent.parent.parent.ids.sc10.init_ui()
            self.manager.current = 'myaddress'
            toast('New address created')


class AddressSuccessful(Screen):
    """Getting Address Detail."""

    pass


class Sent(Screen):
    """Sent Screen uses screen to show widgets of screens."""
    def __init__(self, *args, **kwargs):
        """Association with the screen."""
        super(Sent, self).__init__(*args, **kwargs)
        if state.association == '':
            if BMConfigParser().addresses():
                state.association = BMConfigParser().addresses()[0]
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method sent accounts."""
        self.sentaccounts()
        print dt

    def sentaccounts(self):
        """Load sent accounts."""
        account = state.association
        self.loadSent(account, 'All', '')

    def loadSent(self, account, where="", what=""):
        """Load Sent list for Sent messages."""
        if state.searcing_text:
            where = ['subject', 'message']
            what = state.searcing_text
        xAddress = 'fromaddress'
        data = []
        queryreturn = kivy_helper_search.search_sql(
            xAddress, account, "sent", where, what, False)
        if state.msg_counter_objs and state.association == \
                state.check_sent_acc:
            state.msg_counter_objs.send_cnt.badge_text = str(len(queryreturn))
            state.sent_count = str(int(state.sent_count) + 1)
            state.all_count = str(int(state.all_count) + 1)
            state.msg_counter_objs.allmail_cnt.badge_text = state.all_count
            state.check_sent_acc = None

        if queryreturn:
            src_mng_obj = state.kivyapp.root.children[2].children[0].ids
            src_mng_obj.send_cnt.badge_text = str(len(queryreturn))
            state.sent_count = str(len(queryreturn))
            for mail in queryreturn:
                data.append({
                    'text': mail[1].strip(),
                    'secondary_text': mail[2][:50] + '........' if len(
                        mail[2]) >= 50 else (
                            mail[2] + ',' + mail[3].replace('\n', ''))[0:50] + '........',
                    'ackdata': mail[5]})
            for item in data:
                meny = TwoLineAvatarIconListItem(
                    text=item['text'],
                    secondary_text=item['secondary_text'],
                    theme_text_color='Custom',
                    text_color=NavigateApp().theme_cls.primary_color)
                meny.add_widget(AvatarSampleWidget(
                    source='./images/text_images/{}.png'.format(
                        avatarImageFirstLetter(item['secondary_text'].strip()))))
                meny.bind(on_press=partial(
                    self.sent_detail, item['ackdata']))
                carousel = Carousel(direction='right')
                carousel.height = meny.height
                carousel.size_hint_y = None
                carousel.ignore_perpendicular_swipes = True
                carousel.data_index = 0
                carousel.min_move = 0.2
                del_btn = Button(text='Delete')
                del_btn.background_normal = ''
                del_btn.background_color = (1, 0, 0, 1)
                del_btn.bind(on_press=partial(
                    self.delete, item['ackdata']))
                carousel.add_widget(del_btn)
                carousel.add_widget(meny)
                ach_btn = Button(text='Achieve')
                ach_btn.background_color = (0, 1, 0, 1)
                ach_btn.bind(on_press=partial(
                    self.archive, item['ackdata']))
                carousel.add_widget(ach_btn)
                carousel.index = 1
                self.ids.ml.add_widget(carousel)
        else:
            content = MDLabel(
                font_style='Body1',
                theme_text_color='Primary',
                text="No message found!" if state.searcing_text
                else "yet no message for this account!!!!!!!!!!!!!",
                halign='center',
                bold=True,
                size_hint_y=None,
                valign='top')
            self.ids.ml.add_widget(content)

    def sent_detail(self, ackdata, *args):
        """Load sent mail details."""
        state.detailPageType = 'sent'
        state.mail_id = ackdata
        if self.manager:
            src_mng_obj = self.manager
        else:
            src_mng_obj = self.parent.parent
        src_mng_obj.screens[13].clear_widgets()
        src_mng_obj.screens[13].add_widget(MailDetail())
        src_mng_obj.current = 'mailDetail'

    def delete(self, data_index, instance, *args):
        """Delete sent mail from sent mail listing."""
        try:
            msg_count_objs = self.parent.parent.parent.parent.children[
                2].children[0].ids
        except Exception:
            msg_count_objs = self.parent.parent.parent.parent.parent.children[
                2].children[0].ids
        if int(state.sent_count) > 0:
            msg_count_objs.send_cnt.badge_text = str(
                int(state.sent_count) - 1)
            msg_count_objs.trash_cnt.badge_text = str(
                int(state.trash_count) + 1)
            msg_count_objs.allmail_cnt.badge_text = str(
                int(state.all_count) - 1)
            state.sent_count = str(int(state.sent_count) - 1)
            state.trash_count = str(int(state.trash_count) + 1)
            state.all_count = str(int(state.all_count) - 1)
        sqlExecute(
            "UPDATE sent SET folder = 'trash' \
            WHERE ackdata = ?;", str(data_index))
        self.ids.ml.remove_widget(instance.parent.parent)
        toast('Deleted')
        self.update_trash()

    def archive(self, data_index, instance, *args):
        """Archive sent mail from sent mail listing."""
        sqlExecute(
            "UPDATE sent SET folder = 'trash' \
            WHERE ackdata = ?;", str(data_index))
        self.ids.ml.remove_widget(instance.parent.parent)
        self.update_trash()

    def update_trash(self):
        """Update trash screen mails which is deleted from inbox."""
        try:
            self.parent.screens[4].clear_widgets()
            self.parent.screens[4].add_widget(Trash())
            self.parent.screens[16].clear_widgets()
            self.parent.screens[16].add_widget(Allmails())
        except Exception:
            self.parent.parent.screens[4].clear_widgets()
            self.parent.parent.screens[4].add_widget(Trash())
            self.parent.parent.screens[16].clear_widgets()
            self.parent.parent.screens[16].add_widget(Allmails())


class Trash(Screen):
    """Trash Screen uses screen to show widgets of screens."""

    def __init__(self, *args, **kwargs):
        """Trash method, delete sent message and add in Trash."""
        super(Trash, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method inbox accounts."""
        if state.association == '':
            if BMConfigParser().addresses():
                state.association = BMConfigParser().addresses()[0]

        inbox = sqlQuery(
            "SELECT toaddress, fromaddress, subject, message, folder, received from \
            inbox WHERE folder = 'trash' and toaddress = '{}';".format(
                state.association))
        sent = sqlQuery(
            "SELECT toaddress, fromaddress, subject, message, folder, lastactiontime from \
            sent WHERE folder = 'trash' and fromaddress = '{}';".format(
                state.association))
        trash_data = inbox + sent

        if trash_data:
            src_mng_obj = state.kivyapp.root.children[2].children[0].ids
            src_mng_obj.trash_cnt.badge_text = str(len(trash_data))
            state.trash_count = str(len(trash_data))
            for item in trash_data:
                meny = TwoLineAvatarIconListItem(
                    text=item[1],
                    secondary_text=item[2][:50] + '........' if len(
                        item[2]) >= 50 else (
                            item[2] + ',' + item[3].replace('\n', ''))[0:50] + '........',
                    theme_text_color='Custom',
                    text_color=NavigateApp().theme_cls.primary_color)
                img_latter = './images/text_images/{}.png'.format(
                    item[2][0].upper() if (item[2][0].upper() >= 'A' and item[
                        2][0].upper() <= 'Z') else '!')
                meny.add_widget(AvatarSampleWidget(source=img_latter))
                carousel = Carousel(direction='right')
                carousel.height = meny.height
                carousel.size_hint_y = None
                carousel.ignore_perpendicular_swipes = True
                carousel.data_index = 0
                carousel.min_move = 0.2
                del_btn = Button(text='Delete')
                del_btn.background_normal = ''
                del_btn.background_color = (1, 0, 0, 1)
                del_btn.bind(on_press=partial(
                    self.delete_permanently, item[5]))
                carousel.add_widget(del_btn)
                carousel.add_widget(meny)
                carousel.index = 1
                self.ids.ml.add_widget(carousel)
        else:
            content = MDLabel(
                font_style='Body1',
                theme_text_color='Primary',
                text="yet no trashed message for this account!!!!!!!!!!!!!",
                halign='center',
                bold=True,
                size_hint_y=None,
                valign='top')
            self.ids.ml.add_widget(content)

    def delete_permanently(self, data_index, instance, *args):
        """Deleting trash mail permanently."""
        pass


class Page(Screen):
    """Page Screen show widgets of page."""

    pass


class Create(Screen):
    """Creates the screen widgets."""

    def __init__(self, **kwargs):
        """Getting Labels and address from addressbook."""
        super(Create, self).__init__(**kwargs)
        widget_1 = DropDownWidget()
        widget_1.ids.txt_input.word_list = [
            addr[1] for addr in sqlQuery(
                "SELECT label, address from addressbook")]
        widget_1.ids.txt_input.starting_no = 2
        self.add_widget(widget_1)


class Setting(Screen):
    """Setting the Screen components."""

    pass


class NavigateApp(App):     # pylint: disable=too-many-public-methods
    """Navigation Layout of class."""

    theme_cls = ThemeManager()
    previous_date = ObjectProperty()
    obj_1 = ObjectProperty()
    variable_1 = ListProperty(BMConfigParser().addresses())
    nav_drawer = ObjectProperty()
    state.screen_density = Window.size
    window_size = state.screen_density
    title = "PyBitmessage"
    imgstatus = False
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
        """Method builds the widget."""
        main_widget = Builder.load_file(
            os.path.join(os.path.dirname(__file__), 'main.kv'))
        self.nav_drawer = Navigatorss()
        self.obj_1 = AddressBook()
        kivysignalthread = UIkivySignaler()
        kivysignalthread.daemon = True
        kivysignalthread.start()
        Window.bind(on_keyboard=self.on_key)
        return main_widget

    def run(self):
        """Running the widgets."""
        kivyuisignaler.release()
        super(NavigateApp, self).run()

    # pylint: disable=inconsistent-return-statements
    @staticmethod
    def showmeaddresses(name="text"):
        """Show the addresses in spinner to make as dropdown."""
        if name == "text":
            if BMConfigParser().addresses():
                return BMConfigParser().addresses()[0][:16] + '..'
            return "textdemo"
        elif name == "values":
            if BMConfigParser().addresses():
                return [address[:16] + '..'
                        for address in BMConfigParser().addresses()]
            return "valuesdemo"

    def getCurrentAccountData(self, text):
        """Get Current Address Account Data."""
        self.set_identicon(text)
        address_label = self.current_address_label(
            BMConfigParser().get(text, 'label'), text)
        self.root_window.children[1].ids.toolbar.title = address_label
        state.association = text
        state.searcing_text = ''
        self.root.ids.sc1.ids.ml.clear_widgets()
        self.root.ids.sc1.loadMessagelist(state.association)
        self.root.ids.scr_mngr.current = 'inbox'

        msg_counter_objs = \
            self.root_window.children[1].children[2].children[0].ids
        state.sent_count = str(
            sqlQuery(
                "SELECT COUNT(*) FROM sent WHERE fromaddress = '{}' and \
                folder = 'sent' ;".format(state.association))[0][0])
        state.inbox_count = str(
            sqlQuery(
                "SELECT COUNT(*) FROM inbox WHERE toaddress = '{}' and \
                folder = 'inbox' ;".format(state.association))[0][0])
        state.trash_count = str(sqlQuery("SELECT (SELECT count(*) FROM  sent \
            where fromaddress = '{0}' and  folder = 'trash' ) \
            +(SELECT count(*) FROM inbox where toaddress = '{0}' and  \
            folder = 'trash') AS SumCount".format(state.association))[0][0])
        state.draft_count = str(
            sqlQuery(
                "SELECT COUNT(*) FROM sent WHERE fromaddress = '{}' and \
                folder = 'draft' ;".format(state.association))[0][0])
        state.all_count = str(int(state.sent_count) + int(state.inbox_count))

        if msg_counter_objs:
            msg_counter_objs.send_cnt.badge_text = state.sent_count
            msg_counter_objs.inbox_cnt.badge_text = state.inbox_count
            msg_counter_objs.trash_cnt.badge_text = state.trash_count
            msg_counter_objs.draft_cnt.badge_text = state.draft_count
            msg_counter_objs.allmail_cnt.badge_text = state.all_count

    @staticmethod
    def getCurrentAccount():
        """It uses to get current account label."""
        if state.association:
            return state.association
        return "Bitmessage Login"

    @staticmethod
    def addingtoaddressbook():
        """Adding to address Book."""
        p = GrashofPopup()
        p.open()

    def getDefaultAccData(self):
        """Getting Default Account Data."""
        if BMConfigParser().addresses():
            img = identiconGeneration.generate(BMConfigParser().addresses()[0])
            self.createFolder('./images/default_identicon/')
            if platform == 'android':
                # android_path = os.path.expanduser("~/user/0/org.test.bitapp/files/app/")
                android_path = os.path.join(os.environ['ANDROID_PRIVATE'] + '/app/')
                img.texture.save('{1}/images/default_identicon/{0}.png'.format(
                    BMConfigParser().addresses()[0], android_path))
            else:
                img.texture.save('./images/default_identicon/{}.png'.format(BMConfigParser().addresses()[0]))
            return BMConfigParser().addresses()[0]
        return 'Select Address'

    @staticmethod
    def createFolder(directory):
        """This method is used to create the directory when app starts"""
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            print 'Error: Creating directory. ' + directory

    @staticmethod
    def get_default_image():
        """Getting default image on address"""
        if BMConfigParser().addresses():
            return './images/default_identicon/{}.png'.format(BMConfigParser().addresses()[0])
        return './images/no_identicons.png'

    @staticmethod
    def addressexist():
        """Checking address existence."""
        if BMConfigParser().addresses():
            return True
        return False

    def on_key(self, window, key, *args):
        """Method is used for going on previous screen."""
        if key == 27:
            if self.root.ids.scr_mngr.current == "mailDetail":
                self.root.ids.scr_mngr.current = 'sent'\
                    if state.detailPageType == 'sent' else 'inbox' \
                    if state.detailPageType == 'inbox' else 'draft'
                self.back_press()
            elif self.root.ids.scr_mngr.current == "create":
                composer_objs = self.root
                from_addr = str(self.root.ids.sc3.children[0].ids.ti.text)
                to_addr = str(self.root.ids.sc3.children[0].ids.txt_input.text)
                if from_addr and to_addr and state.detailPageType != 'draft':
                    Draft().draft_msg(composer_objs)
                self.root.ids.scr_mngr.current = 'inbox'
                self.back_press()
            elif self.root.ids.scr_mngr.current == "showqrcode":
                self.root.ids.scr_mngr.current = 'myaddress'
            elif self.root.ids.scr_mngr.current == "random":
                self.root.ids.scr_mngr.current = 'login'
            else:
                self.root.ids.scr_mngr.current = 'inbox'
            self.root.ids.scr_mngr.transition.direction = 'right'
            self.root.ids.scr_mngr.transition.bind(on_complete=self.reset)
            return True

    def reset(self, *args):
        """Method used to set transition direction."""
        self.root.ids.scr_mngr.transition.direction = 'left'
        self.root.ids.scr_mngr.transition.unbind(on_complete=self.reset)

    @staticmethod
    def status_dispatching(data):
        """Method used for status dispatching acknowledgment."""
        ackData, message = data
        if state.ackdata == ackData:
            state.status.status = message

    def clear_composer(self):
        """If slow down the nwe will make new composer edit screen."""
        self.set_navbar_for_composer()
        # self.root.ids.search_bar.clear_widgets()
        composer_obj = self.root.ids.sc3.children[0].ids
        composer_obj.ti.text = ''
        composer_obj.btn.text = 'Select'
        composer_obj.txt_input.text = ''
        composer_obj.subject.text = ''
        composer_obj.body.text = ''
        state.in_composer = True

    def set_navbar_for_composer(self):
        """This method is used for clearing toolbar data when composer open"""
        self.root.ids.toolbar.left_action_items = [
            ['arrow-left', lambda x: self.back_press()]]
        self.root.ids.toolbar.right_action_items = [
            ['refresh', lambda x: self.root.ids.sc3.children[0].reset_composer()],
            ['send', lambda x: self.root.ids.sc3.children[0].send(self)]]

    def back_press(self):
        """Method used for going back from composer to previous page."""
        self.root.ids.toolbar.right_action_items = \
            [['account-plus', lambda x: self.addingtoaddressbook()]]
        self.root.ids.toolbar.left_action_items = \
            [['menu', lambda x: self.root.toggle_nav_drawer()]]
        self.root.ids.scr_mngr.current = 'inbox' \
            if state.in_composer else 'allmails'\
            if state.is_allmail else state.detailPageType\
            if state.detailPageType else 'inbox'
        self.root.ids.scr_mngr.transition.direction = 'right'
        self.root.ids.scr_mngr.transition.bind(on_complete=self.reset)
        if state.is_allmail or state.detailPageType == 'draft':
            state.is_allmail = False
        state.detailPageType = ''
        state.in_composer = False

    @staticmethod
    def on_stop():
        """On stop methos is used for stoping the runing script."""
        print "*******************EXITING FROM APPLICATION*******************"
        import shutdown
        shutdown.doCleanShutdown()

    @staticmethod
    def current_address_label(current_add_label=None, current_addr=None):
        """Getting current address labels."""
        if BMConfigParser().addresses():
            if current_add_label:
                first_name = current_add_label
                addr = current_addr
            else:
                addr = BMConfigParser().addresses()[0]
                first_name = BMConfigParser().get(addr, 'label')
            f_name = first_name.split()
            label = f_name[0][:14].capitalize() + '...' if len(f_name[0]) > 15 else f_name[0].capitalize()
            address = ' (' + addr + '...)'
            return label + address
        return ''

    def searchQuery(self, instance):
        """Method used for showing searched mails."""
        state.search_screen = self.root.ids.scr_mngr.current
        state.searcing_text = str(instance.text).strip()
        if state.search_screen == 'inbox':
            self.root.ids.sc1.ids.ml.clear_widgets()
            self.root.ids.sc1.loadMessagelist(state.association)
        elif state.search_screen == 'addressbook':
            self.root.ids.sc11.ids.ml.clear_widgets()
            self.root.ids.sc11.loadAddresslist(None, 'All', '')
        elif state.search_screen == 'myaddress':
            self.root.ids.sc10.ids.ml.clear_widgets()
            self.root.ids.sc10.init_ui()
        else:
            self.root.ids.sc4.ids.ml.clear_widgets()
            self.root.ids.sc4.loadSent(state.association)
        self.root.ids.scr_mngr.current = state.search_screen

    def refreshScreen(self, instance):
        """Method show search button only on inbox or sent screen."""
        state.searcing_text = ''
        if instance.text == 'Sent':
            self.root.ids.sc4.ids.ml.clear_widgets()
            self.root.ids.sc4.children[1].children[1].ids.search_field.text = ''
            self.root.ids.sc4.loadSent(state.association)
        elif instance.text == 'Inbox':
            self.root.ids.sc1.ids.ml.clear_widgets()
            try:
                self.root.ids.sc1.children[2].children[1].ids.search_field.text = ''
            except Exception as e:
                self.root.ids.sc1.children[1].children[1].ids.search_field.text = ''
            self.root.ids.sc1.loadMessagelist(state.association)
        elif instance.text == 'Draft':
            self.root.ids.sc16.clear_widgets()
            self.root.ids.sc16.add_widget(Draft())
        elif instance.text == 'Trash':
            self.root.ids.sc5.clear_widgets()
            self.root.ids.sc5.add_widget(Trash())
        elif instance.text == 'All Mails':
            self.root.ids.sc17.clear_widgets()
            self.root.ids.sc17.add_widget(Allmails())
        elif instance.text == 'Address Book':
            self.root.ids.sc11.ids.ml.clear_widgets()
            self.root.ids.sc11.children[1].children[1].ids.search_field.text = ''
            self.root.ids.sc11.loadAddresslist(None, 'All', '')
        elif instance.text == 'My Addresses':
            self.root.ids.sc10.ids.ml.clear_widgets()
            try:
                self.root.ids.sc10.children[1].children[1].ids.search_field.text = ''
            except Exception as e:
                self.root.ids.sc10.children[2].children[1].ids.search_field.text = ''
            self.root.ids.sc10.init_ui()
        return

    def set_identicon(self, text):
        """This method is use for showing identicon in address spinner"""
        img = identiconGeneration.generate(text)
        self.root.children[2].children[0].ids.btn.children[1].texture = img.texture

    @staticmethod
    def address_identicon():
        """Address identicon"""
        return './images/drawer_logo1.png'

    def set_mail_detail_header(self):
        """Method is used for setting the details of the page"""
        toolbar_obj = self.root.ids.toolbar
        toolbar_obj.left_action_items = [['arrow-left', lambda x: self.back_press()]]
        delete_btn = ['delete-forever', lambda x: self.root.ids.sc14.delete_mail()]
        dynamic_list = []
        if state.detailPageType == 'inbox':
            dynamic_list = [['reply', lambda x: self.root.ids.sc14.inbox_reply()], delete_btn]
        elif state.detailPageType == 'sent':
            dynamic_list = [delete_btn]
        elif state.detailPageType == 'draft':
            dynamic_list = [['pencil', lambda x: self.root.ids.sc14.write_msg(self)], delete_btn]
        toolbar_obj.right_action_items = dynamic_list


class GrashofPopup(Popup):
    """Methods for saving contacts, error messages."""

    def __init__(self, **kwargs):    # pylint: disable=useless-super-delegation
        """Grash of pop screen settings."""
        super(GrashofPopup, self).__init__(**kwargs)

    def savecontact(self):
        """Method is used for Saving Contacts."""
        label = self.ids.label.text.strip()
        address = self.ids.address.text.strip()
        if label == '' and address == '':
            self.ids.label.focus = True
            self.ids.address.focus = True
        elif address == '':
            self.ids.address.focus = True
        elif label == '':
            self.ids.label.focus = True

        stored_address = [addr[1] for addr in kivy_helper_search.search_sql(
            folder="addressbook")]
        if label and address and address not in stored_address:
            # state.navinstance = self.parent.children[1]
            queues.UISignalQueue.put(('rerenderAddressBook', ''))
            self.dismiss()
            sqlExecute("INSERT INTO addressbook VALUES(?,?)", label, address)
            state.kivyapp.root.ids.sc11.ids.ml.clear_widgets()
            state.kivyapp.root.ids.sc11.loadAddresslist(None, 'All', '')
            self.parent.children[1].ids.scr_mngr.current = 'addressbook'
            toast('Saved')

    # pylint: disable=attribute-defined-outside-init
    def show_error_message(self):
        """Showing error message."""
        content = MDLabel(
            font_style='Body1',
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

    @staticmethod
    def close_pop():
        """Pop is Canceled."""
        toast('Canceled')

    def checkAddress_valid(self, instance):
        """Checking is address is valid or not"""
        my_addresses = self.parent.children[1].children[2].children[0].ids.btn.values
        add_book = [addr[1] for addr in kivy_helper_search.search_sql(
            folder="addressbook")]
        entered_text = str(instance.text).strip()
        if entered_text in add_book:
            text = 'Address is already in the addressbook.'
        elif entered_text in my_addresses:
            text = 'You can not save your own address.'

        if entered_text in my_addresses or entered_text in add_book:
            if len(self.ids.popup_box.children) <= 2:
                err_msg = MDLabel(
                    id='erro_msg',
                    font_style='Body2',
                    text=text,
                    font_size=5)
                err_msg.color = 1, 0, 0, 1
                self.ids.popup_box.add_widget(err_msg)
                self.ids.save_addr.disabled = True
        elif len(self.ids.popup_box.children) > 2:
            self.ids.popup_box.remove_widget(self.ids.popup_box.children[0])
            self.ids.save_addr.disabled = False


class AvatarSampleWidget(ILeftBody, Image):
    """Avatar Sample Widget."""

    pass


class IconLeftSampleWidget(ILeftBodyTouch, MDIconButton):
    """Left icon sample widget."""

    pass


class IconRightSampleWidget(IRightBodyTouch, MDCheckbox):
    """Right icon sample widget."""

    pass


class NavigationDrawerTwoLineListItem(
        TwoLineListItem, NavigationDrawerHeaderBase):
    """Navigation Drawer in Listitems."""

    address_property = StringProperty()

    def __init__(self, **kwargs):
        """Method for Navigation Drawer."""
        super(NavigationDrawerTwoLineListItem, self).__init__(**kwargs)
        Clock.schedule_once(lambda dt: self.setup())

    def setup(self):
        """Bind Controller.current_account property."""
        pass

    def on_current_account(self, account):
        """Account detail."""
        pass

    def _update_specific_text_color(self, instance, value):
        pass

    def _set_active(self, active, list_):
        pass


class MailDetail(Screen):
    """MailDetail Screen uses to show the detail of mails."""

    to_addr = StringProperty()
    from_addr = StringProperty()
    subject = StringProperty()
    message = StringProperty()
    status = StringProperty()
    page_type = StringProperty()

    def __init__(self, *args, **kwargs):
        """Mail Details method."""
        super(MailDetail, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method MailDetail mails."""
        self.page_type = state.detailPageType if state.detailPageType else ''
        if state.detailPageType == 'sent' or state.detailPageType == 'draft':
            data = sqlQuery(
                "select toaddress, fromaddress, subject, message, status, \
                ackdata from sent where ackdata = ?;", state.mail_id)
            state.status = self
            state.ackdata = data[0][5]
            self.assign_mail_details(data)
            state.kivyapp.set_mail_detail_header()
        elif state.detailPageType == 'inbox':
            data = sqlQuery(
                "select toaddress, fromaddress, subject, message from inbox \
                where msgid = ?;", str(state.mail_id))
            self.assign_mail_details(data)
            state.kivyapp.set_mail_detail_header()

    def assign_mail_details(self, data):
        """Assigning mail details."""
        self.to_addr = data[0][0]
        self.from_addr = data[0][1]
        self.subject = data[0][2].upper(
        ) if data[0][2].upper() else '(no subject)'
        self.message = data[0][3]
        if len(data[0]) == 6:
            self.status = data[0][4]
        state.write_msg = {'to_addr': self.to_addr,
                           'from_addr': self.from_addr,
                           'subject': self.subject,
                           'message': self.message}

    def delete_mail(self):
        """Method for mail delete."""
        msg_count_objs = state.kivyapp.root.children[2].children[0].ids
        if state.detailPageType == 'sent':
            sqlExecute(
                "UPDATE sent SET folder = 'trash' WHERE \
                ackdata = ?;", str(state.mail_id))
            msg_count_objs.send_cnt.badge_text = str(int(state.sent_count) - 1)
            state.sent_count = str(int(state.sent_count) - 1)
            self.parent.screens[3].ids.ml.clear_widgets()
            self.parent.screens[3].loadSent(state.association)
        elif state.detailPageType == 'inbox':
            sqlExecute(
                "UPDATE inbox SET folder = 'trash' WHERE \
                msgid = ?;", str(state.mail_id))
            msg_count_objs.inbox_cnt.badge_text = str(int(state.inbox_count) - 1)
            state.inbox_count = str(int(state.inbox_count) - 1)
            self.parent.screens[0].ids.ml.clear_widgets()
            self.parent.screens[0].loadMessagelist(state.association)
        elif state.detailPageType == 'draft':
            sqlExecute("DELETE FROM sent WHERE ackdata = ?;", str(
                state.mail_id))
            msg_count_objs.draft_cnt.badge_text = str(int(state.draft_count) - 1)
            state.draft_count = str(int(state.draft_count) - 1)
            self.parent.screens[15].clear_widgets()
            self.parent.screens[15].add_widget(Draft())

        self.parent.current = 'allmails' if state.is_allmail else state.detailPageType
        if state.detailPageType != 'draft':
            msg_count_objs.trash_cnt.badge_text = str(int(state.trash_count) + 1)
            msg_count_objs.allmail_cnt.badge_text = str(int(state.all_count) - 1)
            state.trash_count = str(int(state.trash_count) + 1)
            state.all_count = str(int(state.all_count) - 1)
            self.parent.screens[4].clear_widgets()
            self.parent.screens[4].add_widget(Trash())
            self.parent.screens[16].clear_widgets()
            self.parent.screens[16].add_widget(Allmails())
        state.kivyapp.back_press()
        toast('Deleted')

    def inbox_reply(self):
        """Method used for replying inbox messages."""
        data = sqlQuery(
            "select toaddress, fromaddress, subject, message from inbox where \
            msgid = ?;", str(state.mail_id))
        composer_obj = self.parent.screens[2].children[0].ids
        composer_obj.ti.text = data[0][0]
        composer_obj.btn.text = data[0][0]
        composer_obj.txt_input.text = data[0][1]
        composer_obj.subject.text = data[0][2]
        composer_obj.body.text = ''
        state.kivyapp.root.ids.sc3.children[0].ids.rv.data = ''
        self.parent.current = 'create'
        state.kivyapp.set_navbar_for_composer()

    def copy_sent_mail(self):
        """Method used for copying sent mail to the composer."""
        pass

    def write_msg(self, navApp):
        """Method used to write on draft mail."""
        state.send_draft_mail = state.mail_id
        composer_ids = \
            self.parent.parent.parent.parent.ids.sc3.children[0].ids
        composer_ids.ti.text = state.write_msg['from_addr']
        composer_ids.btn.text = state.write_msg['from_addr']
        composer_ids.txt_input.text = state.write_msg['to_addr']
        composer_ids.subject.text = state.write_msg['subject']
        composer_ids.body.text = state.write_msg['message']
        self.parent.current = 'create'
        navApp.set_navbar_for_composer()

    @staticmethod
    def copy_composer_text(instance, *args):
        """This method is used for copying the data from mail detail page"""
        if len(instance.parent.text.split(':')) > 1:
            cpy_text = instance.parent.text.split(':')[1].strip()
        else:
            cpy_text = instance.parent.text
        Clipboard.copy(cpy_text)
        toast('Copied')


class MyaddDetailPopup(Popup):
    """MyaddDetailPopup pop is used for showing my address detail."""

    address_label = StringProperty()
    address = StringProperty()

    def __init__(self, **kwargs):    # pylint: disable=useless-super-delegation
        """My Address Details screen setting."""
        super(MyaddDetailPopup, self).__init__(**kwargs)

    def set_address(self, address, label):
        """Getting address for displaying details on popup."""
        self.address_label = label
        self.address = address

    def send_message_from(self):
        """Method used to fill from address of composer autofield."""
        window_obj = self.parent.children[1].ids
        window_obj.sc3.children[0].ids.ti.text = self.address
        window_obj.sc3.children[0].ids.btn.text = self.address
        window_obj.sc3.children[0].ids.txt_input.text = ''
        window_obj.sc3.children[0].ids.subject.text = ''
        window_obj.sc3.children[0].ids.body.text = ''
        window_obj.scr_mngr.current = 'create'
        self.dismiss()

    @staticmethod
    def close_pop():
        """Pop is Canceled."""
        toast('Canceled')


class AddbookDetailPopup(Popup):
    """AddbookDetailPopup pop is used for showing my address detail."""

    address_label = StringProperty()
    address = StringProperty()

    def __init__(self, **kwargs):    # pylint: disable=useless-super-delegation
        """Method used set screen of address detail page."""
        super(AddbookDetailPopup, self).__init__(**kwargs)

    def set_addbook_data(self, address, label):
        """Getting address book data for detial dipaly."""
        self.address_label = label
        self.address = address

    def update_addbook_label(self, address):
        """Updating the label of address book address."""
        if str(self.ids.add_label.text):
            sqlExecute("UPDATE addressbook SET label = '{}' WHERE \
                address = '{}';".format(str(self.ids.add_label.text), address))
            self.parent.children[1].ids.sc11.ids.ml.clear_widgets()
            self.parent.children[1].ids.sc11.loadAddresslist(None, 'All', '')
            self.dismiss()
            toast('Saved')

    def send_message_to(self):
        """Method used to fill to_address of composer autofield."""
        window_obj = self.parent.children[1].ids
        window_obj.sc3.children[0].ids.txt_input.text = self.address
        window_obj.sc3.children[0].ids.ti.text = ''
        window_obj.sc3.children[0].ids.btn.text = 'Select'
        window_obj.sc3.children[0].ids.subject.text = ''
        window_obj.sc3.children[0].ids.body.text = ''
        window_obj.scr_mngr.current = 'create'
        self.dismiss()

    @staticmethod
    def close_pop():
        """Pop is Canceled."""
        toast('Canceled')


class ShowQRCode(Screen):
    """ShowQRCode Screen uses to show the detail of mails."""

    def qrdisplay(self):
        """Method used for showing QR Code."""
        # self.manager.parent.parent.parent.ids.search_bar.clear_widgets()
        self.ids.qr.clear_widgets()
        from kivy.garden.qrcode import QRCodeWidget
        self.ids.qr.add_widget(QRCodeWidget(
            data=self.manager.get_parent_window().children[0].address))
        toast('Show QR code')


class Draft(Screen):
    """Draft screen is used to show the list of draft messages."""

    data = ListProperty()

    def __init__(self, *args, **kwargs):
        """Method used for storing draft messages."""
        super(Draft, self).__init__(*args, **kwargs)
        if state.association == '':
            if BMConfigParser().addresses():
                state.association = BMConfigParser().addresses()[0]
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method draft accounts."""
        self.sentaccounts()
        print dt

    def sentaccounts(self):
        """Load draft accounts."""
        account = state.association
        self.loadDraft(account, 'All', '')

    def loadDraft(self, account, where="", what=""):
        """Load draft list for Draft messages."""
        xAddress = 'fromaddress'
        queryreturn = kivy_helper_search.search_sql(
            xAddress, account, "draft", where, what, False)
        if state.msg_counter_objs:
            state.msg_counter_objs.draft_cnt.badge_text = str(len(queryreturn))
        if queryreturn:
            src_mng_obj = state.kivyapp.root.children[2].children[0].ids
            src_mng_obj.draft_cnt.badge_text = str(len(queryreturn))
            state.draft_count = str(len(queryreturn))
            for mail in queryreturn:
                third_text = mail[3].replace('\n', ' ')
                self.data.append({
                    'text': mail[1].strip(),
                    'secondary_text': mail[2][:10] + '...........' if len(
                        mail[2]) > 10 else mail[2] + '\n' + " " + (
                            third_text[:25] + '...!') if len(
                                third_text) > 25 else third_text,
                    'ackdata': mail[5]})
            for item in self.data:
                meny = TwoLineAvatarIconListItem(
                    text='Draft',
                    secondary_text=item['text'],
                    theme_text_color='Custom',
                    text_color=NavigateApp().theme_cls.primary_color)
                meny.add_widget(AvatarSampleWidget(
                    source='./images/avatar.png'))
                meny.bind(on_press=partial(
                    self.draft_detail, item['ackdata']))
                carousel = Carousel(direction='right')
                carousel.height = meny.height
                carousel.size_hint_y = None
                carousel.ignore_perpendicular_swipes = True
                carousel.data_index = 0
                carousel.min_move = 0.2
                del_btn = Button(text='Delete')
                del_btn.background_normal = ''
                del_btn.background_color = (1, 0, 0, 1)
                del_btn.bind(on_press=partial(
                    self.delete_draft, item['ackdata']))
                carousel.add_widget(del_btn)
                carousel.add_widget(meny)
                carousel.index = 1
                self.ids.ml.add_widget(carousel)
        else:
            content = MDLabel(
                font_style='Body1',
                theme_text_color='Primary',
                text="yet no message for this account!!!!!!!!!!!!!",
                halign='center',
                bold=True,
                size_hint_y=None,
                valign='top')
            self.ids.ml.add_widget(content)

    def draft_detail(self, ackdata, *args):
        """Method used to show draft Details."""
        state.detailPageType = 'draft'
        state.mail_id = ackdata
        if self.manager:
            src_mng_obj = self.manager
        else:
            src_mng_obj = self.parent.parent
        src_mng_obj.screens[13].clear_widgets()
        src_mng_obj.screens[13].add_widget(MailDetail())
        src_mng_obj.current = 'mailDetail'

    def delete_draft(self, data_index, instance, *args):
        """Method used to delete draft message permanently."""
        sqlExecute("DELETE FROM sent WHERE ackdata = ?;", str(
            data_index))
        try:
            msg_count_objs = \
                self.parent.parent.parent.parent.children[2].children[0].ids
        except Exception:
            msg_count_objs = self.parent.parent.parent.parent.parent.children[
                2].children[0].ids
        if int(state.draft_count) > 0:
            msg_count_objs.draft_cnt.badge_text = str(
                int(state.draft_count) - 1)
            state.draft_count = str(int(state.draft_count) - 1)
        self.ids.ml.remove_widget(instance.parent.parent)
        toast('Deleted')

    @staticmethod
    def draft_msg(src_object):
        """Method used for saving draft mails."""
        # pylint: disable=too-many-locals
        composer_object = src_object.children[1].children[0].children[
            0].children[0].children[0].ids
        fromAddress = str(composer_object.ti.text)
        toAddress = str(composer_object.txt_input.text)
        subject = str(composer_object.subject.text)
        message = str(composer_object.body.text)
        encoding = 3
        sendMessageToPeople = True
        if sendMessageToPeople:
            from addresses import decodeAddress
            status, addressVersionNumber, streamNumber, ripe = \
                decodeAddress(toAddress)
            from addresses import addBMIfNotPresent
            toAddress = addBMIfNotPresent(toAddress)
            statusIconColor = 'red'
            stealthLevel = BMConfigParser().safeGetInt(
                'bitmessagesettings', 'ackstealthlevel')
            from helper_ackPayload import genAckPayload
            ackdata = genAckPayload(streamNumber, stealthLevel)
            t = ()
            sqlExecute(
                '''INSERT INTO sent VALUES
                (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
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
                'draft',
                encoding,
                BMConfigParser().getint('bitmessagesettings', 'ttl'))

            state.msg_counter_objs = src_object.children[2].children[0].ids
            state.draft_count = str(int(state.draft_count) + 1)
            src_object.ids.sc16.clear_widgets()
            src_object.ids.sc16.add_widget(Draft())
            toast('Save draft')
        return


class CustomSpinner(Spinner):
    """This class is used for setting spinner size."""

    def __init__(self, *args, **kwargs):
        """Method used for setting size of spinner."""
        super(CustomSpinner, self).__init__(*args, **kwargs)
        self.dropdown_cls.max_height = Window.size[1] / 3


class Allmails(Screen):
    """all mails Screen uses screen to show widgets of screens."""

    data = ListProperty()

    def __init__(self, *args, **kwargs):
        """Method Parsing the address."""
        super(Allmails, self).__init__(*args, **kwargs)
        if state.association == '':
            if BMConfigParser().addresses():
                state.association = BMConfigParser().addresses()[0]
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method all mails."""
        self.mailaccounts()
        print dt

    def mailaccounts(self):
        """Load all mails for account."""
        account = state.association
        self.loadMessagelist(account, 'All', '')

    def loadMessagelist(self, account, where="", what=""):
        """Load Inbox, Sent anf Draft list of messages."""
        all_mails = sqlQuery(
            "SELECT toaddress, fromaddress, subject, message, folder, ackdata As id, DATE(lastactiontime)"
            " As actionTime FROM sent WHERE folder = 'sent' UNION"
            " SELECT toaddress, fromaddress, subject, message, folder, msgid As id, DATE(received) As"
            " actionTime FROM inbox WHERE folder = 'inbox' ORDER BY actionTime DESC")
        if all_mails:
            state.kivyapp.root.children[2].children[0].ids.allmail_cnt.badge_text = str(len(all_mails))
            state.all_count = str(len(all_mails))
            for item in all_mails:
                meny = TwoLineAvatarIconListItem(
                    text=item[1],
                    secondary_text=item[2][:50] + '........' if len(
                        item[2]) >= 50 else (
                            item[2] + ',' + item[3].replace('\n', ''))[0:50] + '........',
                    theme_text_color='Custom',
                    text_color=NavigateApp().theme_cls.primary_color)
                meny.add_widget(AvatarSampleWidget(
                    source='./images/text_images/{}.png'.format(
                        avatarImageFirstLetter(item[2].strip()))))
                meny.bind(on_press=partial(
                    self.mail_detail, item[5], item[4]))
                carousel = Carousel(direction='right')
                carousel.height = meny.height
                carousel.size_hint_y = None
                carousel.ignore_perpendicular_swipes = True
                carousel.data_index = 0
                carousel.min_move = 0.2
                del_btn = Button(text='Delete')
                del_btn.background_normal = ''
                del_btn.background_color = (1, 0, 0, 1)
                del_btn.bind(on_press=partial(
                    self.swipe_delete, item[5], item[4]))
                carousel.add_widget(del_btn)
                carousel.add_widget(meny)
                carousel.index = 1
                self.ids.ml.add_widget(carousel)
        else:
            content = MDLabel(
                font_style='Body1',
                theme_text_color='Primary',
                text="yet no message for this account!!!!!!!!!!!!!",
                halign='center',
                bold=True,
                size_hint_y=None,
                valign='top')
            self.ids.ml.add_widget(content)

    def mail_detail(self, unique_id, folder, *args):
        """Load sent and inbox mail details."""
        state.detailPageType = folder
        state.is_allmail = True
        state.mail_id = unique_id
        if self.manager:
            src_mng_obj = self.manager
        else:
            src_mng_obj = self.parent.parent
        src_mng_obj.screens[13].clear_widgets()
        src_mng_obj.screens[13].add_widget(MailDetail())
        src_mng_obj.current = 'mailDetail'

    def swipe_delete(self, unique_id, folder, instance, *args):
        """Delete inbox mail from all mail listing listing."""
        if folder == 'inbox':
            sqlExecute(
                "UPDATE inbox SET folder = 'trash' WHERE msgid = ?;", str(
                    unique_id))
        else:
            sqlExecute(
                "UPDATE sent SET folder = 'trash' WHERE ackdata = ?;", str(
                    unique_id))
        self.ids.ml.remove_widget(instance.parent.parent)
        try:
            msg_count_objs = self.parent.parent.parent.parent.children[
                2].children[0].ids
            nav_lay_obj = self.parent.parent.parent.parent.ids
        except Exception:
            msg_count_objs = self.parent.parent.parent.parent.parent.children[
                2].children[0].ids
            nav_lay_obj = self.parent.parent.parent.parent.parent.ids
        if folder == 'inbox':
            msg_count_objs.inbox_cnt.badge_text = str(
                int(state.inbox_count) - 1)
            state.inbox_count = str(int(state.inbox_count) - 1)
            nav_lay_obj.sc1.ids.ml.clear_widgets()
            nav_lay_obj.sc1.loadMessagelist(state.association)
        else:
            msg_count_objs.send_cnt.badge_text = str(
                int(state.sent_count) - 1)
            state.sent_count = str(int(state.sent_count) - 1)
            nav_lay_obj.sc4.ids.ml.clear_widgets()
            nav_lay_obj.sc4.loadSent(state.association)
        msg_count_objs.trash_cnt.badge_text = str(
            int(state.trash_count) + 1)
        msg_count_objs.allmail_cnt.badge_text = str(
            int(state.all_count) - 1)
        state.trash_count = str(int(state.trash_count) + 1)
        state.all_count = str(int(state.all_count) - 1)
        nav_lay_obj.sc5.clear_widgets()
        nav_lay_obj.sc5.add_widget(Trash())
        nav_lay_obj.sc17.clear_widgets()
        nav_lay_obj.sc17.add_widget(Allmails())

    # pylint: disable=attribute-defined-outside-init
    def refresh_callback(self, *args):
        """Method updates the state of application, While the spinner remains on the screen."""
        def refresh_callback(interval):
            """Method used for loading the allmails screen data."""
            self.ids.ml.clear_widgets()
            self.remove_widget(self.children[1])
            try:
                screens_obj = self.parent.screens[16]
            except Exception:
                screens_obj = self.parent.parent.screens[16]
            screens_obj.add_widget(Allmails())
            self.ids.refresh_layout.refresh_done()
            self.tick = 0
        Clock.schedule_once(refresh_callback, 1)


def avatarImageFirstLetter(letter_string):
    """This method is used to the first letter for the avatar image"""
    if letter_string[0].upper() >= 'A' and letter_string[0].upper() <= 'Z':
        img_latter = letter_string[0].upper()
    elif int(letter_string[0]) >= 0 and int(letter_string[0]) <= 9:
        img_latter = letter_string[0]
    else:
        img_latter = '!'

    return img_latter


class Starred(Screen):
    """Starred Screen show widgets of page."""

    pass


class Archieve(Screen):
    """Archieve Screen show widgets of page."""

    pass


class Spam(Screen):
    """Spam Screen show widgets of page."""

    pass
