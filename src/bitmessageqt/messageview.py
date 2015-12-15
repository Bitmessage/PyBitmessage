from PyQt4 import QtCore, QtGui

from safehtmlparser import *

class MessageView(QtGui.QTextBrowser):
    MODE_PLAIN = 0
    MODE_HTML = 1
    TEXT_PLAIN = "HTML detected, click here to display"
    TEXT_HTML = "Click here to disable HTML"
    CONFIRM_TITLE = "Follow external link"
    CONFIRM_TEXT = "The link \"%1\" will open in a browser. It may be a security risk, it could de-anonymise you or download malicious data. Are you sure?"
    
    def __init__(self, parent = 0):
        super(MessageView, self).__init__(parent)
        self.mode = MessageView.MODE_PLAIN 
        self.html = None
        self.setOpenExternalLinks(False)
        self.setOpenLinks(False)
        self.anchorClicked.connect(self.confirmURL)
    
    def mousePressEvent(self, event):
        #text = textCursor.block().text()
        if event.button() == QtCore.Qt.LeftButton and self.html.has_html and self.cursorForPosition(event.pos()).block().blockNumber() == 0:
            if self.mode == MessageView.MODE_PLAIN:
                self.showHTML()
            else:
                self.showPlain()
        else:
            super(MessageView, self).mousePressEvent(event)
            
    def confirmURL(self, link):
        reply = QtGui.QMessageBox.question(self,
            QtGui.QApplication.translate(type(self).__name__, MessageView.CONFIRM_TITLE),
            QtGui.QApplication.translate(type(self).__name__, MessageView.CONFIRM_TEXT).arg(str(link.toString())), 
            QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            QtGui.QDesktopServices.openUrl(link)

    def showPlain(self):
        self.mode = MessageView.MODE_PLAIN
        out = self.html.raw
        if self.html.has_html:
            out = "<div align=\"center\" style=\"text-decoration: underline;\"><b>" + QtGui.QApplication.translate(type(self).__name__, MessageView.TEXT_PLAIN) + "</b></div><br/>" + out
        self.setHtml(QtCore.QString(out))

    def showHTML(self):
        self.mode = MessageView.MODE_HTML
        out = self.html.sanitised
        out = "<div align=\"center\" style=\"text-decoration: underline;\"><b>" + QtGui.QApplication.translate(type(self).__name__, MessageView.TEXT_HTML) + "</b></div><br/>" + out
        self.setHtml(QtCore.QString(out))

    def setContent(self, data):
        self.html = SafeHTMLParser()
        self.html.allow_picture = True
        self.html.feed(data)
        self.html.close()
        self.showPlain()
