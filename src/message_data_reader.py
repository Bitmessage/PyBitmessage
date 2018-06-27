# pylint: disable=too-many-locals
"""
This program can be used to print out everything in your Inbox or Sent folders and also take things out of the trash.
Scroll down to the bottom to see the functions that you can uncomment. Save then run this file.
The functions which only read the database file seem to function just
fine even if you have Bitmessage running but you should definitly close
it before running the functions that make changes (like taking items out
of the trash).
"""

from __future__ import absolute_import

import sqlite3
from binascii import hexlify
from time import strftime, localtime

import paths
import queues


appdata = paths.lookupAppdataFolder()

conn = sqlite3.connect(appdata + 'messages.dat')
conn.text_factory = str
cur = conn.cursor()


def readInbox():
    """Print each row from inbox table"""
    print 'Printing everything in inbox table:'
    item = '''select * from inbox'''
    parameters = ''
    cur.execute(item, parameters)
    output = cur.fetchall()
    for row in output:
        print row


def readSent():
    """Print each row from sent table"""
    print 'Printing everything in Sent table:'
    item = '''select * from sent where folder !='trash' '''
    parameters = ''
    cur.execute(item, parameters)
    output = cur.fetchall()
    for row in output:
        (msgid, toaddress, toripe, fromaddress, subject, message, ackdata, lastactiontime,
         sleeptill, status, retrynumber, folder, encodingtype, ttl) = row  # pylint: disable=unused-variable
        print(hexlify(msgid), toaddress, 'toripe:', hexlify(toripe), 'fromaddress:', fromaddress, 'ENCODING TYPE:',
              encodingtype, 'SUBJECT:', repr(subject), 'MESSAGE:', repr(message), 'ACKDATA:', hexlify(ackdata),
              lastactiontime, status, retrynumber, folder)


def readSubscriptions():
    """Print each row from subscriptions table"""
    print 'Printing everything in subscriptions table:'
    item = '''select * from subscriptions'''
    parameters = ''
    cur.execute(item, parameters)
    output = cur.fetchall()
    for row in output:
        print row


def readPubkeys():
    """Print each row from pubkeys table"""
    print 'Printing everything in pubkeys table:'
    item = '''select address, transmitdata, time, usedpersonally from pubkeys'''
    parameters = ''
    cur.execute(item, parameters)
    output = cur.fetchall()
    for row in output:
        address, transmitdata, time, usedpersonally = row
        print(
            'Address:', address, '\tTime first broadcast:', unicode(
                strftime('%a, %d %b %Y  %I:%M %p', localtime(time)), 'utf-8'),
            '\tUsed by me personally:', usedpersonally, '\tFull pubkey message:', hexlify(transmitdata),
        )


def readInventory():
    """Print each row from inventory table"""
    print 'Printing everything in inventory table:'
    item = '''select hash, objecttype, streamnumber, payload, expirestime from inventory'''
    parameters = ''
    cur.execute(item, parameters)
    output = cur.fetchall()
    for row in output:
        obj_hash, objecttype, streamnumber, payload, expirestime = row
        print 'Hash:', hexlify(obj_hash), objecttype, streamnumber, '\t', hexlify(payload), '\t', unicode(
            strftime('%a, %d %b %Y  %I:%M %p', localtime(expirestime)), 'utf-8')


def takeInboxMessagesOutOfTrash():
    """Update all inbox messages with folder=trash to have folder=inbox"""
    item = '''update inbox set folder='inbox' where folder='trash' '''
    parameters = ''
    cur.execute(item, parameters)
    _ = cur.fetchall()
    conn.commit()
    print 'done'


def takeSentMessagesOutOfTrash():
    """Update all sent messages with folder=trash to have folder=sent"""
    item = '''update sent set folder='sent' where folder='trash' '''
    parameters = ''
    cur.execute(item, parameters)
    _ = cur.fetchall()
    conn.commit()
    print 'done'


def markAllInboxMessagesAsUnread():
    """Update all messages in inbox to have read=0"""
    item = '''update inbox set read='0' '''
    parameters = ''
    cur.execute(item, parameters)
    _ = cur.fetchall()
    conn.commit()
    queues.UISignalQueue.put(('changedInboxUnread', None))
    print 'done'


def vacuum():
    """Perform a vacuum on the database"""
    item = '''VACUUM'''
    parameters = ''
    cur.execute(item, parameters)
    _ = cur.fetchall()
    conn.commit()
    print 'done'


if __name__ == '__main__':
    readInbox()
