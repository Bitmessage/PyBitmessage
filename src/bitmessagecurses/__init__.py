# Copyright (c) 2014 Luke Montalvo <lukemontalvo@gmail.com>
# This file adds a alternative commandline interface

import curses
import shared
import os
import sys
import StringIO

from addresses import *

quit = False
menutab = 1
menu = ["Inbox", "Send", "Sent", "Your Identities", "Subscriptions", "Address Book", "Blacklist", "Network Status"]
log = ""

addresses = []
addrcur = 0

class printLog:
    def write(self, output):
        global log
        log += output
printlog = printLog()

def cpair(a):
    r = curses.color_pair(a)
    if r not in range(1, curses.COLOR_PAIRS-1):
        r = curses.color_pair(0)
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

def drawtab(stdscr):
    if menutab in range(0, len(menu)):
        if menutab == 1: # Inbox
            stdscr.addstr(3, 5, "new messages")
        elif menutab == 2: # Send
            stdscr.addstr(3, 5, "to: from:")
        elif menutab == 4: # Identities
            for i, item in enumerate(addresses):
                a = 0
                if i == addrcur:
                    a = curses.A_REVERSE
                stdscr.addstr(3+i, 5, item[0], cpair(item[3]) | a)
    stdscr.refresh()

def redraw(stdscr):
    stdscr.erase()
    stdscr.border()
    drawmenu(stdscr)
    stdscr.refresh()
def handlech(c, stdscr):
    if c != curses.ERR:
        if c in range(256): 
            if chr(c) in '12345678':
                global menutab
                menutab = int(chr(c))
            elif chr(c) == 'q':
                global quit
                quit = True
        else:
            global addrcur
            if c == curses.KEY_UP:
                if (addrcur > 0):
                    addrcur -= 1
            elif c == curses.KEY_DOWN:
                if (addrcur < len(addresses)-1):
                    addrcur += 1
        redraw(stdscr)

def runwrapper():
    sys.stdout = printlog
    stdscr = curses.initscr()
    
    stdscr.nodelay(1)
    curses.curs_set(0)
    curses.start_color()
    
    curses.wrapper(run)
    shutdown()

def run(stdscr):
    # Init list of address in 'Your Identities' tab
    configSections = shared.config.sections()
    if curses.has_colors():
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK) # red
        if curses.can_change_color():
            curses.init_color(8, 500, 500, 500) # gray
            curses.init_pair(8, 8, 0)
            curses.init_color(9, 844, 465, 0) # orange
            curses.init_pair(9, 9, 0)
    else:
        global menutab
        menutab = 4
        curses.beep()
    for addressInKeysFile in configSections:
        if addressInKeysFile != "bitmessagesettings":
            isEnabled = shared.config.getboolean(addressInKeysFile, "enabled")
            addresses.append([shared.config.get(addressInKeysFile, "label"), isEnabled, str(decodeAddress(addressInKeysFile)[2])])
            if not isEnabled:
                addresses[len(addresses)-1].append(8) # gray
            elif shared.safeConfigGetBoolean(addressInKeysFile, 'chan'):
                addresses[len(addresses)-1].append(9) # orange
            elif shared.safeConfigGetBoolean(addressInKeysFile, 'mailinglist'):
                addresses[len(addresses)-1].append(5) # magenta
    
    # Load messages from database
    """
    loadInbox()
    loadSend()
    """
    
    # Initialize address display and send form
    """
    rerenderAddressBook()
    rerenderSubscriptions()
    rerenderComboBoxSendForm()
    """
    
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
    
    os._exit(0)
