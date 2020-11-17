"""
Bitmessage commandline interface
"""
# Copyright (c) 2014 Luke Montalvo <lukemontalvo@gmail.com>
# This file adds a alternative commandline interface, feel free to critique and fork
#
# This has only been tested on Arch Linux and Linux Mint
# Dependencies:
#  * from python2-pip
#     * python2-pythondialog
#  * dialog

import ConfigParser
import curses
import os
import sys
import time
from textwrap import fill
from threading import Timer

from dialog import Dialog
import helper_sent
import l10n
import network.stats
import queues
import shared
import shutdown
import state

from addresses import addBMIfNotPresent, decodeAddress
from bmconfigparser import BMConfigParser
from helper_sql import sqlExecute, sqlQuery
from inventory import Inventory

# pylint: disable=global-statement


quit_ = False
menutab = 1
menu = ["Inbox", "Send", "Sent", "Your Identities", "Subscriptions", "Address Book", "Blacklist", "Network Status"]
naptime = 100
log = ""
logpad = None
inventorydata = 0
startuptime = time.time()

inbox = []
inboxcur = 0
sentbox = []
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
bwtype = "black"

BROADCAST_STR = "[Broadcast subscribers]"


class printLog(object):
    """Printing logs"""
    # pylint: disable=no-self-use

    def write(self, output):
        """Write logs"""
        global log
        log += output

    def flush(self):
        """Flush logs"""
        pass


class errLog(object):
    """Error logs"""
    # pylint: disable=no-self-use

    def write(self, output):
        """Write error logs"""
        global log
        log += "!" + output

    def flush(self):
        """Flush error logs"""
        pass


printlog = printLog()
errlog = errLog()


def cpair(a):
    """Color pairs"""
    r = curses.color_pair(a)
    if r not in range(1, curses.COLOR_PAIRS - 1):
        r = curses.color_pair(0)
    return r


def ascii(s):
    """ASCII values"""
    r = ""
    for c in s:
        if ord(c) in range(128):
            r += c
    return r


def drawmenu(stdscr):
    """Creating menu's"""
    menustr = " "
    for i, _ in enumerate(menu):
        if menutab == i + 1:
            menustr = menustr[:-1]
            menustr += "["
        menustr += str(i + 1) + menu[i]
        if menutab == i + 1:
            menustr += "] "
        elif i != len(menu) - 1:
            menustr += "  "
    stdscr.addstr(2, 5, menustr, curses.A_UNDERLINE)


def set_background_title(d, title):
    """Setting background title"""
    try:
        d.set_background_title(title)
    except:
        d.add_persistent_args(("--backtitle", title))


def scrollbox(d, text, height=None, width=None):
    """Setting scroll box"""
    try:
        d.scrollbox(text, height, width, exit_label="Continue")
    except:
        d.msgbox(text, height or 0, width or 0, ok_label="Continue")


def resetlookups():
    """Reset the Inventory Lookups"""
    global inventorydata
    inventorydata = Inventory().numberOfInventoryLookupsPerformed
    Inventory().numberOfInventoryLookupsPerformed = 0
    Timer(1, resetlookups, ()).start()


def drawtab(stdscr):
    """Method for drawing different tabs"""
    # pylint: disable=too-many-branches, too-many-statements
    if menutab in range(1, len(menu) + 1):
        if menutab == 1:		# Inbox
            stdscr.addstr(3, 5, "To", curses.A_BOLD)
            stdscr.addstr(3, 40, "From", curses.A_BOLD)
            stdscr.addstr(3, 80, "Subject", curses.A_BOLD)
            stdscr.addstr(3, 120, "Time Received", curses.A_BOLD)
            stdscr.hline(4, 5, '-', 121)
            for i, item in enumerate(inbox[max(min(len(inbox) - curses.LINES + 6, inboxcur - 5), 0):]):
                if 6 + i < curses.LINES:
                    a = 0
                    if i == inboxcur - max(min(len(inbox) - curses.LINES + 6, inboxcur - 5), 0):
                        # Highlight current address
                        a = a | curses.A_REVERSE
                    if item[7] is False:		# If not read, highlight
                        a = a | curses.A_BOLD
                    stdscr.addstr(5 + i, 5, item[1][:34], a)
                    stdscr.addstr(5 + i, 40, item[3][:39], a)
                    stdscr.addstr(5 + i, 80, item[5][:39], a)
                    stdscr.addstr(5 + i, 120, item[6][:39], a)
        elif menutab == 3:		 # Sent
            stdscr.addstr(3, 5, "To", curses.A_BOLD)
            stdscr.addstr(3, 40, "From", curses.A_BOLD)
            stdscr.addstr(3, 80, "Subject", curses.A_BOLD)
            stdscr.addstr(3, 120, "Status", curses.A_BOLD)
            stdscr.hline(4, 5, '-', 121)
            for i, item in enumerate(sentbox[max(min(len(sentbox) - curses.LINES + 6, sentcur - 5), 0):]):
                if 6 + i < curses.LINES:
                    a = 0
                    if i == sentcur - max(min(len(sentbox) - curses.LINES + 6, sentcur - 5), 0):
                        # Highlight current address
                        a = a | curses.A_REVERSE
                    stdscr.addstr(5 + i, 5, item[0][:34], a)
                    stdscr.addstr(5 + i, 40, item[2][:39], a)
                    stdscr.addstr(5 + i, 80, item[4][:39], a)
                    stdscr.addstr(5 + i, 120, item[5][:39], a)
        elif menutab == 2 or menutab == 4:		 # Send or Identities
            stdscr.addstr(3, 5, "Label", curses.A_BOLD)
            stdscr.addstr(3, 40, "Address", curses.A_BOLD)
            stdscr.addstr(3, 80, "Stream", curses.A_BOLD)
            stdscr.hline(4, 5, '-', 81)
            for i, item in enumerate(addresses[max(min(len(addresses) - curses.LINES + 6, addrcur - 5), 0):]):
                if 6 + i < curses.LINES:
                    a = 0
                    if i == addrcur - max(min(len(addresses) - curses.LINES + 6, addrcur - 5), 0):
                        # Highlight current address
                        a = a | curses.A_REVERSE
                    if item[1] and item[3] not in [8, 9]:		 # Embolden enabled, non-special addresses
                        a = a | curses.A_BOLD
                    stdscr.addstr(5 + i, 5, item[0][:34], a)
                    stdscr.addstr(5 + i, 40, item[2][:39], cpair(item[3]) | a)
                    stdscr.addstr(5 + i, 80, str(1)[:39], a)
        elif menutab == 5:		 # Subscriptions
            stdscr.addstr(3, 5, "Label", curses.A_BOLD)
            stdscr.addstr(3, 80, "Address", curses.A_BOLD)
            stdscr.addstr(3, 120, "Enabled", curses.A_BOLD)
            stdscr.hline(4, 5, '-', 121)
            for i, item in enumerate(subscriptions[max(min(len(subscriptions) - curses.LINES + 6, subcur - 5), 0):]):
                if 6 + i < curses.LINES:
                    a = 0
                    if i == subcur - max(min(len(subscriptions) - curses.LINES + 6, subcur - 5), 0):
                        # Highlight current address
                        a = a | curses.A_REVERSE
                    if item[2]:		 # Embolden enabled subscriptions
                        a = a | curses.A_BOLD
                    stdscr.addstr(5 + i, 5, item[0][:74], a)
                    stdscr.addstr(5 + i, 80, item[1][:39], a)
                    stdscr.addstr(5 + i, 120, str(item[2]), a)
        elif menutab == 6:		 # Address book
            stdscr.addstr(3, 5, "Label", curses.A_BOLD)
            stdscr.addstr(3, 40, "Address", curses.A_BOLD)
            stdscr.hline(4, 5, '-', 41)
            for i, item in enumerate(addrbook[max(min(len(addrbook) - curses.LINES + 6, abookcur - 5), 0):]):
                if 6 + i < curses.LINES:
                    a = 0
                    if i == abookcur - max(min(len(addrbook) - curses.LINES + 6, abookcur - 5), 0):
                        # Highlight current address
                        a = a | curses.A_REVERSE
                    stdscr.addstr(5 + i, 5, item[0][:34], a)
                    stdscr.addstr(5 + i, 40, item[1][:39], a)
        elif menutab == 7:		 # Blacklist
            stdscr.addstr(3, 5, "Type: " + bwtype)
            stdscr.addstr(4, 5, "Label", curses.A_BOLD)
            stdscr.addstr(4, 80, "Address", curses.A_BOLD)
            stdscr.addstr(4, 120, "Enabled", curses.A_BOLD)
            stdscr.hline(5, 5, '-', 121)
            for i, item in enumerate(blacklist[max(min(len(blacklist) - curses.LINES + 6, blackcur - 5), 0):]):
                if 7 + i < curses.LINES:
                    a = 0
                    if i == blackcur - max(min(len(blacklist) - curses.LINES + 6, blackcur - 5), 0):
                        # Highlight current address
                        a = a | curses.A_REVERSE
                    if item[2]:		 # Embolden enabled subscriptions
                        a = a | curses.A_BOLD
                    stdscr.addstr(6 + i, 5, item[0][:74], a)
                    stdscr.addstr(6 + i, 80, item[1][:39], a)
                    stdscr.addstr(6 + i, 120, str(item[2]), a)
        elif menutab == 8:		 # Network status
            # Connection data
            connected_hosts = network.stats.connectedHostsList()
            stdscr.addstr(
                4, 5, "Total Connections: " +
                str(len(connected_hosts)).ljust(2)
            )
            stdscr.addstr(6, 6, "Stream #", curses.A_BOLD)
            stdscr.addstr(6, 18, "Connections", curses.A_BOLD)
            stdscr.hline(7, 6, '-', 23)
            streamcount = []
            for host, stream in connected_hosts:
                if stream >= len(streamcount):
                    streamcount.append(1)
                else:
                    streamcount[stream] += 1
            for i, item in enumerate(streamcount):
                if i < 4:
                    if i == 0:
                        stdscr.addstr(8 + i, 6, "?")
                    else:
                        stdscr.addstr(8 + i, 6, str(i))
                    stdscr.addstr(8 + i, 18, str(item).ljust(2))

            # Uptime and processing data
            stdscr.addstr(6, 35, "Since startup on " + l10n.formatTimestamp(startuptime, False))
            stdscr.addstr(7, 40, "Processed " + str(
                state.numberOfMessagesProcessed).ljust(4) + " person-to-person messages.")
            stdscr.addstr(8, 40, "Processed " + str(
                state.numberOfBroadcastsProcessed).ljust(4) + " broadcast messages.")
            stdscr.addstr(9, 40, "Processed " + str(
                state.numberOfPubkeysProcessed).ljust(4) + " public keys.")

            # Inventory data
            stdscr.addstr(11, 35, "Inventory lookups per second: " + str(inventorydata).ljust(3))

            # Log
            stdscr.addstr(13, 6, "Log", curses.A_BOLD)
            n = log.count('\n')
            if n > 0:
                lg = log.split('\n')
                if n > 512:
                    del lg[:(n - 256)]
                    logpad.erase()
                    n = len(lg)
                for i, item in enumerate(lg):
                    a = 0
                    if item and item[0] == '!':
                        a = curses.color_pair(1)
                        item = item[1:]
                    logpad.addstr(i, 0, item, a)
                logpad.refresh(n - curses.LINES + 2, 0, 14, 6, curses.LINES - 2, curses.COLS - 7)
    stdscr.refresh()


def redraw(stdscr):
    """Redraw menu"""
    stdscr.erase()
    stdscr.border()
    drawmenu(stdscr)
    stdscr.refresh()


def dialogreset(stdscr):
    """Resetting dialogue"""
    stdscr.clear()
    stdscr.keypad(1)
    curses.curs_set(0)


# pylint: disable=too-many-branches, too-many-statements
def handlech(c, stdscr):
    """Handle character given on the command-line interface"""
    # pylint: disable=redefined-outer-name, too-many-nested-blocks, too-many-locals
    if c != curses.ERR:
        global inboxcur, addrcur, sentcur, subcur, abookcur, blackcur
        if c in range(256):
            if chr(c) in '12345678':
                global menutab
                menutab = int(chr(c))
            elif chr(c) == 'q':
                global quit_
                quit_ = True
            elif chr(c) == '\n':
                curses.curs_set(1)
                d = Dialog(dialog="dialog")
                if menutab == 1:
                    set_background_title(d, "Inbox Message Dialog Box")
                    r, t = d.menu(
                        "Do what with \"" + inbox[inboxcur][5] + "\" from \"" + inbox[inboxcur][3] + "\"?",
                        choices=[
                            ("1", "View message"),
                            ("2", "Mark message as unread"),
                            ("3", "Reply"),
                            ("4", "Add sender to Address Book"),
                            ("5", "Save message as text file"),
                            ("6", "Move to trash")])
                    if r == d.DIALOG_OK:
                        if t == "1":  # View
                            set_background_title(
                                d,
                                "\"" +
                                inbox[inboxcur][5] +
                                "\" from \"" +
                                inbox[inboxcur][3] +
                                "\" to \"" +
                                inbox[inboxcur][1] +
                                "\"")
                            data = ""       # pyint: disable=redefined-outer-name
                            ret = sqlQuery("SELECT message FROM inbox WHERE msgid=?", inbox[inboxcur][0])
                            if ret != []:
                                for row in ret:
                                    data, = row
                                data = shared.fixPotentiallyInvalidUTF8Data(data)
                                msg = ""
                                for i, item in enumerate(data.split("\n")):
                                    msg += fill(item, replace_whitespace=False) + "\n"
                                scrollbox(d, unicode(ascii(msg)), 30, 80)
                                sqlExecute("UPDATE inbox SET read=1 WHERE msgid=?", inbox[inboxcur][0])
                                inbox[inboxcur][7] = 1
                            else:
                                scrollbox(d, unicode("Could not fetch message."))
                        elif t == "2":       # Mark unread
                            sqlExecute("UPDATE inbox SET read=0 WHERE msgid=?", inbox[inboxcur][0])
                            inbox[inboxcur][7] = 0
                        elif t == "3":       # Reply
                            curses.curs_set(1)
                            m = inbox[inboxcur]
                            fromaddr = m[4]
                            ischan = False
                            for i, item in enumerate(addresses):
                                if fromaddr == item[2] and item[3] != 0:
                                    ischan = True
                                    break
                            if not addresses[i][1]:  # pylint: disable=undefined-loop-variable
                                scrollbox(d, unicode(
                                    "Sending address disabled, please either enable it"
                                    "or choose a different address."))
                                return
                            toaddr = m[2]
                            if ischan:
                                toaddr = fromaddr

                            subject = m[5]
                            if not m[5][:4] == "Re: ":
                                subject = "Re: " + m[5]
                            body = ""
                            ret = sqlQuery("SELECT message FROM inbox WHERE msgid=?", m[0])
                            if ret != []:
                                body = "\n\n------------------------------------------------------\n"
                                for row in ret:
                                    body, = row

                            sendMessage(fromaddr, toaddr, ischan, subject, body, True)
                            dialogreset(stdscr)
                        elif t == "4":       # Add to Address Book
                            addr = inbox[inboxcur][4]
                            if addr not in [item[1] for i, item in enumerate(addrbook)]:
                                r, t = d.inputbox("Label for address \"" + addr + "\"")
                                if r == d.DIALOG_OK:
                                    label = t
                                    sqlExecute("INSERT INTO addressbook VALUES (?,?)", label, addr)
                                    # Prepend entry
                                    addrbook.reverse()
                                    addrbook.append([label, addr])
                                    addrbook.reverse()
                            else:
                                scrollbox(d, unicode("The selected address is already in the Address Book."))
                        elif t == "5":      # Save message
                            set_background_title(d, "Save \"" + inbox[inboxcur][5] + "\" as text file")
                            r, t = d.inputbox("Filename", init=inbox[inboxcur][5] + ".txt")
                            if r == d.DIALOG_OK:
                                msg = ""
                                ret = sqlQuery("SELECT message FROM inbox WHERE msgid=?", inbox[inboxcur][0])
                                if ret != []:
                                    for row in ret:
                                        msg, = row
                                    fh = open(t, "a")       # Open in append mode just in case
                                    fh.write(msg)
                                    fh.close()
                                else:
                                    scrollbox(d, unicode("Could not fetch message."))
                        elif t == "6":       # Move to trash
                            sqlExecute("UPDATE inbox SET folder='trash' WHERE msgid=?", inbox[inboxcur][0])
                            del inbox[inboxcur]
                            scrollbox(d, unicode(
                                "Message moved to trash. There is no interface to view your trash,"
                                " \nbut the message is still on disk if you are desperate to recover it."))
                elif menutab == 2:
                    a = ""
                    if addresses[addrcur][3] != 0:      # if current address is a chan
                        a = addresses[addrcur][2]
                    sendMessage(addresses[addrcur][2], a)
                elif menutab == 3:
                    set_background_title(d, "Sent Messages Dialog Box")
                    r, t = d.menu(
                        "Do what with \"" + sentbox[sentcur][4] + "\" to \"" + sentbox[sentcur][0] + "\"?",
                        choices=[
                            ("1", "View message"),
                            ("2", "Move to trash")])
                    if r == d.DIALOG_OK:
                        if t == "1":  # View
                            set_background_title(
                                d,
                                "\"" +
                                sentbox[sentcur][4] +
                                "\" from \"" +
                                sentbox[sentcur][3] +
                                "\" to \"" +
                                sentbox[sentcur][1] +
                                "\"")
                            data = ""
                            ret = sqlQuery(
                                "SELECT message FROM sent WHERE subject=? AND ackdata=?",
                                sentbox[sentcur][4],
                                sentbox[sentcur][6])
                            if ret != []:
                                for row in ret:
                                    data, = row
                                data = shared.fixPotentiallyInvalidUTF8Data(data)
                                msg = ""
                                for i, item in enumerate(data.split("\n")):
                                    msg += fill(item, replace_whitespace=False) + "\n"
                                scrollbox(d, unicode(ascii(msg)), 30, 80)
                            else:
                                scrollbox(d, unicode("Could not fetch message."))
                        elif t == "2":       # Move to trash
                            sqlExecute(
                                "UPDATE sent SET folder='trash' WHERE subject=? AND ackdata=?",
                                sentbox[sentcur][4],
                                sentbox[sentcur][6])
                            del sentbox[sentcur]
                            scrollbox(d, unicode(
                                "Message moved to trash. There is no interface to view your trash"
                                " \nbut the message is still on disk if you are desperate to recover it."))
                elif menutab == 4:
                    set_background_title(d, "Your Identities Dialog Box")
                    if len(addresses) <= addrcur:
                        r, t = d.menu(
                            "Do what with addresses?",
                            choices=[
                                ("1", "Create new address")])
                    else:
                        r, t = d.menu(
                            "Do what with \"" + addresses[addrcur][0] + "\" : \"" + addresses[addrcur][2] + "\"?",
                            choices=[
                                ("1", "Create new address"),
                                ("2", "Send a message from this address"),
                                ("3", "Rename"),
                                ("4", "Enable"),
                                ("5", "Disable"),
                                ("6", "Delete"),
                                ("7", "Special address behavior")])
                    if r == d.DIALOG_OK:
                        if t == "1":         # Create new address
                            set_background_title(d, "Create new address")
                            scrollbox(
                                d, unicode(
                                    "Here you may generate as many addresses as you like.\n"
                                    "Indeed, creating and abandoning addresses is encouraged.\n"
                                    "Deterministic addresses have several pros and cons:\n"
                                    "\nPros:\n"
                                    "  * You can recreate your addresses on any computer from memory\n"
                                    "  * You need not worry about backing up your keys.dat file as long as you"
                                    " \n    can remember your passphrase\n"
                                    "Cons:\n"
                                    "  * You must remember (or write down) your passphrase in order to recreate"
                                    " \n    your keys if they are lost\n"
                                    "  * You must also remember the address version and stream numbers\n"
                                    "  * If you choose a weak passphrase someone may be able to brute-force it"
                                    " \n    and then send and receive messages as you"))
                            r, t = d.menu(
                                "Choose an address generation technique",
                                choices=[
                                    ("1", "Use a random number generator"),
                                    ("2", "Use a passphrase")])
                            if r == d.DIALOG_OK:
                                if t == "1":
                                    set_background_title(d, "Randomly generate address")
                                    r, t = d.inputbox("Label (not shown to anyone except you)")
                                    label = ""
                                    if r == d.DIALOG_OK and t:
                                        label = t
                                    r, t = d.menu(
                                        "Choose a stream",
                                        choices=[("1", "Use the most available stream"),
                                                 ("", "(Best if this is the first of many addresses you will create)"),
                                                 ("2", "Use the same stream as an existing address"),
                                                 ("", "(Saves you some bandwidth and processing power)")])
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
                                        r, t = d.checklist(
                                            "Miscellaneous options",
                                            choices=[(
                                                "1",
                                                "Spend time shortening the address",
                                                1 if shorten else 0)])
                                        if r == d.DIALOG_OK and "1" in t:
                                            shorten = True
                                        queues.addressGeneratorQueue.put((
                                            "createRandomAddress",
                                            4,
                                            stream,
                                            label,
                                            1,
                                            "",
                                            shorten))
                                elif t == "2":
                                    set_background_title(d, "Make deterministic addresses")
                                    r, t = d.passwordform(
                                        "Enter passphrase",
                                        [
                                            ("Passphrase", 1, 1, "", 2, 1, 64, 128),
                                            ("Confirm passphrase", 3, 1, "", 4, 1, 64, 128)],
                                        form_height=4, insecure=True)
                                    if r == d.DIALOG_OK:
                                        if t[0] == t[1]:
                                            passphrase = t[0]
                                            r, t = d.rangebox(
                                                "Number of addresses to generate",
                                                width=48,
                                                min=1,
                                                max=99,
                                                init=8)
                                            if r == d.DIALOG_OK:
                                                number = t
                                                stream = 1
                                                shorten = False
                                                r, t = d.checklist(
                                                    "Miscellaneous options",
                                                    choices=[(
                                                        "1",
                                                        "Spend time shortening the address",
                                                        1 if shorten else 0)])
                                                if r == d.DIALOG_OK and "1" in t:
                                                    shorten = True
                                                scrollbox(
                                                    d, unicode(
                                                        "In addition to your passphrase, be sure to remember the"
                                                        " following numbers:\n"
                                                        "\n  * Address version number: " + str(4) + "\n"
                                                        "  * Stream number: " + str(stream)))
                                                queues.addressGeneratorQueue.put(
                                                    ('createDeterministicAddresses', 4, stream,
                                                     "unused deterministic address", number,
                                                     str(passphrase), shorten))
                                        else:
                                            scrollbox(d, unicode("Passphrases do not match"))
                        elif t == "2":      # Send a message
                            a = ""
                            if addresses[addrcur][3] != 0:       # if current address is a chan
                                a = addresses[addrcur][2]
                            sendMessage(addresses[addrcur][2], a)
                        elif t == "3":      # Rename address label
                            a = addresses[addrcur][2]
                            label = addresses[addrcur][0]
                            r, t = d.inputbox("New address label", init=label)
                            if r == d.DIALOG_OK:
                                label = t
                                BMConfigParser().set(a, "label", label)
                                # Write config
                                BMConfigParser().save()
                                addresses[addrcur][0] = label
                        elif t == "4":      # Enable address
                            a = addresses[addrcur][2]
                            BMConfigParser().set(a, "enabled", "true")       # Set config
                            # Write config
                            BMConfigParser().save()
                            # Change color
                            if BMConfigParser().safeGetBoolean(a, 'chan'):
                                addresses[addrcur][3] = 9       # orange
                            elif BMConfigParser().safeGetBoolean(a, 'mailinglist'):
                                addresses[addrcur][3] = 5       # magenta
                            else:
                                addresses[addrcur][3] = 0       # black
                            addresses[addrcur][1] = True
                            shared.reloadMyAddressHashes()      # Reload address hashes
                        elif t == "5":       # Disable address
                            a = addresses[addrcur][2]
                            BMConfigParser().set(a, "enabled", "false")     # Set config
                            addresses[addrcur][3] = 8       # Set color to gray
                            # Write config
                            BMConfigParser().save()
                            addresses[addrcur][1] = False
                            shared.reloadMyAddressHashes()      # Reload address hashes
                        elif t == "6":      # Delete address
                            r, t = d.inputbox("Type in \"I want to delete this address\"", width=50)
                            if r == d.DIALOG_OK and t == "I want to delete this address":
                                BMConfigParser().remove_section(addresses[addrcur][2])
                                BMConfigParser().save()
                                del addresses[addrcur]
                        elif t == "7":      # Special address behavior
                            a = addresses[addrcur][2]
                            set_background_title(d, "Special address behavior")
                            if BMConfigParser().safeGetBoolean(a, "chan"):
                                scrollbox(d, unicode(
                                    "This is a chan address. You cannot use it as a pseudo-mailing list."))
                            else:
                                m = BMConfigParser().safeGetBoolean(a, "mailinglist")
                                r, t = d.radiolist(
                                    "Select address behavior",
                                    choices=[
                                        ("1", "Behave as a normal address", not m),
                                        ("2", "Behave as a pseudo-mailing-list address", m)])
                                if r == d.DIALOG_OK:
                                    if t == "1" and m:
                                        BMConfigParser().set(a, "mailinglist", "false")
                                        if addresses[addrcur][1]:
                                            addresses[addrcur][3] = 0       # Set color to black
                                        else:
                                            addresses[addrcur][3] = 8       # Set color to gray
                                    elif t == "2" and m is False:
                                        try:
                                            mn = BMConfigParser().get(a, "mailinglistname")
                                        except ConfigParser.NoOptionError:
                                            mn = ""
                                        r, t = d.inputbox("Mailing list name", init=mn)
                                        if r == d.DIALOG_OK:
                                            mn = t
                                            BMConfigParser().set(a, "mailinglist", "true")
                                            BMConfigParser().set(a, "mailinglistname", mn)
                                            addresses[addrcur][3] = 6       # Set color to magenta
                                    # Write config
                                    BMConfigParser().save()
                elif menutab == 5:
                    set_background_title(d, "Subscriptions Dialog Box")
                    if len(subscriptions) <= subcur:
                        r, t = d.menu(
                            "Do what with subscription to \"" + subscriptions[subcur][0] + "\"?",
                            choices=[
                                ("1", "Add new subscription")])
                    else:
                        r, t = d.menu(
                            "Do what with subscription to \"" + subscriptions[subcur][0] + "\"?",
                            choices=[
                                ("1", "Add new subscription"),
                                ("2", "Delete this subscription"),
                                ("3", "Enable"),
                                ("4", "Disable")])
                    if r == d.DIALOG_OK:
                        if t == "1":
                            r, t = d.inputbox("New subscription address")
                            if r == d.DIALOG_OK:
                                addr = addBMIfNotPresent(t)
                                if not shared.isAddressInMySubscriptionsList(addr):
                                    r, t = d.inputbox("New subscription label")
                                    if r == d.DIALOG_OK:
                                        label = t
                                        # Prepend entry
                                        subscriptions.reverse()
                                        subscriptions.append([label, addr, True])
                                        subscriptions.reverse()

                                        sqlExecute("INSERT INTO subscriptions VALUES (?,?,?)", label, addr, True)
                                        shared.reloadBroadcastSendersForWhichImWatching()
                        elif t == "2":
                            r, t = d.inputbox("Type in \"I want to delete this subscription\"")
                            if r == d.DIALOG_OK and t == "I want to delete this subscription":
                                sqlExecute(
                                    "DELETE FROM subscriptions WHERE label=? AND address=?",
                                    subscriptions[subcur][0],
                                    subscriptions[subcur][1])
                                shared.reloadBroadcastSendersForWhichImWatching()
                                del subscriptions[subcur]
                        elif t == "3":
                            sqlExecute(
                                "UPDATE subscriptions SET enabled=1 WHERE label=? AND address=?",
                                subscriptions[subcur][0],
                                subscriptions[subcur][1])
                            shared.reloadBroadcastSendersForWhichImWatching()
                            subscriptions[subcur][2] = True
                        elif t == "4":
                            sqlExecute(
                                "UPDATE subscriptions SET enabled=0 WHERE label=? AND address=?",
                                subscriptions[subcur][0],
                                subscriptions[subcur][1])
                            shared.reloadBroadcastSendersForWhichImWatching()
                            subscriptions[subcur][2] = False
                elif menutab == 6:
                    set_background_title(d, "Address Book Dialog Box")
                    if len(addrbook) <= abookcur:
                        r, t = d.menu(
                            "Do what with addressbook?",
                            choices=[("3", "Add new address to Address Book")])
                    else:
                        r, t = d.menu(
                            "Do what with \"" + addrbook[abookcur][0] + "\" : \"" + addrbook[abookcur][1] + "\"",
                            choices=[
                                ("1", "Send a message to this address"),
                                ("2", "Subscribe to this address"),
                                ("3", "Add new address to Address Book"),
                                ("4", "Delete this address")])
                    if r == d.DIALOG_OK:
                        if t == "1":
                            sendMessage(recv=addrbook[abookcur][1])
                        elif t == "2":
                            r, t = d.inputbox("New subscription label")
                            if r == d.DIALOG_OK:
                                label = t
                                # Prepend entry
                                subscriptions.reverse()
                                subscriptions.append([label, addr, True])
                                subscriptions.reverse()

                                sqlExecute("INSERT INTO subscriptions VALUES (?,?,?)", label, addr, True)
                                shared.reloadBroadcastSendersForWhichImWatching()
                        elif t == "3":
                            r, t = d.inputbox("Input new address")
                            if r == d.DIALOG_OK:
                                addr = t
                                if addr not in [item[1] for i, item in enumerate(addrbook)]:
                                    r, t = d.inputbox("Label for address \"" + addr + "\"")
                                    if r == d.DIALOG_OK:
                                        sqlExecute("INSERT INTO addressbook VALUES (?,?)", t, addr)
                                        # Prepend entry
                                        addrbook.reverse()
                                        addrbook.append([t, addr])
                                        addrbook.reverse()
                                else:
                                    scrollbox(d, unicode("The selected address is already in the Address Book."))
                        elif t == "4":
                            r, t = d.inputbox("Type in \"I want to delete this Address Book entry\"")
                            if r == d.DIALOG_OK and t == "I want to delete this Address Book entry":
                                sqlExecute(
                                    "DELETE FROM addressbook WHERE label=? AND address=?",
                                    addrbook[abookcur][0],
                                    addrbook[abookcur][1])
                                del addrbook[abookcur]
                elif menutab == 7:
                    set_background_title(d, "Blacklist Dialog Box")
                    r, t = d.menu(
                        "Do what with \"" + blacklist[blackcur][0] + "\" : \"" + blacklist[blackcur][1] + "\"?",
                        choices=[
                            ("1", "Delete"),
                            ("2", "Enable"),
                            ("3", "Disable")])
                    if r == d.DIALOG_OK:
                        if t == "1":
                            r, t = d.inputbox("Type in \"I want to delete this Blacklist entry\"")
                            if r == d.DIALOG_OK and t == "I want to delete this Blacklist entry":
                                sqlExecute(
                                    "DELETE FROM blacklist WHERE label=? AND address=?",
                                    blacklist[blackcur][0],
                                    blacklist[blackcur][1])
                                del blacklist[blackcur]
                        elif t == "2":
                            sqlExecute(
                                "UPDATE blacklist SET enabled=1 WHERE label=? AND address=?",
                                blacklist[blackcur][0],
                                blacklist[blackcur][1])
                            blacklist[blackcur][2] = True
                        elif t == "3":
                            sqlExecute(
                                "UPDATE blacklist SET enabled=0 WHERE label=? AND address=?",
                                blacklist[blackcur][0],
                                blacklist[blackcur][1])
                            blacklist[blackcur][2] = False
                dialogreset(stdscr)
        else:
            if c == curses.KEY_UP:
                if menutab == 1 and inboxcur > 0:
                    inboxcur -= 1
                if (menutab == 2 or menutab == 4) and addrcur > 0:
                    addrcur -= 1
                if menutab == 3 and sentcur > 0:
                    sentcur -= 1
                if menutab == 5 and subcur > 0:
                    subcur -= 1
                if menutab == 6 and abookcur > 0:
                    abookcur -= 1
                if menutab == 7 and blackcur > 0:
                    blackcur -= 1
            elif c == curses.KEY_DOWN:
                if menutab == 1 and inboxcur < len(inbox) - 1:
                    inboxcur += 1
                if (menutab == 2 or menutab == 4) and addrcur < len(addresses) - 1:
                    addrcur += 1
                if menutab == 3 and sentcur < len(sentbox) - 1:
                    sentcur += 1
                if menutab == 5 and subcur < len(subscriptions) - 1:
                    subcur += 1
                if menutab == 6 and abookcur < len(addrbook) - 1:
                    abookcur += 1
                if menutab == 7 and blackcur < len(blacklist) - 1:
                    blackcur += 1
            elif c == curses.KEY_HOME:
                if menutab == 1:
                    inboxcur = 0
                if menutab == 2 or menutab == 4:
                    addrcur = 0
                if menutab == 3:
                    sentcur = 0
                if menutab == 5:
                    subcur = 0
                if menutab == 6:
                    abookcur = 0
                if menutab == 7:
                    blackcur = 0
            elif c == curses.KEY_END:
                if menutab == 1:
                    inboxcur = len(inbox) - 1
                if menutab == 2 or menutab == 4:
                    addrcur = len(addresses) - 1
                if menutab == 3:
                    sentcur = len(sentbox) - 1
                if menutab == 5:
                    subcur = len(subscriptions) - 1
                if menutab == 6:
                    abookcur = len(addrbook) - 1
                if menutab == 7:
                    blackcur = len(blackcur) - 1
        redraw(stdscr)


# pylint: disable=too-many-locals, too-many-arguments
def sendMessage(sender="", recv="", broadcast=None, subject="", body="", reply=False):
    """Method for message sending"""
    if sender == "":
        return
    d = Dialog(dialog="dialog")
    set_background_title(d, "Send a message")
    if recv == "":
        r, t = d.inputbox(
            "Recipient address (Cancel to load from the Address Book or leave blank to broadcast)",
            10,
            60)
        if r != d.DIALOG_OK:
            global menutab
            menutab = 6
            return
        recv = t
    if broadcast is None and sender != recv:
        r, t = d.radiolist(
            "How to send the message?",
            choices=[
                ("1", "Send to one or more specific people", 1),
                ("2", "Broadcast to everyone who is subscribed to your address", 0)])
        if r != d.DIALOG_OK:
            return
        broadcast = False
        if t == "2":        # Broadcast
            broadcast = True
    if subject == "" or reply:
        r, t = d.inputbox("Message subject", width=60, init=subject)
        if r != d.DIALOG_OK:
            return
        subject = t
    if body == "" or reply:
        r, t = d.inputbox("Message body", 10, 80, init=body)
        if r != d.DIALOG_OK:
            return
        body = t
        body = body.replace("\\n", "\n").replace("\\t", "\t")

    if not broadcast:
        recvlist = []
        for _, item in enumerate(recv.replace(",", ";").split(";")):
            recvlist.append(item.strip())
        list(set(recvlist))         # Remove exact duplicates
        for addr in recvlist:
            if addr != "":
                status, version, stream = decodeAddress(addr)[:3]
                if status != "success":
                    set_background_title(d, "Recipient address error")
                    err = "Could not decode" + addr + " : " + status + "\n\n"
                    if status == "missingbm":
                        err += "Bitmessage addresses should start with \"BM-\"."
                    elif status == "checksumfailed":
                        err += "The address was not typed or copied correctly."
                    elif status == "invalidcharacters":
                        err += "The address contains invalid characters."
                    elif status == "versiontoohigh":
                        err += ("The address version is too high. Either you need to upgrade your Bitmessage software"
                                " or your acquaintance is doing something clever.")
                    elif status == "ripetooshort":
                        err += ("Some data encoded in the address is too short. There might be something wrong with"
                                " the software of your acquaintance.")
                    elif status == "ripetoolong":
                        err += ("Some data encoded in the address is too long. There might be something wrong with"
                                " the software of your acquaintance.")
                    elif status == "varintmalformed":
                        err += ("Some data encoded in the address is malformed. There might be something wrong with"
                                " the software of your acquaintance.")
                    else:
                        err += "It is unknown what is wrong with the address."
                    scrollbox(d, unicode(err))
                else:
                    addr = addBMIfNotPresent(addr)
                    if version > 4 or version <= 1:
                        set_background_title(d, "Recipient address error")
                        scrollbox(d, unicode(
                            "Could not understand version number " +
                            version +
                            "of address" +
                            addr +
                            "."))
                        continue
                    if stream > 1 or stream == 0:
                        set_background_title(d, "Recipient address error")
                        scrollbox(d, unicode(
                            "Bitmessage currently only supports stream numbers of 1,"
                            "unlike as requested for address " + addr + "."))
                        continue
                    if not network.stats.connectedHostsList():
                        set_background_title(d, "Not connected warning")
                        scrollbox(d, unicode("Because you are not currently connected to the network, "))
                    helper_sent.insert(
                        toAddress=addr, fromAddress=sender, subject=subject, message=body)
                    queues.workerQueue.put(("sendmessage", addr))
    else:       # Broadcast
        if recv == "":
            set_background_title(d, "Empty sender error")
            scrollbox(d, unicode("You must specify an address to send the message from."))
        else:
            # dummy ackdata, no need for stealth
            helper_sent.insert(
                fromAddress=sender, subject=subject,
                message=body, status='broadcastqueued')
            queues.workerQueue.put(('sendbroadcast', ''))


# pylint: disable=redefined-outer-name, too-many-locals
def loadInbox():
    """Load the list of messages"""
    sys.stdout = sys.__stdout__
    print "Loading inbox messages..."
    sys.stdout = printlog

    where = "toaddress || fromaddress || subject || message"
    what = "%%"
    ret = sqlQuery("""SELECT msgid, toaddress, fromaddress, subject, received, read
        FROM inbox WHERE folder='inbox' AND %s LIKE ?
        ORDER BY received
        """ % (where,), what)
    for row in ret:
        msgid, toaddr, fromaddr, subject, received, read = row
        subject = ascii(shared.fixPotentiallyInvalidUTF8Data(subject))

        # Set label for to address
        try:
            if toaddr == BROADCAST_STR:
                tolabel = BROADCAST_STR
            else:
                tolabel = BMConfigParser().get(toaddr, "label")
        except:
            tolabel = ""
        if tolabel == "":
            tolabel = toaddr
        tolabel = shared.fixPotentiallyInvalidUTF8Data(tolabel)

        # Set label for from address
        fromlabel = ""
        if BMConfigParser().has_section(fromaddr):
            fromlabel = BMConfigParser().get(fromaddr, "label")
        if fromlabel == "":         # Check Address Book
            qr = sqlQuery("SELECT label FROM addressbook WHERE address=?", fromaddr)
            if qr != []:
                for r in qr:
                    fromlabel, = r
        if fromlabel == "":         # Check Subscriptions
            qr = sqlQuery("SELECT label FROM subscriptions WHERE address=?", fromaddr)
            if qr != []:
                for r in qr:
                    fromlabel, = r
        if fromlabel == "":
            fromlabel = fromaddr
        fromlabel = shared.fixPotentiallyInvalidUTF8Data(fromlabel)

        # Load into array
        inbox.append([msgid, tolabel, toaddr, fromlabel, fromaddr, subject, l10n.formatTimestamp(
            received, False), read])
    inbox.reverse()


def loadSent():
    """Load the messages that sent"""
    sys.stdout = sys.__stdout__
    print "Loading sent messages..."
    sys.stdout = printlog

    where = "toaddress || fromaddress || subject || message"
    what = "%%"
    ret = sqlQuery("""SELECT toaddress, fromaddress, subject, status, ackdata, lastactiontime
        FROM sent WHERE folder='sent' AND %s LIKE ?
        ORDER BY lastactiontime
        """ % (where,), what)
    for row in ret:
        toaddr, fromaddr, subject, status, ackdata, lastactiontime = row
        subject = ascii(shared.fixPotentiallyInvalidUTF8Data(subject))

        # Set label for to address
        tolabel = ""
        qr = sqlQuery("SELECT label FROM addressbook WHERE address=?", toaddr)
        if qr != []:
            for r in qr:
                tolabel, = r
        if tolabel == "":
            qr = sqlQuery("SELECT label FROM subscriptions WHERE address=?", toaddr)
            if qr != []:
                for r in qr:
                    tolabel, = r
        if tolabel == "":
            if BMConfigParser().has_section(toaddr):
                tolabel = BMConfigParser().get(toaddr, "label")
        if tolabel == "":
            tolabel = toaddr

        # Set label for from address
        fromlabel = ""
        if BMConfigParser().has_section(fromaddr):
            fromlabel = BMConfigParser().get(fromaddr, "label")
        if fromlabel == "":
            fromlabel = fromaddr

        # Set status string
        if status == "awaitingpubkey":
            statstr = "Waiting for their public key. Will request it again soon"
        elif status == "doingpowforpubkey":
            statstr = "Encryption key request queued"
        elif status == "msgqueued":
            statstr = "Message queued"
        elif status == "msgsent":
            t = l10n.formatTimestamp(lastactiontime, False)
            statstr = "Message sent at " + t + ".Waiting for acknowledgement."
        elif status == "msgsentnoackexpected":
            t = l10n.formatTimestamp(lastactiontime, False)
            statstr = "Message sent at " + t + "."
        elif status == "doingmsgpow":
            statstr = "The proof of work required to send the message has been queued."
        elif status == "ackreceived":
            t = l10n.formatTimestamp(lastactiontime, False)
            statstr = "Acknowledgment of the message received at " + t + "."
        elif status == "broadcastqueued":
            statstr = "Broadcast queued."
        elif status == "broadcastsent":
            t = l10n.formatTimestamp(lastactiontime, False)
            statstr = "Broadcast sent at " + t + "."
        elif status == "forcepow":
            statstr = "Forced difficulty override. Message will start sending soon."
        elif status == "badkey":
            statstr = "Warning: Could not encrypt message because the recipient's encryption key is no good."
        elif status == "toodifficult":
            statstr = "Error: The work demanded by the recipient is more difficult than you are willing to do."
        else:
            t = l10n.formatTimestamp(lastactiontime, False)
            statstr = "Unknown status " + status + " at " + t + "."

        # Load into array
        sentbox.append([
            tolabel,
            toaddr,
            fromlabel,
            fromaddr,
            subject,
            statstr,
            ackdata,
            l10n.formatTimestamp(lastactiontime, False)])
    sentbox.reverse()


def loadAddrBook():
    """Load address book"""
    sys.stdout = sys.__stdout__
    print "Loading address book..."
    sys.stdout = printlog

    ret = sqlQuery("SELECT label, address FROM addressbook")
    for row in ret:
        label, addr = row
        label = shared.fixPotentiallyInvalidUTF8Data(label)
        addrbook.append([label, addr])
    addrbook.reverse()


def loadSubscriptions():
    """Load subscription functionality"""
    ret = sqlQuery("SELECT label, address, enabled FROM subscriptions")
    for row in ret:
        label, address, enabled = row
        subscriptions.append([label, address, enabled])
    subscriptions.reverse()


def loadBlackWhiteList():
    """load black/white list"""
    global bwtype
    bwtype = BMConfigParser().get("bitmessagesettings", "blackwhitelist")
    if bwtype == "black":
        ret = sqlQuery("SELECT label, address, enabled FROM blacklist")
    else:
        ret = sqlQuery("SELECT label, address, enabled FROM whitelist")
    for row in ret:
        label, address, enabled = row
        blacklist.append([label, address, enabled])
    blacklist.reverse()


def runwrapper():
    """Main method"""
    sys.stdout = printlog
    # sys.stderr = errlog

    loadInbox()
    loadSent()
    loadAddrBook()
    loadSubscriptions()
    loadBlackWhiteList()

    stdscr = curses.initscr()

    global logpad
    logpad = curses.newpad(1024, curses.COLS)

    stdscr.nodelay(0)
    curses.curs_set(0)
    stdscr.timeout(1000)

    curses.wrapper(run)
    doShutdown()


def run(stdscr):
    """Main loop"""
    # Schedule inventory lookup data
    resetlookups()

    # Init color pairs
    if curses.has_colors():
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)       # red
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)         # green
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)        # yellow
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)      # blue
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)       # magenta
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)      # cyan
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)         # white
        if curses.can_change_color():
            curses.init_color(8, 500, 500, 500)         # gray
            curses.init_pair(8, 8, 0)
            curses.init_color(9, 844, 465, 0)       # orange
            curses.init_pair(9, 9, 0)
        else:
            curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLACK)         # grayish
            curses.init_pair(9, curses.COLOR_YELLOW, curses.COLOR_BLACK)        # orangish

    # Init list of address in 'Your Identities' tab
    configSections = BMConfigParser().addresses()
    for addressInKeysFile in configSections:
        isEnabled = BMConfigParser().getboolean(addressInKeysFile, "enabled")
        addresses.append([BMConfigParser().get(addressInKeysFile, "label"), isEnabled, addressInKeysFile])
        # Set address color
        if not isEnabled:
            addresses[len(addresses) - 1].append(8)         # gray
        elif BMConfigParser().safeGetBoolean(addressInKeysFile, 'chan'):
            addresses[len(addresses) - 1].append(9)         # orange
        elif BMConfigParser().safeGetBoolean(addressInKeysFile, 'mailinglist'):
            addresses[len(addresses) - 1].append(5)         # magenta
        else:
            addresses[len(addresses) - 1].append(0)         # black
    addresses.reverse()

    stdscr.clear()
    redraw(stdscr)
    while quit_ is False:
        drawtab(stdscr)
        handlech(stdscr.getch(), stdscr)


def doShutdown():
    """Shutting the app down"""
    sys.stdout = sys.__stdout__
    print "Shutting down..."
    sys.stdout = printlog
    shutdown.doCleanShutdown()
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    os._exit(0)  # pylint: disable=protected-access
