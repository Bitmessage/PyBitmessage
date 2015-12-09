#!/usr/bin/python2.7

from PyQt4 import QtCore, QtGui

class SettingsMixin(object):
    def warnIfNoObjectName(self):
        if self.objectName() == "":
            # TODO: logger
            pass
    
    def writeState(self, source):
        self.warnIfNoObjectName()
        settings = QtCore.QSettings()
        settings.beginGroup(self.objectName())
        settings.setValue("state", source.saveState())
        settings.endGroup()
    
    def writeGeometry(self, source):
        self.warnIfNoObjectName()
        settings = QtCore.QSettings()
        settings.beginGroup(self.objectName())
        settings.setValue("geometry", source.saveGeometry())
        settings.endGroup()
        
    def readGeometry(self, target):
        self.warnIfNoObjectName()
        settings = QtCore.QSettings()
        try:
            geom = settings.value("/".join([str(self.objectName()), "geometry"]))
            target.restoreGeometry(geom.toByteArray() if hasattr(geom, 'toByteArray') else geom)
        except Exception as e:
            pass

    def readState(self, target):
        self.warnIfNoObjectName()
        settings = QtCore.QSettings()
        try:
            state = settings.value("/".join([str(self.objectName()), "state"]))
            target.restoreState(state.toByteArray() if hasattr(state, 'toByteArray') else state)
        except Exception as e:
            pass

            
class SMainWindow(QtGui.QMainWindow, SettingsMixin):
    def loadSettings(self):
        self.readGeometry(self)
        self.readState(self)
        
    def saveSettings(self):
        self.writeState(self)
        self.writeGeometry(self)


class STableWidget(QtGui.QTableWidget, SettingsMixin):
    def loadSettings(self):
        self.readState(self.horizontalHeader())

    def saveSettings(self):
        self.writeState(self.horizontalHeader())

        
class SSplitter(QtGui.QSplitter, SettingsMixin):
    def loadSettings(self):
        self.readState(self)

    def saveSettings(self):
        self.writeState(self)
        

class STreeWidget(QtGui.QTreeWidget, SettingsMixin):
    def loadSettings(self):
        #recurse children
        #self.readState(self)
        pass

    def saveSettings(self):
        #recurse children
        #self.writeState(self)
        pass
