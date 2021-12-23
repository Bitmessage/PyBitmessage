# pylint: disable=too-many-lines,import-error,no-name-in-module,unused-argument
# pylint: disable=too-many-ancestors,too-many-locals,useless-super-delegation
# pylint: disable=protected-access
# pylint: disable=import-outside-toplevel,ungrouped-imports,wrong-import-order,unused-import,arguments-differ
# pylint: disable=invalid-name,unnecessary-comprehension,broad-except,simplifiable-if-expression,no-member
# pylint: disable=too-many-return-statements

"""
Bitmessage android(mobile) interface
"""

from pybitmessage.get_platform import platform
import os
# from pybitmessage import identiconGeneration
from pybitmessage import kivy_helper_search
from pybitmessage.uikivysignaler import UIkivySignaler
from pybitmessage.bmconfigparser import BMConfigParser
# from debug import logger
from functools import partial
from pybitmessage.helper_sql import sqlExecute, sqlQuery
from kivymd.app import MDApp
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
    StringProperty
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.list import (
    IRightBodyTouch,
    OneLineAvatarIconListItem,
    OneLineListItem
)

from kivy.uix.screenmanager import RiseInTransition, SlideTransition, FallOutTransition

from pybitmessage import queues
from pybitmessage.semaphores import kivyuisignaler

from pybitmessage import state
from kivymd.uix.bottomsheet import MDCustomBottomSheet

from kivy.lang import Observable
# import gettext
# import l10n
# import locale
import ast

from pybitmessage.baseclass.common import toast

# from qr_scanner.zbarcam import ZBarCam
# from pyzbar.pyzbar import ZBarSymbol

if platform != "android":
    from kivy.config import Config
    Config.set("input", "mouse", "mouse, multitouch_on_demand")
elif platform == "android":
    from jnius import autoclass, cast
    from android.runnable import run_on_ui_thread
    from android import python_act as PythonActivity

    Toast = autoclass("android.widget.Toast")
    String = autoclass("java.lang.String")
    CharSequence = autoclass("java.lang.CharSequence")
    context = PythonActivity.mActivity

    @run_on_ui_thread
    def show_toast(text, length):
        """Its showing toast on screen"""
        t = Toast.makeText(context, text, length)
        t.show()


with open(os.path.join(os.path.dirname(__file__), "screens_data.json")) as read_file:
    all_data = ast.literal_eval(read_file.read())
    data_screens = list(all_data.keys())

for modules in data_screens:
    exec(all_data[modules]['Import'])

# pylint: disable=too-few-public-methods,too-many-arguments,attribute-defined-outside-init


class Lang(Observable):
    observers = []
    lang = None

    def __init__(self, defaultlang):
        super(Lang, self).__init__()
        self.ugettext = None
        self.lang = defaultlang
        self.switch_lang(self.lang)

    def _(self, text):
        # return self.ugettext(text)
        return text

    def fbind(self, name, func, args, **kwargs):
        if name == "_":
            self.observers.append((func, args, kwargs))
        else:
            return super(Lang, self).fbind(name, func, *largs, **kwargs)

    def funbind(self, name, func, args, **kwargs):
        if name == "_":
            key = (func, args, kwargs)
            if key in self.observers:
                self.observers.remove(key)
        else:
            return super(Lang, self).funbind(name, func, *args, **kwargs)

    def switch_lang(self, lang):
        # get the right locales directory, and instanciate a gettext
        # locale_dir = os.path.join(os.path.dirname(__file__), 'translations', 'mo', 'locales')
        # locales = gettext.translation('langapp', locale_dir, languages=[lang])
        # self.ugettext = locales.gettext

        # update all the kv rules attached to this text
        for func, largs, kwargs in self.observers:
            func(largs, None, None)


class NavigationItem(OneLineAvatarIconListItem):
    """NavigationItem class for kivy Ui"""
    badge_text = StringProperty()
    icon = StringProperty()
    active = BooleanProperty(False)

    def currentlyActive(self):
        """Currenly active"""
        for nav_obj in self.parent.children:
            nav_obj.active = False
        self.active = True


class NavigationDrawerDivider(OneLineListItem):
    """
    A small full-width divider that can be placed
    in the :class:`MDNavigationDrawer`
    """

    disabled = True
    divider = None
    _txt_top_pad = NumericProperty(dp(8))
    _txt_bot_pad = NumericProperty(dp(8))

    def __init__(self, **kwargs):
        # pylint: disable=bad-super-call
        super(OneLineListItem, self).__init__(**kwargs)
        self.height = dp(16)


class NavigationDrawerSubheader(OneLineListItem):
    """
    A subheader for separating content in :class:`MDNavigationDrawer`

    Works well alongside :class:`NavigationDrawerDivider`
    """

    disabled = True
    divider = None
    theme_text_color = 'Secondary'


class ContentNavigationDrawer(BoxLayout):
    """ContentNavigationDrawer class for kivy Uir"""

    def __init__(self, *args, **kwargs):
        """Method used for contentNavigationDrawer"""
        super(ContentNavigationDrawer, self).__init__(*args, **kwargs)
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for class contentNavigationDrawer"""
        self.ids.scroll_y.bind(scroll_y=self.check_scroll_y)

    def check_scroll_y(self, instance, somethingelse):
        """show data on scroll down"""
        if self.ids.btn.is_open:
            self.ids.btn.is_open = False


class BadgeText(IRightBodyTouch, MDLabel):
    """BadgeText class for kivy Ui"""


class CustomSpinner(Spinner):
    """CustomSpinner class for kivy Ui"""

    def __init__(self, *args, **kwargs):
        """Method used for setting size of spinner"""
        super(CustomSpinner, self).__init__(*args, **kwargs)
        self.dropdown_cls.max_height = Window.size[1] / 3
        self.values = list(addr for addr in BMConfigParser().addresses()
                           if BMConfigParser().get(str(addr), 'enabled') == 'true')


class NavigateApp(MDApp):
    """Navigation Layout of class"""
    # pylint: disable=too-many-public-methods,inconsistent-return-statements

    # theme_cls = ThemeManager()
    previous_date = ObjectProperty()
    obj_1 = ObjectProperty()
    variable_1 = ListProperty(addr for addr in BMConfigParser().addresses()
                              if BMConfigParser().get(str(addr), 'enabled') == 'true')
    nav_drawer = ObjectProperty()
    state.screen_density = Window.size
    window_size = state.screen_density
    app_platform = platform
    title = "PyBitmessage"
    imgstatus = False
    count = 0
    manager_open = False
    file_manager = None
    state.imageDir = os.path.join('./images', 'kivy')
    image_path = state.imageDir
    tr = Lang("en")  # for changing in franch replace en with fr

    def build(self):
        """Method builds the widget"""
        for kv in data_screens:
            Builder.load_file(
                os.path.join(
                    os.path.dirname(__file__),
                    'kv',
                    # f'{all_data[kv]["kv_string"]}.kv',
                    '{0}.kv'.format(all_data[kv]["kv_string"]),
                )
            )
            print('{0}.kv'.format(all_data[kv]["kv_string"]))
            # import pdb; pdb.set_trace()
        # self.obj_1 = AddressBook()
        kivysignalthread = UIkivySignaler()
        kivysignalthread.daemon = True
        kivysignalthread.start()
        Window.bind(on_keyboard=self.on_key, on_request_close=self.on_request_close)
        return Builder.load_file(
            os.path.join(os.path.dirname(__file__), 'main.kv'))
        # return Builder.load_file('/home/cis/Bitmessagepeter/KivyPoject/PyBitmessage/src/tests/mock/pybitmessage/main.kv')


    def run(self):
        """Running the widgets"""
        print('run 251 ---------------------------------')
        kivyuisignaler.release()
        super(NavigateApp, self).run()

    @staticmethod
    def showmeaddresses(name="text"):
        print('showmeaddresses 257 ---------------------------------')
        """Show the addresses in spinner to make as dropdown"""
        if name == "text":
            print('if')
            if BMConfigParser().addresses():
                return BMConfigParser().addresses()[0][:16] + '..'
            return "textdemo"
        elif name == "values":
            print('else')
            if BMConfigParser().addresses():
                return [address[:16] + '..'
                        for address in BMConfigParser().addresses()]
            return "valuesdemo"

    def getCurrentAccountData(self, text):
        """Get Current Address Account Data"""
        # print('getCurrentAccountData 273 ---------------------------------')
        # if text != '':
        #     if os.path.exists(state.imageDir + '/default_identicon/{}.png'.format(text)):
        #         self.load_selected_Image(text)
        #     else:
        #         self.set_identicon(text)
        #         self.root.ids.content_drawer.ids.reset_image.opacity = 0
        #         self.root.ids.content_drawer.ids.reset_image.disabled = True
        #     address_label = self.current_address_label(
        #         BMConfigParser().get(text, 'label'), text)

        #     self.root_window.children[1].ids.toolbar.title = address_label
        #     state.association = text
        #     state.searcing_text = ''
        #     LoadingPopup().open()
        #     self.set_message_count()
        #     for nav_obj in self.root.ids.content_drawer.children[
        #             0].children[0].children[0].children:
        #         nav_obj.active = True if nav_obj.text == 'Inbox' else False
        #     self.fileManagerSetting()
        #     Clock.schedule_once(self.setCurrentAccountData, 0.5)
        pass

    def fileManagerSetting(self):
        """This method is for file manager setting"""
        if not self.root.ids.content_drawer.ids.file_manager.opacity and \
                self.root.ids.content_drawer.ids.file_manager.disabled:
            self.root.ids.content_drawer.ids.file_manager.opacity = 1
            self.root.ids.content_drawer.ids.file_manager.disabled = False

    def setCurrentAccountData(self, dt=0):
        """This method set the current accout data on all the screens"""
        print('setCurrentAccountData 304 ---------------------------------')
        
        # self.root.ids.sc1.ids.ml.clear_widgets()
        # self.root.ids.sc1.loadMessagelist(state.association)

        # self.root.ids.sc4.ids.ml.clear_widgets()
        # self.root.ids.sc4.children[2].children[2].ids.search_field.text = ''
        # self.root.ids.sc4.loadSent(state.association)

        # self.root.ids.sc16.clear_widgets()
        # self.root.ids.sc16.add_widget(Draft())

        # self.root.ids.sc5.clear_widgets()
        # self.root.ids.sc5.add_widget(Trash())

        # self.root.ids.sc17.clear_widgets()
        # self.root.ids.sc17.add_widget(Allmails())

        # self.root.ids.sc10.ids.ml.clear_widgets()
        # self.root.ids.sc10.init_ui()

        self.root.ids.scr_mngr.current = 'inbox'
        pass

    @staticmethod
    def getCurrentAccount():
        print('getCurrentAccount 329 ----------------------------')
        """It uses to get current account label"""
        if state.association:
            return state.association
        return "Bitmessage Login"

    # @staticmethod
    def addingtoaddressbook(self):
        """Adding to address Book"""
        width = .85 if platform == 'android' else .8
        self.add_popup = MDDialog(
            title='Add contact\'s',
            type="custom",
            size_hint=(width, .23),
            content_cls=GrashofPopup(),
            buttons=[
                MDRaisedButton(
                    text="Save",
                    on_release=self.savecontact,
                ),
                MDRaisedButton(
                    text="Cancel",
                    on_release=self.close_pop,
                ),
                MDRaisedButton(
                    text="Scan QR code",
                    on_release=self.scan_qr_code,
                ),
            ],
        )
        # self.add_popup.set_normal_height()
        self.add_popup.auto_dismiss = False
        self.add_popup.open()
        # p = GrashofPopup()
        # p.open()

    def scan_qr_code(self, instance):
        """this method is used for showing QR code scanner"""
        if self.is_camara_attached():
            self.add_popup.dismiss()
            self.root.ids.sc23.get_screen(self.root.ids.scr_mngr.current, self.add_popup)
            self.root.ids.scr_mngr.current = 'scanscreen'
        else:
            altet_txt = (
                'Currently this feature is not avaialbe!' if platform == 'android' else 'Camera is not available!')
            self.add_popup.dismiss()
            toast(altet_txt)

    def is_camara_attached(self):
        print('is_camara_attached -----------------------378')
        """This method is for checking is camera available or not"""
        self.root.ids.sc23.check_camera()
        is_available = self.root.ids.sc23.camera_avaialbe
        return is_available

    def savecontact(self, instance):
        # """Method is used for saving contacts"""
        # pupup_obj = self.add_popup.content_cls
        # label = pupup_obj.ids.label.text.strip()
        # address = pupup_obj.ids.address.text.strip()
        # if label == '' and address == '':
        #     pupup_obj.ids.label.focus = True
        #     pupup_obj.ids.address.focus = True
        # elif address == '':
        #     pupup_obj.ids.address.focus = True
        # elif label == '':
        #     pupup_obj.ids.label.focus = True
        # else:
        #     pupup_obj.ids.address.focus = True
        #     # pupup_obj.ids.label.focus = True

        # stored_address = [addr[1] for addr in kivy_helper_search.search_sql(
        #     folder="addressbook")]
        # stored_labels = [labels[0] for labels in kivy_helper_search.search_sql(
        #     folder="addressbook")]
        # if label and address and address not in stored_address \
        #         and label not in stored_labels and pupup_obj.valid:
        #     # state.navinstance = self.parent.children[1]
        #     queues.UISignalQueue.put(('rerenderAddressBook', ''))
        #     self.add_popup.dismiss()
        #     sqlExecute("INSERT INTO addressbook VALUES(?,?)", label, address)
        #     try:
        #         rootIds = self.root.ids
        #     except Exception as e:
        #         rootIds = state.kivyapp.root.ids
        #     rootIds.sc11.ids.ml.clear_widgets()
        #     rootIds.sc11.loadAddresslist(None, 'All', '')
        #     rootIds.scr_mngr.current = 'addressbook'
        #     toast('Saved')
        pass

    def close_pop(self, instance):
        """Pop is Canceled"""
        self.add_popup.dismiss()
        toast('Canceled')

    def getDefaultAccData(self, instance):
        """Getting Default Account Data"""
        print('getDefaultAccData---------------------------------')
        if self.variable_1:
            state.association = first_addr = self.variable_1[0]
            # if BMConfigParser().get(str(first_addr), 'enabled') == 'true':
                # img = identiconGeneration.generate(first_addr)
                # print('line...........................................426')
                # self.createFolder(state.imageDir + '/default_identicon/')
                # if platform == 'android':
                #     # android_path = os.path.expanduser
                #     # ("~/user/0/org.test.bitapp/files/app/")
                #     if not os.path.exists(state.imageDir + '/default_identicon/{}.png'.format(
                #             BMConfigParser().addresses()[0])):
                #         android_path = os.path.join(
                #             os.environ['ANDROID_PRIVATE'] + '/app/')
                #         img.texture.save('{1}/images/kivy/default_identicon/{0}.png'.format(
                #             BMConfigParser().addresses()[0], android_path))
                # else:
                #     if not os.path.exists(state.imageDir + '/default_identicon/{}.png'.format(
                #             BMConfigParser().addresses()[0])):
                #         img.texture.save(state.imageDir + '/default_identicon/{}.png'.format(
                #             BMConfigParser().addresses()[0]))
                # instance.parent.parent.parent.parent.parent.ids.top_box.children[0].texture = (
                    # img.texture)
            return first_addr
        return 'Select Address'

    def get_default_logo(self, instance):
        """Getting default logo image"""
        # if self.variable_1:
        #     first_addr = self.variable_1[0]
        #     if BMConfigParser().get(str(first_addr), 'enabled') == 'true':
        #         if os.path.exists(
        #             state.imageDir + '/default_identicon/{}.png'.format(first_addr)):
        #             return state.imageDir + '/default_identicon/{}.png'.format(
        #                     first_addr)
        #         else:
        #             img = identiconGeneration.generate(first_addr)
        #             instance.texture = img.texture
        #             return
        # return state.imageDir + '/drawer_logo1.png'
        pass
    @staticmethod
    def addressexist():
        print('addressexist 469 --------------------------')
        """Checking address existence"""
        if BMConfigParser().addresses():
            return True
        return False

    def on_key(self, window, key, *args):
        pass
    #     # pylint: disable=inconsistent-return-statements, too-many-branches
    #     """Method is used for going on previous screen"""
    #     if key == 27:
    #         if state.in_search_mode and self.root.ids.scr_mngr.current not in [
    #                 "mailDetail", "create"]:
    #             self.closeSearchScreen()
    #         elif self.root.ids.scr_mngr.current == "mailDetail":
    #             self.root.ids.scr_mngr.current = 'sent'\
    #                 if state.detailPageType == 'sent' else 'inbox' \
    #                 if state.detailPageType == 'inbox' else 'draft'
    #             self.back_press()
    #             if state.in_search_mode and state.searcing_text:
    #                 toolbar_obj = self.root.ids.toolbar
    #                 toolbar_obj.left_action_items = [
    #                     ['arrow-left', lambda x: self.closeSearchScreen()]]
    #                 toolbar_obj.right_action_items = []
    #                 self.root.ids.toolbar.title = ''
    #         elif self.root.ids.scr_mngr.current == "create":
    #             self.save_draft()
    #             self.set_common_header()
    #             state.in_composer = False
    #             self.root.ids.scr_mngr.current = 'inbox'
    #         elif self.root.ids.scr_mngr.current == "showqrcode":
    #             self.set_common_header()
    #             self.root.ids.scr_mngr.current = 'myaddress'
    #         elif self.root.ids.scr_mngr.current == "random":
    #             self.root.ids.scr_mngr.current = 'login'
    #         elif self.root.ids.scr_mngr.current == 'pay-options':
    #             self.set_common_header()
    #             self.root.ids.scr_mngr.current = 'payment'
    #         elif self.root.ids.scr_mngr.current == 'chroom':
    #             if state.association:
    #                 address_label = self.current_address_label(
    #                     BMConfigParser().get(
    #                         state.association, 'label'), state.association)
    #                 self.root.ids.toolbar.title = address_label
    #             self.set_common_header()
    #             self.root.ids.scr_mngr.transition = FallOutTransition()
    #             self.root.ids.scr_mngr.current = 'chlist'
    #             self.root.ids.scr_mngr.transition = SlideTransition()
    #         else:
    #             if state.kivyapp.variable_1:
    #                 self.root.ids.scr_mngr.current = 'inbox'
    #         self.root.ids.scr_mngr.transition.direction = 'right'
    #         self.root.ids.scr_mngr.transition.bind(on_complete=self.reset)
    #         return True
    #     elif key == 13 and state.searcing_text and not state.in_composer:
    #         if state.search_screen == 'inbox':
    #             self.root.ids.sc1.children[1].active = True
    #             Clock.schedule_once(self.search_callback, 0.5)
    #         elif state.search_screen == 'addressbook':
    #             self.root.ids.sc11.children[1].active = True
    #             Clock.schedule_once(self.search_callback, 0.5)
    #         elif state.search_screen == 'myaddress':
    #             self.loadMyAddressScreen(True)
    #             Clock.schedule_once(self.search_callback, 0.5)
    #         elif state.search_screen == 'sent':
    #             self.root.ids.sc4.children[1].active = True
    #             Clock.schedule_once(self.search_callback, 0.5)

    def search_callback(self, dt=0):
        """Show data after loader is loaded"""
        # if state.search_screen == 'inbox':
        #     self.root.ids.sc1.ids.ml.clear_widgets()
        #     self.root.ids.sc1.loadMessagelist(state.association)
        #     self.root.ids.sc1.children[1].active = False
        # elif state.search_screen == 'addressbook':
        #     self.root.ids.sc11.ids.ml.clear_widgets()
        #     self.root.ids.sc11.loadAddresslist(None, 'All', '')
        #     self.root.ids.sc11.children[1].active = False
        # elif state.search_screen == 'myaddress':
        #     self.root.ids.sc10.ids.ml.clear_widgets()
        #     self.root.ids.sc10.init_ui()
        #     self.loadMyAddressScreen(False)
        # else:
        #     self.root.ids.sc4.ids.ml.clear_widgets()
        #     self.root.ids.sc4.loadSent(state.association)
        #     self.root.ids.sc4.children[1].active = False
        # self.root.ids.scr_mngr.current = state.search_screen
        pass

    def loadMyAddressScreen(self, action):
        # """loadMyAddressScreen method spin the loader"""
        # if len(self.root.ids.sc10.children) <= 2:
        #     self.root.ids.sc10.children[0].active = action
        # else:
        #     self.root.ids.sc10.children[1].active = action
        pass
    def save_draft(self):
        # """Saving drafts messages"""
        # composer_objs = self.root
        # from_addr = str(self.root.ids.sc3.children[1].ids.ti.text)
        # # to_addr = str(self.root.ids.sc3.children[1].ids.txt_input.text)
        # if from_addr and state.detailPageType != 'draft' \
        #         and not state.in_sent_method:
        #     Draft().draft_msg(composer_objs)
        # return
        pass

    def reset(self, *args):
        # """Set transition direction"""
        # self.root.ids.scr_mngr.transition.direction = 'left'
        # self.root.ids.scr_mngr.transition.unbind(on_complete=self.reset)
        pass 
    @staticmethod
    def status_dispatching(data):
        # """Dispatching Status acknowledgment"""
        # ackData, message = data
        # if state.ackdata == ackData:
        #     state.status.status = message
        pass

    def clear_composer(self):
        # """If slow down, the new composer edit screen"""
        # self.set_navbar_for_composer()
        # composer_obj = self.root.ids.sc3.children[1].ids
        # composer_obj.ti.text = ''
        # composer_obj.btn.text = 'Select'
        # composer_obj.txt_input.text = ''
        # composer_obj.subject.text = ''
        # composer_obj.body.text = ''
        # state.in_composer = True
        # state.in_sent_method = False
        pass

    def set_navbar_for_composer(self):
        # """Clearing toolbar data when composer open"""
        # self.root.ids.toolbar.left_action_items = [
        #     ['arrow-left', lambda x: self.back_press()]]
        # self.root.ids.toolbar.right_action_items = [
        #     ['refresh',
        #      lambda x: self.root.ids.sc3.children[1].reset_composer()],
        #     ['send',
        #      lambda x: self.root.ids.sc3.children[1].send(self)]]
        pass
    def set_toolbar_for_QrCode(self):
        # """This method is use for setting Qr code toolbar."""
        # self.root.ids.toolbar.left_action_items = [
        #     ['arrow-left', lambda x: self.back_press()]]
        # self.root.ids.toolbar.right_action_items = []
        pass

    def set_common_header(self):
        # """Common header for all window"""
        # self.root.ids.toolbar.right_action_items = [
        #     ['account-plus', lambda x: self.addingtoaddressbook()]]
        # # self.root.ids.toolbar.left_action_items = [
        # #     ['menu', lambda x: self.root.toggle_nav_drawer()]]
        # self.root.ids.toolbar.left_action_items = [
        #     ['menu', lambda x: self.root.ids.nav_drawer.set_state("toggle")]]
        # return
        pass

    def back_press(self):
        # """Method for, reverting composer to previous page"""
        # if self.root.ids.scr_mngr.current == 'create':
        #     self.save_draft()
        # if self.root.ids.scr_mngr.current == \
        #         'mailDetail' and state.in_search_mode:
        #     toolbar_obj = self.root.ids.toolbar
        #     toolbar_obj.left_action_items = [
        #         ['arrow-left', lambda x: self.closeSearchScreen()]]
        #     toolbar_obj.right_action_items = []
        #     self.root.ids.toolbar.title = ''
        # else:
        #     self.set_common_header()
        #     if self.root.ids.scr_mngr.current == 'chroom' and state.association:
        #         self.root.ids.scr_mngr.transition = FallOutTransition()
        #         address_label = self.current_address_label(
        #             BMConfigParser().get(
        #                 state.association, 'label'), state.association)
        #         self.root.ids.toolbar.title = address_label
        # self.root.ids.scr_mngr.current = 'inbox' \
        #     if state.in_composer else 'allmails'\
        #     if state.is_allmail else state.detailPageType\
        #     if state.detailPageType else 'myaddress'\
        #     if self.root.ids.scr_mngr.current == 'showqrcode' else 'payment'\
        #     if self.root.ids.scr_mngr.current == 'pay-options' else 'chlist'\
        #     if self.root.ids.scr_mngr.current == 'chroom' else 'inbox'
        # if self.root.ids.scr_mngr.current == 'chlist':
        #     self.root.ids.scr_mngr.transition = SlideTransition()
        # self.root.ids.scr_mngr.transition.direction = 'right'
        # self.root.ids.scr_mngr.transition.bind(on_complete=self.reset)
        # if state.is_allmail or state.detailPageType == 'draft':
        #     state.is_allmail = False
        # state.detailPageType = ''
        # state.in_composer = False
        pass
    @staticmethod
    def get_inbox_count():
        # """Getting inbox count"""
        # state.inbox_count = str(sqlQuery(
        #     "SELECT COUNT(*) FROM inbox WHERE toaddress = '{}' and"
        #     " folder = 'inbox' ;".format(state.association))[0][0])
        pass
    @staticmethod
    def get_sent_count():
        # """Getting sent count"""
        # state.sent_count = str(sqlQuery(
        #     "SELECT COUNT(*) FROM sent WHERE fromaddress = '{}' and"
        #     " folder = 'sent' ;".format(state.association))[0][0])
        pass
    def set_message_count(self):
        """Setting message count"""
        # msg_counter_objs = state.kivyapp.root.children[0].children[0].ids
        # try:
        #     msg_counter_objs = (
        #         self.root_window.children[0].children[2].children[0].ids)
        # except Exception:
        #     msg_counter_objs = (
        #         self.root_window.children[2].children[2].children[0].ids)
        # self.get_inbox_count()
        # self.get_sent_count()
        # state.trash_count = str(sqlQuery(
        #     "SELECT (SELECT count(*) FROM  sent"
        #     " where fromaddress = '{0}' and  folder = 'trash' )"
        #     "+(SELECT count(*) FROM inbox where toaddress = '{0}' and"
        #     " folder = 'trash') AS SumCount".format(state.association))[0][0])
        # state.draft_count = str(sqlQuery(
        #     "SELECT COUNT(*) FROM sent WHERE fromaddress = '{}' and"
        #     " folder = 'draft' ;".format(state.association))[0][0])
        # state.all_count = str(int(state.sent_count) + int(state.inbox_count))
        # if msg_counter_objs:
        #     msg_counter_objs.send_cnt.badge_text = state.sent_count
        #     msg_counter_objs.inbox_cnt.badge_text = state.inbox_count
        #     msg_counter_objs.trash_cnt.badge_text = state.trash_count
        #     msg_counter_objs.draft_cnt.badge_text = state.draft_count
        #     msg_counter_objs.allmail_cnt.badge_text = state.all_count
        pass
    def on_start(self):
        # """Setting message count"""
        # self.set_message_count()
        pass

    # @staticmethod
    # def on_stop():
    #     """On stop methos is used for stoping the runing script"""
    #     print("*******************EXITING FROM APPLICATION*******************")
    #     import shutdown
    #     shutdown.doCleanShutdown()

    @staticmethod
    def current_address_label(current_add_label=None, current_addr=None):
        """Getting current address labels"""
        addresses = [addr for addr in BMConfigParser().addresses()
                        if BMConfigParser().get(str(addr), 'enabled') == 'true']
        if addresses:
            if current_add_label:
                first_name = current_add_label
                addr = current_addr
            else:
                addr = addresses[0]
                first_name = BMConfigParser().get(addr, 'label')
                if BMConfigParser().get(addr, 'enabled') != 'true':
                    return ''
            f_name = first_name.split()
            label = f_name[0][:14].capitalize() + '...' if len(
                f_name[0]) > 15 else f_name[0].capitalize()
            address = ' (' + addr + ')'
            return label + address
        return ''

    def searchQuery(self, instance):
        # """Showing searched mails"""
        # state.search_screen = self.root.ids.scr_mngr.current
        # state.searcing_text = str(instance.text).strip()
        # if instance.focus and state.searcing_text:
        #     toolbar_obj = self.root.ids.toolbar
        #     toolbar_obj.left_action_items = [
        #         ['arrow-left', lambda x: self.closeSearchScreen()]]
        #     toolbar_obj.right_action_items = []
        #     self.root.ids.toolbar.title = ''
        #     state.in_search_mode = True
        pass

    def closeSearchScreen(self):
        """Function for close search screen"""
        # self.set_common_header()
        # if state.association:
        #     address_label = self.current_address_label(
        #         BMConfigParser().get(
        #             state.association, 'label'), state.association)
        #     self.root.ids.toolbar.title = address_label
        # state.searcing_text = ''
        # self.refreshScreen()
        # state.in_search_mode = False
        pass

    def refreshScreen(self):
        # """Method show search button only on inbox or sent screen"""
        # # pylint: disable=unused-variable
        # state.searcing_text = ''
        # if state.search_screen == 'inbox':
        #     self.root.ids.sc1.ids.inbox_search.ids.search_field.text = ''
        #     # try:
        #     #     self.root.ids.sc1.children[
        #     #         3].children[2].ids.search_field.text = ''
        #     # except Exception:
        #     #     self.root.ids.sc1.children[
        #     #         2].children[2].ids.search_field.text = ''
        #     self.root.ids.sc1.children[1].active = True
        #     Clock.schedule_once(self.search_callback, 0.5)
        # elif state.search_screen == 'addressbook':
        #     self.root.ids.sc11.ids.address_search.ids.search_field.text = ''
        #     # self.root.ids.sc11.children[
        #     #     2].children[2].ids.search_field.text = ''
        #     self.root.ids.sc11.children[
        #         1].active = True
        #     Clock.schedule_once(self.search_callback, 0.5)
        # elif state.search_screen == 'myaddress':
        #     self.root.ids.sc10.ids.search_bar.ids.search_field.text = ''
        #     # try:
        #     #     self.root.ids.sc10.children[
        #     #         1].children[2].ids.search_field.text = ''
        #     # except Exception:
        #     #     self.root.ids.sc10.children[
        #     #         2].children[2].ids.search_field.text = ''
        #     self.loadMyAddressScreen(True)
        #     Clock.schedule_once(self.search_callback, 0.5)
        # else:
        #     self.root.ids.sc4.ids.sent_search.ids.search_field.text = ''
        #     # self.root.ids.sc4.children[
        #     #     2].children[2].ids.search_field.text = ''
        #     self.root.ids.sc4.children[1].active = True
        #     Clock.schedule_once(self.search_callback, 0.5)
        # return
        pass

    def set_identicon(self, text):
        # """Show identicon in address spinner"""
        # img = identiconGeneration.generate(text)
        # # self.root.children[0].children[0].ids.btn.children[1].texture = (img.texture)
        # # below line is for displaing logo
        # self.root.ids.content_drawer.ids.top_box.children[0].texture = (img.texture)
        pass
    def set_mail_detail_header(self):
        # """Setting the details of the page"""
        # if state.association and state.in_search_mode:
        #     address_label = self.current_address_label(
        #         BMConfigParser().get(
        #             state.association, 'label'), state.association)
        #     self.root.ids.toolbar.title = address_label
        # toolbar_obj = self.root.ids.toolbar
        # toolbar_obj.left_action_items = [
        #     ['arrow-left', lambda x: self.back_press()]]
        # delete_btn = ['delete-forever',
        #               lambda x: self.root.ids.sc14.delete_mail()]
        # dynamic_list = []
        # if state.detailPageType == 'inbox':
        #     dynamic_list = [
        #         ['reply', lambda x: self.root.ids.sc14.inbox_reply()],
        #         delete_btn]
        # elif state.detailPageType == 'sent':
        #     dynamic_list = [delete_btn]
        # elif state.detailPageType == 'draft':
        #     dynamic_list = [
        #         ['pencil', lambda x: self.root.ids.sc14.write_msg(self)],
        #         delete_btn]
        # toolbar_obj.right_action_items = dynamic_list
        pass 
    def load_screen(self, instance):
        # """This method is used for loading screen on every click"""
        # if instance.text == 'Inbox':
        #     self.root.ids.scr_mngr.current = 'inbox'
        #     self.root.ids.sc1.children[1].active = True
        # elif instance.text == 'All Mails':
        #     self.root.ids.scr_mngr.current = 'allmails'
        #     try:
        #         self.root.ids.sc17.children[1].active = True
        #     except Exception:
        #         self.root.ids.sc17.children[0].children[1].active = True
        # elif instance.text == 'Trash':
        #     self.root.ids.scr_mngr.current = 'trash'
        #     try:
        #         self.root.ids.sc5.children[1].active = True
        #     except Exception as e:
        #         self.root.ids.sc5.children[0].children[1].active = True
        # Clock.schedule_once(partial(self.load_screen_callback, instance), 1)
        pass

    def load_screen_callback(self, instance, dt=0):
        # """This method is rotating loader for few seconds"""
        # if instance.text == 'Inbox':
        #     self.root.ids.sc1.ids.ml.clear_widgets()
        #     self.root.ids.sc1.loadMessagelist(state.association)
        #     self.root.ids.sc1.children[1].active = False
        # elif instance.text == 'All Mails':
        #     self.root.ids.sc17.clear_widgets()
        #     self.root.ids.sc17.add_widget(Allmails())
        #     try:
        #         self.root.ids.sc17.children[1].active = False
        #     except Exception:
        #         self.root.ids.sc17.children[0].children[1].active = False
        # elif instance.text == 'Trash':
        #     # self.root.ids.sc5.ids.ml.clear_widgets()
        #     # self.root.ids.sc5.init_ui(0)
        #     self.root.ids.sc5.clear_widgets()
        #     self.root.ids.sc5.add_widget(Trash())
        #     try:
        #         self.root.ids.sc5.children[1].active = False
        #     except Exception as e:
        #         self.root.ids.sc5.children[0].children[1].active = False
        pass
    def on_request_close(self, *args):  # pylint: disable=no-self-use
        """This method is for app closing request"""
        AppClosingPopup().open()
        return True

    def file_manager_open(self):
        # """This method open the file manager of local system"""
        # from kivymd.uix.filemanager import MDFileManager

        # if not self.file_manager:
        #     self.file_manager = MDFileManager(
        #         exit_manager=self.exit_manager,
        #         select_path=self.select_path,
        #         ext=['.png', '.jpg']
        #     )
        # self.file_manager.previous = False
        # self.file_manager.current_path = '/'
        # if platform == 'android':
        #     from android.permissions import request_permissions, Permission, check_permission
        #     if check_permission(Permission.WRITE_EXTERNAL_STORAGE) and \
        #             check_permission(Permission.READ_EXTERNAL_STORAGE):
        #         self.file_manager.show(os.getenv('EXTERNAL_STORAGE'))
        #         self.manager_open = True
        #     else:
        #         request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])
        # else:
        #     self.file_manager.show(os.environ["HOME"])
        #     self.manager_open = True
        pass

    def select_path(self, path):
        """This method is used to save the select image"""
        # try:
        #     from PIL import Image as PilImage
        #     newImg = PilImage.open(path).resize((300, 300))
        #     if platform == 'android':
        #         android_path = os.path.join(
        #             os.environ['ANDROID_PRIVATE'] + '/app' + '/images' + '/kivy/')
        #         if not os.path.exists(android_path + '/default_identicon/'):
        #             os.makedirs(android_path + '/default_identicon/')
        #         newImg.save('{1}/default_identicon/{0}.png'.format(
        #             state.association, android_path))
        #     else:
        #         if not os.path.exists(state.imageDir + '/default_identicon/'):
        #             os.makedirs(state.imageDir + '/default_identicon/')
        #         newImg.save(state.imageDir + '/default_identicon/{0}.png'.format(state.association))
        #     self.load_selected_Image(state.association)
        #     toast('Image changed')
        # except Exception:
        #     toast('Exit')
        # self.exit_manager()
        pass


    def exit_manager(self, *args):
        """Called when the user reaches the root of the directory tree."""
        self.manager_open = False
        self.file_manager.close()

    def load_selected_Image(self, curerentAddr):
        # """This method load the selected image on screen"""
        # top_box_obj = self.root.ids.content_drawer.ids.top_box.children[0]
        # # spinner_img_obj = self.root.ids.content_drawer.ids.btn.children[1]
        # # spinner_img_obj.source = top_box_obj.source ='./images/default_identicon/{0}.png'.format(curerentAddr)
        # top_box_obj.source = state.imageDir + '/default_identicon/{0}.png'.format(curerentAddr)
        # self.root.ids.content_drawer.ids.reset_image.opacity = 1
        # self.root.ids.content_drawer.ids.reset_image.disabled = False
        # top_box_obj.reload()
        pass
        # spinner_img_obj.reload()

    def rest_default_avatar_img(self):
        # """set default avatar generated image"""
        # self.set_identicon(state.association)
        # img_path = state.imageDir + '/default_identicon/{}.png'.format(state.association)
        # try:
        #     if os.path.exists(img_path):
        #         os.remove(img_path)
        #         self.root.ids.content_drawer.ids.reset_image.opacity = 0
        #         self.root.ids.content_drawer.ids.reset_image.disabled = True
        # except Exception as e:
        #     pass
        # toast('Avatar reset')
        pass

    def copy_composer_text(self, text):  # pylint: disable=no-self-use
        # """Copy the data from mail detail page"""
        # Clipboard.copy(text)
        # toast('Copied')
        pass 

    def reset_login_screen(self):
        """This method is used for clearing random screen"""
        # if self.root.ids.sc7.ids.add_random_bx.children:
        #     self.root.ids.sc7.ids.add_random_bx.clear_widgets()
        pass

    def open_payment_layout(self, sku):
        """It basically open up a payment layout for kivy Ui"""
        # pml = PaymentMethodLayout()
        # self.product_id = sku
        # self.custom_sheet = MDCustomBottomSheet(screen=pml)
        # self.custom_sheet.open()
        pass
    def initiate_purchase(self, method_name):
        """initiate_purchase module"""
        # print("Purchasing {} through {}".format(self.product_id, method_name))
        pass
    def _after_scan(self, text):
        # if platform == 'android':
        #     toast_txt = cast(CharSequence, String(text))
        #     show_toast(toast_txt, Toast.LENGTH_SHORT)
        # if self.root.ids.sc23.previous_open_screen == 'composer':
        #     self.root.ids.sc3.children[1].ids.txt_input.text = text
        #     self.root.ids.scr_mngr.current = 'create'
        # elif self.root.ids.sc23.previous_open_screen:
        #     back_screen = self.root.ids.sc23.previous_open_screen
        #     self.root.ids.scr_mngr.current = 'inbox' if back_screen == 'scanscreen' else back_screen
        #     add_obj = self.root.ids.sc23.pop_up_instance
        #     add_obj.content_cls.ids.address.text = text
        #     Clock.schedule_once(partial(self.open_popup, add_obj), .5)
        pass
    @staticmethod
    def open_popup(instance, dt):
        """This method is used for opening popup"""
        instance.open()


class PaymentMethodLayout(BoxLayout):
    """PaymentMethodLayout class for kivy Ui"""
