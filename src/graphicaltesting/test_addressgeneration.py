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
        QTest.qWait(500)
        self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.inbox)
        QTest.qWait(500)
        try:
            random_label = ""
            self.myapp.ui.pushButtonNewAddress.setStyleSheet("QPushButton {background-color: #FF5733; color: white;}")
            QTest.qWait(50)
            self.myapp.ui.pushButtonNewAddress.setStyleSheet("")
            label_gen_obj = address_dialogs.NewAddressDialog()
            QTest.qWait(500)
            address_count = len(BMConfigParser().addresses())
            QTest.qWait(400)
            for _ in range(12):
                random_label = random_label + choice(ascii_lowercase)
                label_gen_obj.newaddresslabel.setText(random_label)
                QTest.qWait(5)
            QTest.qWait(500)
            label_gen_obj.accept()
            QTest.qWait(800)
            self.assertEqual(len(BMConfigParser().addresses()), address_count + 1)
            self.assertEqual(str(BMConfigParser().get(BMConfigParser().addresses()[-1], "label")), random_label)
            print("\n Test Pass :--> Address Generated Successfully \n")
            self.assertTrue(True, " \n Test Pass :-->  Address Generated Successfully")
            return 1  # if every thing is ok
        except:
            print("\n Test Fail :-->  Address Generatation Failed or Taking too much time to generate address \n")
            self.assertTrue(False, " \n Test Fail :-->  Address Generation Failed!")
            return 0  # if test fail

    def test_generateaddresswithpassphrase(self):
        """Clicks on the create new label with passphrase pushbutton and generates 8 address"""
        QTest.qWait(500)
        self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.inbox)
        QTest.qWait(500)
        try:
            random_password1, random_password2 = "", ""
            self.myapp.ui.pushButtonNewAddress.setStyleSheet("QPushButton {background-color: #FF5733; color: white;}")
            QTest.qWait(50)
            self.myapp.ui.pushButtonNewAddress.setStyleSheet("")
            label_gen_obj = address_dialogs.NewAddressDialog()
            QTest.qWait(500)
            address_count = len(BMConfigParser().addresses())
            QTest.qWait(400)
            label_gen_obj.radioButtonDeterministicAddress.click()
            QTest.qWait(400)
            for i in range(15):
                random_password1 += choice(ascii_lowercase)
                label_gen_obj.lineEditPassphrase.setText(random_password1)
                QTest.qWait(5)
            QTest.qWait(500)
            for i in random_password1:
                random_password2 += i
                label_gen_obj.lineEditPassphraseAgain.setText(random_password2)
                QTest.qWait(5)
            QTest.qWait(800)
            label_gen_obj.accept()
            self.assertEqual(random_password1, random_password2)
            print(" Creating Address ......")
            QTest.qWait(3000)
            print(" Please Wait.! Creating 8 Address ......")
            QTest.qWait(3000)
            self.assertEqual(len(BMConfigParser().addresses()), address_count + 8)
            QTest.qWait(100)
            print("\n Test Pass :--> Address Generated Successfully with passphrase \n")
            self.assertTrue(True, " \n Test Pass :-->  Address Generated Successfully with passphrase")
            return 1
        except:
            QTest.qWait(100)
            print(
                "\n Test Fail :-->  Address Generatation Failed with passphrase"
                " or Taking too much time to generate address \n")
            self.assertTrue(False, " \n Test Fail :-->  Address Generatation Failed with passphrase")
            return 0
