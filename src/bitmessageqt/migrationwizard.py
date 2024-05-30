from qtpy import QtCore, QtWidgets

class MigrationWizardIntroPage(QtWidgets.QWizardPage):
    def __init__(self):
        super(QtWidgets.QWizardPage, self).__init__()
        self.setTitle("Migrating configuration")

        label = QtWidgets.QLabel("This wizard will help you to migrate your configuration. "
            "You can still keep using PyBitMessage once you migrate, the changes are backwards compatible.")
        label.setWordWrap(True)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)
        
    def nextId(self):
        return 1
    

class MigrationWizardAddressesPage(QtWidgets.QWizardPage):
    def __init__(self, addresses):
        super(QtWidgets.QWizardPage, self).__init__()
        self.setTitle("Addresses")

        label = QtWidgets.QLabel("Please select addresses that you are already using with mailchuck. ")
        label.setWordWrap(True)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)
        
    def nextId(self):
        return 10
    

class MigrationWizardGPUPage(QtWidgets.QWizardPage):
    def __init__(self):
        super(QtWidgets.QWizardPage, self).__init__()
        self.setTitle("GPU")

        label = QtWidgets.QLabel("Are you using a GPU? ")
        label.setWordWrap(True)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)
        
    def nextId(self):
        return 10
    

class MigrationWizardConclusionPage(QtWidgets.QWizardPage):
    def __init__(self):
        super(QtWidgets.QWizardPage, self).__init__()
        self.setTitle("All done!")

        label = QtWidgets.QLabel("You successfully migrated.")
        label.setWordWrap(True)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)


class Ui_MigrationWizard(QtWidgets.QWizard):
    def __init__(self, addresses):
        super(QtWidgets.QWizard, self).__init__()

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
