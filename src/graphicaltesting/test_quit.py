"""Quits the application"""
import time

from PyQt4 import QtCore, QtGui

import bitmessageqt.sound
import shared
import shutdown
from bitmessageqt import settingsmixin
from bmconfigparser import BMConfigParser
from debug import logger
from network.stats import pendingDownload, pendingUpload
from proofofwork import getPowType
from testloader import BitmessageTestCase
from tr import _translate


class BitmessageTest_QuitTest(BitmessageTestCase):
    """Quit the bitmessage qt application"""

    def test_quitapplication(self):
        """wait for pow and shutdown the application"""
        print("=====================Test - Quitting Application=====================")
        if self.myapp.quitAccepted and not self.myapp.wait:
            return

        self.myapp.show()
        self.myapp.raise_()
        self.myapp.activateWindow()

        waitForPow = True
        waitForConnection = False
        waitForSync = False
        if getPowType() == "python" and (bitmessageqt.powQueueSize() > 0 or pendingUpload() > 0):
            waitForPow = False
        if pendingDownload() > 0:
            self.myapp.wait = waitForSync = True
        if shared.statusIconColor == "red" and not BMConfigParser().safeGetBoolean(
            "bitmessagesettings", "dontconnect"
        ):
            waitForConnection = True
            self.myapp.wait = waitForSync = True
        self.myapp.quitAccepted = True
        self.myapp.updateStatusBar(_translate("MainWindow", "Shutting down PyBitmessage... %1%").arg(0))
        if waitForConnection:
            self.myapp.updateStatusBar(_translate("MainWindow", "Waiting for network connection..."))
            while shared.statusIconColor == "red":
                time.sleep(0.5)
                QtCore.QCoreApplication.processEvents(QtCore.QEventLoop.AllEvents, 1000)
        if waitForSync:
            self.myapp.updateStatusBar(_translate("MainWindow", "Waiting for finishing synchronisation..."))
            while pendingDownload() > 0:
                time.sleep(0.5)
                QtCore.QCoreApplication.processEvents(QtCore.QEventLoop.AllEvents, 1000)
        if waitForPow:
            maxWorkerQueue = 0
            curWorkerQueue = bitmessageqt.powQueueSize()
            while curWorkerQueue > 0:
                curWorkerQueue = bitmessageqt.powQueueSize()
                if curWorkerQueue > maxWorkerQueue:
                    maxWorkerQueue = curWorkerQueue
                if curWorkerQueue > 0:
                    self.myapp.updateStatusBar(
                        _translate("MainWindow", "Waiting for PoW to finish... %1%").arg(
                            50 * (maxWorkerQueue - curWorkerQueue) / maxWorkerQueue
                        )
                    )
                    time.sleep(0.5)
                    QtCore.QCoreApplication.processEvents(QtCore.QEventLoop.AllEvents, 1000)
            self.myapp.updateStatusBar(_translate("MainWindow", "Shutting down Pybitmessage... %1%").arg(50))
            QtCore.QCoreApplication.processEvents(QtCore.QEventLoop.AllEvents, 1000)
            if maxWorkerQueue > 0:
                time.sleep(0.5)
            QtCore.QCoreApplication.processEvents(QtCore.QEventLoop.AllEvents, 1000)
            self.myapp.updateStatusBar(_translate("MainWindow", "Waiting for objects to be sent... %1%").arg(50))
            maxPendingUpload = max(1, pendingUpload())
            while pendingUpload() > 1:
                self.myapp.updateStatusBar(
                    _translate("MainWindow", "Waiting for objects to be sent... %1%").arg(
                        int(50 + 20 * (pendingUpload() / maxPendingUpload))
                    )
                )
                time.sleep(0.5)
                QtCore.QCoreApplication.processEvents(QtCore.QEventLoop.AllEvents, 1000)
            QtCore.QCoreApplication.processEvents(QtCore.QEventLoop.AllEvents, 1000)
        QtCore.QCoreApplication.processEvents(QtCore.QEventLoop.AllEvents, 1000)
        self.myapp.updateStatusBar(_translate("MainWindow", "Saving settings... %1%").arg(70))
        QtCore.QCoreApplication.processEvents(QtCore.QEventLoop.AllEvents, 1000)
        self.myapp.saveSettings()
        for attr, obj in self.myapp.ui.__dict__.iteritems():
            if hasattr(obj, "__class__") and isinstance(obj, settingsmixin.SettingsMixin):
                saveMethod = getattr(obj, "saveSettings", None)
                if callable(saveMethod):
                    obj.saveSettings()
        self.myapp.updateStatusBar(_translate("MainWindow", "Shutting down core... %1%").arg(80))
        QtCore.QCoreApplication.processEvents(QtCore.QEventLoop.AllEvents, 1000)
        shutdown.doCleanShutdown()
        self.myapp.updateStatusBar(_translate("MainWindow", "Stopping notifications... %1%").arg(90))
        self.myapp.tray.hide()
        self.myapp.updateStatusBar(_translate("MainWindow", "Shutdown imminent... %1%").arg(100))
        logger.info("Shutdown complete")
        QtGui.qApp.closeAllWindows()
