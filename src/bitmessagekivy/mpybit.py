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


userAddress = ''

class Navigatorss(MDNavigationDrawer):
    image_source = StringProperty('images/qidenticon_two.png')
    title = StringProperty('Navigation')
    drawer_logo = StringProperty()
    # print("priiiiiiiiiiiiinnnnnnnnnnnnnnnnnnnnnttttttttttthethingsss.................", )


class Inbox(Screen):
    """Inbox Screen uses screen to show widgets of screens."""
    def __init__(self, *args, **kwargs):
        super(Inbox, self).__init__(*args, **kwargs)
        # if state.association == '':
        #     state.association = 'BM-2cTuPpAPbu44sbkfVJN2F99sXGJoeNpDBh'
        # print(self.get_address_via_split(state.association))
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method inbox accounts."""
        print("generateaddressgenerateaddressgenerateaddressgenerateaddressgenerateaddress", BMConfigParser().addresses())
        if BMConfigParser().addresses():
            data = [{'text': "surbhi cis222222", 'secondary_text': "party invitation..........." + '\n' + " " + "lets gather for party on 1st JANUARY...!"},
                    {'text': "peter surda", 'secondary_text': "party invitation..........." + '\n' + " " + "lets gather for party on 1st JANUARY...!"},
                    {'text': "uber", 'secondary_text': "party invitation..........." + '\n' + " " + "lets gather for party on 1st JANUARY...!"},
                    {'text': "ola", 'secondary_text': "party invitation..........." + '\n' + " " + "lets gather for party on 1st JANUARY...!"},
                    {'text': "glitch", 'secondary_text': "party invitation..........." + '\n' + " " + "lets gather for party on 1st JANUARY...!"},
                    {'text': "github", 'secondary_text': "party invitation..........." + '\n' + " " + "lets gather for party on 1st JANUARY...!"},
                    {'text': "amazon", 'secondary_text': "party invitation..........." + '\n' + " " + "lets gather for party on 1st JANUARY...!"},
                    {'text': "onkar", 'secondary_text': "party invitation..........." + '\n' + " " + "lets gather for party on 1st JANUARY...!"},
                    {'text': "kivy", 'secondary_text': "party invitation..........." + '\n' + " " + "lets gather for party on 1st JANUARY...!"},
                    {'text': "andrew", 'secondary_text': "party invitation..........." + '\n' + " " + "lets gather for party on 1st JANUARY...!"}]
            for item in data:
                meny = ThreeLineAvatarIconListItem(text=item['text'], secondary_text=item['secondary_text'], theme_text_color= 'Custom',text_color=NavigateApp().theme_cls.primary_color)
                meny.add_widget(AvatarSampleWidget(source='./images/kivymd_logo.png'))
                self.ids.ml.add_widget(meny)
        else:
            self.manager.current = 'login'


class MyAddress(Screen):
    """MyAddress Screen uses screen to show widgets of screens."""
    def __init__(self, *args, **kwargs):
        super(MyAddress, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method inbox accounts."""
        pass
        # if BMConfigParser().AddressSuccessful():
        #     data = [{'text': "me", 'secondary_text': "BM-2cWyUfBdY2FbgyuCb7abFZ49JYxSzUhNFe"},
        #             {'text': "me", 'secondary_text': "BM-2cWyTfBdY2FbgyuCb7abFZ49JYxSzUhNFe"},
        #             {'text': "me", 'secondary_text': "BM-2cWyVfBdY2FbgyuCb7abFZ49JYxSzUhNFe"},
        #             {'text': "me", 'secondary_text': "BM-2cWySfBdY2FbgyuCb7abFZ49JYxSzUhNFe"},
        #             {'text': "me", 'secondary_text': "BM-2cWyHfBdY2FbgyuCb7abFZ49JYxSzUhNFe"},
        #             {'text': "me", 'secondary_text': "BM-2cWyJfBdY2FbgyuCb7abFZ49JYxSzUhNFe"},
        #             {'text': "me", 'secondary_text': "BM-2cWyKfBdY2FbgyuCb7abFZ49JYxSzUhNFe"},
        #             {'text': "me", 'secondary_text': "BM-2cWyMnBdY2FbgyuCb7abFZ49JYxSzUhNFe"},
        #             {'text': "me", 'secondary_text': "BM-2cWyOkBdY2FbgyuCb7abFZ49JYxSzUhNFe"},
        #             {'text': "me", 'secondary_text': "BM-2cWyWuBdY2FbgyuCb7abFZ49JYxSzUhNFe"}]
        #     for item in data:
        #         meny = TwoLineAvatarIconListItem(text=item['text'], secondary_text=item['secondary_text'], theme_text_color= 'Custom',text_color=NavigateApp().theme_cls.primary_color)
        #         meny.add_widget(AvatarSampleWidget(source='./images/avatar.png'))
        #         self.ids.ml.add_widget(meny)
        # else:
        #     self.manager.current = 'login'



class AddressBook(Screen):
    """AddressBook Screen uses screen to show widgets of screens."""
    def __init__(self, *args, **kwargs):
        super(AddressBook, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method inbox accounts."""
        # sqlExecute("DELETE FROM addressbook WHERE label='' ")
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
        print("chek iniiiiiiiiiiiiiittttttttttttttttttttttttttttttttt", self)
        # self.ids.ml.clear_widgets()

    def refreshs(self, *args):
        state.navinstance.ids.sc11.clear_widgets()
        state.navinstance.ids.sc11.add_widget(AddressBook())

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''


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
        # For now we are using static address i.e we are not using recipent field value.
        # toAddress = str(self.ids.txt_input.text)
        # print("hiiiiiiiiiiiiiiiiii i am hereeeeeeeeeeeeeeeeeeeeee..............")
        # print("hiiiiiiiiiseeeee to addresssssssssss..........................", self.ids)
        # print("ssssssssssseeeeeeeeeeeeeeeeeeetheeeeeeeeeeetexttinput....data...", self.ids.txt_input.text)
        # toAddress = "BM-2cVJ8Bb9CM5XTEjZK1CZ9pFhm7jNA1rsa6"
        # print("every thng is good for the day..................", str(self.ids.txt_input.text))
        toAddress = str(self.ids.txt_input.text)
        print("alllllllllllllllllllllllllllsss wel ends wellllllllllllllll", )
        subject = str(self.ids.subject.text)
        message = str(self.ids.body.text)
        print("RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR")
        encoding = 3
        print("message: ", self.ids.body.text)
        sendMessageToPeople = True
        print("SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS")
        if sendMessageToPeople:
            print("TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT")
            print("did_addresssssssssssssssss_existsssssssssssssssssssss.........buyyyyy", toAddress)
            if toAddress != '':
                print("UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU")
                from addresses import decodeAddress
                status, addressVersionNumber, streamNumber, ripe = decodeAddress(
                    toAddress)
                print("VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV")
                if status == 'success':
                    from addresses import *
                    toAddress = addBMIfNotPresent(toAddress)
                    statusIconColor = 'red'
                    print("WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW")
                    if addressVersionNumber > 4 or addressVersionNumber <= 1:
                        print("addressVersionNumber > 4 or addressVersionNumber <= 1")
                    if streamNumber > 1 or streamNumber == 0:
                        print("streamNumber > 1 or streamNumber == 0")
                    if statusIconColor == 'red':
                        print("shared.statusIconColor == 'red'")
                    print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                    stealthLevel = BMConfigParser().safeGetInt(
                        'bitmessagesettings', 'ackstealthlevel')
                    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                    from helper_ackPayload import genAckPayload
                    ackdata = genAckPayload(streamNumber, stealthLevel)
                    print("YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY")
                    t = ()
                    print("ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ")
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
                    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
                    self.parent.parent.screens[3].clear_widgets()
                    self.parent.parent.screens[3].add_widget(Sent())
                    toLabel = ''
                    queues.workerQueue.put(('sendmessage', toAddress))
                    print("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")
                    print("DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD")
                    print("sqlExecute successfully #######################")
                    self.ids.body.text = ''
                    self.ids.ti.text = ''
                    self.ids.subject.text = ''
                    self.ids.txt_input.text = ''
                    # self.manager.current
                    # self.ids.scr_mngr.current = 'add_sucess'
                    self.parent.parent.current = 'sent'
                    # print("whattttttttttttttttisdebuggerbtnssssssssss........................", self.ids)
                    self.ids.btn.text = 'select'
                    self.ids.ti.text = ''
                    print("sssssssssssuvvvvvvvvvvvvvvvvvtttttttttttttttttt...............")
                    return None


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
            self.parent.height = (250 + (len(matches)*20))
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
        queues.addressGeneratorQueue.put((
            'createRandomAddress',
            4, streamNumberForAddress,
            label, 1, "", eighteenByteRipe,
            nonceTrialsPerByte,
            payloadLengthExtraBytes)
        )
        self.manager.current = 'add_sucess'
        print("whhhheeeeeeee55566666666666666666666..................", self)
        print("what is the screeen forrrrrrrrrrrrrrrrr...............", self.ids)
        self.ids.label.text = ''
        # print("whatttttt99999999999999999999999999999999999988888888......", self.parent.parent)
        # print("go.....more...parenxccccccccccccccccccccccc555559955555555555", self.parent.parent.parent)
        # print("ssssshooooocxvxcvxcvoooouuuuuuuuuuuuuuuuuueeeettttttttteeeeeeeeeee............... ", ContentNavigationDrawer().ids.btn)
        # print("spiiiiinnnxcvxcxc99999999999999999999999999999999999999tttt..........", ContentNavigationDrawer().ids.btn.text)
        # print("text_dirrrrrrrrrrrrrrrrrrrrrr9999999999999999fgdg.............................", dir(ContentNavigationDrawer().ids.btn))
        # print("ttttttttttttttiiiiiiiiilllllllllllllllttttleeeeeeeee9999999999999999999", ContentNavigationDrawer().ids.btn.text)
        # prnit("55555557777777777777777888888888888888888jjjjjjjjjj", ContentNavigationDrawer().ids.btn.text)
        # print("what account is associated..............................", state.association)
        # print("pppppppppp999999999666666666663333333333333333333333..............", BMConfigParser().addresses())
        # print("whatssssssssssssssssssssssstheva,lllllllllllleeeeeeeee...........")
        # print("wh.....................8888888899999999999999999999999999", queues.addressGeneratorQueue.get())

        # print("ljjkkkkkkkkkkkkkkkkkkk666666666666666666666666666666666", self.parent.parent.parent.parent.parent)
        # ContentNavigationDrawer().ids.btn.text = BMConfigParser().addresses()[0]
        # if BMConfigParser().addresses():
            # print("iiiinnnnnnnnnnnnnnnnnnnnnnnnnnsssssssssssiiiiiiiiiideeeeeeeee")
            # ContentNavigationDrawer().ids.btn.text = BMConfigParser().addresses()[0]
            # return BMConfigParser().addresses()[0]
        # print("iiiiiiiiiiiiiihhhhhhhhhhhhhhhhh5555555555555555555....", ContentNavigationDrawer())
        # print("khhhhhhhhhhhhhyaaaaaaaaaaaaaaaa5555555555555555...............", ContentNavigationDrawer().ids)
        # print("it is sccccccccccccefssssfulllllll............................", ContentNavigationDrawer().ids.btn.text)
        # ids.btn.text


class AddressSuccessful(Screen):
    pass


class NavigationLayout():
    pass

class Sent(Screen):
    """Sent Screen uses screen to show widgets of screens."""
    data = ListProperty()

    def __init__(self, *args, **kwargs):
        super(Sent, self).__init__(*args, **kwargs)
        # print("I amuuuuuupfatgd vale should get..................... .", ContentNavigationDrawer().ids.btn.text)
        # print("yyyyyyuuuuuuuuuuuuuuuuuoooooooooouuuyyyyyyyyyyyy...............", ContentNavigationDrawer().ids.btn.values)
        # print("ccchekkkkkkkkkccccccccccclre..................................................", ContentNavigationDrawer().ids.btn)
        # print("llllllllllleeeeetttttttttttttttttttttheeeeeeeeemmmmmmcheccccccccccckkk........", dir(ContentNavigationDrawer().ids.btn))
        # print("llllllllllllllllllllllllllleeeeeeeeeeeeeeeeeeeeeeeexfgcgcgvcgvcvgbeeechhhhhhhhhhheck", state.association)
        if state.association == '':
            # state.association = Navigatocoming inside thew methoddddddddddddddddddds1buildrss().ids.btn.text
            print("uuuuuuuuuuuuuuuuuuuuuuuuu999999999999999999999999999999")
            print("lllllllllllllllllllllllllllllll55555555556666666666", BMConfigParser().addresses())
            if BMConfigParser().addresses():
                state.association = BMConfigParser().addresses()[0]
        print("kkkkkkkkkkkkkkkkkkkkkkkkkkkk6666666666888888888888888888...................", state.association)
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method sent accounts."""
        print("oooooooooooooooooooooooooooo999999999999999999999000000000")
        self.sentaccounts()
        print(dt)

    def sentaccounts(self):
        """Load sent accounts."""
        print("mmmmmmmmmmmmmmmmmmmmmmmm44444444444444444455555555555__........")
        account = state.association
        print("zzzzzzzzzzzzzzzzzzzzzzz99999999999999999999999999999999999", account)
        self.loadSent(account, 'All', '')

    def loadSent(self, account, where="", what=""):
        """Load Sent list for Sent messages."""
        # print("uuuuuuuuuuuuuuuuyyyyyyyyyrrrrrrrrrrrinside_loadSent..........")
        xAddress = 'fromaddress'
        data = []
        # print("check--------thre.................somethiong.......cvmnvb mvn xmnvcxv.")
        queryreturn = kivy_helper_search.search_sql(
            xAddress, account, "sent", where, what, False)
        print("qqqqqqqq77777777777777777777777777777777555hhhhhhhhhhhhhhhfffffff....", queryreturn)
        if queryreturn:
            # for mail in sqlQuery("SELECT toaddress, subject, message   FROM addressbook a, sent s WHERE a.address = s.fromaddress and s.fromaddress = 'BM-2cUz6dniZHjFTqv6j2es2wBSe3NydZdk4R';"):
            for mail in queryreturn:
                third_text = mail[3].replace('\n', ' ')
                print("whatttttttttttttttttttttttttttisssssssssssssssssssssssserrrrrrrrrrrrror")
                print("nowwwwwwwwww9999999999999999999999999999999..................", third_text)
                # print("sssssssssssssssseeeeeeeeeeeeeeeeeeeeeeeeeeeepprob.....", mail[2][:20] + '.....' if len(mail[2]) > 20 else mail[2])
                # data.append({'text': mail[0].strip(), 'secondary_text': mail[2][:20] + '.....' if len(mail[2]) > 20 else mail[2] + '\n' + " " + (third_text[:35] + '...!') if len(third_text) > 35 else third_text })
                # data.append({'text': '', 'secondary_text': mail[2] + '\n' + " " + (third_text[:35] + '...!') if len(third_text) > 35 else third_text })
                data.append({'text': mail[0].strip(), 'secondary_text': mail[2][:10] + '...........' if len(mail[2]) > 10 else mail[2] + '\n' + " " + (third_text[:25] + '...!') if len(third_text) > 25 else third_text })
                print("kyaaaaaaaaaaaaaaaaaaaaaaaaaayhaaaaaaaaaaaaerorrrrrrrrrr")
            # self.data = [{
            #     'data_index': i,
            #     'index': 1,
            #     'height': 48,
            #     'text': row[2],
            #     }
            #     for i, row in enumerate(queryreturn)
            # ]
            print("show 6666666666666666666eeeeeee555555555555555daaaaaaaaaaa.......", data)
            for item in data:
                meny = ThreeLineAvatarIconListItem(text=item['text'], secondary_text=item['secondary_text'], theme_text_color= 'Custom',text_color=NavigateApp().theme_cls.primary_color)
                meny.add_widget(AvatarSampleWidget(source='./images/avatar.png'))
                self.ids.ml.add_widget(meny)
            print("uyyyyyyyyyyyyyyyyyyyyyyyyyuuuuuuuuuggg558888888888gggggggoooooooooooooooooooooooooooooooooooooooo....")
            # print("ufffffffffffffffffffffffff6666666666666ffffyyyyyyyyyyyyyyyyyyyyyyyyypp.......", self.data)
        else:
            # self.data = [{
            #     'data_index': 1,
            #     'index': 1,
            #     'height': 48,
            #     'text': "yet no message for this account!!!!!!!!!!!!!"}
            # ]
            content = MDLabel(font_style='Body1',
                                      theme_text_color='Primary',
                                      text="yet no message for this account!!!!!!!!!!!!!",
                                      halign='center',
                                      bold=True,
                                      size_hint_y=None,
                                      valign='top')
            self.ids.ml.add_widget(content)

class Trash(Screen):
    """Trash Screen uses screen to show widgets of screens."""
    def __init__(self, *args, **kwargs):
        super(Trash, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method inbox accounts."""
        data = [{'text': "neha cis", 'secondary_text': "party invitation..........." + '\n' + " " + "lets gather for party on 1st JANUARY...!"},
                {'text': "onkar", 'secondary_text': "party invitation..........." + '\n' + " " + "lets gather for party on 1st JANUARY...!"},
                {'text': "amazon", 'secondary_text': "party invitation..........." + '\n' + " " + "lets gather for party on 1st JANUARY...!"},
                {'text': "paytm", 'secondary_text': "party invitation..........." + '\n' + " " + "lets gather for party on 1st JANUARY...!"},
                {'text': "pol", 'secondary_text': "party invitation..........." + '\n' + " " + "lets gather for party on 1st JANUARY...!"},
                {'text': "akshayaura", 'secondary_text': "party invitation..........." + '\n' + " " + "lets gather for party on 1st JANUARY...!"},
                {'text': "codementor", 'secondary_text': "party invitation..........." + '\n' + " " + "lets gather for party on 1st JANUARY...!"},
                {'text': "yatra", 'secondary_text': "party invitation..........." + '\n' + " " + "lets gather for party on 1st JANUARY...!"},
                {'text': "mdtezm", 'secondary_text': "party invitation..........." + '\n' + " " + "lets gather for party on 1st JANUARY...!"},
                {'text': "crewqt", 'secondary_text': "party invitation..........." + '\n' + " " + "lets gather for party on 1st JANUARY...!"}]
        for item in data:
            meny = ThreeLineAvatarIconListItem(text=item['text'], secondary_text=item['secondary_text'], theme_text_color= 'Custom',text_color=NavigateApp().theme_cls.primary_color)
            meny.add_widget(AvatarSampleWidget(source='./images/avatar.png'))
            self.ids.ml.add_widget(meny)


class Page(Screen):
    pass


class Create(Screen):
    def __init__(self, **kwargs):
        super(Create, self).__init__(**kwargs)
        # from kivy.core.window import Window
        print("cheeeeeeeeeeeehn888888888888888888888888gggkkkkkkkthe windowwwwwwwwwwwwwwww", Window.size)
        # print("take the onlyyyyyyyyyyyyyyyyyyyyyyyyyyyy x axssssssssssssssssssssssswindow", Window.size[0])
        # print("realllllllllllyyyyyyyyyyyyy yyyyyyyyyyyoooooouuuuuuu wwwwwwaaaaaaaaaaaannnnnnnnnntttt", Window._get_width)
        # print("mmmmmmmmmmmmmminnnnnnnnnnnnnnnn and mmmmmmmmaaaaaaaaxxxxxxxesssssssss", Window.minimum_height, Window.minimum_width)
        # print("dir in windowwwwwwwwwkkkkkkkkkkkww of the mobile screen", dir(Window))
        # print("cheeeeeeeeeeeeeeeeeckkkkkkkkkkkkkkkk width and heightttttttttttttttttttt", Window.width, window.height)
        widget_1 = DropDownWidget()
        from helper_sql import *
        widget_1.ids.txt_input.word_list = [addr[1] for addr in sqlQuery("SELECT label, address from addressbook")]
        # widget_1.ids.txt_input.word_list = ['how to use python', 'how to use kivy', 'how to use django', 'BM-2cTik2JBHAS92U633LPY', 'BM-2cUYmQofWjTQeUitL7']
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
    variable_1 = ListProperty(BMConfigParser().addresses())
    nav_drawer = ObjectProperty()
    # user_address = StringProperty('jai')
    scr_size = Window.size[0]

    title = "KivyMD"
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
        print('kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkllllllllllrrrrrrrrrrahut......')
        print('chreckoooooooooooooooo........................', self.variable_1)
        print("dsssssssssssoddddddddd77777777777777777777eeeeeeeeetheroot", dir(self))
        import os
        main_widget = Builder.load_file(
            os.path.join(os.path.dirname(__file__), 'main.kv'))
        self.nav_drawer = Navigatorss()
        self.obj_1 = AddressBook()
        kivysignalthread = UIkivySignaler()
        kivysignalthread.daemon = True
        kivysignalthread.start()
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
        print("9062 I am pressed...............................................................")
        content = MDLabel(font_style='Body1',
                          theme_text_color='Secondary',
                          text="Successfully Saved your contact address. "
                               "That's pretty awesome right!",
                          size_hint_y=None,
                          valign='top')
        print("9063 I am pressed...............................................................")
        content.bind(texture_size=content.setter('size'))
        print("9064 I am pressed...............................................................")
        # self.dialog = MDDialog(content=content,
        #                        size_hint=(.8, None),
        #                        height=dp(200),
        #                        auto_dismiss=False)
        print("9065 I am pressed...............................................................")
        # self.dialog.add_action_button("Dismiss",
        #                               action=lambda *x: self.dialog.dismiss())
        print("966 I am pressed...............................................................")
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
            # return [BMConfigParser().get(address, 'label')[:12] + '..' for address in BMConfigParser().sections()[1:]]
            # return BMConfigParser().addresses()

    def getCurrentAccountData(self, text):
        """Get Current Address Account Data."""
        print("self tttttttttttttttttttttteeeeeeeeeexfgvbcvgfcgfdgfdgfgxxxxxxxxtttttttttzzzzzzzz    ", text)
        state.association = text
        # print("eeeeeeeeeeeeerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrorrrrrrrrrrrrrrrrrr", self.root)
        # print("iiiiiiiiiiiiiidddddddddddddddddeeeeeeeessssssssssssssssss55......", self.root.ids)
        self.root.ids.sc1.clear_widgets()
        self.root.ids.sc4.clear_widgets()
        self.root.ids.sc5.clear_widgets()
        # print("resffffffffffffffffffffffffffffuuuuuuuuuuuuuuuuuuurrrrrrrrrrrrr......")
        self.root.ids.sc1.add_widget(Inbox())
        self.root.ids.sc4.add_widget(Sent())
        self.root.ids.sc5.add_widget(Trash())
        # print("again aaaaddddddddddddddddddinggggggggggggggggguuuuuuuuuuuuuuuu1 ........")

        # self.root.ids.toolbar.title = BMConfigParser().get(
        #     state.association, 'label') + '({})'.format(state.association)
        # print("what theyyyyyyyyyyyyyyyyyyyy areeeeeeeeeeeee printing11........", self.root.ids.toolbar.title)
        # Inbox()
        # Sent()
        # Trash()
        # print("finish gamneeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee!")

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
        print("coming inside thew methodddddddddddddddddddsdcassdfs1")
        print("combbbbbbbbbbbbggggffffffdfgdgfffffffgggggggggggggggggggllllllloooo", BMConfigParser().addresses())
        # return BMConfigParser.addresses[0]
        if BMConfigParser().addresses():
            return BMConfigParser().addresses()[0]
        return 'Select Address'


class GrashofPopup(Popup):
    def __init__(self, **kwargs):
        super(GrashofPopup, self).__init__(**kwargs)
        self.size_hint_y = 0.7
        self.size_hint_x = 0.9

    def savecontact(self):
        print("show the addedes addess in databaseeeeeeeeeeeeeeeeee............................")
        print("1110 I am pressed...............................................................")
        label = self.ids.label.text
        print("2210 I am pressed...............................................................")
        address = self.ids.address.text
        print("3310 I am pressed...............................................................")
        if label and address:
            state.navinstance = self.parent.children[1]
            queues.UISignalQueue.put(('rerenderAddressBook', ''))
            self.dismiss()
            sqlExecute("INSERT INTO addressbook VALUES(?,?)", label, address)
        # self.parent.children[1].ids.sc11.clear_widgets()
        # self.parent.children[1].ids.sc11.add_widget(AddressBook())

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
        # self.controller = App.get_running_app().controller
        # self.controller.bind(
        #     current_account=lambda _, value: self.on_current_account(value))

    def on_current_account(self, account):
        pass
        # e.g. deleting the last account, would set
        # Controller.current_account to None
        # if account is None:
        #     return
        # address = "0x" + account.address.encode("hex")
        # self.address_property = address

    def _update_specific_text_color(self, instance, value):
        pass

    def _set_active(self, active, list):
        pass