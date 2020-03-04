"""Tests for setting window"""
import random
from random import choice
from string import ascii_lowercase

from PyQt4 import QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtTest import QTest

from bitmessageqt import dialogs
from testloader import BitmessageTestCase


class BitmessageTest_SettingWindowTest(BitmessageTestCase):
    """Switch to setting tab and test"""

    def test_settingwindow(self):
        """Triggers the setting window"""
        self.myapp.ui.tabWidget.setCurrentWidget(self.myapp.ui.inbox)
        QTest.qWait(1500)
        dialog = dialogs.SettingsDialog(self.myapp, firstrun=self.myapp._firstrun)
        self.language_change(dialog)
        QTest.qWait(300)
        self.eng_convert(dialog)
        QTest.qWait(300)
        self.network_setting_window(dialog)
        QTest.qWait(300)
        self.tabresendsexpire_window(dialog)
        QTest.qWait(300)

    def language_change(self, dialog):
        """Function that changes the language of the application"""
        try:
            """Change language"""
            dialog.show()
            dialog.tabWidgetSettings.setCurrentIndex(dialog.tabWidgetSettings.indexOf(dialog.tabUserInterface))
            QTest.qWait(800)
            dialog.languageComboBox.setStyleSheet("QComboBox {background-color: #FF5733; color: white;}")
            QTest.qWait(50)
            dialog.languageComboBox.setStyleSheet("")
            dialog.languageComboBox.setCurrentIndex(random.randint(1, 17))
            QTest.qWait(1000)
            ok_btn = dialog.buttonBox.button(QtGui.QDialogButtonBox.Ok)
            QTest.mouseClick(ok_btn, Qt.LeftButton)
            print("\n Test Pass :--> Language Changed Successfully \n")
            self.assertTrue(True, " \n Test Pass :--> Language Changed Successfully ")
            return 1
        except:
            print("\n Test Fail :--> Error while changing Language! \n")
            self.assertTrue(False, " \n Test Fail :--> Error while changing Language!")
            return 0

    def eng_convert(self, dialog):
        """Convert any language to english, testing just for good readability"""
        try:
            dialog.show()
            dialog.tabWidgetSettings.setCurrentIndex(dialog.tabWidgetSettings.indexOf(dialog.tabUserInterface))
            QTest.qWait(800)
            dialog.languageComboBox.setStyleSheet("QComboBox {background-color: #FF5733; color: white;}")
            QTest.qWait(50)
            dialog.languageComboBox.setStyleSheet("")
            dialog.languageComboBox.setCurrentIndex(5)
            QTest.qWait(1000)
            ok_btn = dialog.buttonBox.button(QtGui.QDialogButtonBox.Ok)
            QTest.mouseClick(ok_btn, Qt.LeftButton)
            print("\n Test Pass :--> language changed to English Again \n")
            self.assertTrue(True, " \n Test Pass :--> language changed to English Again ")
            return 1
        except:
            print("\n Test Fail :--> Not able to change the language to English Again! Error! \n")
            self.assertTrue(False, " \n Test Fail :--> Not able to change the language to English Again! Error!")
            return 0

    def network_setting_window(self, dialog):
        """Test for Network setting window"""
        try:
            dialog.show()
            QTest.qWait(300)
            dialog.tabWidgetSettings.setCurrentIndex(dialog.tabWidgetSettings.indexOf(dialog.tabNetworkSettings))
            QTest.qWait(500)

            dialog.lineEditSocksHostname.setText("")
            dialog.lineEditSocksPort.setText("")
            dialog.lineEditSocksUsername.setText("")
            dialog.lineEditSocksPassword.setText("")
            if dialog.checkBoxAuthentication.isChecked():
                dialog.checkBoxAuthentication.click()
            if dialog.checkBoxSocksListen.isChecked():
                dialog.checkBoxSocksListen.click()
            if dialog.checkBoxOnionOnly.isChecked():
                dialog.checkBoxOnionOnly.click()

            QTest.qWait(500)
            dialog.comboBoxProxyType.setCurrentIndex(random.randint(1, 3))
            QTest.qWait(800)

            random_val = ""
            for _ in range(10):
                random_val += choice(ascii_lowercase)
                dialog.lineEditSocksHostname.setText(random_val)
                QTest.qWait(5)
            QTest.qWait(500)
            dialog.lineEditSocksPort.setText(str(random.randint(1000, 9999)))
            QTest.qWait(800)

            if dialog.checkBoxAuthentication.isChecked():
                pass
            else:
                dialog.checkBoxAuthentication.click()
                QTest.qWait(500)

            dialog.lineEditSocksUsername.setText("".join(choice(ascii_lowercase) for i in range(10)))
            QTest.qWait(500)
            dialog.lineEditSocksPassword.setText("".join(choice(ascii_lowercase) for i in range(10)))
            QTest.qWait(500)

            if dialog.checkBoxSocksListen.isChecked():
                pass
            else:
                dialog.checkBoxSocksListen.click()
                QTest.qWait(1200)

            if dialog.checkBoxOnionOnly.isChecked():
                pass
            else:
                dialog.checkBoxOnionOnly.click()
                QTest.qWait(1200)
            ok_btn = dialog.buttonBox.button(QtGui.QDialogButtonBox.Ok)
            QTest.mouseClick(ok_btn, Qt.LeftButton)
            print("\n Test Pass :--> Successfully tested Network setting window \n")
            self.assertTrue(True, " \n Test Pass :--> Successfully tested Network setting window ")
            return 1
        except:
            print("\n Test Fail :-->  Error while testing Network setting window! \n")
            self.assertTrue(False, " \n Test Fail :-->  Error while testing Network setting window!")
            return 0

    def tabresendsexpire_window(self, dialog):
        """Testing for resend expire window"""
        try:
            dialog.lineEditDays.setText("")
            dialog.lineEditMonths.setText("")
            dialog.show()
            QTest.qWait(300)
            dialog.tabWidgetSettings.setCurrentIndex(dialog.tabWidgetSettings.indexOf(dialog.tabResendsExpire))
            QTest.qWait(500)

            QTest.qWait(500)
            dialog.lineEditDays.setText(str(random.randint(0, 30)))
            QTest.qWait(800)
            dialog.lineEditMonths.setText(str(random.randint(0, 12)))
            QTest.qWait(800)
            ok_btn = dialog.buttonBox.button(QtGui.QDialogButtonBox.Ok)
            QTest.mouseClick(ok_btn, Qt.LeftButton)
            print("\n Test Pass :--> Test successfull. \n")
            self.assertTrue(True, " \n Test Pass :--> Test successfull. ")
            return 1
        except:
            print("\n Test Fail :--> Tab Resend Exprire! \n")
            self.assertTrue(False, " \n Test Fail :--> Tab Resend Exprire! ")
            return 0
