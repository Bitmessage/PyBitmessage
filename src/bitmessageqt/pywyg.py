# PyWyg - Open Source Wysiwyg Editor on Python
# 20.12.2013
# arnukk@gmail.com
# Areg Karapetyan
# For Installation details and detailed explanation please refer
# to

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class PyWyg:

    def __init__(self, TheGui):
        self.ui = TheGui
        self.messagecontainer = self.ui.textEditMessage
        self.mycursor = self.messagecontainer.textCursor()
        self.myformat = self.mycursor.charFormat()
        #Initializing default style and applying it to container
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
        #Accepted font sizes
        self.FontSizes = []
        self.FontSizes.append(6)
        self.FontSizes.append(7)
        self.FontSizes.append(8)
        self.FontSizes.append(9)
        self.FontSizes.append(10)
        self.FontSizes.append(11)
        self.FontSizes.append(12)
        self.FontSizes.append(14)
        self.FontSizes.append(16)
        self.FontSizes.append(18)
        self.FontSizes.append(20)
        self.FontSizes.append(22)
        self.FontSizes.append(24)
        self.FontSizes.append(26)
        self.FontSizes.append(28)
        self.FontSizes.append(36)
        self.FontSizes.append(48)
        self.FontSizes.append(72)
        #Initializing Font Size combo box
        self.InitializeFontComboBox()


    #General function for applying current Font style to container
    def setStyle(self, thebutton, commandname, posvalueselected, negvalueselected, posvalueposition, negvalueposition ):
        self.mycursor = self.messagecontainer.textCursor()
        self.myformat = self.mycursor.charFormat()
        #Command names
        self.commands = {}
        self.commands["Bold"] = []
        self.commands["Bold"].append(self.myformat.setFontWeight)
        self.commands["Bold"].append(self.thefont.setBold)
        self.commands["Underlined"] = []
        self.commands["Underlined"].append(self.myformat.setFontUnderline)
        self.commands["Underlined"].append(self.thefont.setUnderline)
        self.commands["Striked"] = []
        self.commands["Striked"].append(self.myformat.setFontStrikeOut)
        self.commands["Striked"].append(self.thefont.setStrikeOut)
        self.commands["Italic"] = []
        self.commands["Italic"].append(self.myformat.setFontItalic)
        self.commands["Italic"].append(self.thefont.setItalic)


        self.mycursor.beginEditBlock()
        if self.mycursor.hasSelection():
            if thebutton.isChecked():
                self.commands[commandname][0](posvalueselected)
            else:
                self.commands[commandname][0](negvalueselected)
            self.mycursor.mergeCharFormat(self.myformat)
        elif self.mycursor.position() >= 0:
            tempvar = self.getButtonsstatuses()
            for i in tempvar.iterkeys():
                self.commands[i][1](tempvar[i])
            if thebutton.isChecked():
                self.commands[commandname][1](posvalueposition)
                self.messagecontainer.setCurrentFont(self.thefont)
            else:
                self.commands[commandname][1](negvalueposition)
                self.messagecontainer.setCurrentFont(self.thefont)
        self.mycursor.endEditBlock()

    #Getting current style and setting according checked states to buttons
    def getCurrentStyle(self):
        mycursor = self.messagecontainer.textCursor()
        if mycursor.hasSelection():
            print "sdf"
        elif mycursor.position() >= 0:
            self.setButtonsStates()
        else:
            return False

    def getButtonsstatuses(self):
        ButtonStatuses = {}
        ButtonStatuses["Bold"] = self.ui.pushButtonBold.isChecked()
        ButtonStatuses["Underlined"] = self.ui.pushButtonUnderline.isChecked()
        ButtonStatuses["Striked"] = self.ui.pushButtonStrike.isChecked()
        ButtonStatuses["Italic"] = self.ui.pushButtonItalic.isChecked()
        return ButtonStatuses

    def setButtonsStates(self):
        #setting basic buttons statuses
        self.ui.pushButtonBold.setChecked(self.messagecontainer.currentFont().bold())
        self.ui.pushButtonItalic.setChecked(self.messagecontainer.currentFont().italic())
        self.ui.pushButtonUnderline.setChecked(self.messagecontainer.currentFont().underline())
        self.ui.pushButtonStrike.setChecked(self.messagecontainer.currentFont().strikeOut())
        theindex = self.ui.comboBoxFontSize.findText(str(self.messagecontainer.currentFont().pointSize()))
        self.ui.comboBoxFontSize.setCurrentIndex(theindex)
        #setting corresponding alignment button's status
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

        self.setStyle(self.ui.pushButtonBold, "Bold", QFont.Bold, QFont.Normal, True, False)

    def click_pushButtonUnderline(self):

        self.setStyle(self.ui.pushButtonUnderline, "Underlined", True, False, True, False)

    def click_pushButtonStrike(self):

        self.setStyle(self.ui.pushButtonStrike, "Striked", True, False, True, False)

    def click_pushButtonItalic(self):

        self.setStyle(self.ui.pushButtonItalic, "Italic", True, False, True, False)

    def click_comboBoxFontSize(self, fontsize):

        if self.mycursor.hasSelection():
            self.mycursor.beginEditBlock()
            self.myformat.setFontPointSize(float(fontsize))
            self.mycursor.mergeCharFormat(self.myformat)
            self.mycursor.endEditBlock()
        elif self.mycursor.position() >= 0:
            self.mycursor.beginEditBlock()
            self.messagecontainer.setFontPointSize(float(fontsize))
            self.mycursor.endEditBlock()
        else:
            return False

    def click_pushButtonFontIncrease(self):
        curfontsize = self.messagecontainer.currentFont().pointSize()
        currindex = self.FontSizes.index(curfontsize)
        if currindex >= 0 and currindex+1 < len(self.FontSizes):
            if self.mycursor.hasSelection():
                self.mycursor.beginEditBlock()
                fontsizetobe = self.FontSizes[currindex+1]
                self.myformat.setFontPointSize(float(fontsizetobe))
                self.ui.comboBoxFontSize.setCurrentIndex(currindex+1)
                self.mycursor.mergeCharFormat(self.myformat)
                self.mycursor.endEditBlock()
            elif self.mycursor.position() >= 0:
                self.mycursor.beginEditBlock()
                fontsizetobe = self.FontSizes[currindex+1]
                self.messagecontainer.setFontPointSize(float(fontsizetobe))
                self.ui.comboBoxFontSize.setCurrentIndex(currindex+1)
                self.mycursor.endEditBlock()
        else:
            return False

    def click_pushButtonFontDecrease(self):
        curfontsize = self.messagecontainer.currentFont().pointSize()
        currindex = self.FontSizes.index(curfontsize)
        if currindex and currindex-1 >= 0:
            if self.mycursor.hasSelection():
                self.mycursor.beginEditBlock()
                fontsizetobe = self.FontSizes[currindex-1]
                self.myformat.setFontPointSize(float(fontsizetobe))
                self.ui.comboBoxFontSize.setCurrentIndex(currindex-1)
                self.mycursor.mergeCharFormat(self.myformat)
                self.mycursor.endEditBlock()
            elif self.mycursor.position() >= 0:
                self.mycursor.beginEditBlock()
                fontsizetobe = self.FontSizes[currindex-1]
                self.messagecontainer.setFontPointSize(float(fontsizetobe))
                self.ui.comboBoxFontSize.setCurrentIndex(currindex-1)
                self.mycursor.endEditBlock()
        else:
            return False

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

    def InitializeFontComboBox(self):
        for i in range(0, len(self.FontSizes), 1):
            self.ui.comboBoxFontSize.addItem("")
            self.ui.comboBoxFontSize.setItemText(i, str(self.FontSizes[i]))
        self.ui.comboBoxFontSize.setCurrentIndex(6)

    def click_pushButtonPastPlainText(self):

        self.messagecontainer.insertPlainText(QApplication.clipboard().text())

    def click_pushButtonPastFormattedText(self):

        self.messagecontainer.paste()

    def click_pushButtonClear(self):

        self.messagecontainer.clear()

    def Alignment_Buttons_Checked_Status(self, initiator, to_uncheck1, to_uncheck2, to_uncheck3):
        if initiator.isChecked():
            to_uncheck1.setChecked(False)
            to_uncheck2.setChecked(False)
            to_uncheck3.setChecked(False)

    def click_pushButtonAlignmentCenter(self):
        self.Alignment_Buttons_Checked_Status(self.ui.pushButtonAlignmentCenter, self.ui.pushButtonAlignmentRight, self.ui.pushButtonAlignmentLeft, self.ui.pushButtonAlignmentJustify)
        self.messagecontainer.setAlignment(QtCore.Qt.AlignCenter)

    def click_pushButtonAlignmentLeft(self):
        self.Alignment_Buttons_Checked_Status(self.ui.pushButtonAlignmentLeft, self.ui.pushButtonAlignmentRight, self.ui.pushButtonAlignmentCenter, self.ui.pushButtonAlignmentJustify)
        self.messagecontainer.setAlignment(QtCore.Qt.AlignLeft)

    def click_pushButtonAlignmentRight(self):
        self.Alignment_Buttons_Checked_Status(self.ui.pushButtonAlignmentRight, self.ui.pushButtonAlignmentLeft, self.ui.pushButtonAlignmentCenter, self.ui.pushButtonAlignmentJustify)
        self.messagecontainer.setAlignment(QtCore.Qt.AlignRight)

    def click_pushButtonAlignmentJustify(self):
        self.Alignment_Buttons_Checked_Status(self.ui.pushButtonAlignmentJustify, self.ui.pushButtonAlignmentLeft, self.ui.pushButtonAlignmentRight, self.ui.pushButtonAlignmentCenter)
        self.messagecontainer.setAlignment(QtCore.Qt.AlignJustify)

    def click_pushButtonUndo(self):

        self.messagecontainer.undo()

    def click_pushButtonRedo(self):

        self.messagecontainer.redo()
