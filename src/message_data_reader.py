#This program can be used to print out everything in your Inbox or Sent folders and also take things out of the trash.
#Scroll down to the bottom to see the functions that you can uncomment. Save then run this file.
#The functions which only read the database file seem to function just fine even if you have Bitmessage running but you should definitly close it before running the functions that make changes (like taking items out of the trash).

import sqlite3
from time import strftime, localtime
import sys
import paths
import queues
import state
from binascii import hexlify

appdata = paths.lookupAppdataFolder()

conn = sqlite3.connect( appdata + 'messages.dat' )
conn.text_factory = str
cur = conn.cursor()

def readInbox():
    print 'Printing everything in inbox table:'
    item = '''select * from inbox'''
    parameters = ''
    cur.execute(item, parameters)
    output = cur.fetchall()
    for row in output:
        print row

def readSent():
    print 'Printing everything in Sent table:'
    item = '''select * from sent where folder !='trash' '''
    parameters = ''
    cur.execute(item, parameters)
    output = cur.fetchall()
    for row in output:
        msgid, toaddress, toripe, fromaddress, subject, message, ackdata, lastactiontime, sleeptill, status, retrynumber, folder, encodingtype, ttl = row
        print hexlify(msgid), toaddress, 'toripe:', hexlify(toripe), 'fromaddress:', fromaddress, 'ENCODING TYPE:', encodingtype, 'SUBJECT:', repr(subject), 'MESSAGE:', repr(message), 'ACKDATA:', hexlify(ackdata), lastactiontime, status, retrynumber, folder

def readSubscriptions():
    print 'Printing everything in subscriptions table:'
    item = '''select * from subscriptions'''
    parameters = ''
    cur.execute(item, parameters)
    output = cur.fetchall()
    for row in output:
        print row

def readPubkeys():
    print 'Printing everything in pubkeys table:'
    item = '''select address, transmitdata, time, usedpersonally from pubkeys'''
    parameters = ''
    cur.execute(item, parameters)
    output = cur.fetchall()
    for row in output:
        address, transmitdata, time, usedpersonally = row
        print 'Address:', address, '\tTime first broadcast:', unicode(strftime('%a, %d %b %Y  %I:%M %p',localtime(time)),'utf-8'), '\tUsed by me personally:', usedpersonally, '\tFull pubkey message:', hexlify(transmitdata)

def readInventory():
    print 'Printing everything in inventory table:'
    item = '''select hash, objecttype, streamnumber, payload, expirestime from inventory'''
    parameters = ''
    cur.execute(item, parameters)
    output = cur.fetchall()
    for row in output:
        hash, objecttype, streamnumber, payload, expirestime = row
        print 'Hash:', hexlify(hash), objecttype, streamnumber, '\t', hexlify(payload), '\t', unicode(strftime('%a, %d %b %Y  %I:%M %p',localtime(expirestime)),'utf-8')


def takeInboxMessagesOutOfTrash():
    item = '''update inbox set folder='inbox' where folder='trash' '''
    parameters = ''
    cur.execute(item, parameters)
    output = cur.fetchall()
    conn.commit()
    print 'done'

def takeSentMessagesOutOfTrash():
    item = '''update sent set folder='sent' where folder='trash' '''
    parameters = ''
    cur.execute(item, parameters)
    output = cur.fetchall()
    conn.commit()
    print 'done'

def markAllInboxMessagesAsUnread():
    item = '''update inbox set read='0' '''
    parameters = ''
    cur.execute(item, parameters)
    output = cur.fetchall()
    conn.commit()
    queues.UISignalQueue.put(('changedInboxUnread', None))
    print 'done'

def vacuum():
    item = '''VACUUM'''
    parameters = ''
    cur.execute(item, parameters)
    output = cur.fetchall()
    conn.commit()
    print 'done'

#takeInboxMessagesOutOfTrash()
#takeSentMessagesOutOfTrash()
#markAllInboxMessagesAsUnread()
readInbox()
#readSent()
#readPubkeys()
#readSubscriptions()
#readInventory()
#vacuum()  #will defragment and clean empty space from the messages.dat file.



