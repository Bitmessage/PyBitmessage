"""
src/bitmessageqt/statusbar.py
=============================
"""

from time import time

from PyQt4 import QtGui


class BMStatusBar(QtGui.QStatusBar):
    """Encapsulate statusbar behaviour"""

    duration = 10000
    deleteAfter = 60

    def __init__(self, parent=None):
        super(BMStatusBar, self).__init__(parent)
        self.important = []
        self.timer = self.startTimer(BMStatusBar.duration)
        self.iterator = 0

    def timerEvent(self):
        """Timer supporting display of important messages"""
        while self.important:
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
        """Handle an important message"""
        self.important.append([message, time()])
        self.iterator = len(self.important) - 2
        self.timerEvent()
