"""
Network status tab widget definition.
"""

import time

from PyQt4 import QtCore, QtGui

import knownnodes
import l10n
import network.stats
import state
import widgets
from inventory import Inventory
from network.connectionpool import BMConnectionPool
from retranslateui import RetranslateMixin
from tr import _translate
from uisignaler import UISignaler


class NetworkStatus(QtGui.QWidget, RetranslateMixin):
    """Network status tab"""
    def __init__(self, parent=None):
        super(NetworkStatus, self).__init__(parent)
        widgets.load('networkstatus.ui', self)

        header = self.tableWidgetConnectionCount.horizontalHeader()
        header.setResizeMode(QtGui.QHeaderView.ResizeToContents)

        # Somehow this value was 5 when I tested
        if header.sortIndicatorSection() > 4:
            header.setSortIndicator(0, QtCore.Qt.AscendingOrder)

        self.startup = time.localtime()

        self.UISignalThread = UISignaler.get()
        # pylint: disable=no-member
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "updateNumberOfMessagesProcessed()"), self.updateNumberOfMessagesProcessed)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "updateNumberOfPubkeysProcessed()"), self.updateNumberOfPubkeysProcessed)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "updateNumberOfBroadcastsProcessed()"), self.updateNumberOfBroadcastsProcessed)
        QtCore.QObject.connect(self.UISignalThread, QtCore.SIGNAL(
            "updateNetworkStatusTab(PyQt_PyObject,PyQt_PyObject,PyQt_PyObject)"), self.updateNetworkStatusTab)

        self.timer = QtCore.QTimer()

        QtCore.QObject.connect(self.timer, QtCore.SIGNAL("timeout()"), self.runEveryTwoSeconds)
        # pylint: enable=no-member

    def startUpdate(self):
        """Start a timer to update counters every 2 seconds"""
        Inventory().numberOfInventoryLookupsPerformed = 0
        self.runEveryTwoSeconds()
        self.timer.start(2000)  # milliseconds

    def stopUpdate(self):
        """Stop counter update timer"""
        self.timer.stop()

    def formatBytes(self, num):
        """Format bytes nicely (SI prefixes)"""
        # pylint: disable=no-self-use
        for x in [
                _translate(
                    "networkstatus",
                    "byte(s)",
                    None,
                    QtCore.QCoreApplication.CodecForTr,
                    num),
                "kB",
                "MB",
                "GB",
        ]:
            if num < 1000.0:
                return "%3.0f %s" % (num, x)
            num /= 1000.0
        return "%3.0f %s" % (num, 'TB')

    def formatByteRate(self, num):
        """Format transfer speed in kB/s"""
        # pylint: disable=no-self-use
        num /= 1000
        return "%4.0f kB" % num

    def updateNumberOfObjectsToBeSynced(self):
        """Update the counter for number of objects to be synced"""
        self.labelSyncStatus.setText(
            _translate(
                "networkstatus",
                "Object(s) to be synced: %n",
                None,
                QtCore.QCoreApplication.CodecForTr,
                network.stats.pendingDownload()
                + network.stats.pendingUpload()))

    def updateNumberOfMessagesProcessed(self):
        """Update the counter for number of processed messages"""
        self.updateNumberOfObjectsToBeSynced()
        self.labelMessageCount.setText(
            _translate(
                "networkstatus",
                "Processed %n person-to-person message(s).",
                None,
                QtCore.QCoreApplication.CodecForTr,
                state.numberOfMessagesProcessed))

    def updateNumberOfBroadcastsProcessed(self):
        """Update the counter for the number of processed broadcasts"""
        self.updateNumberOfObjectsToBeSynced()
        self.labelBroadcastCount.setText(
            _translate(
                "networkstatus",
                "Processed %n broadcast message(s).",
                None,
                QtCore.QCoreApplication.CodecForTr,
                state.numberOfBroadcastsProcessed))

    def updateNumberOfPubkeysProcessed(self):
        """Update the counter for the number of processed pubkeys"""
        self.updateNumberOfObjectsToBeSynced()
        self.labelPubkeyCount.setText(
            _translate(
                "networkstatus",
                "Processed %n public key(s).",
                None,
                QtCore.QCoreApplication.CodecForTr,
                state.numberOfPubkeysProcessed))

    def updateNumberOfBytes(self):
        """
        This function is run every two seconds, so we divide the rate of bytes
        sent and received by 2.
        """
        self.labelBytesRecvCount.setText(
            _translate(
                "networkstatus",
                "Down: %1/s  Total: %2").arg(
                    self.formatByteRate(network.stats.downloadSpeed()),
                    self.formatBytes(network.stats.receivedBytes())))
        self.labelBytesSentCount.setText(
            _translate(
                "networkstatus", "Up: %1/s  Total: %2").arg(
                    self.formatByteRate(network.stats.uploadSpeed()),
                    self.formatBytes(network.stats.sentBytes())))

    def updateNetworkStatusTab(self, outbound, add, destination):
        """Add or remove an entry to the list of connected peers"""
        # pylint: disable=too-many-branches,undefined-variable
        if outbound:
            try:
                c = BMConnectionPool().outboundConnections[destination]
            except KeyError:
                if add:
                    return
        else:
            try:
                c = BMConnectionPool().inboundConnections[destination]
            except KeyError:
                try:
                    c = BMConnectionPool().inboundConnections[destination.host]
                except KeyError:
                    if add:
                        return

        self.tableWidgetConnectionCount.setUpdatesEnabled(False)
        self.tableWidgetConnectionCount.setSortingEnabled(False)

        if add:
            self.tableWidgetConnectionCount.insertRow(0)
            self.tableWidgetConnectionCount.setItem(
                0, 0,
                QtGui.QTableWidgetItem("%s:%i" % (destination.host, destination.port))
            )
            self.tableWidgetConnectionCount.setItem(
                0, 2,
                QtGui.QTableWidgetItem("%s" % (c.userAgent))
            )
            self.tableWidgetConnectionCount.setItem(
                0, 3,
                QtGui.QTableWidgetItem("%s" % (c.tlsVersion))
            )
            self.tableWidgetConnectionCount.setItem(
                0, 4,
                QtGui.QTableWidgetItem("%s" % (",".join(map(str, c.streams))))
            )
            try:
                # .. todo:: FIXME: hard coded stream no
                rating = "%.1f" % (knownnodes.knownNodes[1][destination]['rating'])
            except KeyError:
                rating = "-"
            self.tableWidgetConnectionCount.setItem(
                0, 1,
                QtGui.QTableWidgetItem("%s" % (rating))
            )
            if outbound:
                brush = QtGui.QBrush(QtGui.QColor("yellow"), QtCore.Qt.SolidPattern)
            else:
                brush = QtGui.QBrush(QtGui.QColor("green"), QtCore.Qt.SolidPattern)
            for j in range(1):
                self.tableWidgetConnectionCount.item(0, j).setBackground(brush)
            self.tableWidgetConnectionCount.item(0, 0).setData(QtCore.Qt.UserRole, destination)
            self.tableWidgetConnectionCount.item(0, 1).setData(QtCore.Qt.UserRole, outbound)
        else:
            if not BMConnectionPool().inboundConnections:
                self.window().setStatusIcon('yellow')
            for i in range(self.tableWidgetConnectionCount.rowCount()):
                if self.tableWidgetConnectionCount.item(i, 0).data(QtCore.Qt.UserRole).toPyObject() != destination:
                    continue
                if self.tableWidgetConnectionCount.item(i, 1).data(QtCore.Qt.UserRole).toPyObject() == outbound:
                    self.tableWidgetConnectionCount.removeRow(i)
                    break

        self.tableWidgetConnectionCount.setUpdatesEnabled(True)
        self.tableWidgetConnectionCount.setSortingEnabled(True)
        self.labelTotalConnections.setText(
            _translate(
                "networkstatus", "Total Connections: %1").arg(
                    str(self.tableWidgetConnectionCount.rowCount())))
        # FYI: The 'singlelistener' thread sets the icon color to green when it
        # receives an incoming connection, meaning that the user's firewall is
        # configured correctly.
        if self.tableWidgetConnectionCount.rowCount() and state.statusIconColor == 'red':
            self.window().setStatusIcon('yellow')
        elif self.tableWidgetConnectionCount.rowCount() == 0 and state.statusIconColor != "red":
            self.window().setStatusIcon('red')

    # timer driven
    def runEveryTwoSeconds(self):
        """Updates counters, runs every 2 seconds if the timer is running"""
        self.labelLookupsPerSecond.setText(_translate("networkstatus", "Inventory lookups per second: %1").arg(
            str(Inventory().numberOfInventoryLookupsPerformed / 2)))
        Inventory().numberOfInventoryLookupsPerformed = 0
        self.updateNumberOfBytes()
        self.updateNumberOfObjectsToBeSynced()

    def retranslateUi(self):
        """Conventional Qt Designer method for dynamic l10n"""
        super(NetworkStatus, self).retranslateUi()
        self.labelTotalConnections.setText(
            _translate(
                "networkstatus", "Total Connections: %1").arg(
                    str(self.tableWidgetConnectionCount.rowCount())))
        self.labelStartupTime.setText(_translate(
            "networkstatus", "Since startup on %1"
        ).arg(l10n.formatTimestamp(self.startup)))
        self.updateNumberOfMessagesProcessed()
        self.updateNumberOfBroadcastsProcessed()
        self.updateNumberOfPubkeysProcessed()
