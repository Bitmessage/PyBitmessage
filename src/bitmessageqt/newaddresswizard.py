#!/usr/bin/env python2.7
from PyQt4 import QtCore, QtGui

class NewAddressWizardIntroPage(QtGui.QWizardPage):
    def __init__(self):
        super(QtGui.QWizardPage, self).__init__()
        self.setTitle("Creating a new address")

        label = QtGui.QLabel("This wizard will help you create as many addresses as you like. Indeed, creating and abandoning addresses is encouraged.\n\n"
            "What type of address would you like? Would you like to send emails or not?\n"
            "You can still change your mind later, and register/unregister with an email service provider.\n\n")
        label.setWordWrap(True)

        self.emailAsWell = QtGui.QRadioButton("Combined email and bitmessage address")
        self.onlyBM = QtGui.QRadioButton("Bitmessage-only address (no email)")
        self.emailAsWell.setChecked(True)
        self.registerField("emailAsWell", self.emailAsWell)
        self.registerField("onlyBM", self.onlyBM)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.emailAsWell)
        layout.addWidget(self.onlyBM)
        self.setLayout(layout)
        
    def nextId(self):
        if self.emailAsWell.isChecked():
            return 4
        else:
            return 1
    

class NewAddressWizardRngPassphrasePage(QtGui.QWizardPage):
    def __init__(self):
        super(QtGui.QWizardPage, self).__init__()
        self.setTitle("Random or Passphrase")

        label = QtGui.QLabel("<html><head/><body><p>You may generate addresses by using either random numbers or by using a passphrase. "
            "If you use a passphrase, the address is called a &quot;deterministic&quot; address. "
            "The \'Random Number\' option is selected by default but deterministic addresses have several pros and cons:</p>"
            "<table border=0><tr><td><span style=\" font-weight:600;\">Pros:</span></td><td><span style=\" font-weight:600;\">Cons:</span></td></tr>"
            "<tr><td>You can recreate your addresses on any computer from memory. "
            "You need-not worry about backing up your keys.dat file as long as you can remember your passphrase.</td>"
            "<td>You must remember (or write down) your passphrase if you expect to be able "
            "to recreate your keys if they are lost. "
#            "You must remember the address version number and the stream number along with your passphrase. "
            "If you choose a weak passphrase and someone on the Internet can brute-force it, they can read your messages and send messages as you."
            "</p></body></html>")
        label.setWordWrap(True)

        self.randomAddress = QtGui.QRadioButton("Use a random number generator to make an address")
        self.deterministicAddress = QtGui.QRadioButton("Use a passphrase to make an address")
        self.randomAddress.setChecked(True)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.randomAddress)
        layout.addWidget(self.deterministicAddress)
        self.setLayout(layout)

    def nextId(self):
        if self.randomAddress.isChecked():
            return 2
        else:
            return 3

class NewAddressWizardRandomPage(QtGui.QWizardPage):
    def __init__(self, addresses):
        super(QtGui.QWizardPage, self).__init__()
        self.setTitle("Random")

        label = QtGui.QLabel("Random address.")
        label.setWordWrap(True)

        labelLabel = QtGui.QLabel("Label (not shown to anyone except you):")
        self.labelLineEdit = QtGui.QLineEdit()

        self.radioButtonMostAvailable = QtGui.QRadioButton("Use the most available stream\n"
            "(best if this is the first of many addresses you will create)")
        self.radioButtonExisting = QtGui.QRadioButton("Use the same stream as an existing address\n"
            "(saves you some bandwidth and processing power)")
        self.radioButtonMostAvailable.setChecked(True)
        self.comboBoxExisting = QtGui.QComboBox()
        self.comboBoxExisting.setEnabled(False)
        self.comboBoxExisting.setEditable(True)

        for address in addresses:
            self.comboBoxExisting.addItem(address)
        
#        self.comboBoxExisting.setObjectName(_fromUtf8("comboBoxExisting"))
        self.checkBoxEighteenByteRipe = QtGui.QCheckBox("Spend several minutes of extra computing time to make the address(es) 1 or 2 characters shorter")
        
        layout = QtGui.QGridLayout()
        layout.addWidget(label, 0, 0)
        layout.addWidget(labelLabel, 1, 0)
        layout.addWidget(self.labelLineEdit, 2, 0)
        layout.addWidget(self.radioButtonMostAvailable, 3, 0)
        layout.addWidget(self.radioButtonExisting, 4, 0)
        layout.addWidget(self.comboBoxExisting, 5, 0)
        layout.addWidget(self.checkBoxEighteenByteRipe, 6, 0)
        self.setLayout(layout)

        QtCore.QObject.connect(self.radioButtonExisting, QtCore.SIGNAL("toggled(bool)"), self.comboBoxExisting.setEnabled)
        
        self.registerField("label", self.labelLineEdit)
        self.registerField("radioButtonMostAvailable", self.radioButtonMostAvailable)
        self.registerField("radioButtonExisting", self.radioButtonExisting)
        self.registerField("comboBoxExisting", self.comboBoxExisting)

#        self.emailAsWell = QtGui.QRadioButton("Combined email and bitmessage account")
#        self.onlyBM = QtGui.QRadioButton("Bitmessage-only account (no email)")
#        self.emailAsWell.setChecked(True)

    def nextId(self):
        return 6

        
class NewAddressWizardPassphrasePage(QtGui.QWizardPage):
    def __init__(self):
        super(QtGui.QWizardPage, self).__init__()
        self.setTitle("Passphrase")

        label = QtGui.QLabel("Deterministric address.")
        label.setWordWrap(True)

        passphraseLabel = QtGui.QLabel("Passphrase")
        self.lineEditPassphrase = QtGui.QLineEdit()
        self.lineEditPassphrase.setEchoMode(QtGui.QLineEdit.Password)
        self.lineEditPassphrase.setInputMethodHints(QtCore.Qt.ImhHiddenText|QtCore.Qt.ImhNoAutoUppercase|QtCore.Qt.ImhNoPredictiveText)
        retypePassphraseLabel = QtGui.QLabel("Retype passphrase")
        self.lineEditPassphraseAgain = QtGui.QLineEdit()
        self.lineEditPassphraseAgain.setEchoMode(QtGui.QLineEdit.Password)

        numberLabel = QtGui.QLabel("Number of addresses to make based on your passphrase:")
        self.spinBoxNumberOfAddressesToMake = QtGui.QSpinBox()
        self.spinBoxNumberOfAddressesToMake.setMinimum(1)
        self.spinBoxNumberOfAddressesToMake.setProperty("value", 8)
#        self.spinBoxNumberOfAddressesToMake.setObjectName(_fromUtf8("spinBoxNumberOfAddressesToMake"))
        label2 = QtGui.QLabel("In addition to your passphrase, you must remember these numbers:")
        label3 = QtGui.QLabel("Address version number: 4")
        label4 = QtGui.QLabel("Stream number: 1")
        
        layout = QtGui.QGridLayout()
        layout.addWidget(label, 0, 0, 1, 4)
        layout.addWidget(passphraseLabel, 1, 0, 1, 4)
        layout.addWidget(self.lineEditPassphrase, 2, 0, 1, 4)
        layout.addWidget(retypePassphraseLabel, 3, 0, 1, 4)
        layout.addWidget(self.lineEditPassphraseAgain, 4, 0, 1, 4)
        layout.addWidget(numberLabel, 5, 0, 1, 3)
        layout.addWidget(self.spinBoxNumberOfAddressesToMake, 5, 3)
        layout.setColumnMinimumWidth(3, 1)
        layout.addWidget(label2, 6, 0, 1, 4)
        layout.addWidget(label3, 7, 0, 1, 2)
        layout.addWidget(label4, 7, 2, 1, 2)
        self.setLayout(layout)

    def nextId(self):
        return 6

        
class NewAddressWizardEmailProviderPage(QtGui.QWizardPage):
    def __init__(self):
        super(QtGui.QWizardPage, self).__init__()
        self.setTitle("Choose email provider")

        label = QtGui.QLabel("Currently only Mailchuck email gateway is available "
            "(@mailchuck.com email address). In the future, maybe other gateways will be available. "
            "Press Next.")
        label.setWordWrap(True)

#        self.mailchuck = QtGui.QRadioButton("Mailchuck email gateway (@mailchuck.com)")
#        self.mailchuck.setChecked(True)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
#        layout.addWidget(self.mailchuck)
        self.setLayout(layout)

    def nextId(self):
        return 5

        
class NewAddressWizardEmailAddressPage(QtGui.QWizardPage):
    def __init__(self):
        super(QtGui.QWizardPage, self).__init__()
        self.setTitle("Email address")

        label = QtGui.QLabel("Choosing an email address. Address must end with @mailchuck.com")
        label.setWordWrap(True)

        self.specificEmail = QtGui.QRadioButton("Pick your own email address:")
        self.specificEmail.setChecked(True)
        self.emailLineEdit = QtGui.QLineEdit()
        self.randomEmail = QtGui.QRadioButton("Generate a random email address")
        
        QtCore.QObject.connect(self.specificEmail, QtCore.SIGNAL("toggled(bool)"), self.emailLineEdit.setEnabled)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.specificEmail)
        layout.addWidget(self.emailLineEdit)
        layout.addWidget(self.randomEmail)
        self.setLayout(layout)

    def nextId(self):
        return 6

        
class NewAddressWizardWaitPage(QtGui.QWizardPage):
    def __init__(self):
        super(QtGui.QWizardPage, self).__init__()
        self.setTitle("Wait")
        
        self.label = QtGui.QLabel("Wait!")
        self.label.setWordWrap(True)
        self.progressBar = QtGui.QProgressBar()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)
        
#        self.emailAsWell = QtGui.QRadioButton("Combined email and bitmessage account")
#        self.onlyBM = QtGui.QRadioButton("Bitmessage-only account (no email)")
#        self.emailAsWell.setChecked(True)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.progressBar)
#        layout.addWidget(self.emailAsWell)
#        layout.addWidget(self.onlyBM)
        self.setLayout(layout)

    def update(self, i):
        if i == 101 and self.wizard().currentId() == 6:
            self.wizard().button(QtGui.QWizard.NextButton).click()
            return
        elif i == 101:
            print("haha")
            return
        self.progressBar.setValue(i)
        if i == 50:
            self.emit(QtCore.SIGNAL('completeChanged()'))
            
    def isComplete(self):
#        print "val = " + str(self.progressBar.value())
        if self.progressBar.value() >= 50:
            return True
        else:
            return False
    
    def initializePage(self):
        if self.field("emailAsWell").toBool():
            val = "yes/"
        else:
            val = "no/"
        if self.field("onlyBM").toBool():
            val += "yes"
        else:
            val += "no"

        self.label.setText("Wait! " + val)
#        self.wizard().button(QtGui.QWizard.NextButton).setEnabled(False)
        self.progressBar.setValue(0)
        self.thread = NewAddressThread()
        self.connect(self.thread, self.thread.signal, self.update)
        self.thread.start()
    
    def nextId(self):
        return 10

        
class NewAddressWizardConclusionPage(QtGui.QWizardPage):
    def __init__(self):
        super(QtGui.QWizardPage, self).__init__()
        self.setTitle("All done!")

        label = QtGui.QLabel("You successfully created a new address.")
        label.setWordWrap(True)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)        

class Ui_NewAddressWizard(QtGui.QWizard):
    def __init__(self, addresses):
        super(QtGui.QWizard, self).__init__()

        self.pages = {}
        
        page = NewAddressWizardIntroPage()
        self.setPage(0, page)
        self.setStartId(0)
        page = NewAddressWizardRngPassphrasePage()
        self.setPage(1, page)
        page = NewAddressWizardRandomPage(addresses)
        self.setPage(2, page)
        page = NewAddressWizardPassphrasePage()
        self.setPage(3, page)
        page = NewAddressWizardEmailProviderPage()
        self.setPage(4, page)
        page = NewAddressWizardEmailAddressPage()
        self.setPage(5, page)
        page = NewAddressWizardWaitPage()
        self.setPage(6, page)
        page = NewAddressWizardConclusionPage()
        self.setPage(10, page)

        self.setWindowTitle("New address wizard")
        self.adjustSize()
        self.show()

class NewAddressThread(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.signal = QtCore.SIGNAL("signal")

    def __del__(self):
        self.wait()
        
    def createDeterministic(self):
        pass
        
    def createPassphrase(self):
        pass
    
    def broadcastAddress(self):
        pass
    
    def registerMailchuck(self):
        pass
    
    def waitRegistration(self):
        pass

    def run(self):
        import time
        for i in range(1, 101):
            time.sleep(0.1) # artificial time delay
            self.emit(self.signal, i)
        self.emit(self.signal, 101)
#        self.terminate()

if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)

    wizard = Ui_NewAddressWizard(["a", "b", "c", "d"])
    if (wizard.exec_()):
        print("Email: " + ("yes" if wizard.field("emailAsWell").toBool() else "no"))
        print("BM: " + ("yes" if wizard.field("onlyBM").toBool() else "no"))
    else:
        print("Wizard cancelled")
    sys.exit()
