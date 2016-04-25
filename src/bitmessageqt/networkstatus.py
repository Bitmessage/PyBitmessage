from PyQt4 import QtCore, QtGui
import time
import shared
from tr import _translate
import l10n
from retranslateui import RetranslateMixin
from uisignaler import UISignaler
import widgets


class NetworkStatus(QtGui.QWidget, RetranslateMixin):
    def __init__(self, parent=None):
        super(NetworkStatus, self).__init__(parent)
        widgets.load('networkstatus.ui', self)

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
        
        self.totalNumberOfBytesReceived = 0
        self.totalNumberOfBytesSent = 0
        
        self.timer = QtCore.QTimer()
        self.timer.start(2000) # milliseconds
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.runEveryTwoSeconds)

    def formatBytes(self, num):
        for x in [_translate("networkstatus", "byte(s)"), "kB", "MB", "GB"]:
            if num < 1000.0:
                return "%3.0f %s" % (num, x)
            num /= 1000.0
        return "%3.0f %s" % (num, 'TB')

    def formatByteRate(self, num):
        num /= 1000
        return "%4.0f kB" % num

    def updateNumberOfMessagesProcessed(self):
        self.labelSyncStatus.setText(_translate("networkstatus", "Objects to be synced: %1").arg(str(sum(shared.numberOfObjectsThatWeHaveYetToGetPerPeer.itervalues()))))
        self.labelMessageCount.setText(_translate(
            "networkstatus", "Processed %1 person-to-person messages.").arg(str(shared.numberOfMessagesProcessed)))

    def updateNumberOfBroadcastsProcessed(self):
        self.labelSyncStatus.setText(_translate("networkstatus", "Objects to be synced: %1").arg(str(sum(shared.numberOfObjectsThatWeHaveYetToGetPerPeer.itervalues()))))
        self.labelBroadcastCount.setText(_translate(
            "networkstatus", "Processed %1 broadcast messages.").arg(str(shared.numberOfBroadcastsProcessed)))

    def updateNumberOfPubkeysProcessed(self):
        self.labelSyncStatus.setText(_translate("networkstatus", "Objects to be synced: %1").arg(str(sum(shared.numberOfObjectsThatWeHaveYetToGetPerPeer.itervalues()))))
        self.labelPubkeyCount.setText(_translate(
            "networkstatus", "Processed %1 public keys.").arg(str(shared.numberOfPubkeysProcessed)))

    def updateNumberOfBytes(self):
        """
        This function is run every two seconds, so we divide the rate of bytes
        sent and received by 2.
        """
        self.labelBytesRecvCount.setText(_translate(
            "networkstatus", "Down: %1/s  Total: %2").arg(self.formatByteRate(shared.numberOfBytesReceived/2), self.formatBytes(self.totalNumberOfBytesReceived)))
        self.labelBytesSentCount.setText(_translate(
            "networkstatus", "Up: %1/s  Total: %2").arg(self.formatByteRate(shared.numberOfBytesSent/2), self.formatBytes(self.totalNumberOfBytesSent)))
        self.totalNumberOfBytesReceived += shared.numberOfBytesReceived
        self.totalNumberOfBytesSent += shared.numberOfBytesSent
        shared.numberOfBytesReceived = 0
        shared.numberOfBytesSent = 0

    def updateNetworkStatusTab(self):
        totalNumberOfConnectionsFromAllStreams = 0  # One would think we could use len(sendDataQueues) for this but the number doesn't always match: just because we have a sendDataThread running doesn't mean that the connection has been fully established (with the exchange of version messages).
        streamNumberTotals = {}
        for host, streamNumber in shared.connectedHostsList.items():
            if not streamNumber in streamNumberTotals:
                streamNumberTotals[streamNumber] = 1
            else:
                streamNumberTotals[streamNumber] += 1

        while self.tableWidgetConnectionCount.rowCount() > 0:
            self.tableWidgetConnectionCount.removeRow(0)
        for streamNumber, connectionCount in streamNumberTotals.items():
            self.tableWidgetConnectionCount.insertRow(0)
            if streamNumber == 0:
                newItem = QtGui.QTableWidgetItem("?")
            else:
                newItem = QtGui.QTableWidgetItem(str(streamNumber))
            newItem.setFlags(
                QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.tableWidgetConnectionCount.setItem(0, 0, newItem)
            newItem = QtGui.QTableWidgetItem(str(connectionCount))
            newItem.setFlags(
                QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.tableWidgetConnectionCount.setItem(0, 1, newItem)
        """for currentRow in range(self.tableWidgetConnectionCount.rowCount()):
            rowStreamNumber = int(self.tableWidgetConnectionCount.item(currentRow,0).text())
            if streamNumber == rowStreamNumber:
                foundTheRowThatNeedsUpdating = True
                self.tableWidgetConnectionCount.item(currentRow,1).setText(str(connectionCount))
                #totalNumberOfConnectionsFromAllStreams += connectionCount
        if foundTheRowThatNeedsUpdating == False:
            #Add a line to the table for this stream number and update its count with the current connection count.
            self.tableWidgetConnectionCount.insertRow(0)
            newItem =  QtGui.QTableWidgetItem(str(streamNumber))
            newItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            self.tableWidgetConnectionCount.setItem(0,0,newItem)
            newItem =  QtGui.QTableWidgetItem(str(connectionCount))
            newItem.setFlags( QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled )
            self.tableWidgetConnectionCount.setItem(0,1,newItem)
            totalNumberOfConnectionsFromAllStreams += connectionCount"""
        self.labelTotalConnections.setText(_translate(
            "networkstatus", "Total Connections: %1").arg(str(len(shared.connectedHostsList))))
        if len(shared.connectedHostsList) > 0 and shared.statusIconColor == 'red':  # FYI: The 'singlelistener' thread sets the icon color to green when it receives an incoming connection, meaning that the user's firewall is configured correctly.
            self.window().setStatusIcon('yellow')
        elif len(shared.connectedHostsList) == 0:
            self.window().setStatusIcon('red')

    # timer driven
    def runEveryTwoSeconds(self):
        self.labelLookupsPerSecond.setText(_translate(
            "networkstatus", "Inventory lookups per second: %1").arg(str(shared.numberOfInventoryLookupsPerformed/2)))
        shared.numberOfInventoryLookupsPerformed = 0
        self.updateNumberOfBytes()

    def retranslateUi(self):
        super(QtGui.QWidget, self).retranslateUi()
        self.labelStartupTime.setText(_translate("networkstatus", "Since startup on %1").arg(
            l10n.formatTimestamp(self.startup)))
