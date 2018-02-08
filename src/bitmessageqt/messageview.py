from PyQt4 import QtCore, QtGui

import multiprocessing
import Queue
from urlparse import urlparse
from safehtmlparser import *

class MessageView(QtGui.QTextBrowser):
    MODE_PLAIN = 0
    MODE_HTML = 1
    
    def __init__(self, parent = 0):
        super(MessageView, self).__init__(parent)
        self.mode = MessageView.MODE_PLAIN 
        self.html = None
        self.setOpenExternalLinks(False)
        self.setOpenLinks(False)
        self.anchorClicked.connect(self.confirmURL)
        self.out = ""
        self.outpos = 0
        self.document().setUndoRedoEnabled(False)
        self.rendering = False
        self.defaultFontPointSize = self.currentFont().pointSize()
        self.verticalScrollBar().valueChanged.connect(self.lazyRender)
        self.setWrappingWidth()

    def resizeEvent(self, event):
        super(MessageView, self).resizeEvent(event)
        self.setWrappingWidth(event.size().width())
    
    def mousePressEvent(self, event):
        #text = textCursor.block().text()
        if event.button() == QtCore.Qt.LeftButton and self.html and self.html.has_html and self.cursorForPosition(event.pos()).block().blockNumber() == 0:
            if self.mode == MessageView.MODE_PLAIN:
                self.showHTML()
            else:
                self.showPlain()
        else:
            super(MessageView, self).mousePressEvent(event)

    def wheelEvent(self, event):
        # super will actually automatically take care of zooming
        super(MessageView, self).wheelEvent(event)
        if (QtGui.QApplication.queryKeyboardModifiers() & QtCore.Qt.ControlModifier) == QtCore.Qt.ControlModifier and event.orientation() == QtCore.Qt.Vertical:
            zoom = self.currentFont().pointSize() * 100 / self.defaultFontPointSize
            QtGui.QApplication.activeWindow().statusBar().showMessage(QtGui.QApplication.translate("MainWindow", "Zoom level %1%").arg(str(zoom)))

    def setWrappingWidth(self, width=None):
        self.setLineWrapMode(QtGui.QTextEdit.FixedPixelWidth)
        if width is None:
            width = self.width()
        self.setLineWrapColumnOrWidth(width)

    def confirmURL(self, link):
        if link.scheme() == "mailto":
            window = QtGui.QApplication.activeWindow()
            window.ui.lineEditTo.setText(link.path())
            if link.hasQueryItem("subject"):
                window.ui.lineEditSubject.setText(
                    link.queryItemValue("subject"))
            if link.hasQueryItem("body"):
                window.ui.textEditMessage.setText(
                    link.queryItemValue("body"))
            window.setSendFromComboBox()
            window.ui.tabWidgetSend.setCurrentIndex(0)
            window.ui.tabWidget.setCurrentIndex(
                window.ui.tabWidget.indexOf(window.ui.send)
            )
            window.ui.textEditMessage.setFocus()
            return
        reply = QtGui.QMessageBox.warning(self,
            QtGui.QApplication.translate("MessageView", "Follow external link"),
            QtGui.QApplication.translate("MessageView", "The link \"%1\" will open in a browser. It may be a security risk, it could de-anonymise you or download malicious data. Are you sure?").arg(unicode(link.toString())),
            QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            QtGui.QDesktopServices.openUrl(link)

    def loadResource (self, restype, name):
        if restype == QtGui.QTextDocument.ImageResource and name.scheme() == "bmmsg":
            pass
#            QImage correctImage;
#            lookup the correct QImage from a cache
#            return QVariant::fromValue(correctImage);
#        elif restype == QtGui.QTextDocument.HtmlResource:
#        elif restype == QtGui.QTextDocument.ImageResource:
#        elif restype == QtGui.QTextDocument.StyleSheetResource:
#        elif restype == QtGui.QTextDocument.UserResource:
        else:
            pass
#            by default, this will interpret it as a local file
#            QtGui.QTextBrowser.loadResource(restype, name)

    def lazyRender(self):
        if self.rendering:
            return
        self.rendering = True
        position = self.verticalScrollBar().value()
        cursor = QtGui.QTextCursor(self.document())
        while self.outpos < len(self.out) and self.verticalScrollBar().value() >= self.document().size().height() - 2 * self.size().height():
            startpos = self.outpos
            self.outpos += 10240
            # find next end of tag
            if self.mode == MessageView.MODE_HTML:
                pos = self.out.find(">", self.outpos)
                if pos > self.outpos:
                    self.outpos = pos + 1
            cursor.movePosition(QtGui.QTextCursor.End, QtGui.QTextCursor.MoveAnchor)
            cursor.insertHtml(QtCore.QString(self.out[startpos:self.outpos]))
        self.verticalScrollBar().setValue(position)
        self.rendering = False
    
    def showPlain(self):
        self.mode = MessageView.MODE_PLAIN
        out = self.html.raw
        if self.html.has_html:
            out = "<div align=\"center\" style=\"text-decoration: underline;\"><b>" + unicode(QtGui.QApplication.translate("MessageView", "HTML detected, click here to display")) + "</b></div><br/>" + out
        self.out = out
        self.outpos = 0
        self.setHtml("")
        self.lazyRender()

    def showHTML(self):
        self.mode = MessageView.MODE_HTML
        out = self.html.sanitised
        out = "<div align=\"center\" style=\"text-decoration: underline;\"><b>" + unicode(QtGui.QApplication.translate("MessageView", "Click here to disable HTML")) + "</b></div><br/>" + out
        self.out = out
        self.outpos = 0
        self.setHtml("")
        self.lazyRender()

    def setContent(self, data):
        self.html = SafeHTMLParser()
        self.html.reset()
        self.html.reset_safe()
        self.html.allow_picture = True
        self.html.feed(data)
        self.html.close()
        self.showPlain()
