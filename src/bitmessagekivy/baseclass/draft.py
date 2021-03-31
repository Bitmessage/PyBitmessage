import time

from bitmessagekivy import kivy_helper_search
from bmconfigparser import BMConfigParser
from helper_sql import sqlExecute
from functools import partial
from addresses import decodeAddress
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import (
    ListProperty,
    StringProperty
)
from kivy.uix.button import Button
from kivy.uix.carousel import Carousel
from kivy.uix.screenmanager import Screen
from kivymd.uix.label import MDLabel
from kivymd.uix.list import TwoLineAvatarIconListItem

import state

from bitmessagekivy.baseclass.common import (
    showLimitedCnt, toast, ThemeClsColor,
    AddTimeWidget, AvatarSampleWidget
)
from bitmessagekivy.baseclass.maildetail import MailDetail


class Draft(Screen):
    """Draft screen class for kivy Ui"""

    data = ListProperty()
    account = StringProperty()
    queryreturn = ListProperty()
    has_refreshed = True

    def __init__(self, *args, **kwargs):
        """Method used for storing draft messages"""
        super(Draft, self).__init__(*args, **kwargs)
        if state.association == '':
            if BMConfigParser().addresses():
                state.association = BMConfigParser().addresses()[0]
        Clock.schedule_once(self.init_ui, 0)

    def init_ui(self, dt=0):
        """Clock Schdule for method draft accounts"""
        self.sentaccounts()
        print(dt)

    def sentaccounts(self):
        """Load draft accounts"""
        # self.account = state.association
        self.loadDraft()

    def loadDraft(self, where="", what=""):
        """Load draft list for Draft messages"""
        self.account = state.association
        xAddress = 'fromaddress'
        self.ids.tag_label.text = ''
        self.draftDataQuery(xAddress, where, what)
        # if state.msg_counter_objs:
        #     state.msg_counter_objs.draft_cnt.children[0].children[0].text = showLimitedCnt(len(self.queryreturn))
        if self.queryreturn:
            self.ids.tag_label.text = 'Draft'
            self.set_draftCnt(state.draft_count)
            self.set_mdList()
            self.ids.scroll_y.bind(scroll_y=self.check_scroll_y)
        else:
            self.set_draftCnt('0')
            content = MDLabel(
                font_style='Caption',
                theme_text_color='Primary',
                text="yet no message for this account!!!!!!!!!!!!!",
                halign='center',
                size_hint_y=None,
                valign='top')
            self.ids.ml.add_widget(content)

    def draftDataQuery(self, xAddress, where, what, start_indx=0, end_indx=20):
        """This methosd is for retrieving draft messages"""
        self.queryreturn = kivy_helper_search.search_sql(
            xAddress, self.account, "draft", where, what,
            False, start_indx, end_indx)

    def set_draftCnt(self, Count):  # pylint: disable=no-self-use
        """This method set the count of draft mails"""
        draftCnt_obj = state.kivyapp.root.ids.content_drawer.ids.draft_cnt
        draftCnt_obj.ids.badge_txt.text = showLimitedCnt(int(Count))

    def set_mdList(self):
        """This method is used to create mdlist"""
        data = []
        total_draft_msg = len(self.ids.ml.children)
        for mail in self.queryreturn:
            third_text = mail[3].replace('\n', ' ')
            data.append({
                'text': mail[1].strip(),
                'secondary_text': mail[2][:10] + '...........' if len(
                    mail[2]) > 10 else mail[2] + '\n' + " " + (
                        third_text[:25] + '...!') if len(
                            third_text) > 25 else third_text,
                'ackdata': mail[5], 'senttime': mail[6]})
        for item in data:
            meny = TwoLineAvatarIconListItem(
                text='Draft', secondary_text=item['text'],
                theme_text_color='Custom',
                text_color=ThemeClsColor)
            meny._txt_right_pad = dp(70)
            meny.add_widget(AvatarSampleWidget(
                source=state.imageDir + '/avatar.png'))
            meny.bind(on_press=partial(
                self.draft_detail, item['ackdata']))
            meny.add_widget(AddTimeWidget(item['senttime']))
            carousel = Carousel(direction='right')
            carousel.height = meny.height
            carousel.size_hint_y = None
            carousel.ignore_perpendicular_swipes = True
            carousel.data_index = 0
            carousel.min_move = 0.2
            del_btn = Button(text='Delete')
            del_btn.background_normal = ''
            del_btn.background_color = (1, 0, 0, 1)
            del_btn.bind(on_press=partial(self.delete_draft, item['ackdata']))
            carousel.add_widget(del_btn)
            carousel.add_widget(meny)
            carousel.index = 1
            self.ids.ml.add_widget(carousel)
        updated_msg = len(self.ids.ml.children)
        self.has_refreshed = True if total_draft_msg != updated_msg else False

    def check_scroll_y(self, instance, somethingelse):
        """Load data on scroll"""
        if self.ids.scroll_y.scroll_y <= -0.0 and self.has_refreshed:
            self.ids.scroll_y.scroll_y = 0.06
            total_draft_msg = len(self.ids.ml.children)
            self.update_draft_screen_on_scroll(total_draft_msg)

    def update_draft_screen_on_scroll(self, total_draft_msg, where='', what=''):
        """Load more data on scroll down"""
        self.draftDataQuery('fromaddress', where, what, total_draft_msg, 5)
        self.set_mdList()

    def draft_detail(self, ackdata, *args):
        """Show draft Details"""
        state.detailPageType = 'draft'
        state.mail_id = ackdata
        if self.manager:
            src_mng_obj = self.manager
        else:
            src_mng_obj = self.parent.parent
        src_mng_obj.screens[11].clear_widgets()
        src_mng_obj.screens[11].add_widget(MailDetail())
        src_mng_obj.current = 'mailDetail'

    def delete_draft(self, data_index, instance, *args):
        """Delete draft message permanently"""
        sqlExecute("DELETE FROM sent WHERE ackdata = ?;", data_index)
        if int(state.draft_count) > 0:
            state.draft_count = str(int(state.draft_count) - 1)
            self.set_draftCnt(state.draft_count)
            if int(state.draft_count) <= 0:
                # self.ids.identi_tag.children[0].text = ''
                self.ids.tag_label.text = ''
        self.ids.ml.remove_widget(instance.parent.parent)
        toast('Deleted')

    @staticmethod
    def draft_msg(src_object):
        """Save draft mails"""
        composer_object = state.kivyapp.root.ids.sc3.children[1].ids
        fromAddress = str(composer_object.ti.text)
        toAddress = str(composer_object.txt_input.text)
        subject = str(composer_object.subject.text)
        message = str(composer_object.body.text)
        encoding = 3
        sendMessageToPeople = True
        if sendMessageToPeople:
            streamNumber, ripe = decodeAddress(toAddress)[2:]
            from addresses import addBMIfNotPresent
            toAddress = addBMIfNotPresent(toAddress)
            stealthLevel = BMConfigParser().safeGetInt(
                'bitmessagesettings', 'ackstealthlevel')
            from helper_ackPayload import genAckPayload
            ackdata = genAckPayload(streamNumber, stealthLevel)
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
                BMConfigParser().safeGetInt('bitmessagesettings', 'ttl'))
            state.msg_counter_objs = src_object.children[2].children[0].ids
            state.draft_count = str(int(state.draft_count) + 1) \
                if state.association == fromAddress else state.draft_count
            src_object.ids.sc16.clear_widgets()
            src_object.ids.sc16.add_widget(Draft())
            toast('Save draft')
        return
