"""Generate Address for tests"""
from random import choice
from string import ascii_lowercase

from PyQt4.QtTest import QTest

from bitmessageqt import address_dialogs
from bmconfigparser import BMConfigParser
from testloader import BitmessageTestCase


class BitmessageTest_AddressGeneration(BitmessageTestCase):
    """Testing Environment"""

    def test_generateaddress(self):
        """Method clicks on new label pushbutton and create new address with random label"""
        print("=====================Test - Generating Address=====================")
        try:
            QTest.qWait(500)
            bm_addresses = BMConfigParser().addresses()
            self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.inbox)
            QTest.qWait(500)
            self.myapp.ui.pushButtonNewAddress.setStyleSheet("QPushButton {background-color: #FF5733; color: white;}")
            QTest.qWait(50)
            self.myapp.ui.pushButtonNewAddress.setStyleSheet("")
            label_gen_obj = address_dialogs.NewAddressDialog()
            QTest.qWait(750)
            random_label = ""
            for _ in range(15):
                random_label += choice(ascii_lowercase)
                label_gen_obj.newaddresslabel.setText(random_label)
                QTest.qWait(4)
            QTest.qWait(500)
            label_gen_obj.accept()
            QTest.qWait(750)
            new_bm_addresses = BMConfigParser().addresses()
            self.assertEqual(len(new_bm_addresses), len(bm_addresses) + 1)
            self.assertEqual(str(BMConfigParser().get(new_bm_addresses[-1], "label")), random_label)
            print("Test Pass:--> Address Generated Successfully")
            return 1  # if every thing is ok
        except:
            print("Test Fail:-->  Address Generatation Failed or Taking too much time to generate address")
            return 0  # if test fail

    def test_generateaddresswithpassphrase(self):
        """Clicks on the create new label with passphrase pushbutton and generates 8 address"""
        print("=====================Test - Generating Address with passphrase=====================")
        try:
            QTest.qWait(500)
            bm_addresses = BMConfigParser().addresses()
            self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.inbox)
            QTest.qWait(500)
            self.myapp.ui.pushButtonNewAddress.setStyleSheet("QPushButton {background-color: #FF5733; color: white;}")
            QTest.qWait(50)
            self.myapp.ui.pushButtonNewAddress.setStyleSheet("")
            label_gen_obj = address_dialogs.NewAddressDialog()
            QTest.qWait(750)
            label_gen_obj.radioButtonDeterministicAddress.click()
            QTest.qWait(250)
            random_password1 = ""
            for _ in range(15):
                random_password1 += choice(ascii_lowercase)
                label_gen_obj.lineEditPassphrase.setText(random_password1)
                QTest.qWait(4)
            QTest.qWait(500)
            random_password2 = ""
            for i in random_password1:
                random_password2 += i
                label_gen_obj.lineEditPassphraseAgain.setText(random_password2)
                QTest.qWait(2)
            QTest.qWait(500)
            label_gen_obj.accept()
            QTest.qWait(750)
            self.assertEqual(random_password1, random_password2)
            print(" Creating 8 Addresses. Please Wait! ......")
            QTest.qWait(2500)
            print(" Generating ......... ")
            QTest.qWait(2500)
            self.assertEqual(len(BMConfigParser().addresses()), len(bm_addresses) + 8)
            print("Test Pass:--> Address Generated Successfully with passphrase")
            return 1
        except:
            print(
                "Test Fail:-->  Address Generatation Failed"
                " with passphrase or Taking too much time to generate address"
            )
            return 0
