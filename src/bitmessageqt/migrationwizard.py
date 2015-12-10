#!/usr/bin/env python2.7
from PyQt4 import QtCore, QtGui

class MigrationWizardIntroPage(QtGui.QWizardPage):
    def __init__(self):
        super(QtGui.QWizardPage, self).__init__()
        self.setTitle("Migrating configuration")

        label = QtGui.QLabel("This wizard will help you to migrate your configuration. "
            "You can still keep using PyBitMessage once you migrate, the changes are backwards compatible.")
        label.setWordWrap(True)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)
        
    def nextId(self):
        return 1
    

class MigrationWizardAddressesPage(QtGui.QWizardPage):
    def __init__(self, addresses):
        super(QtGui.QWizardPage, self).__init__()
        self.setTitle("Addresses")

        label = QtGui.QLabel("Please select addresses that you are already using with mailchuck. ")
        label.setWordWrap(True)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)
        
    def nextId(self):
        return 10
    

class MigrationWizardGPUPage(QtGui.QWizardPage):
    def __init__(self):
        super(QtGui.QWizardPage, self).__init__()
        self.setTitle("GPU")

        label = QtGui.QLabel("Are you using a GPU? ")
        label.setWordWrap(True)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)
        
    def nextId(self):
        return 10
    

class MigrationWizardConclusionPage(QtGui.QWizardPage):
    def __init__(self):
        super(QtGui.QWizardPage, self).__init__()
        self.setTitle("All done!")

        label = QtGui.QLabel("You successfully migrated.")
        label.setWordWrap(True)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)


class Ui_MigrationWizard(QtGui.QWizard):
    def __init__(self, addresses):
        super(QtGui.QWizard, self).__init__()

        self.pages = {}
        
        page = MigrationWizardIntroPage()
        self.setPage(0, page)
        self.setStartId(0)
        page = MigrationWizardAddressesPage(addresses)
        self.setPage(1, page)
        page = MigrationWizardGPUPage()
        self.setPage(2, page)
        page = MigrationWizardConclusionPage()
        self.setPage(10, page)

        self.setWindowTitle("Migration from PyBitMessage wizard")
        self.adjustSize()
        self.show()