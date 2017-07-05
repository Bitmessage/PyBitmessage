from PyQt4 import QtCore, QtGui
import time
import shared

from tr import _translate
from inventory import Inventory, PendingDownloadQueue, PendingUpload
import knownnodes
import l10n
import network.stats
from retranslateui import RetranslateMixin
from uisignaler import UISignaler
import widgets


class NetworkStatus(QtGui.QWidget, RetranslateMixin):
    def __init__(self, parent=None):
        super(NetworkStatus, self).__init__(parent)
        widgets.load('networkstatus.ui', self)

        self.tableWidgetConnectionCount.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)

        self.startup = time.localtime()
        self.labelStartupTime.setText(_translate("networkstatus", "Since startup on %1").arg(
            l10n.formatTimestamp(self.startup)))
        
        self.UISignalThread = UISignaler.get()
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "updateNumberOfMessagesProcessed()"), self.updateNumberOfMessagesProcessed)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "updateNumberOfPubkeysProcessed()"), self.updateNumberOfPubkeysProcessed)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "updateNumberOfBroadcastsProcessed()"), self.updateNumberOfBroadcastsProcessed)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "updateNetworkStatusTab()"), self.updateNetworkStatusTab)
        
        self.timer = QtCore.QTimer()
        self.timer.start(2000) # milliseconds
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.runEveryTwoSeconds)

    def formatBytes(self, num):
        for x in [_translate("networkstatus", "byte(s)", None, QtCore.QCoreApplication.CodecForTr, num), "kB", "MB", "GB"]:
            if num < 1000.0:
                return "%3.0f %s" % (num, x)
            num /= 1000.0
        return "%3.0f %s" % (num, 'TB')

    def formatByteRate(self, num):
        num /= 1000
        return "%4.0f kB" % num
        
    def updateNumberOfObjectsToBeSynced(self):
        self.labelSyncStatus.setText(_translate("networkstatus", "Object(s) to be synced: %n", None, QtCore.QCoreApplication.CodecForTr, network.stats.pendingDownload() + network.stats.pendingUpload()))

    def updateNumberOfMessagesProcessed(self):
#        self.updateNumberOfObjectsToBeSynced()
        self.labelMessageCount.setText(_translate(
            "networkstatus", "Processed %n person-to-person message(s).", None, QtCore.QCoreApplication.CodecForTr, shared.numberOfMessagesProcessed))

    def updateNumberOfBroadcastsProcessed(self):
#        self.updateNumberOfObjectsToBeSynced()
        self.labelBroadcastCount.setText(_translate(
            "networkstatus", "Processed %n broadcast message(s).", None, QtCore.QCoreApplication.CodecForTr, shared.numberOfBroadcastsProcessed))

    def updateNumberOfPubkeysProcessed(self):
#        self.updateNumberOfObjectsToBeSynced()
        self.labelPubkeyCount.setText(_translate(
            "networkstatus", "Processed %n public key(s).", None, QtCore.QCoreApplication.CodecForTr, shared.numberOfPubkeysProcessed))

    def updateNumberOfBytes(self):
        """
        This function is run every two seconds, so we divide the rate of bytes
        sent and received by 2.
        """
        self.labelBytesRecvCount.setText(_translate(
            "networkstatus", "Down: %1/s  Total: %2").arg(self.formatByteRate(network.stats.downloadSpeed()), self.formatBytes(network.stats.receivedBytes())))
        self.labelBytesSentCount.setText(_translate(
            "networkstatus", "Up: %1/s  Total: %2").arg(self.formatByteRate(network.stats.uploadSpeed()), self.formatBytes(network.stats.sentBytes())))

    def updateNetworkStatusTab(self):
        connectedHosts = network.stats.connectedHostsList()

        self.tableWidgetConnectionCount.setUpdatesEnabled(False)
        #self.tableWidgetConnectionCount.setSortingEnabled(False)
        #self.tableWidgetConnectionCount.clearContents()
        self.tableWidgetConnectionCount.setRowCount(0)
        for i in connectedHosts:
            self.tableWidgetConnectionCount.insertRow(0)
            self.tableWidgetConnectionCount.setItem(0, 0,
                QtGui.QTableWidgetItem("%s:%i" % (i.destination.host, i.destination.port))
                )
            self.tableWidgetConnectionCount.setItem(0, 2,
                QtGui.QTableWidgetItem("%s" % (i.userAgent))
                )
            self.tableWidgetConnectionCount.setItem(0, 3,
                QtGui.QTableWidgetItem("%s" % (i.tlsVersion))
                )
            self.tableWidgetConnectionCount.setItem(0, 4,
                QtGui.QTableWidgetItem("%s" % (",".join(map(str,i.streams))))
                )
            try:
                # FIXME hard coded stream no
                rating = knownnodes.knownNodes[1][i.destination]['rating']
            except KeyError:
                rating = "-"
            self.tableWidgetConnectionCount.setItem(0, 1,
                QtGui.QTableWidgetItem("%s" % (rating))
                )
            if i.isOutbound:
                brush = QtGui.QBrush(QtGui.QColor("yellow"), QtCore.Qt.SolidPattern)
            else:
                brush = QtGui.QBrush(QtGui.QColor("green"), QtCore.Qt.SolidPattern)
            for j in (range(1)):
                self.tableWidgetConnectionCount.item(0, j).setBackground(brush)
        self.tableWidgetConnectionCount.setUpdatesEnabled(True)
        #self.tableWidgetConnectionCount.setSortingEnabled(True)
        #self.tableWidgetConnectionCount.horizontalHeader().setSortIndicator(1, QtCore.Qt.AscendingOrder)
        self.labelTotalConnections.setText(_translate(
            "networkstatus", "Total Connections: %1").arg(str(len(connectedHosts))))
       # FYI: The 'singlelistener' thread sets the icon color to green when it receives an incoming connection, meaning that the user's firewall is configured correctly.
        if connectedHosts and shared.statusIconColor == 'red':
            self.window().setStatusIcon('yellow')
        elif not connectedHosts and shared.statusIconColor != "red":
            self.window().setStatusIcon('red')

    # timer driven
    def runEveryTwoSeconds(self):
        self.labelLookupsPerSecond.setText(_translate(
            "networkstatus", "Inventory lookups per second: %1").arg(str(Inventory().numberOfInventoryLookupsPerformed/2)))
        Inventory().numberOfInventoryLookupsPerformed = 0
        self.updateNumberOfBytes()
        self.updateNumberOfObjectsToBeSynced()
        self.updateNumberOfMessagesProcessed()
        self.updateNumberOfBroadcastsProcessed()
        self.updateNumberOfPubkeysProcessed()

    def retranslateUi(self):
        super(NetworkStatus, self).retranslateUi()
        self.labelStartupTime.setText(_translate("networkstatus", "Since startup on %1").arg(
            l10n.formatTimestamp(self.startup)))
