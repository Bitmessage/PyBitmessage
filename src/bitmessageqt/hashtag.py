# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'hashtag.ui'
#
# Created: Mon Nov 11 18:53:39 2013
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_hashtagDialog(object):
    def setupUi(self, hashtagDialog):
        hashtagDialog.setObjectName(_fromUtf8("hashtagDialog"))
        hashtagDialog.resize(550, 380)
        self.buttonBox = QtGui.QDialogButtonBox(hashtagDialog)
        self.buttonBox.setGeometry(QtCore.QRect(190, 330, 111, 31))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.hastgaLabel = QtGui.QLabel(hashtagDialog)
        self.hastgaLabel.setGeometry(QtCore.QRect(150, 20, 211, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.hastgaLabel.setFont(font)
        self.hastgaLabel.setObjectName(_fromUtf8("hastgaLabel"))
        self.tableWidgetHashtag = QtGui.QTableWidget(hashtagDialog)
        self.tableWidgetHashtag.setGeometry(QtCore.QRect(50, 70, 401, 234))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidgetHashtag.sizePolicy().hasHeightForWidth())
        self.tableWidgetHashtag.setSizePolicy(sizePolicy)
        self.tableWidgetHashtag.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tableWidgetHashtag.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tableWidgetHashtag.setObjectName(_fromUtf8("tableWidgetHashtag"))
        self.tableWidgetHashtag.setColumnCount(4)
        self.tableWidgetHashtag.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetHashtag.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetHashtag.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetHashtag.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetHashtag.setHorizontalHeaderItem(3, item)
        self.tableWidgetHashtag.verticalHeader().setVisible(False)
        self.label = QtGui.QLabel(hashtagDialog)
        self.label.setGeometry(QtCore.QRect(460, 160, 81, 61))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Abyssinica SIL"))
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(hashtagDialog)
        self.label_2.setGeometry(QtCore.QRect(470, 110, 61, 61))
        self.label_2.setText(_fromUtf8(""))
        self.label_2.setPixmap(QtGui.QPixmap(_fromUtf8(":/imagesPrefix/images/arrow-28-48(1).png")))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(hashtagDialog)
        self.label_3.setGeometry(QtCore.QRect(470, 220, 58, 61))
        self.label_3.setText(_fromUtf8(""))
        self.label_3.setPixmap(QtGui.QPixmap(_fromUtf8(":/imagesPrefix/images/arrow-28-48.png")))
        self.label_3.setObjectName(_fromUtf8("label_3"))

        self.retranslateUi(hashtagDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), hashtagDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), hashtagDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(hashtagDialog)

    def retranslateUi(self, hashtagDialog):
        hashtagDialog.setWindowTitle(QtGui.QApplication.translate("hashtagDialog", "Hashtag", None, QtGui.QApplication.UnicodeUTF8))
        self.hastgaLabel.setText(QtGui.QApplication.translate("hashtagDialog", "Trending Hashtags", None, QtGui.QApplication.UnicodeUTF8))
        item = self.tableWidgetHashtag.horizontalHeaderItem(0)
        item.setText(QtGui.QApplication.translate("hashtagDialog", "Day", None, QtGui.QApplication.UnicodeUTF8))
        item = self.tableWidgetHashtag.horizontalHeaderItem(1)
        item.setText(QtGui.QApplication.translate("hashtagDialog", "Week", None, QtGui.QApplication.UnicodeUTF8))
        item = self.tableWidgetHashtag.horizontalHeaderItem(2)
        item.setText(QtGui.QApplication.translate("hashtagDialog", "Month", None, QtGui.QApplication.UnicodeUTF8))
        item = self.tableWidgetHashtag.horizontalHeaderItem(3)
        item.setText(QtGui.QApplication.translate("hashtagDialog", "All Time", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("hashtagDialog", "Popularity", None, QtGui.QApplication.UnicodeUTF8))

import bitmessage_images_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    hashtagDialog = QtGui.QDialog()
    ui = Ui_hashtagDialog()
    ui.setupUi(hashtagDialog)
    hashtagDialog.show()
    sys.exit(app.exec_())

