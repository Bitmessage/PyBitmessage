from PyQt4 import QtCore, QtGui
from queue.Queue import Queue
from time import time

class BMStatusBar(QtGui.QStatusBar):
    duration = 10000
    deleteAfter = 60

    def __init__(self, parent=None):
        super(BMStatusBar, self).__init__(parent)
        self.important = []
        self.timer = self.startTimer(BMStatusBar.duration)
        self.iterator = 0

    def timerEvent(self, event):
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

    def showMessage(self, message, timeout=0):
        super(BMStatusBar, self).showMessage(message, timeout)

    def clearMessage(self):
        super(BMStatusBar, self).clearMessage()
