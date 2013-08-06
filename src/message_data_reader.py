#This program can be used to print out everything in your Inbox or Sent folders and also take things out of the trash.
#Scroll down to the bottom to see the functions that you can uncomment. Save then run this file.
#The functions which only read the database file seem to function just fine even if you have Bitmessage running but you should definitly close it before running the functions that make changes (like taking items out of the trash).

import sqlite3
from time import strftime, localtime
import sys
import shared
import string

appdata = shared.lookupAppdataFolder()

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
        msgid, toaddress, toripe, fromaddress, subject, message, ackdata, lastactiontime, status, pubkeyretrynumber, msgretrynumber, folder, encodingtype = row
        print msgid.encode('hex'), toaddress, 'toripe:', toripe.encode('hex'), 'fromaddress:', fromaddress, 'ENCODING TYPE:', encodingtype, 'SUBJECT:', repr(subject), 'MESSAGE:', repr(message), 'ACKDATA:', ackdata.encode('hex'), lastactiontime, status, pubkeyretrynumber, msgretrynumber, folder

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
    item = '''select hash, transmitdata, time, usedpersonally from pubkeys'''
    parameters = ''
    cur.execute(item, parameters)
    output = cur.fetchall()
    for row in output:
        hash, transmitdata, time, usedpersonally = row
        print 'Hash:', hash.encode('hex'), '\tTime first broadcast:', unicode(strftime('%a, %d %b %Y  %I:%M %p',localtime(time)),'utf-8'), '\tUsed by me personally:', usedpersonally, '\tFull pubkey message:', transmitdata.encode('hex')

def readInventory():
    print 'Printing everything in inventory table:'
    item = '''select hash, objecttype, streamnumber, payload, receivedtime, first20bytesofencryptedmessage from inventory where objecttype = 'msg' '''
    parameters = ''
    cur.execute(item, parameters)
    output = cur.fetchall()
    for row in output[:50]:
        hash, objecttype, streamnumber, payload, receivedtime, first20bytesofencryptedmessage = row
        print 'Hash:', hash.encode('hex'), objecttype, streamnumber, '\t', 'first20bytesofencryptedmessage:', first20bytesofencryptedmessage.encode('hex'), '\t', payload.encode('hex'), '\t', unicode(strftime('%a, %d %b %Y  %I:%M %p',localtime(receivedtime)),'utf-8')

def readInventory2():
    searchValue = ' '
    
    item = '''PRAGMA case_sensitive_like = true '''
    parameters = ''
    cur.execute(item, parameters)
    
    searchValue = string.replace(searchValue,'e','ee')
    searchValue = string.replace(searchValue,'%','e%')
    searchValue = string.replace(searchValue,'_','e_')
    
    print 'Printing subset of inventory table:'
    item = '''SELECT substr(payload,20) FROM inventory'''
    #parameters = ('%'+ searchValue + '%',)
    #print repr(parameters), len(parameters[0])
    parameters = ''
    cur.execute(item, parameters)
    output = cur.fetchall()
    print 'Number of results:', len(output)
    for row in output[:100]:
        print row
        #hash, objecttype, streamnumber, payload, receivedtime = row
        #print 'Hash:', hash.encode('hex'), objecttype, streamnumber, '\t', payload.encode('hex'), '\t', unicode(strftime('%a, %d %b %Y  %I:%M %p',localtime(receivedtime)),'utf-8')
    print 'done'


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
#readInbox()
#readSent()
#readPubkeys()
#readSubscriptions()
readInventory()
#vacuum()  #will defragment and clean empty space from the messages.dat file.
#readInventory2()



