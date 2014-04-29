# Copyright (c) 2014 Luke Montalvo <lukemontalvo@gmail.com>
# This file adds a alternative commandline interface, feel free to critique and fork
# 
# This has only been tested on Arch Linux
# Dependencies:
#  * from python2-pip
#     * python2-pythondialog
#  * dialog

import os
import sys
import StringIO

import time
from time import strftime, localtime
from threading import Timer

import curses
import dialog
from dialog import Dialog
from helper_sql import *

import shared
import ConfigParser
from addresses import *
from pyelliptic.openssl import OpenSSL

quit = False
menutab = 1
menu = ["Inbox", "Send", "Sent", "Your Identities", "Subscriptions", "Address Book", "Blacklist", "Network Status"]
naptime = 100
log = ""
logpad = None
inventorydata = 0
startuptime = time.time()

inbox = []
inboxcur = 0
sent = []
sentcur = 0
addresses = []
addrcur = 0
addrcopy = 0
subscriptions = []
subcur = 0
addrbook = []
abookcur = 0
blacklist = []
blackcur = 0

BROADCAST_STR = "[Broadcast subscribers]"

class printLog:
    def write(self, output):
        global log
        log += output
    def flush(self):
        pass
class errLog:
    def write(self, output):
        global log
        log += "!"+output
    def flush(self):
        pass
printlog = printLog()
errlog = errLog()


def cpair(a):
    r = curses.color_pair(a)
    if r not in range(1, curses.COLOR_PAIRS-1):
        r = curses.color_pair(0)
    return r
def ascii(s):
    r = ""
    for c in s:
        if ord(c) in range(128):
            r += c
    return r

def drawmenu(stdscr):
    menustr = " "
    for i in range(0, len(menu)):
        if menutab == i+1:
            menustr = menustr[:-1]
            menustr += "["
        menustr += str(i+1)+menu[i]
        if menutab == i+1:
            menustr += "] "
        elif i != len(menu)-1:
            menustr += "  "
    stdscr.addstr(2, 5, menustr, curses.A_UNDERLINE)

def resetlookups():
    global inventorydata
    inventorydata = shared.numberOfInventoryLookupsPerformed
    shared.numberOfInventoryLookupsPerformed = 0
    Timer(1, resetlookups, ()).start()
def drawtab(stdscr):
    if menutab in range(1, len(menu)+1):
        if menutab == 1: # Inbox
            stdscr.addstr(3, 5, "To", curses.A_BOLD)
            stdscr.addstr(3, 30, "From", curses.A_BOLD)
            stdscr.addstr(3, 60, "Subject", curses.A_BOLD)
            stdscr.addstr(3, 90, "Time Received", curses.A_BOLD)
            stdscr.hline(4, 5, '-', 91)
            for i, item in enumerate(inbox[max(min(len(inbox)-curses.LINES+6, inboxcur-5), 0):]):
                if 6+i < curses.LINES:
                    a = 0
                    if i == inboxcur - max(min(len(inbox)-curses.LINES+6, inboxcur-5), 0): # Highlight current address
                        a = a | curses.A_REVERSE
                    if item[7] == False: # If not read, highlight
                        a = a | curses.A_BOLD
                    stdscr.addstr(5+i, 5, item[1][:29], a)
                    stdscr.addstr(5+i, 30, item[3][:29], a)
                    stdscr.addstr(5+i, 60, item[5][:29], a)
                    stdscr.addstr(5+i, 90, item[6][:29], a)
        elif menutab == 3: # Sent
            pass
        elif menutab == 2 or menutab == 4: # Send or Identities
            stdscr.addstr(3, 5, "Label", curses.A_BOLD)
            stdscr.addstr(3, 30, "Address", curses.A_BOLD)
            stdscr.addstr(3, 60, "Stream", curses.A_BOLD)
            stdscr.hline(4, 5, '-', 61)
            for i, item in enumerate(addresses[max(min(len(addresses)-curses.LINES+6, addrcur-5), 0):]):
                a = 0
                if i == addrcur - max(min(len(addresses)-curses.LINES+6, addrcur-5), 0): # Highlight current address
                    a = a | curses.A_REVERSE
                if item[1] == True and item[3] not in [8,9]: # Embolden enabled, non-special addresses
                    a = a | curses.A_BOLD
                stdscr.addstr(5+i, 5, item[0][:30], a)
                stdscr.addstr(5+i, 30, item[2][:30], cpair(item[3]) | a)
                stdscr.addstr(5+i, 60, str(1)[:30], a)
        elif menutab == 5: # Subscriptions
            pass
        elif menutab == 6: # Address book
            stdscr.addstr(3, 5, "Label", curses.A_BOLD)
            stdscr.addstr(3, 30, "Address", curses.A_BOLD)
            stdscr.hline(4, 5, '-', 31)
            for i, item in enumerate(addrbook[max(min(len(addrbook)-curses.LINES+6, abookcur-5), 0):]):
                a = 0
                if i == abookcur - max(min(len(addrbook)-curses.LINES+6, abookcur-5), 0): # Highlight current address
                    a = a | curses.A_REVERSE
                stdscr.addstr(5+i, 5, item[0][:30], a)
                stdscr.addstr(5+i, 30, item[1][:30], a)
        elif menutab == 7: # Blacklist
            pass
        elif menutab == 8: # Network status
            # Connection data
            stdscr.addstr(4, 5, "Total Connections: "+str(len(shared.connectedHostsList)).ljust(2))
            stdscr.addstr(6, 6, "Stream #", curses.A_BOLD)
            stdscr.addstr(6, 18, "Connections", curses.A_BOLD)
            stdscr.hline(7, 6, '-', 23)
            streamcount = []
            for host, stream in shared.connectedHostsList.items():
                if stream >= len(streamcount):
                    streamcount.append(1)
                else:
                    streamcount[stream] += 1
            for i, item in enumerate(streamcount):
                if i < 4:
                    if i == 0:
                        stdscr.addstr(8+i, 6, "?")
                    else:
                        stdscr.addstr(8+i, 6, str(i))
                    stdscr.addstr(8+i, 18, str(item).ljust(2))
            
            # Uptime and processing data
            stdscr.addstr(6, 35, "Since startup on "+unicode(strftime(shared.config.get('bitmessagesettings', 'timeformat'), localtime(int(startuptime)))))
            stdscr.addstr(7, 40, "Processed "+str(shared.numberOfMessagesProcessed).ljust(4)+" person-to-person messages.")
            stdscr.addstr(8, 40, "Processed "+str(shared.numberOfBroadcastsProcessed).ljust(4)+" broadcast messages.")
            stdscr.addstr(9, 40, "Processed "+str(shared.numberOfPubkeysProcessed).ljust(4)+" public keys.")
            
            # Inventory data
            stdscr.addstr(11, 35, "Inventory lookups per second: "+str(inventorydata).ljust(3))
            
            # Log
            stdscr.addstr(13, 6, "Log", curses.A_BOLD)
            n = log.count('\n')
            if n > 0:
                l = log.split('\n')
                if n > 512:
                    del l[:(n-256)]
                    logpad.erase()
                    n = len(l)
                for i, item in enumerate(l):
                    a = 0
                    if len(item) > 0 and item[0] == '!':
                        a = curses.color_pair(1)
                        item = item[1:]
                    logpad.addstr(i, 0, item, a)
                logpad.refresh(n-curses.LINES+2, 0, 14, 6, curses.LINES-2, curses.COLS-7)
    stdscr.refresh()

def redraw(stdscr):
    stdscr.erase()
    stdscr.border()
    drawmenu(stdscr)
    stdscr.refresh()
def dialogreset(stdscr):
    stdscr.clear()
    stdscr.keypad(1)
    curses.curs_set(0)
def handlech(c, stdscr):
    if c != curses.ERR:
        if c in range(256): 
            if chr(c) in '12345678':
                global menutab
                menutab = int(chr(c))
            elif chr(c) == 'q':
                global quit
                quit = True
            elif chr(c) == '\n':
                if menutab == 1:
                    curses.curs_set(1)
                    d = Dialog(dialog="dialog")
                    d.set_background_title("Inbox Message Dialog Box")
                    r, t = d.menu("Do what with \""+inbox[inboxcur][5]+"\" from \""+inbox[inboxcur][3]+"\"?",
                        choices=[("1", "View message"),
                            ("2", "Mark message as unread"),
                            ("3", "Reply"),
                            ("4", "Add sender to Address Book"),
                            ("5", "Save message as text file"),
                            ("6", "Move to trash")])
                    if r == d.DIALOG_OK:
                        if t == "1": # View
                            d.set_background_title("\""+inbox[inboxcur][5]+"\" from \""+inbox[inboxcur][3]+"\" to \""+inbox[inboxcur][1]+"\"")
                            msg = ""
                            ret = sqlQuery("SELECT message FROM inbox WHERE msgid=?", inbox[inboxcur][0])
                            if ret != []:
                                for row in ret:
                                    msg, = row
                                msg = shared.fixPotentiallyInvalidUTF8Data(msg)
                                d.scrollbox(unicode(ascii(msg)), 30, 100, exit_label="Continue")
                                sqlExecute("UPDATE inbox SET read=1 WHERE msgid=?", inbox[inboxcur][0])
                                inbox[inboxcur][7] = 1
                            else:
                                d.scrollbox(unicode("Could not fetch message."), exit_label="Continue")
                        elif t == "2": # Mark unread
                            sqlExecute("UPDATE inbox SET read=0 WHERE msgid=?", inbox[inboxcur][0])
                            inbox[inboxcur][7] = 0
                        elif t == "3": # Reply
                            curses.curs_set(1)
                            m = inbox[inboxcur]
                            fromaddr = m[4]
                            ischan = False
                            for i, item in enumerate(addresses):
                                if fromaddr == item[2] and item[3] != 0:
                                    ischan = True
                                    break
                            if not addresses[i][1]:
                                d.scrollbox(unicode("Sending address disabled, please either enable it or choose a different address."), exit_label="Continue")
                                return
                            toaddr = m[2]
                            if ischan:
                                toaddr = fromaddr
                            
                            subject = m[5]
                            if not m[5][:4] == "Re: ":
                                subject = "Re: "+m[5]
                            body = ""
                            ret = sqlQuery("SELECT message FROM inbox WHERE msgid=?", m[0])
                            if ret != []:
                                body = "\n\n------------------------------------------------------\n"
                                for row in ret:
                                    body, = row
                            
                            sendMessage(fromaddr, toaddr, ischan, subject, body)
                            dialogreset(stdscr)
                        elif t == "4": # Add to Address Book
                            addr = inbox[inboxcur][4]
                            if addr in [item[1] for i,item in enumerate(addrbook)]:
                                r, t = d.inputbox("Label for address \""+addr+"\"")
                                if r == d.DIALOG_OK:
                                    sqlExecute("INSERT INTO addressbook VALUES (?,?)", t, addr)
                                    addrbook.reverse().append([t, addr]).reverse() # Prepend new entry
                            else:
                                d.scrollbox(unicode("The selected address is already in the Address Book."), exit_label="Continue")
                        elif t == "5": # Save message
                            d.set_background_title("Save \""+inbox[inboxcur][5]+"\" as text file")
                            r, t = d.inputbox("Filename", init=inbox[inboxcur][5]+".txt")
                            if r == d.DIALOG_OK:
                                msg = ""
                                ret = sqlQuery("SELECT message FROM inbox WHERE msgid=?", inbox[inboxcur][0])
                                if ret != []:
                                    for row in ret:
                                        msg, = row
                                    fh = open(t, "a") # Open in append mode just in case
                                    fh.write(msg)
                                    fh.close()
                                else:
                                    d.scrollbox(unicode("Could not fetch message."), exit_label="Continue")
                        elif t == "6": # Move to trash
                            sqlExecute("UPDATE inbox SET folder='trash' WHERE msgid=?", inbox[inboxcur][0])
                            del inbox[inboxcur]
                            d.scrollbox(unicode("Message moved to trash. There is no interface to view your trash, but the message is still on disk if you are desperate to recover it."),
                                exit_label="Continue")
                    dialogreset(stdscr)
                elif menutab == 2:
                    curses.curs_set(1)
                    sendMessage(addresses[addrcur][2])
                    dialogreset(stdscr)
                elif menutab == 4:
                    curses.curs_set(1)
                    d = Dialog(dialog="dialog")
                    d.set_background_title("Your Identities Dialog Box")
                    r, t = d.menu("Do what with \""+addresses[addrcur][0]+"\" : \""+addresses[addrcur][2]+"\"?",
                        choices=[("1", "Create new address"),
                            ("2", "Copy address to internal buffer"),
                            ("3", "Rename"),
                            ("4", "Enable"),
                            ("5", "Disable"),
                            ("6", "Delete"),
                            ("7", "Special address behavior")])
                    if r == d.DIALOG_OK:
                        if t == "1": # Create new address
                            d.set_background_title("Create new address")
                            d.scrollbox(unicode("Here you may generate as many addresses as you like.\n"
                                "Indeed, creating and abandoning addresses is encouraged.\n"
                                "Deterministic addresses have several pros and cons:\n"
                                "\nPros:\n"
                                "  * You can recreate your addresses on any computer from memory\n"
                                "  * You need not worry about backing up your keys.dat file as long as you \n    can remember your passphrase\n"
                                "Cons:\n"
                                "  * You must remember (or write down) your passphrase in order to recreate \n    your keys if they are lost\n"
                                "  * You must also remember the address version and stream numbers\n"
                                "  * If you choose a weak passphrase someone may be able to brute-force it \n    and then send and receive messages as you"),
                                exit_label="Continue")
                            r, t = d.menu("Choose an address generation technique",
                                choices=[("1", "Use a random number generator"),
                                    ("2", "Use a passphrase")])
                            if r == d.DIALOG_OK:
                                if t == "1":
                                    d.set_background_title("Randomly generate address")
                                    r, t = d.inputbox("Label (not shown to anyone except you)")
                                    label = ""
                                    if r == d.DIALOG_OK and len(t) > 0:
                                        label = t
                                    r, t = d.menu("Choose a stream",
                                        choices=[("1", "Use the most available stream"),("", "(Best if this is the first of many addresses you will create)"),
                                            ("2", "Use the same stream as an existing address"),("", "(Saves you some bandwidth and processing power)")])
                                    if r == d.DIALOG_OK:
                                        if t == "1":
                                            stream = 1
                                        elif t == "2":
                                            addrs = []
                                            for i, item in enumerate(addresses):
                                                addrs.append([str(i), item[2]])
                                            r, t = d.menu("Choose an existing address's stream", choices=addrs)
                                            if r == d.DIALOG_OK:
                                                stream = decodeAddress(addrs[int(t)][1])[2]
                                        shorten = False
                                        r, t = d.checklist("Miscellaneous options",
                                            choices=[("1", "Spend time shortening the address", shorten)])
                                        if r == d.DIALOG_OK and "1" in t:
                                            shorten = True
                                        shared.addressGeneratorQueue.put(("createRandomAddress", 4, stream, label, 1, "", shorten))
                                elif t == "2":
                                    d.set_background_title("Make deterministic addresses")
                                    r, t = d.passwordform("Enter passphrase",
                                        [("Passphrase", 1, 1, "", 2, 1, 64, 128),
                                        ("Confirm passphrase", 3, 1, "", 4, 1, 64, 128)],
                                        form_height=4, insecure=True)
                                    if r == d.DIALOG_OK:
                                        if t[0] == t[1]:
                                            passphrase = t[0]
                                            r, t = d.rangebox("Number of addresses to generate",
                                                width=48, min=1, max=99, init=8)
                                            if r == d.DIALOG_OK:
                                                number = t
                                                stream = 1
                                                shorten = False
                                                r, t = d.checklist("Miscellaneous options",
                                                    choices=[("1", "Spend time shortening the address", shorten)])
                                                if r == d.DIALOG_OK and "1" in t:
                                                    shorten = True
                                                d.scrollbox(unicode("In addition to your passphrase, be sure to remember the following numbers:\n"
                                                    "\n  * Address version number: "+str(4)+"\n"
                                                    "  * Stream number: "+str(stream)),
                                                    exit_label="Continue")
                                                shared.addressGeneratorQueue.put(('createDeterministicAddresses', 4, stream, "unused deterministic address", number, str(passphrase), shorten))
                                        else:
                                            d.scrollbox(unicode("Passphrases do not match"), exit_label="Continue")
                        elif t == "2": # Copy address to internal buffer
                            global addrcopy
                            addrcopy = addrcur
                        elif t == "3": # Rename address label
                            a = addresses[addrcur][2]
                            label = addresses[addrcur][0]
                            r, t = d.inputbox("New address label", init=label)
                            if r == d.DIALOG_OK:
                                label = t
                                shared.config.set(a, "label", label)
                                # Write config
                                with open(shared.appdata + 'keys.dat', 'wb') as configfile:
                                    shared.config.write(configfile)
                                addresses[addrcur][0] = label
                        elif t == "4": # Enable address
                            a = addresses[addrcur][2]
                            shared.config.set(a, "enabled", "true") # Set config
                            # Write config
                            with open(shared.appdata + 'keys.dat', 'wb') as configfile:
                                shared.config.write(configfile)
                            # Change color
                            if shared.safeConfigGetBoolean(a, 'chan'):
                                addresses[addrcur][3] = 9 # orange
                            elif shared.safeConfigGetBoolean(a, 'mailinglist'):
                                addresses[addrcur][3] = 5 # magenta
                            else:
                                addresses[addrcur][3] = 0 # black
                            addresses[addrcur][1] = True
                            shared.reloadMyAddressHashes() # Reload address hashes
                        elif t == "5": # Disable address
                            a = addresses[addrcur][2]
                            shared.config.set(a, "enabled", "false") # Set config
                            addresses[addrcur][3] = 8 # Set color to gray
                            # Write config
                            with open(shared.appdata + 'keys.dat', 'wb') as configfile:
                                shared.config.write(configfile)
                            addresses[addrcur][1] = False
                            shared.reloadMyAddressHashes() # Reload address hashes
                        elif t == "6": # Delete address
                            pass
                        elif t == "7": # Special address behavior
                            a = addresses[addrcur][2]
                            d.set_background_title("Special address behavior")
                            if shared.safeConfigGetBoolean(a, "chan"):
                                d.scrollbox(unicode("This is a chan address. You cannot use it as a pseudo-mailing list."), exit_label="Continue")
                            else:
                                m = shared.safeConfigGetBoolean(a, "mailinglist")
                                r, t = d.radiolist("Select address behavior",
                                    choices=[("1", "Behave as a normal address", not m),
                                        ("2", "Behave as a pseudo-mailing-list address", m)])
                                if r == d.DIALOG_OK:
                                    if t == "1" and m == True:
                                        shared.config.set(a, "mailinglist", "false")
                                        if addresses[addrcur][1]:
                                            addresses[addrcur][3] = 0 # Set color to black
                                        else:
                                            addresses[addrcur][3] = 8 # Set color to gray
                                    elif t == "2" and m == False:
                                        try:
                                            mn = shared.config.get(a, "mailinglistname")
                                        except ConfigParser.NoOptionError:
                                           mn = ""
                                        r, t = d.inputbox("Mailing list name", init=mn)
                                        if r == d.DIALOG_OK:
                                            mn = t
                                            shared.config.set(a, "mailinglist", "true")
                                            shared.config.set(a, "mailinglistname", mn)
                                            addresses[addrcur][3] = 6 # Set color to magenta
                                    # Write config
                                    with open(shared.appdata + 'keys.dat', 'wb') as configfile:
                                        shared.config.write(configfile)
                    dialogreset(stdscr)
        else:
            global addrcur, inboxcur, abookcur
            if c == curses.KEY_UP:
                if menutab == 1 and inboxcur > 0:
                    inboxcur -= 1
                if (menutab == 2 or menutab == 4) and addrcur > 0:
                    addrcur -= 1
                if menutab == 6 and abookcur > 0:
                    abookcur -= 1
            elif c == curses.KEY_DOWN:
                if menutab == 1 and inboxcur < len(inbox)-1:
                    inboxcur += 1
                if (menutab == 2 or menutab == 4) and addrcur < len(addresses)-1:
                    addrcur += 1
                if menutab == 6 and abookcur < len(addrbook)-1:
                    abookcur += 1
            elif c == curses.KEY_HOME:
                if menutab == 1:
                    inboxcur = 0
                if menutab == 2 or menutab == 4:
                    addrcur = 0
                if menutab == 6:
                    abookcur = 0
            elif c == curses.KEY_END:
                if menutab == 1:
                    inboxcur = len(inbox)-1
                if menutab == 2 or menutab == 4:
                    addrcur = len(addresses)-1
                if menutab == 6:
                    abookcur = len(addrbook)-1
        redraw(stdscr)
def sendMessage(sender="", recv="", broadcast=None, subject="", body=""):
    if sender == "":
        return
    d = Dialog(dialog="dialog")
    d.set_background_title("Send a message")
    if recv == "":
        r, t = d.inputbox("Recipient address (Cancel to load from the Address Book or leave blank to broadcast)", 10, 60)
        if r != d.DIALOG_OK:
            global menutab
            menutab = 6
            return
        recv = t
    if broadcast == None:
        r, t = d.radiolist("How to send the message?",
            choices=[("1", "Send to one or more specific people", True),
                ("2", "Broadcast to everyone who is subscribed to your address", False)])
        if r != d.DIALOG_OK:
            return
        broadcast = False
        if t == "2": # Broadcast
            broadcast = True
    if subject == "":
        r, t = d.inputbox("Message subject", width=60)
        if r != d.DIALOG_OK:
            return
        subject = shared.fixPotentiallyInvalidUTF8Data(t)
    if body == "":
        r, t = d.inputbox("Message body", 10, 80)
        if r != d.DIALOG_OK:
            return
        body = shared.fixPotentiallyInvalidUTF8Data(t)
    
    if not broadcast:
        recvlist = []
        for i, item in enumerate(recv.replace(",", ";").split(";")):
            recvlist.append(item.strip())
        list(set(recvlist)) # Remove exact duplicates
        for addr in recvlist:
            if addr != "":
                status, version, stream, ripe = decodeAddress(addr)
                if status != "success":
                    d.set_background_title("Recipient address error")
                    err = "Could not decode" + addr + " : " + status + "\n\n"
                    if status == "missingbm":
                        err += "Bitmessage addresses should start with \"BM-\"."
                    elif status == "checksumfailed":
                        err += "The address was not typed or copied correctly."
                    elif status == "invalidcharacters":
                        err += "The address contains invalid characters."
                    elif status == "versiontoohigh":
                        err += "The address version is too high. Either you need to upgrade your Bitmessage software or your acquaintance is doing something clever."
                    elif status == "ripetooshort":
                        err += "Some data encoded in the address is too short. There might be something wrong with the software of your acquaintance."
                    elif status == "ripetoolong":
                        err += "Some data encoded in the address is too long. There might be something wrong with the software of your acquaintance."
                    else:
                        err += "It is unknown what is wrong with the address."
                    d.scrollbox(unicode(err), exit_label="Continue")
                else:
                    addr = addBMIfNotPresent(addr)
                    if version > 4 or version <= 1:
                        d.set_background_title("Recipient address error")
                        d.scrollbox(unicode("Could not understand version number " + version + "of address" + addr + "."),
                            exit_label="Continue")
                        continue
                    if stream > 1 or stream == 0:
                        d.set_background_title("Recipient address error")
                        d.scrollbox(unicode("Bitmessage currently only supports stream numbers of 1, unlike as requested for address " + addr + "."),
                            exit_label="Continue")
                        continue
                    if len(shared.connectedHostsList) == 0:
                        d.set_background_title("Not connected warning")
                        d.scrollbox(unicode("Because you are not currently connected to the network, "),
                            exit_label="Continue")
                    
                    ackdata = OpenSSL.rand(32)
                    sqlExecute(
                        '''INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                        '',
                        addr,
                        ripe,
                        sender,
                        subject,
                        body,
                        ackdata,
                        int(time.time()),
                        'msgqueued',
                        1,
                        1,
                        'sent',
                        2)
                    shared.workerQueue.put(("sendmessage", addr))
    else: # Broadcast
        if addr == "":
            d.set_background_title("Empty sender error")
            d.scrollbox(unicode("You must specify an address to send the message from."),
                exit_label="Continue")
        else:
            ackdata = OpenSSL.rand(32)
            addr = BROADCAST_STR
            ripe = ""
            sqlExecute(
                '''INSERT INTO sent VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                '',
                addr,
                ripe,
                sender,
                subject,
                body,
                ackdata,
                int(time.time()),
                'broadcastqueued',
                1,
                1,
                'sent',
                2)
            shared.workerQueue.put(('sendbroadcast', ''))

def loadInbox():
    sys.stdout = sys.__stdout__
    print("Loading inbox messages...")
    sys.stdout = printlog
    
    where = "toaddress || fromaddress || subject || message"
    what = "%%"
    ret = sqlQuery("""SELECT msgid, toaddress, fromaddress, subject, received, read
        FROM inbox WHERE folder='inbox' AND %s LIKE ?
        ORDER BY received
        """ % (where,), what)
    global inbox
    for row in ret:
        msgid, toaddr, fromaddr, subject, received, read = row
        subject = ascii(shared.fixPotentiallyInvalidUTF8Data(subject))
        
        # Set label for to address
        try:
            if toaddr == BROADCAST_STR:
                tolabel = BROADCAST_STR
            else:
                tolabel = shared.config.get(toaddr, "label")
        except:
            tolabel = ""
        if tolabel == "":
            tolabel = toaddr
        tolabel = shared.fixPotentiallyInvalidUTF8Data(tolabel)
        
        # Set label for from address
        fromlabel = ""
        if shared.config.has_section(fromaddr):
            fromlabel = shared.config.get(fromaddr, "label")
        if fromlabel == "": # Check Address Book
            qr = sqlQuery("SELECT label FROM addressbook WHERE address=?", fromaddr)
            if qr != []:
                for r in qr:
                    fromlabel, = r
        if fromlabel == "": # Check Subscriptions
            qr = sqlQuery("SELECT label FROM subscriptions WHERE address=?", fromaddr)
            if qr != []:
                for r in qr:
                    fromlabel, = r
        if fromlabel == "":
            fromlabel = fromaddr
        fromlabel = shared.fixPotentiallyInvalidUTF8Data(fromlabel)
        
        # Load into array
        inbox.append([msgid, tolabel, toaddr, fromlabel, fromaddr, subject,
            strftime(shared.config.get('bitmessagesettings', 'timeformat'), localtime(int(received))),
            read])
    inbox.reverse()
def loadAddrBook():
    sys.stdout = sys.__stdout__
    print("Loading address book...")
    sys.stdout = printlog
    
    ret = sqlQuery("SELECT label, address FROM addressbook")
    global addrbook
    for row in ret:
        label, addr = row
        label = shared.fixPotentiallyInvalidUTF8Data(label)
        addrbook.append([label, addr])
    addrbook.reverse()

def runwrapper():
    sys.stdout = printlog
    #sys.stderr = errlog
    
    # Load messages from database
    loadInbox()
    #loadSent()
    loadAddrBook()
    
    stdscr = curses.initscr()
    
    global logpad
    logpad = curses.newpad(1024, curses.COLS)
    
    stdscr.nodelay(0)
    curses.curs_set(0)
    stdscr.timeout(1000)
    
    curses.wrapper(run)
    shutdown()

def run(stdscr):
    # Schedule inventory lookup data
    resetlookups()
    
    # Init color pairs
    if curses.has_colors():
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK) # red
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK) # green
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # yellow
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK) # blue
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # magenta
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK) # cyan
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK) # white
        if curses.can_change_color():
            curses.init_color(8, 500, 500, 500) # gray
            curses.init_pair(8, 8, 0)
            curses.init_color(9, 844, 465, 0) # orange
            curses.init_pair(9, 9, 0)
        else:
            curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLACK) # grayish
            curses.init_pair(9, curses.COLOR_YELLOW, curses.COLOR_BLACK) # orangish
    
    # Init list of address in 'Your Identities' tab
    configSections = shared.config.sections()
    for addressInKeysFile in configSections:
        if addressInKeysFile != "bitmessagesettings":
            isEnabled = shared.config.getboolean(addressInKeysFile, "enabled")
            addresses.append([shared.config.get(addressInKeysFile, "label"), isEnabled, addressInKeysFile])
            # Set address color
            if not isEnabled:
                addresses[len(addresses)-1].append(8) # gray
            elif shared.safeConfigGetBoolean(addressInKeysFile, 'chan'):
                addresses[len(addresses)-1].append(9) # orange
            elif shared.safeConfigGetBoolean(addressInKeysFile, 'mailinglist'):
                addresses[len(addresses)-1].append(5) # magenta
            else:
                addresses[len(addresses)-1].append(0) # black
    addresses.reverse()
    
    stdscr.clear()
    redraw(stdscr)
    while quit == False:
        drawtab(stdscr)
        handlech(stdscr.getch(), stdscr)

def shutdown():
    sys.stdout = sys.__stdout__
    print("Shutting down...")
    sys.stdout = printlog
    shared.doCleanShutdown()
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    
    os._exit(0)
