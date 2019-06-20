"""
src/bitmessageqt/messageview.py
===============================

"""

from PyQt4 import QtCore, QtGui

from safehtmlparser import SafeHTMLParser


class MessageView(QtGui.QTextBrowser):
    """Message content viewer class, can switch between plaintext and HTML"""
    MODE_PLAIN = 0
    MODE_HTML = 1

    def __init__(self, parent=0):
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
        """View resize event handler"""
        super(MessageView, self).resizeEvent(event)
        self.setWrappingWidth(event.size().width())

    def mousePressEvent(self, event):
        """Mouse press button event handler"""
        if event.button() == QtCore.Qt.LeftButton and self.html and self.html.has_html and self.cursorForPosition(
                event.pos()).block().blockNumber() == 0:
            if self.mode == MessageView.MODE_PLAIN:
                self.showHTML()
            else:
                self.showPlain()
        else:
            super(MessageView, self).mousePressEvent(event)

    def wheelEvent(self, event):
        """Mouse wheel scroll event handler"""
        # super will actually automatically take care of zooming
        super(MessageView, self).wheelEvent(event)
        if (QtGui.QApplication.queryKeyboardModifiers() &
                QtCore.Qt.ControlModifier) == QtCore.Qt.ControlModifier and event.orientation() == QtCore.Qt.Vertical:
            zoom = self.currentFont().pointSize() * 100 / self.defaultFontPointSize
            QtGui.QApplication.activeWindow().statusBar().showMessage(
                QtGui.QApplication.translate("MainWindow", "Zoom level %1%").arg(str(zoom)))

    def setWrappingWidth(self, width=None):
        """Set word-wrapping width"""
        self.setLineWrapMode(QtGui.QTextEdit.FixedPixelWidth)
        if width is None:
            width = self.width()
        self.setLineWrapColumnOrWidth(width)

    def confirmURL(self, link):
        """Show a dialog requesting URL opening confirmation"""
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
        reply = QtGui.QMessageBox.warning(
            self,
            QtGui.QApplication.translate(
                "MessageView",
                "Follow external link"),
            QtGui.QApplication.translate(
                "MessageView",
                "The link \"%1\" will open in a browser. It may be a security risk, it could de-anonymise you"
                " or download malicious data. Are you sure?").arg(unicode(link.toString())),
            QtGui.QMessageBox.Yes,
            QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            QtGui.QDesktopServices.openUrl(link)

    def loadResource(self, restype, name):
        """
        Callback for loading referenced objects, such as an image. For security reasons at the moment doesn't do
        anything)
        """
        pass

    def lazyRender(self):
        """
        Partially render a message. This is to avoid UI freezing when loading huge messages. It continues loading as
        you scroll down.
        """
        if self.rendering:
            return
        self.rendering = True
        position = self.verticalScrollBar().value()
        cursor = QtGui.QTextCursor(self.document())
        while self.outpos < len(self.out) and self.verticalScrollBar().value(
        ) >= self.document().size().height() - 2 * self.size().height():
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
        """Render message as plain text."""
        self.mode = MessageView.MODE_PLAIN
        out = self.html.raw
        if self.html.has_html:
            out = "<div align=\"center\" style=\"text-decoration: underline;\"><b>" + unicode(
                QtGui.QApplication.translate(
                    "MessageView", "HTML detected, click here to display")) + "</b></div><br/>" + out
        self.out = out
        self.outpos = 0
        self.setHtml("")
        self.lazyRender()

    def showHTML(self):
        """Render message as HTML"""
        self.mode = MessageView.MODE_HTML
        out = self.html.sanitised
        out = "<div align=\"center\" style=\"text-decoration: underline;\"><b>" + unicode(
            QtGui.QApplication.translate("MessageView", "Click here to disable HTML")) + "</b></div><br/>" + out
        self.out = out
        self.outpos = 0
        self.setHtml("")
        self.lazyRender()

    def setContent(self, data):
        """Set message content from argument"""
        self.html = SafeHTMLParser()
        self.html.reset()
        self.html.reset_safe()
        self.html.allow_picture = True
        self.html.feed(data)
        self.html.close()
        self.showPlain()
