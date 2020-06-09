# pylint: disable=unused-argument
"""Status bar Module"""

from time import time
from PyQt4 import QtGui


class BMStatusBar(QtGui.QStatusBar):
    """Status bar with queue and priorities"""
    duration = 10000
    deleteAfter = 60

    def __init__(self, parent=None):
        super(BMStatusBar, self).__init__(parent)
        self.important = []
        self.timer = self.startTimer(BMStatusBar.duration)
        self.iterator = 0

    def timerEvent(self, event):
        """an event handler which allows to queue and prioritise messages to
        show in the status bar, for example if many messages come very quickly
        after one another, it adds delays and so on"""
        while len(self.important) > 0:
            self.iterator += 1
            try:
                if time() > self.important[self.iterator][1] + BMStatusBar.deleteAfter:
                    del self.important[self.iterator]
                    self.iterator -= 1
                    continue
            except IndexError:
                self.iterator = -1
                continue
            super(BMStatusBar, self).showMessage(self.important[self.iterator][0], 0)
            break

    def addImportant(self, message):
        self.important.append([message, time()])
        self.iterator = len(self.important) - 2
        self.timerEvent(None)
