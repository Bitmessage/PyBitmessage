#!/usr/bin/env python2.7
"""
src/bitmessageqt/migrationwizard.py
===============================

"""
# pylint: disable=too-few-public-methods,no-self-use,unused-argument
from PyQt4 import QtGui


class MigrationWizardIntroPage(QtGui.QWizardPage):
    """MigrationWizardIntroPage class for Qt UI"""
    def __init__(self):
        super(QtGui.QWizardPage, self).__init__()
        self.setTitle("Migrating configuration")

        label = QtGui.QLabel("This wizard will help you to migrate your configuration. "
                             "You can still keep using PyBitMessage once you migrate, "
                             "the changes are backwards compatible.")
        label.setWordWrap(True)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)

    def nextId(self):
        """It returns next id"""
        return 1


class MigrationWizardAddressesPage(QtGui.QWizardPage):
    """MigrationWizardAddressesPage class for Qt Ui"""
    def __init__(self, addresses):
        super(QtGui.QWizardPage, self).__init__()
        self.setTitle("Addresses")

        label = QtGui.QLabel("Please select addresses that you are already using with mailchuck. ")
        label.setWordWrap(True)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)

    def nextId(self):
        """It returns next id"""
        return 10


class MigrationWizardGPUPage(QtGui.QWizardPage):
    """MigrationWizardGPUPage class for Qt Ui"""
    def __init__(self):
        super(QtGui.QWizardPage, self).__init__()
        self.setTitle("GPU")

        label = QtGui.QLabel("Are you using a GPU? ")
        label.setWordWrap(True)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)

    def nextId(self):
        """It returns next id"""
        return 10


class MigrationWizardConclusionPage(QtGui.QWizardPage):
    """MigrationWizardConclusionPage class for Qt Ui"""
    def __init__(self):
        super(QtGui.QWizardPage, self).__init__()
        self.setTitle("All done!")

        label = QtGui.QLabel("You successfully migrated.")
        label.setWordWrap(True)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)


class Ui_MigrationWizard(QtGui.QWizard):
    """Ui_MigrationWizard class for Qt Ui"""
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
