"""
This module setting file is for settings
"""
import ConfigParser
import os
import sys
import tempfile

from PyQt4 import QtCore, QtGui

import debug
import defaults
import namecoin
import openclpow
import paths
import queues
import state
import widgets
from bmconfigparser import config as config_obj
from helper_sql import sqlExecute, sqlStoredProcedure
from helper_startup import start_proxyconfig
from network import knownnodes, AnnounceThread
from network.asyncore_pollchoose import set_rates
from tr import _translate


def getSOCKSProxyType(config):
    """Get user socksproxytype setting from *config*"""
    try:
        result = ConfigParser.SafeConfigParser.get(
            config, 'bitmessagesettings', 'socksproxytype')
    except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        return None
    else:
        if result.lower() in ('', 'none', 'false'):
            result = None
    return result


class SettingsDialog(QtGui.QDialog):
    """The "Settings" dialog"""
    def __init__(self, parent=None, firstrun=False):
        super(SettingsDialog, self).__init__(parent)
        widgets.load('settings.ui', self)

        self.parent = parent
        self.firstrun = firstrun
        self.config = config_obj
        self.net_restart_needed = False
        self.timer = QtCore.QTimer()

        if self.config.safeGetBoolean('bitmessagesettings', 'dontconnect'):
            self.firstrun = False
        try:
            import pkg_resources
        except ImportError:
            pass
        else:
            # Append proxy types defined in plugins
            # FIXME: this should be a function in mod:`plugin`
            for ep in pkg_resources.iter_entry_points(
                    'bitmessage.proxyconfig'):
                try:
                    ep.load()
                except Exception:  # it should add only functional plugins
                    # many possible exceptions, which are don't matter
                    pass
                else:
                    self.comboBoxProxyType.addItem(ep.name)

        self.lineEditMaxOutboundConnections.setValidator(
            QtGui.QIntValidator(0, 8, self.lineEditMaxOutboundConnections))

        self.adjust_from_config(self.config)
        if firstrun:
            # switch to "Network Settings" tab if user selected
            # "Let me configure special network settings first" on first run
            self.tabWidgetSettings.setCurrentIndex(
                self.tabWidgetSettings.indexOf(self.tabNetworkSettings)
            )
        QtGui.QWidget.resize(self, QtGui.QWidget.sizeHint(self))

    def adjust_from_config(self, config):
        """Adjust all widgets state according to config settings"""
        # pylint: disable=too-many-branches,too-many-statements
        if not self.parent.tray.isSystemTrayAvailable():
            self.groupBoxTray.setEnabled(False)
            self.groupBoxTray.setTitle(_translate(
                "MainWindow", "Tray (not available in your system)"))
            for setting in (
                    'minimizetotray', 'trayonclose', 'startintray'):
                config.set('bitmessagesettings', setting, 'false')
        else:
            self.checkBoxMinimizeToTray.setChecked(
                config.getboolean('bitmessagesettings', 'minimizetotray'))
            self.checkBoxTrayOnClose.setChecked(
                config.safeGetBoolean('bitmessagesettings', 'trayonclose'))
            self.checkBoxStartInTray.setChecked(
                config.getboolean('bitmessagesettings', 'startintray'))

        self.checkBoxHideTrayConnectionNotifications.setChecked(
            config.getboolean(
                'bitmessagesettings', 'hidetrayconnectionnotifications'))
        self.checkBoxShowTrayNotifications.setChecked(
            config.getboolean('bitmessagesettings', 'showtraynotifications'))

        self.checkBoxStartOnLogon.setChecked(
            config.getboolean('bitmessagesettings', 'startonlogon'))

        self.checkBoxWillinglySendToMobile.setChecked(
            config.safeGetBoolean(
                'bitmessagesettings', 'willinglysendtomobile'))
        self.checkBoxUseIdenticons.setChecked(
            config.safeGetBoolean('bitmessagesettings', 'useidenticons'))
        self.checkBoxReplyBelow.setChecked(
            config.safeGetBoolean('bitmessagesettings', 'replybelow'))

        if state.appdata == paths.lookupExeFolder():
            self.checkBoxPortableMode.setChecked(True)
        else:
            try:
                tempfile.NamedTemporaryFile(
                    dir=paths.lookupExeFolder(), delete=True
                ).close()  # should autodelete
            except Exception:
                self.checkBoxPortableMode.setDisabled(True)

        if 'darwin' in sys.platform:
            self.checkBoxMinimizeToTray.setDisabled(True)
            self.checkBoxMinimizeToTray.setText(_translate(
                "MainWindow",
                "Minimize-to-tray not yet supported on your OS."))
            self.checkBoxShowTrayNotifications.setDisabled(True)
            self.checkBoxShowTrayNotifications.setText(_translate(
                "MainWindow",
                "Tray notifications not yet supported on your OS."))

        if 'win' not in sys.platform and not self.parent.desktop:
            self.checkBoxStartOnLogon.setDisabled(True)
            self.checkBoxStartOnLogon.setText(_translate(
                "MainWindow", "Start-on-login not yet supported on your OS."))

        # On the Network settings tab:
        self.lineEditTCPPort.setText(str(
            config.get('bitmessagesettings', 'port')))
        self.checkBoxUPnP.setChecked(
            config.safeGetBoolean('bitmessagesettings', 'upnp'))
        self.checkBoxUDP.setChecked(
            config.safeGetBoolean('bitmessagesettings', 'udp'))
        self.checkBoxAuthentication.setChecked(
            config.getboolean('bitmessagesettings', 'socksauthentication'))
        self.checkBoxSocksListen.setChecked(
            config.getboolean('bitmessagesettings', 'sockslisten'))
        self.checkBoxOnionOnly.setChecked(
            config.safeGetBoolean('bitmessagesettings', 'onionservicesonly'))

        self._proxy_type = getSOCKSProxyType(config)
        self.comboBoxProxyType.setCurrentIndex(
            0 if not self._proxy_type
            else self.comboBoxProxyType.findText(self._proxy_type))
        self.comboBoxProxyTypeChanged(self.comboBoxProxyType.currentIndex())

        self.lineEditSocksHostname.setText(
            config.get('bitmessagesettings', 'sockshostname'))
        self.lineEditSocksPort.setText(str(
            config.get('bitmessagesettings', 'socksport')))
        self.lineEditSocksUsername.setText(
            config.get('bitmessagesettings', 'socksusername'))
        self.lineEditSocksPassword.setText(
            config.get('bitmessagesettings', 'sockspassword'))

        self.lineEditMaxDownloadRate.setText(str(
            config.get('bitmessagesettings', 'maxdownloadrate')))
        self.lineEditMaxUploadRate.setText(str(
            config.get('bitmessagesettings', 'maxuploadrate')))
        self.lineEditMaxOutboundConnections.setText(str(
            config.get('bitmessagesettings', 'maxoutboundconnections')))

        # Demanded difficulty tab
        self.lineEditTotalDifficulty.setText(str((float(
            config.getint(
                'bitmessagesettings', 'defaultnoncetrialsperbyte')
        ) / defaults.networkDefaultProofOfWorkNonceTrialsPerByte)))
        self.lineEditSmallMessageDifficulty.setText(str((float(
            config.getint(
                'bitmessagesettings', 'defaultpayloadlengthextrabytes')
        ) / defaults.networkDefaultPayloadLengthExtraBytes)))

        # Max acceptable difficulty tab
        self.lineEditMaxAcceptableTotalDifficulty.setText(str((float(
            config.getint(
                'bitmessagesettings', 'maxacceptablenoncetrialsperbyte')
        ) / defaults.networkDefaultProofOfWorkNonceTrialsPerByte)))
        self.lineEditMaxAcceptableSmallMessageDifficulty.setText(str((float(
            config.getint(
                'bitmessagesettings', 'maxacceptablepayloadlengthextrabytes')
        ) / defaults.networkDefaultPayloadLengthExtraBytes)))

        # OpenCL
        self.comboBoxOpenCL.setEnabled(openclpow.openclAvailable())
        self.comboBoxOpenCL.clear()
        self.comboBoxOpenCL.addItem("None")
        self.comboBoxOpenCL.addItems(openclpow.vendors)
        self.comboBoxOpenCL.setCurrentIndex(0)
        for i in range(self.comboBoxOpenCL.count()):
            if self.comboBoxOpenCL.itemText(i) == config.safeGet(
                    'bitmessagesettings', 'opencl'):
                self.comboBoxOpenCL.setCurrentIndex(i)
                break

        # Namecoin integration tab
        nmctype = config.get('bitmessagesettings', 'namecoinrpctype')
        self.lineEditNamecoinHost.setText(
            config.get('bitmessagesettings', 'namecoinrpchost'))
        self.lineEditNamecoinPort.setText(str(
            config.get('bitmessagesettings', 'namecoinrpcport')))
        self.lineEditNamecoinUser.setText(
            config.get('bitmessagesettings', 'namecoinrpcuser'))
        self.lineEditNamecoinPassword.setText(
            config.get('bitmessagesettings', 'namecoinrpcpassword'))

        if nmctype == "namecoind":
            self.radioButtonNamecoinNamecoind.setChecked(True)
        elif nmctype == "nmcontrol":
            self.radioButtonNamecoinNmcontrol.setChecked(True)
            self.lineEditNamecoinUser.setEnabled(False)
            self.labelNamecoinUser.setEnabled(False)
            self.lineEditNamecoinPassword.setEnabled(False)
            self.labelNamecoinPassword.setEnabled(False)
        else:
            assert False

        # Message Resend tab
        self.lineEditDays.setText(str(
            config.get('bitmessagesettings', 'stopresendingafterxdays')))
        self.lineEditMonths.setText(str(
            config.get('bitmessagesettings', 'stopresendingafterxmonths')))

    def comboBoxProxyTypeChanged(self, comboBoxIndex):
        """A callback for currentIndexChanged event of comboBoxProxyType"""
        if comboBoxIndex == 0:
            self.lineEditSocksHostname.setEnabled(False)
            self.lineEditSocksPort.setEnabled(False)
            self.lineEditSocksUsername.setEnabled(False)
            self.lineEditSocksPassword.setEnabled(False)
            self.checkBoxAuthentication.setEnabled(False)
            self.checkBoxSocksListen.setEnabled(False)
            self.checkBoxOnionOnly.setEnabled(False)
        else:
            self.lineEditSocksHostname.setEnabled(True)
            self.lineEditSocksPort.setEnabled(True)
            self.checkBoxAuthentication.setEnabled(True)
            self.checkBoxSocksListen.setEnabled(True)
            self.checkBoxOnionOnly.setEnabled(True)
            if self.checkBoxAuthentication.isChecked():
                self.lineEditSocksUsername.setEnabled(True)
                self.lineEditSocksPassword.setEnabled(True)

    def getNamecoinType(self):
        """
        Check status of namecoin integration radio buttons
        and translate it to a string as in the options.
        """
        if self.radioButtonNamecoinNamecoind.isChecked():
            return "namecoind"
        if self.radioButtonNamecoinNmcontrol.isChecked():
            return "nmcontrol"
        assert False

    # Namecoin connection type was changed.
    def namecoinTypeChanged(self, checked):  # pylint: disable=unused-argument
        """A callback for toggled event of radioButtonNamecoinNamecoind"""
        nmctype = self.getNamecoinType()
        assert nmctype == "namecoind" or nmctype == "nmcontrol"

        isNamecoind = (nmctype == "namecoind")
        self.lineEditNamecoinUser.setEnabled(isNamecoind)
        self.labelNamecoinUser.setEnabled(isNamecoind)
        self.lineEditNamecoinPassword.setEnabled(isNamecoind)
        self.labelNamecoinPassword.setEnabled(isNamecoind)

        if isNamecoind:
            self.lineEditNamecoinPort.setText(defaults.namecoinDefaultRpcPort)
        else:
            self.lineEditNamecoinPort.setText("9000")

    def click_pushButtonNamecoinTest(self):
        """Test the namecoin settings specified in the settings dialog."""
        self.labelNamecoinTestResult.setText(
            _translate("MainWindow", "Testing..."))
        nc = namecoin.namecoinConnection({
            'type': self.getNamecoinType(),
            'host': str(self.lineEditNamecoinHost.text().toUtf8()),
            'port': str(self.lineEditNamecoinPort.text().toUtf8()),
            'user': str(self.lineEditNamecoinUser.text().toUtf8()),
            'password': str(self.lineEditNamecoinPassword.text().toUtf8())
        })
        status, text = nc.test()
        self.labelNamecoinTestResult.setText(text)
        if status == 'success':
            self.parent.namecoin = nc

    def accept(self):
        """A callback for accepted event of buttonBox (OK button pressed)"""
        # pylint: disable=too-many-branches,too-many-statements
        super(SettingsDialog, self).accept()
        if self.firstrun:
            self.config.remove_option('bitmessagesettings', 'dontconnect')
        self.config.set('bitmessagesettings', 'startonlogon', str(
            self.checkBoxStartOnLogon.isChecked()))
        self.config.set('bitmessagesettings', 'minimizetotray', str(
            self.checkBoxMinimizeToTray.isChecked()))
        self.config.set('bitmessagesettings', 'trayonclose', str(
            self.checkBoxTrayOnClose.isChecked()))
        self.config.set(
            'bitmessagesettings', 'hidetrayconnectionnotifications',
            str(self.checkBoxHideTrayConnectionNotifications.isChecked()))
        self.config.set('bitmessagesettings', 'showtraynotifications', str(
            self.checkBoxShowTrayNotifications.isChecked()))
        self.config.set('bitmessagesettings', 'startintray', str(
            self.checkBoxStartInTray.isChecked()))
        self.config.set('bitmessagesettings', 'willinglysendtomobile', str(
            self.checkBoxWillinglySendToMobile.isChecked()))
        self.config.set('bitmessagesettings', 'useidenticons', str(
            self.checkBoxUseIdenticons.isChecked()))
        self.config.set('bitmessagesettings', 'replybelow', str(
            self.checkBoxReplyBelow.isChecked()))

        lang = str(self.languageComboBox.itemData(
            self.languageComboBox.currentIndex()).toString())
        self.config.set('bitmessagesettings', 'userlocale', lang)
        self.parent.change_translation()

        if int(self.config.get('bitmessagesettings', 'port')) != int(
                self.lineEditTCPPort.text()):
            self.config.set(
                'bitmessagesettings', 'port', str(self.lineEditTCPPort.text()))
            if not self.config.safeGetBoolean(
                    'bitmessagesettings', 'dontconnect'):
                self.net_restart_needed = True

        if self.checkBoxUPnP.isChecked() != self.config.safeGetBoolean(
                'bitmessagesettings', 'upnp'):
            self.config.set(
                'bitmessagesettings', 'upnp',
                str(self.checkBoxUPnP.isChecked()))
            if self.checkBoxUPnP.isChecked():
                import upnp
                upnpThread = upnp.uPnPThread()
                upnpThread.start()

        udp_enabled = self.checkBoxUDP.isChecked()
        if udp_enabled != self.config.safeGetBoolean(
                'bitmessagesettings', 'udp'):
            self.config.set('bitmessagesettings', 'udp', str(udp_enabled))
            if udp_enabled:
                announceThread = AnnounceThread()
                announceThread.daemon = True
                announceThread.start()
            else:
                try:
                    state.announceThread.stopThread()
                except AttributeError:
                    pass

        proxytype_index = self.comboBoxProxyType.currentIndex()
        if proxytype_index == 0:
            if self._proxy_type and state.statusIconColor != 'red':
                self.net_restart_needed = True
        elif state.statusIconColor == 'red' and self.config.safeGetBoolean(
                'bitmessagesettings', 'dontconnect'):
            self.net_restart_needed = False
        elif self.comboBoxProxyType.currentText() != self._proxy_type:
            self.net_restart_needed = True
            self.parent.statusbar.clearMessage()

        self.config.set(
            'bitmessagesettings', 'socksproxytype',
            'none' if self.comboBoxProxyType.currentIndex() == 0
            else str(self.comboBoxProxyType.currentText())
        )
        if proxytype_index > 2:  # last literal proxytype in ui
            start_proxyconfig()

        self.config.set('bitmessagesettings', 'socksauthentication', str(
            self.checkBoxAuthentication.isChecked()))
        self.config.set('bitmessagesettings', 'sockshostname', str(
            self.lineEditSocksHostname.text()))
        self.config.set('bitmessagesettings', 'socksport', str(
            self.lineEditSocksPort.text()))
        self.config.set('bitmessagesettings', 'socksusername', str(
            self.lineEditSocksUsername.text()))
        self.config.set('bitmessagesettings', 'sockspassword', str(
            self.lineEditSocksPassword.text()))
        self.config.set('bitmessagesettings', 'sockslisten', str(
            self.checkBoxSocksListen.isChecked()))
        if (
            self.checkBoxOnionOnly.isChecked()
            and not self.config.safeGetBoolean(
                'bitmessagesettings', 'onionservicesonly')
        ):
            self.net_restart_needed = True
        self.config.set('bitmessagesettings', 'onionservicesonly', str(
            self.checkBoxOnionOnly.isChecked()))
        try:
            # Rounding to integers just for aesthetics
            self.config.set('bitmessagesettings', 'maxdownloadrate', str(
                int(float(self.lineEditMaxDownloadRate.text()))))
            self.config.set('bitmessagesettings', 'maxuploadrate', str(
                int(float(self.lineEditMaxUploadRate.text()))))
        except ValueError:
            QtGui.QMessageBox.about(
                self, _translate("MainWindow", "Number needed"),
                _translate(
                    "MainWindow",
                    "Your maximum download and upload rate must be numbers."
                    " Ignoring what you typed.")
            )
        else:
            set_rates(
                self.config.safeGetInt('bitmessagesettings', 'maxdownloadrate'),
                self.config.safeGetInt('bitmessagesettings', 'maxuploadrate'))

        self.config.set('bitmessagesettings', 'maxoutboundconnections', str(
            int(float(self.lineEditMaxOutboundConnections.text()))))

        self.config.set(
            'bitmessagesettings', 'namecoinrpctype', self.getNamecoinType())
        self.config.set('bitmessagesettings', 'namecoinrpchost', str(
            self.lineEditNamecoinHost.text()))
        self.config.set('bitmessagesettings', 'namecoinrpcport', str(
            self.lineEditNamecoinPort.text()))
        self.config.set('bitmessagesettings', 'namecoinrpcuser', str(
            self.lineEditNamecoinUser.text()))
        self.config.set('bitmessagesettings', 'namecoinrpcpassword', str(
            self.lineEditNamecoinPassword.text()))
        self.parent.resetNamecoinConnection()

        # Demanded difficulty tab
        if float(self.lineEditTotalDifficulty.text()) >= 1:
            self.config.set(
                'bitmessagesettings', 'defaultnoncetrialsperbyte',
                str(int(
                    float(self.lineEditTotalDifficulty.text())
                    * defaults.networkDefaultProofOfWorkNonceTrialsPerByte)))
        if float(self.lineEditSmallMessageDifficulty.text()) >= 1:
            self.config.set(
                'bitmessagesettings', 'defaultpayloadlengthextrabytes',
                str(int(
                    float(self.lineEditSmallMessageDifficulty.text())
                    * defaults.networkDefaultPayloadLengthExtraBytes)))

        if self.comboBoxOpenCL.currentText().toUtf8() != self.config.safeGet(
                'bitmessagesettings', 'opencl'):
            self.config.set(
                'bitmessagesettings', 'opencl',
                str(self.comboBoxOpenCL.currentText()))
            queues.workerQueue.put(('resetPoW', ''))

        acceptableDifficultyChanged = False

        if (
            float(self.lineEditMaxAcceptableTotalDifficulty.text()) >= 1
            or float(self.lineEditMaxAcceptableTotalDifficulty.text()) == 0
        ):
            if self.config.get(
                    'bitmessagesettings', 'maxacceptablenoncetrialsperbyte'
            ) != str(int(
                float(self.lineEditMaxAcceptableTotalDifficulty.text())
                    * defaults.networkDefaultProofOfWorkNonceTrialsPerByte)):
                # the user changed the max acceptable total difficulty
                acceptableDifficultyChanged = True
                self.config.set(
                    'bitmessagesettings', 'maxacceptablenoncetrialsperbyte',
                    str(int(
                        float(self.lineEditMaxAcceptableTotalDifficulty.text())
                        * defaults.networkDefaultProofOfWorkNonceTrialsPerByte))
                )
        if (
            float(self.lineEditMaxAcceptableSmallMessageDifficulty.text()) >= 1
            or float(self.lineEditMaxAcceptableSmallMessageDifficulty.text()) == 0
        ):
            if self.config.get(
                    'bitmessagesettings', 'maxacceptablepayloadlengthextrabytes'
            ) != str(int(
                float(self.lineEditMaxAcceptableSmallMessageDifficulty.text())
                    * defaults.networkDefaultPayloadLengthExtraBytes)):
                # the user changed the max acceptable small message difficulty
                acceptableDifficultyChanged = True
                self.config.set(
                    'bitmessagesettings', 'maxacceptablepayloadlengthextrabytes',
                    str(int(
                        float(self.lineEditMaxAcceptableSmallMessageDifficulty.text())
                        * defaults.networkDefaultPayloadLengthExtraBytes))
                )
        if acceptableDifficultyChanged:
            # It might now be possible to send msgs which were previously
            # marked as toodifficult. Let us change them to 'msgqueued'.
            # The singleWorker will try to send them and will again mark
            # them as toodifficult if the receiver's required difficulty
            # is still higher than we are willing to do.
            sqlExecute(
                "UPDATE sent SET status='msgqueued'"
                " WHERE status='toodifficult'")
            queues.workerQueue.put(('sendmessage', ''))

        stopResendingDefaults = False

        # UI setting to stop trying to send messages after X days/months
        # I'm open to changing this UI to something else if someone has a better idea.
        if self.lineEditDays.text() == '' and self.lineEditMonths.text() == '':
            # We need to handle this special case. Bitmessage has its
            # default behavior. The input is blank/blank
            self.config.set('bitmessagesettings', 'stopresendingafterxdays', '')
            self.config.set('bitmessagesettings', 'stopresendingafterxmonths', '')
            state.maximumLengthOfTimeToBotherResendingMessages = float('inf')
            stopResendingDefaults = True

        try:
            days = float(self.lineEditDays.text())
        except ValueError:
            self.lineEditDays.setText("0")
            days = 0.0
        try:
            months = float(self.lineEditMonths.text())
        except ValueError:
            self.lineEditMonths.setText("0")
            months = 0.0

        if days >= 0 and months >= 0 and not stopResendingDefaults:
            state.maximumLengthOfTimeToBotherResendingMessages = \
                days * 24 * 60 * 60 + months * 60 * 60 * 24 * 365 / 12
            if state.maximumLengthOfTimeToBotherResendingMessages < 432000:
                # If the time period is less than 5 hours, we give
                # zero values to all fields. No message will be sent again.
                QtGui.QMessageBox.about(
                    self,
                    _translate("MainWindow", "Will not resend ever"),
                    _translate(
                        "MainWindow",
                        "Note that the time limit you entered is less"
                        " than the amount of time Bitmessage waits for"
                        " the first resend attempt therefore your"
                        " messages will never be resent.")
                )
                self.config.set(
                    'bitmessagesettings', 'stopresendingafterxdays', '0')
                self.config.set(
                    'bitmessagesettings', 'stopresendingafterxmonths', '0')
                state.maximumLengthOfTimeToBotherResendingMessages = 0.0
            else:
                self.config.set(
                    'bitmessagesettings', 'stopresendingafterxdays', str(days))
                self.config.set(
                    'bitmessagesettings', 'stopresendingafterxmonths',
                    str(months))

        self.config.save()

        if self.net_restart_needed:
            self.net_restart_needed = False
            self.config.setTemp('bitmessagesettings', 'dontconnect', 'true')
            self.timer.singleShot(
                5000, lambda:
                self.config.setTemp(
                    'bitmessagesettings', 'dontconnect', 'false')
            )

        self.parent.updateStartOnLogon()

        if (
            state.appdata != paths.lookupExeFolder()
            and self.checkBoxPortableMode.isChecked()
        ):
            # If we are NOT using portable mode now but the user selected
            # that we should...
            # Write the keys.dat file to disk in the new location
            sqlStoredProcedure('movemessagstoprog')
            with open(paths.lookupExeFolder() + 'keys.dat', 'wb') as configfile:
                self.config.write(configfile)
            # Write the knownnodes.dat file to disk in the new location
            knownnodes.saveKnownNodes(paths.lookupExeFolder())
            os.remove(state.appdata + 'keys.dat')
            os.remove(state.appdata + 'knownnodes.dat')
            previousAppdataLocation = state.appdata
            state.appdata = paths.lookupExeFolder()
            debug.resetLogging()
            try:
                os.remove(previousAppdataLocation + 'debug.log')
                os.remove(previousAppdataLocation + 'debug.log.1')
            except Exception:
                pass

        if (
            state.appdata == paths.lookupExeFolder()
            and not self.checkBoxPortableMode.isChecked()
        ):
            # If we ARE using portable mode now but the user selected
            # that we shouldn't...
            state.appdata = paths.lookupAppdataFolder()
            if not os.path.exists(state.appdata):
                os.makedirs(state.appdata)
            sqlStoredProcedure('movemessagstoappdata')
            # Write the keys.dat file to disk in the new location
            self.config.save()
            # Write the knownnodes.dat file to disk in the new location
            knownnodes.saveKnownNodes(state.appdata)
            os.remove(paths.lookupExeFolder() + 'keys.dat')
            os.remove(paths.lookupExeFolder() + 'knownnodes.dat')
            debug.resetLogging()
            try:
                os.remove(paths.lookupExeFolder() + 'debug.log')
                os.remove(paths.lookupExeFolder() + 'debug.log.1')
            except Exception:
                pass
