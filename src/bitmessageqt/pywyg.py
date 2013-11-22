#PyWyg - Wysiwyg Editor on Python
#
#
#
#
__author__ = 'akarapetyan'
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class PyWyg:

    def __init__(self, TheGui):
        self.ui = TheGui
        self.messagecontainer = self.ui.textEditMessage
        #initializing default style and applying it to container
        self.thefont = QFont()
        self.thefont.setBold(False)
        self.thefont.setItalic(False)
        self.thefont.setPointSize(12)
        self.thefont.setStrikeOut(False)
        self.thefont.setUnderline(False)
        self.messagecontainer.setFont(self.thefont)
        self.thealignment = QtCore.Qt.AlignLeft
        self.messagecontainer.setAlignment(self.thealignment)
        self.txtcol = QtGui.QColor(0, 0, 0)
        self.bgcol = QtGui.QColor(255, 255, 255)
        self.messagecontainer.setTextColor(self.txtcol)
        self.messagecontainer.setTextBackgroundColor(self.bgcol)

    #Setting style to container
    def setCurrentStyle(self, CurrentFont):
        self.messagecontainer.setCurrentFont(CurrentFont)
        #self.messagecontainer.setFont(self.thefont)
        #self.messagecontainer.setAlignment(self.thealignment)
        #self.messagecontainer.setTextColor(self.txtcol)
        #self.messagecontainer.setTextBackgroundColor(self.bgcol)

    #Getting current style and setting according checked states to buttons
    def getCurrentStyle(self):
        mycursor = self.messagecontainer.textCursor()
        if mycursor.hasSelection():
            print "sdf"
        elif mycursor.position() >= 0:
            self.setButtonsStates()
        else:
            return False

    def setButtonsStates(self):
        #setting basic buttons statuses
        self.ui.pushButtonBold.setChecked(self.messagecontainer.currentFont().bold())
        self.ui.pushButtonItalic.setChecked(self.messagecontainer.currentFont().italic())
        self.ui.pushButtonUnderline.setChecked(self.messagecontainer.currentFont().underline())
        self.ui.pushButtonStrike.setChecked(self.messagecontainer.currentFont().strikeOut())
        #check maybe there doesn't exist this font size
        theindex = self.ui.comboBoxFontSize.findText(str(self.messagecontainer.currentFont().pointSize()))
        self.ui.comboBoxFontSize.setCurrentIndex(theindex)
        #setting according alignment button status
        if self.messagecontainer.alignment() == QtCore.Qt.AlignLeft:
            self.ui.pushButtonAlignmentLeft.setChecked(True)
            self.Alignment_Buttons_Checked_Status(self.ui.pushButtonAlignmentLeft, self.ui.pushButtonAlignmentRight, self.ui.pushButtonAlignmentCenter, self.ui.pushButtonAlignmentJustify)
        elif self.messagecontainer.alignment() == QtCore.Qt.AlignRight:
            self.ui.pushButtonAlignmentRight.setChecked(True)
            self.Alignment_Buttons_Checked_Status(self.ui.pushButtonAlignmentRight, self.ui.pushButtonAlignmentLeft, self.ui.pushButtonAlignmentCenter, self.ui.pushButtonAlignmentJustify)
        elif self.messagecontainer.alignment() == QtCore.Qt.AlignCenter:
            self.ui.pushButtonAlignmentCenter.setChecked(True)
            self.Alignment_Buttons_Checked_Status(self.ui.pushButtonAlignmentCenter, self.ui.pushButtonAlignmentLeft, self.ui.pushButtonAlignmentRight, self.ui.pushButtonAlignmentJustify)
        elif self.messagecontainer.alignment() == QtCore.Qt.AlignJustify:
            self.ui.pushButtonAlignmentJustify.setChecked(True)
            self.Alignment_Buttons_Checked_Status(self.ui.pushButtonAlignmentJustify, self.ui.pushButtonAlignmentLeft, self.ui.pushButtonAlignmentRight, self.ui.pushButtonAlignmentCenter)

    def click_pushButtonBold(self):
        mycursor = self.messagecontainer.textCursor()
        myformat = mycursor.charFormat()
        if mycursor.hasSelection():
            mycursor.beginEditBlock()
            if self.ui.pushButtonBold.isChecked():
                myformat.setFontWeight(QFont.Bold)
            else:
                myformat.setFontWeight(QFont.Normal)
            mycursor.mergeCharFormat(myformat)
            mycursor.endEditBlock()
        elif mycursor.position() >= 0:
            mycursor.beginEditBlock()
            if self.ui.pushButtonBold.isChecked():
                self.thefont.setBold(True)
                self.setCurrentStyle(self.thefont)
            else:
                self.thefont.setBold(False)
                self.setCurrentStyle(self.thefont)
            mycursor.endEditBlock()
        else:
            return False

    def click_pushButtonUnderline(self):
        mycursor = self.messagecontainer.textCursor()
        myformat = mycursor.charFormat()
        if mycursor.hasSelection():
            mycursor.beginEditBlock()
            if self.ui.pushButtonUnderline.isChecked():
                myformat.setFontUnderline(True)
            else:
                myformat.setFontUnderline(False)
            mycursor.mergeCharFormat(myformat)
            mycursor.endEditBlock()
        elif mycursor.position() >= 0:
            mycursor.beginEditBlock()
            if self.ui.pushButtonUnderline.isChecked():
                self.thefont.setUnderline(True)
                self.setCurrentStyle(self.thefont)
            else:
                self.thefont.setUnderline(False)
                self.setCurrentStyle(self.thefont)
            mycursor.endEditBlock()
        else:
            return False

    def click_pushButtonStrike(self):
        messagecontainer = self.ui.textEditMessage
        mycursor = messagecontainer.textCursor()
        myformat = mycursor.charFormat()
        if mycursor.hasSelection():
            mycursor.beginEditBlock()
            if self.ui.pushButtonStrike.isChecked():
                myformat.setFontStrikeOut(True)
            else:
                myformat.setFontStrikeOut(False)
            mycursor.setCharFormat(myformat)
            mycursor.endEditBlock()
        elif mycursor.position() >= 0:
            mycursor.beginEditBlock()
            if self.ui.pushButtonStrike.isChecked():
                striked = QFont()
                striked.setStrikeOut(True)
                messagecontainer.setCurrentFont(striked)
            else:
                striked = QFont()
                striked.setStrikeOut(False)
                messagecontainer.setCurrentFont(striked)
            mycursor.endEditBlock()
        else:
            return False

    def click_pushButtonHighlight(self):
        col = QtGui.QColor(0, 0, 0)
        col = QtGui.QColorDialog.getColor()
        messagecontainer = self.ui.textEditMessage
        mycursor = messagecontainer.textCursor()
        if col.isValid():
            if mycursor.hasSelection():
                mycursor.beginEditBlock()
                myformat = mycursor.charFormat()
                myformat.setBackground(col)
                mycursor.setCharFormat(myformat)
                mycursor.endEditBlock()
            else:
                mycursor.beginEditBlock()
                messagecontainer.setTextBackgroundColor(col)
                mycursor.endEditBlock()
        else:
            return False

    def click_comboBoxFontSize(self, fontsize):
        messagecontainer = self.ui.textEditMessage
        mycursor = messagecontainer.textCursor()
        myformat = mycursor.charFormat()
        if mycursor.hasSelection():
            mycursor.beginEditBlock()
            myformat.setFontPointSize(float(fontsize))
            mycursor.setCharFormat(myformat)
            mycursor.endEditBlock()
        elif mycursor.position() >= 0:
            mycursor.beginEditBlock()
            messagecontainer.setFontPointSize(float(fontsize))
            mycursor.endEditBlock()
        else:
            return False

    def click_pushButtonItalic(self):
        mycursor = self.messagecontainer.textCursor()
        myformat = mycursor.charFormat()
        if mycursor.hasSelection():
            mycursor.beginEditBlock()
            if self.ui.pushButtonItalic.isChecked():
                myformat.setFontItalic(True)
            else:
                myformat.setFontItalic(False)
            mycursor.mergeCharFormat(myformat)
            mycursor.endEditBlock()
        elif mycursor.position() >= 0:
            mycursor.beginEditBlock()
            if self.ui.pushButtonItalic.isChecked():
                self.thefont.setItalic(True)
                self.setCurrentStyle(self.thefont)
            else:
                self.thefont.setItalic(True)
                self.setCurrentStyle(self.thefont)
            mycursor.endEditBlock()
        else:
            return False
    def click_pushButtonPastPlainText(self):
        print "sdfsdf"

    def click_pushButtonPastFormattedText(self):
        print "dsfsd"

    def click_pushButtonClear(self):
        messagecontainer = self.ui.textEditMessage
        messagecontainer.clear()

    def Alignment_Buttons_Checked_Status(self, initiator, to_uncheck1, to_uncheck2, to_uncheck3):
        if initiator.isChecked():
            to_uncheck1.setChecked(False)
            to_uncheck2.setChecked(False)
            to_uncheck3.setChecked(False)

    def click_pushButtonFontIncrease(self):
        messagecontainer = self.ui.textEditMessage
        mycursor = messagecontainer.textCursor()
        myformat = mycursor.charFormat()
        if mycursor.hasSelection():
            mycursor.beginEditBlock()
            curfontsize = messagecontainer.currentFont().pointSize()
            if curfontsize <= 70:
                curfontsize += 2
                myformat.setFontPointSize(float(curfontsize))
                mycursor.setCharFormat(myformat)
            mycursor.endEditBlock()
        elif mycursor.position() >= 0:
            mycursor.beginEditBlock()
            curfontsize = messagecontainer.currentFont().pointSize()
            if curfontsize <= 70:
                curfontsize += 2
                messagecontainer.setFontPointSize(float(curfontsize))
            mycursor.endEditBlock()
        else:
            return False

    def click_pushButtonFontDecrease(self):
        messagecontainer = self.ui.textEditMessage
        mycursor = messagecontainer.textCursor()
        myformat = mycursor.charFormat()
        if mycursor.hasSelection():
            thepoint = QPoint()
            thepoint.setX(1)
            thepoint.setY(100)
            print messagecontainer.cursorForPosition(thepoint).charFormat().font().pointSize()
            curfontsize = messagecontainer.currentFont().pointSize()
            if curfontsize >= 8:
                curfontsize -= 2
                myformat.setFontPointSize(float(curfontsize))
                mycursor.setCharFormat(myformat)
            mycursor.endEditBlock()
        elif mycursor.position() >= 0:
            mycursor.beginEditBlock()
            curfontsize = messagecontainer.currentFont().pointSize()
            if curfontsize >= 8:
                curfontsize -= 2
                messagecontainer.setFontPointSize(float(curfontsize))
            mycursor.endEditBlock()
        else:
            return False

    def click_pushButtonAlignmentCenter(self):
        self.Alignment_Buttons_Checked_Status(self.ui.pushButtonAlignmentCenter, self.ui.pushButtonAlignmentRight, self.ui.pushButtonAlignmentLeft, self.ui.pushButtonAlignmentJustify)
        messagecontainer = self.ui.textEditMessage
        messagecontainer.setAlignment(QtCore.Qt.AlignCenter)

    def click_pushButtonAlignmentLeft(self):
        self.Alignment_Buttons_Checked_Status(self.ui.pushButtonAlignmentLeft, self.ui.pushButtonAlignmentRight, self.ui.pushButtonAlignmentCenter, self.ui.pushButtonAlignmentJustify)
        messagecontainer = self.ui.textEditMessage
        messagecontainer.setAlignment(QtCore.Qt.AlignLeft)

    def click_pushButtonAlignmentRight(self):
        self.Alignment_Buttons_Checked_Status(self.ui.pushButtonAlignmentRight, self.ui.pushButtonAlignmentLeft, self.ui.pushButtonAlignmentCenter, self.ui.pushButtonAlignmentJustify)
        messagecontainer = self.ui.textEditMessage
        messagecontainer.setAlignment(QtCore.Qt.AlignRight)

    def click_pushButtonAlignmentJustify(self):
        self.Alignment_Buttons_Checked_Status(self.ui.pushButtonAlignmentJustify, self.ui.pushButtonAlignmentLeft, self.ui.pushButtonAlignmentRight, self.ui.pushButtonAlignmentCenter)
        messagecontainer = self.ui.textEditMessage
        messagecontainer.setAlignment(QtCore.Qt.AlignJustify)


    def click_pushButtonTextColor(self):
        col = QtGui.QColor(0, 0, 0)
        col = QtGui.QColorDialog.getColor()
        messagecontainer = self.ui.textEditMessage
        mycursor = messagecontainer.textCursor()
        if col.isValid():
            if mycursor.hasSelection():
                mycursor.beginEditBlock()
                myformat = mycursor.charFormat()
                myformat.setForeground(col)
                mycursor.setCharFormat(myformat)
                mycursor.endEditBlock()
            else:
                mycursor.beginEditBlock()
                messagecontainer.setTextColor(col)
                mycursor.endEditBlock()
        else:
            return False

    def click_pushButtonPaste(self):
        messagecontainer = self.ui.textEditMessage
        messagecontainer.paste()

    def click_pushButtonCopy(self):
        messagecontainer = self.ui.textEditMessage
        messagecontainer.copy()

    def click_pushButtonUndo(self):
        messagecontainer = self.ui.textEditMessage
        messagecontainer.undo()

    def click_pushButtonRedo(self):
        messagecontainer = self.ui.textEditMessage
        messagecontainer.redo()
