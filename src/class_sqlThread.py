import threading
import shared
import sqlite3
import time
import shutil  # used for moving the messages.dat file
import sys
import os
from debug import logger
from namecoin import ensureNamecoinOptions
import random
import string
import tr#anslate

# This thread exists because SQLITE3 is so un-threadsafe that we must
# submit queries to it and it puts results back in a different queue. They
# won't let us just use locks.


class sqlThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self, name="SQL")

    def run(self):        
        self.conn = sqlite3.connect(shared.appdata + 'messages.dat')
        self.conn.text_factory = str
        self.cur = self.conn.cursor()
        
        self.cur.execute('PRAGMA secure_delete = true')

        try:
            self.cur.execute(
                '''CREATE TABLE inbox (msgid blob, toaddress text, fromaddress text, subject text, received text, message text, folder text, encodingtype int, read bool, sighash blob, UNIQUE(msgid) ON CONFLICT REPLACE)''' )
            self.cur.execute(
                '''CREATE TABLE sent (msgid blob, toaddress text, toripe blob, fromaddress text, subject text, message text, ackdata blob, senttime integer, lastactiontime integer, sleeptill integer, status text, retrynumber integer, folder text, encodingtype int, ttl int)''' )
            self.cur.execute(
                '''CREATE TABLE subscriptions (label text, address text, enabled bool)''' )
            self.cur.execute(
                '''CREATE TABLE addressbook (label text, address text)''' )
            self.cur.execute(
                '''CREATE TABLE blacklist (label text, address text, enabled bool)''' )
            self.cur.execute(
                '''CREATE TABLE whitelist (label text, address text, enabled bool)''' )
            self.cur.execute(
                '''CREATE TABLE pubkeys (address text, addressversion int, transmitdata blob, time int, usedpersonally text, UNIQUE(address) ON CONFLICT REPLACE)''' )
            self.cur.execute(
                '''CREATE TABLE inventory (hash blob, objecttype int, streamnumber int, payload blob, expirestime integer, tag blob, UNIQUE(hash) ON CONFLICT REPLACE)''' )
            self.cur.execute(
                '''INSERT INTO subscriptions VALUES('Bitmessage new releases/announcements','BM-GtovgYdgs7qXPkoYaRgrLFuFKz1SFpsw',1)''')
            self.cur.execute(
                '''CREATE TABLE settings (key blob, value blob, UNIQUE(key) ON CONFLICT REPLACE)''' )
            self.cur.execute( '''INSERT INTO settings VALUES('version','10')''')
            self.cur.execute( '''INSERT INTO settings VALUES('lastvacuumtime',?)''', (
                int(time.time()),))
            self.cur.execute(
                '''CREATE TABLE objectprocessorqueue (objecttype int, data blob, UNIQUE(objecttype, data) ON CONFLICT REPLACE)''' )
            self.conn.commit()
            logger.info('Created messages database file')
        except Exception as err:
            if str(err) == 'table inbox already exists':
                logger.debug('Database file already exists.')

            else:
                sys.stderr.write(
                    'ERROR trying to create database file (message.dat). Error message: %s\n' % str(err))
                os._exit(0)

        if shared.config.getint('bitmessagesettings', 'settingsversion') == 1:
            shared.config.set('bitmessagesettings', 'settingsversion', '2')
                      # If the settings version is equal to 2 or 3 then the
                      # sqlThread will modify the pubkeys table and change
                      # the settings version to 4.
            shared.config.set('bitmessagesettings', 'socksproxytype', 'none')
            shared.config.set('bitmessagesettings', 'sockshostname', 'localhost')
            shared.config.set('bitmessagesettings', 'socksport', '9050')
            shared.config.set('bitmessagesettings', 'socksauthentication', 'false')
            shared.config.set('bitmessagesettings', 'socksusername', '')
            shared.config.set('bitmessagesettings', 'sockspassword', '')
            shared.config.set('bitmessagesettings', 'sockslisten', 'false')
            shared.config.set('bitmessagesettings', 'keysencrypted', 'false')
            shared.config.set('bitmessagesettings', 'messagesencrypted', 'false')

        # People running earlier versions of PyBitmessage do not have the
        # usedpersonally field in their pubkeys table. Let's add it.
        if shared.config.getint('bitmessagesettings', 'settingsversion') == 2:
            item = '''ALTER TABLE pubkeys ADD usedpersonally text DEFAULT 'no' '''
            parameters = ''
            self.cur.execute(item, parameters)
            self.conn.commit()

            shared.config.set('bitmessagesettings', 'settingsversion', '3')

        # People running earlier versions of PyBitmessage do not have the
        # encodingtype field in their inbox and sent tables or the read field
        # in the inbox table. Let's add them.
        if shared.config.getint('bitmessagesettings', 'settingsversion') == 3:
            item = '''ALTER TABLE inbox ADD encodingtype int DEFAULT '2' '''
            parameters = ''
            self.cur.execute(item, parameters)

            item = '''ALTER TABLE inbox ADD read bool DEFAULT '1' '''
            parameters = ''
            self.cur.execute(item, parameters)

            item = '''ALTER TABLE sent ADD encodingtype int DEFAULT '2' '''
            parameters = ''
            self.cur.execute(item, parameters)
            self.conn.commit()

            shared.config.set('bitmessagesettings', 'settingsversion', '4')

        if shared.config.getint('bitmessagesettings', 'settingsversion') == 4:
            shared.config.set('bitmessagesettings', 'defaultnoncetrialsperbyte', str(
                shared.networkDefaultProofOfWorkNonceTrialsPerByte))
            shared.config.set('bitmessagesettings', 'defaultpayloadlengthextrabytes', str(
                shared.networkDefaultPayloadLengthExtraBytes))
            shared.config.set('bitmessagesettings', 'settingsversion', '5')

        if shared.config.getint('bitmessagesettings', 'settingsversion') == 5:
            shared.config.set(
                'bitmessagesettings', 'maxacceptablenoncetrialsperbyte', '0')
            shared.config.set(
                'bitmessagesettings', 'maxacceptablepayloadlengthextrabytes', '0')
            shared.config.set('bitmessagesettings', 'settingsversion', '6')

        # From now on, let us keep a 'version' embedded in the messages.dat
        # file so that when we make changes to the database, the database
        # version we are on can stay embedded in the messages.dat file. Let us
        # check to see if the settings table exists yet.
        item = '''SELECT name FROM sqlite_master WHERE type='table' AND name='settings';'''
        parameters = ''
        self.cur.execute(item, parameters)
        if self.cur.fetchall() == []:
            # The settings table doesn't exist. We need to make it.
            logger.debug('In messages.dat database, creating new \'settings\' table.')
            self.cur.execute(
                '''CREATE TABLE settings (key text, value blob, UNIQUE(key) ON CONFLICT REPLACE)''' )
            self.cur.execute( '''INSERT INTO settings VALUES('version','1')''')
            self.cur.execute( '''INSERT INTO settings VALUES('lastvacuumtime',?)''', (
                int(time.time()),))
            logger.debug('In messages.dat database, removing an obsolete field from the pubkeys table.')
            self.cur.execute(
                '''CREATE TEMPORARY TABLE pubkeys_backup(hash blob, transmitdata blob, time int, usedpersonally text, UNIQUE(hash) ON CONFLICT REPLACE);''')
            self.cur.execute(
                '''INSERT INTO pubkeys_backup SELECT hash, transmitdata, time, usedpersonally FROM pubkeys;''')
            self.cur.execute( '''DROP TABLE pubkeys''')
            self.cur.execute(
                '''CREATE TABLE pubkeys (hash blob, transmitdata blob, time int, usedpersonally text, UNIQUE(hash) ON CONFLICT REPLACE)''' )
            self.cur.execute(
                '''INSERT INTO pubkeys SELECT hash, transmitdata, time, usedpersonally FROM pubkeys_backup;''')
            self.cur.execute( '''DROP TABLE pubkeys_backup;''')
            logger.debug('Deleting all pubkeys from inventory. They will be redownloaded and then saved with the correct times.')
            self.cur.execute(
                '''delete from inventory where objecttype = 'pubkey';''')
            logger.debug('replacing Bitmessage announcements mailing list with a new one.')
            self.cur.execute(
                '''delete from subscriptions where address='BM-BbkPSZbzPwpVcYZpU4yHwf9ZPEapN5Zx' ''')
            self.cur.execute(
                '''INSERT INTO subscriptions VALUES('Bitmessage new releases/announcements','BM-GtovgYdgs7qXPkoYaRgrLFuFKz1SFpsw',1)''')
            logger.debug('Commiting.')
            self.conn.commit()
            logger.debug('Vacuuming message.dat. You might notice that the file size gets much smaller.')
            self.cur.execute( ''' VACUUM ''')

        # After code refactoring, the possible status values for sent messages
        # have changed.
        self.cur.execute(
            '''update sent set status='doingmsgpow' where status='doingpow'  ''')
        self.cur.execute(
            '''update sent set status='msgsent' where status='sentmessage'  ''')
        self.cur.execute(
            '''update sent set status='doingpubkeypow' where status='findingpubkey'  ''')
        self.cur.execute(
            '''update sent set status='broadcastqueued' where status='broadcastpending'  ''')
        self.conn.commit()
        
        if not shared.config.has_option('bitmessagesettings', 'sockslisten'):
            shared.config.set('bitmessagesettings', 'sockslisten', 'false')
            
        ensureNamecoinOptions()
            
        """# Add a new column to the inventory table to store the first 20 bytes of encrypted messages to support Android app
        item = '''SELECT value FROM settings WHERE key='version';'''
        parameters = ''
        self.cur.execute(item, parameters)
        if int(self.cur.fetchall()[0][0]) == 1:
            print 'upgrading database'
            item = '''ALTER TABLE inventory ADD first20bytesofencryptedmessage blob DEFAULT '' '''
            parameters = ''
            self.cur.execute(item, parameters)
            item = '''update settings set value=? WHERE key='version';'''
            parameters = (2,)
            self.cur.execute(item, parameters)"""

        # Let's get rid of the first20bytesofencryptedmessage field in the inventory table.
        item = '''SELECT value FROM settings WHERE key='version';'''
        parameters = ''
        self.cur.execute(item, parameters)
        if int(self.cur.fetchall()[0][0]) == 2:
            logger.debug('In messages.dat database, removing an obsolete field from the inventory table.')
            self.cur.execute(
                '''CREATE TEMPORARY TABLE inventory_backup(hash blob, objecttype text, streamnumber int, payload blob, receivedtime integer, UNIQUE(hash) ON CONFLICT REPLACE);''')
            self.cur.execute(
                '''INSERT INTO inventory_backup SELECT hash, objecttype, streamnumber, payload, receivedtime FROM inventory;''')
            self.cur.execute( '''DROP TABLE inventory''')
            self.cur.execute(
                '''CREATE TABLE inventory (hash blob, objecttype text, streamnumber int, payload blob, receivedtime integer, UNIQUE(hash) ON CONFLICT REPLACE)''' )
            self.cur.execute(
                '''INSERT INTO inventory SELECT hash, objecttype, streamnumber, payload, receivedtime FROM inventory_backup;''')
            self.cur.execute( '''DROP TABLE inventory_backup;''')
            item = '''update settings set value=? WHERE key='version';'''
            parameters = (3,)
            self.cur.execute(item, parameters)

        # Add a new column to the inventory table to store tags.
        item = '''SELECT value FROM settings WHERE key='version';'''
        parameters = ''
        self.cur.execute(item, parameters)
        currentVersion = int(self.cur.fetchall()[0][0])
        if currentVersion == 1 or currentVersion == 3:
            logger.debug('In messages.dat database, adding tag field to the inventory table.')
            item = '''ALTER TABLE inventory ADD tag blob DEFAULT '' '''
            parameters = ''
            self.cur.execute(item, parameters)
            item = '''update settings set value=? WHERE key='version';'''
            parameters = (4,)
            self.cur.execute(item, parameters)

        if not shared.config.has_option('bitmessagesettings', 'userlocale'):
            shared.config.set('bitmessagesettings', 'userlocale', 'system')
        if not shared.config.has_option('bitmessagesettings', 'sendoutgoingconnections'):
            shared.config.set('bitmessagesettings', 'sendoutgoingconnections', 'True')

        # Raise the default required difficulty from 1 to 2
        # With the change to protocol v3, this is obsolete.
        if shared.config.getint('bitmessagesettings', 'settingsversion') == 6:
            """if int(shared.config.get('bitmessagesettings','defaultnoncetrialsperbyte')) == shared.networkDefaultProofOfWorkNonceTrialsPerByte:
                shared.config.set('bitmessagesettings','defaultnoncetrialsperbyte', str(shared.networkDefaultProofOfWorkNonceTrialsPerByte * 2))
                """
            shared.config.set('bitmessagesettings', 'settingsversion', '7')

        # Add a new column to the pubkeys table to store the address version.
        # We're going to trash all of our pubkeys and let them be redownloaded.
        item = '''SELECT value FROM settings WHERE key='version';'''
        parameters = ''
        self.cur.execute(item, parameters)
        currentVersion = int(self.cur.fetchall()[0][0])
        if currentVersion == 4:
            self.cur.execute( '''DROP TABLE pubkeys''')
            self.cur.execute(
                '''CREATE TABLE pubkeys (hash blob, addressversion int, transmitdata blob, time int, usedpersonally text, UNIQUE(hash, addressversion) ON CONFLICT REPLACE)''' )
            self.cur.execute(
                '''delete from inventory where objecttype = 'pubkey';''')
            item = '''update settings set value=? WHERE key='version';'''
            parameters = (5,)
            self.cur.execute(item, parameters)
            
        if not shared.config.has_option('bitmessagesettings', 'useidenticons'):
            shared.config.set('bitmessagesettings', 'useidenticons', 'True')
        if not shared.config.has_option('bitmessagesettings', 'identiconsuffix'): # acts as a salt
            shared.config.set('bitmessagesettings', 'identiconsuffix', ''.join(random.choice("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz") for x in range(12))) # a twelve character pseudo-password to salt the identicons

        #Add settings to support no longer resending messages after a certain period of time even if we never get an ack
        if shared.config.getint('bitmessagesettings', 'settingsversion') == 7:
            shared.config.set(
                'bitmessagesettings', 'stopresendingafterxdays', '')
            shared.config.set(
                'bitmessagesettings', 'stopresendingafterxmonths', '')
            shared.config.set('bitmessagesettings', 'settingsversion', '8') 

        # Add a new table: objectprocessorqueue with which to hold objects
        # that have yet to be processed if the user shuts down Bitmessage.
        item = '''SELECT value FROM settings WHERE key='version';'''
        parameters = ''
        self.cur.execute(item, parameters)
        currentVersion = int(self.cur.fetchall()[0][0])
        if currentVersion == 5:
            self.cur.execute( '''DROP TABLE knownnodes''')
            self.cur.execute(
                '''CREATE TABLE objectprocessorqueue (objecttype text, data blob, UNIQUE(objecttype, data) ON CONFLICT REPLACE)''' )
            item = '''update settings set value=? WHERE key='version';'''
            parameters = (6,)
            self.cur.execute(item, parameters)
        
        # changes related to protocol v3
		#    In table inventory and objectprocessorqueue, objecttype is now an integer (it was a human-friendly string previously)
        item = '''SELECT value FROM settings WHERE key='version';'''
        parameters = ''
        self.cur.execute(item, parameters)
        currentVersion = int(self.cur.fetchall()[0][0])
        if currentVersion == 6:
            logger.debug('In messages.dat database, dropping and recreating the inventory table.')
            self.cur.execute( '''DROP TABLE inventory''')
            self.cur.execute( '''CREATE TABLE inventory (hash blob, objecttype int, streamnumber int, payload blob, expirestime integer, tag blob, UNIQUE(hash) ON CONFLICT REPLACE)''' )
            self.cur.execute( '''DROP TABLE objectprocessorqueue''')
            self.cur.execute( '''CREATE TABLE objectprocessorqueue (objecttype int, data blob, UNIQUE(objecttype, data) ON CONFLICT REPLACE)''' )
            item = '''update settings set value=? WHERE key='version';'''
            parameters = (7,)
            self.cur.execute(item, parameters)
            logger.debug('Finished dropping and recreating the inventory table.')
        
        # With the change to protocol version 3, reset the user-settable difficulties to 1    
        if shared.config.getint('bitmessagesettings', 'settingsversion') == 8:
            shared.config.set('bitmessagesettings','defaultnoncetrialsperbyte', str(shared.networkDefaultProofOfWorkNonceTrialsPerByte))
            shared.config.set('bitmessagesettings','defaultpayloadlengthextrabytes', str(shared.networkDefaultPayloadLengthExtraBytes))
            previousTotalDifficulty = int(shared.config.getint('bitmessagesettings', 'maxacceptablenoncetrialsperbyte')) / 320
            previousSmallMessageDifficulty = int(shared.config.getint('bitmessagesettings', 'maxacceptablepayloadlengthextrabytes')) / 14000
            shared.config.set('bitmessagesettings','maxacceptablenoncetrialsperbyte', str(previousTotalDifficulty * 1000))
            shared.config.set('bitmessagesettings','maxacceptablepayloadlengthextrabytes', str(previousSmallMessageDifficulty * 1000))
            shared.config.set('bitmessagesettings', 'settingsversion', '9')
                
        # Adjust the required POW values for each of this user's addresses to conform to protocol v3 norms.
        if shared.config.getint('bitmessagesettings', 'settingsversion') == 9:
            for addressInKeysFile in shared.config.sections():
                try:
                    previousTotalDifficulty = float(shared.config.getint(addressInKeysFile, 'noncetrialsperbyte')) / 320
                    previousSmallMessageDifficulty = float(shared.config.getint(addressInKeysFile, 'payloadlengthextrabytes')) / 14000
                    if previousTotalDifficulty <= 2:
                        previousTotalDifficulty = 1
                    if previousSmallMessageDifficulty < 1:
                        previousSmallMessageDifficulty = 1
                    shared.config.set(addressInKeysFile,'noncetrialsperbyte', str(int(previousTotalDifficulty * 1000)))
                    shared.config.set(addressInKeysFile,'payloadlengthextrabytes', str(int(previousSmallMessageDifficulty * 1000)))
                except:
                    continue
            shared.config.set('bitmessagesettings', 'maxdownloadrate', '0')
            shared.config.set('bitmessagesettings', 'maxuploadrate', '0')
            shared.config.set('bitmessagesettings', 'settingsversion', '10')
            shared.writeKeysFile()
            
        # sanity check
        if shared.config.getint('bitmessagesettings', 'maxacceptablenoncetrialsperbyte') == 0:
            shared.config.set('bitmessagesettings','maxacceptablenoncetrialsperbyte', str(shared.ridiculousDifficulty * shared.networkDefaultProofOfWorkNonceTrialsPerByte))
        if shared.config.getint('bitmessagesettings', 'maxacceptablepayloadlengthextrabytes') == 0:
            shared.config.set('bitmessagesettings','maxacceptablepayloadlengthextrabytes', str(shared.ridiculousDifficulty * shared.networkDefaultPayloadLengthExtraBytes))

        # The format of data stored in the pubkeys table has changed. Let's
        # clear it, and the pubkeys from inventory, so that they'll be re-downloaded.
        item = '''SELECT value FROM settings WHERE key='version';'''
        parameters = ''
        self.cur.execute(item, parameters)
        currentVersion = int(self.cur.fetchall()[0][0])
        if currentVersion == 7:
            logger.debug('In messages.dat database, clearing pubkeys table because the data format has been updated.')
            self.cur.execute(
                '''delete from inventory where objecttype = 1;''')
            self.cur.execute(
                '''delete from pubkeys;''')
            # Any sending messages for which we *thought* that we had the pubkey must
            # be rechecked.
            self.cur.execute(
                '''UPDATE sent SET status='msgqueued' WHERE status='doingmsgpow' or status='badkey';''')
            query = '''update settings set value=? WHERE key='version';'''
            parameters = (8,)
            self.cur.execute(query, parameters)
            logger.debug('Finished clearing currently held pubkeys.')

        # Add a new column to the inbox table to store the hash of the message signature.
        # We'll use this as temporary message UUID in order to detect duplicates. 
        item = '''SELECT value FROM settings WHERE key='version';'''
        parameters = ''
        self.cur.execute(item, parameters)
        currentVersion = int(self.cur.fetchall()[0][0])
        if currentVersion == 8:
            logger.debug('In messages.dat database, adding sighash field to the inbox table.')
            item = '''ALTER TABLE inbox ADD sighash blob DEFAULT '' '''
            parameters = ''
            self.cur.execute(item, parameters)
            item = '''update settings set value=? WHERE key='version';'''
            parameters = (9,)
            self.cur.execute(item, parameters)
            
        # TTL is now user-specifiable. Let's add an option to save whatever the user selects. 
        if not shared.config.has_option('bitmessagesettings', 'ttl'):
            shared.config.set('bitmessagesettings', 'ttl', '367200')
        # We'll also need a `sleeptill` field and a `ttl` field. Also we can combine 
        # the pubkeyretrynumber and msgretrynumber into one.
        item = '''SELECT value FROM settings WHERE key='version';'''
        parameters = ''
        self.cur.execute(item, parameters)
        currentVersion = int(self.cur.fetchall()[0][0])
        if currentVersion == 9:
            logger.info('In messages.dat database, making TTL-related changes: combining the pubkeyretrynumber and msgretrynumber fields into the retrynumber field and adding the sleeptill and ttl fields...')
            self.cur.execute(
                '''CREATE TEMPORARY TABLE sent_backup (msgid blob, toaddress text, toripe blob, fromaddress text, subject text, message text, ackdata blob, lastactiontime integer, status text, retrynumber integer, folder text, encodingtype int)''' )
            self.cur.execute(
                '''INSERT INTO sent_backup SELECT msgid, toaddress, toripe, fromaddress, subject, message, ackdata, lastactiontime, status, 0, folder, encodingtype FROM sent;''')
            self.cur.execute( '''DROP TABLE sent''')
            self.cur.execute(
                '''CREATE TABLE sent (msgid blob, toaddress text, toripe blob, fromaddress text, subject text, message text, ackdata blob, senttime integer, lastactiontime integer, sleeptill int, status text, retrynumber integer, folder text, encodingtype int, ttl int)''' )
            self.cur.execute(
                '''INSERT INTO sent SELECT msgid, toaddress, toripe, fromaddress, subject, message, ackdata, lastactiontime, lastactiontime, 0, status, 0, folder, encodingtype, 216000 FROM sent_backup;''')
            self.cur.execute( '''DROP TABLE sent_backup''')
            logger.info('In messages.dat database, finished making TTL-related changes.')
            logger.debug('In messages.dat database, adding address field to the pubkeys table.')
            # We're going to have to calculate the address for each row in the pubkeys
            # table. Then we can take out the hash field. 
            self.cur.execute('''ALTER TABLE pubkeys ADD address text DEFAULT '' ''')
            self.cur.execute('''SELECT hash, addressversion FROM pubkeys''')
            queryResult = self.cur.fetchall()
            from addresses import encodeAddress
            for row in queryResult:
                hash, addressVersion = row
                address = encodeAddress(addressVersion, 1, hash)
                item = '''UPDATE pubkeys SET address=? WHERE hash=?;'''
                parameters = (address, hash)
                self.cur.execute(item, parameters)
            # Now we can remove the hash field from the pubkeys table.
            self.cur.execute(
                '''CREATE TEMPORARY TABLE pubkeys_backup (address text, addressversion int, transmitdata blob, time int, usedpersonally text, UNIQUE(address) ON CONFLICT REPLACE)''' )
            self.cur.execute(
                '''INSERT INTO pubkeys_backup SELECT address, addressversion, transmitdata, time, usedpersonally FROM pubkeys;''')
            self.cur.execute( '''DROP TABLE pubkeys''')
            self.cur.execute(
                '''CREATE TABLE pubkeys (address text, addressversion int, transmitdata blob, time int, usedpersonally text, UNIQUE(address) ON CONFLICT REPLACE)''' )
            self.cur.execute(
                '''INSERT INTO pubkeys SELECT address, addressversion, transmitdata, time, usedpersonally FROM pubkeys_backup;''')
            self.cur.execute( '''DROP TABLE pubkeys_backup''')
            logger.debug('In messages.dat database, done adding address field to the pubkeys table and removing the hash field.')
            self.cur.execute('''update settings set value=10 WHERE key='version';''')
        
        if not shared.config.has_option('bitmessagesettings', 'onionhostname'):
            shared.config.set('bitmessagesettings', 'onionhostname', '')
        if not shared.config.has_option('bitmessagesettings', 'onionport'):
            shared.config.set('bitmessagesettings', 'onionport', '8444')
        if not shared.config.has_option('bitmessagesettings', 'onionbindip'):
            shared.config.set('bitmessagesettings', 'onionbindip', '127.0.0.1')
        if not shared.config.has_option('bitmessagesettings', 'smtpdeliver'):
            shared.config.set('bitmessagesettings', 'smtpdeliver', '')
        if not shared.config.has_option('bitmessagesettings', 'hidetrayconnectionnotifications'):
            shared.config.set('bitmessagesettings', 'hidetrayconnectionnotifications', 'false')
        shared.writeKeysFile()
        
        # Are you hoping to add a new option to the keys.dat file of existing
        # Bitmessage users or modify the SQLite database? Add it right above this line!
        
        try:
            testpayload = '\x00\x00'
            t = ('1234', 1, testpayload, '12345678', 'no')
            self.cur.execute( '''INSERT INTO pubkeys VALUES(?,?,?,?,?)''', t)
            self.conn.commit()
            self.cur.execute(
                '''SELECT transmitdata FROM pubkeys WHERE address='1234' ''')
            queryreturn = self.cur.fetchall()
            for row in queryreturn:
                transmitdata, = row
            self.cur.execute('''DELETE FROM pubkeys WHERE address='1234' ''')
            self.conn.commit()
            if transmitdata == '':
                logger.fatal('Problem: The version of SQLite you have cannot store Null values. Please download and install the latest revision of your version of Python (for example, the latest Python 2.7 revision) and try again.\n')
                logger.fatal('PyBitmessage will now exit very abruptly. You may now see threading errors related to this abrupt exit but the problem you need to solve is related to SQLite.\n\n')
                os._exit(0)
        except Exception as err:
            if str(err) == 'database or disk is full':
                logger.fatal('(While null value test) Alert: Your disk or data storage volume is full. sqlThread will now exit.')
                shared.UISignalQueue.put(('alert', (tr._translate("MainWindow", "Disk full"), tr._translate("MainWindow", 'Alert: Your disk or data storage volume is full. Bitmessage will now exit.'), True)))
                os._exit(0)
            else:
                logger.error(err)

        # Let us check to see the last time we vaccumed the messages.dat file.
        # If it has been more than a month let's do it now.
        item = '''SELECT value FROM settings WHERE key='lastvacuumtime';'''
        parameters = ''
        self.cur.execute(item, parameters)
        queryreturn = self.cur.fetchall()
        for row in queryreturn:
            value, = row
            if int(value) < int(time.time()) - 86400:
                logger.info('It has been a long time since the messages.dat file has been vacuumed. Vacuuming now...')
                try:
                    self.cur.execute( ''' VACUUM ''')
                except Exception as err:
                    if str(err) == 'database or disk is full':
                        logger.fatal('(While VACUUM) Alert: Your disk or data storage volume is full. sqlThread will now exit.')
                        shared.UISignalQueue.put(('alert', (tr._translate("MainWindow", "Disk full"), tr._translate("MainWindow", 'Alert: Your disk or data storage volume is full. Bitmessage will now exit.'), True)))
                        os._exit(0)
                item = '''update settings set value=? WHERE key='lastvacuumtime';'''
                parameters = (int(time.time()),)
                self.cur.execute(item, parameters)

        while True:
            item = shared.sqlSubmitQueue.get()
            if item == 'commit':
                try:
                    self.conn.commit()
                except Exception as err:
                    if str(err) == 'database or disk is full':
                        logger.fatal('(While committing) Alert: Your disk or data storage volume is full. sqlThread will now exit.')
                        shared.UISignalQueue.put(('alert', (tr._translate("MainWindow", "Disk full"), tr._translate("MainWindow", 'Alert: Your disk or data storage volume is full. Bitmessage will now exit.'), True)))
                        os._exit(0)
            elif item == 'exit':
                self.conn.close()
                logger.info('sqlThread exiting gracefully.')

                return
            elif item == 'movemessagstoprog':
                logger.debug('the sqlThread is moving the messages.dat file to the local program directory.')

                try:
                    self.conn.commit()
                except Exception as err:
                    if str(err) == 'database or disk is full':
                        logger.fatal('(while movemessagstoprog) Alert: Your disk or data storage volume is full. sqlThread will now exit.')
                        shared.UISignalQueue.put(('alert', (tr._translate("MainWindow", "Disk full"), tr._translate("MainWindow", 'Alert: Your disk or data storage volume is full. Bitmessage will now exit.'), True)))
                        os._exit(0)
                self.conn.close()
                shutil.move(
                    shared.lookupAppdataFolder() + 'messages.dat', shared.lookupExeFolder() + 'messages.dat')
                self.conn = sqlite3.connect(shared.lookupExeFolder() + 'messages.dat')
                self.conn.text_factory = str
                self.cur = self.conn.cursor()
            elif item == 'movemessagstoappdata':
                logger.debug('the sqlThread is moving the messages.dat file to the Appdata folder.')

                try:
                    self.conn.commit()
                except Exception as err:
                    if str(err) == 'database or disk is full':
                        logger.fatal('(while movemessagstoappdata) Alert: Your disk or data storage volume is full. sqlThread will now exit.')
                        shared.UISignalQueue.put(('alert', (tr._translate("MainWindow", "Disk full"), tr._translate("MainWindow", 'Alert: Your disk or data storage volume is full. Bitmessage will now exit.'), True)))
                        os._exit(0)
                self.conn.close()
                shutil.move(
                    shared.lookupExeFolder() + 'messages.dat', shared.lookupAppdataFolder() + 'messages.dat')
                self.conn = sqlite3.connect(shared.lookupAppdataFolder() + 'messages.dat')
                self.conn.text_factory = str
                self.cur = self.conn.cursor()
            elif item == 'deleteandvacuume':
                self.cur.execute('''delete from inbox where folder='trash' ''')
                self.cur.execute('''delete from sent where folder='trash' ''')
                self.conn.commit()
                try:
                    self.cur.execute( ''' VACUUM ''')
                except Exception as err:
                    if str(err) == 'database or disk is full':
                        logger.fatal('(while deleteandvacuume) Alert: Your disk or data storage volume is full. sqlThread will now exit.')
                        shared.UISignalQueue.put(('alert', (tr._translate("MainWindow", "Disk full"), tr._translate("MainWindow", 'Alert: Your disk or data storage volume is full. Bitmessage will now exit.'), True)))
                        os._exit(0)
            else:
                parameters = shared.sqlSubmitQueue.get()
                rowcount = 0
                # print 'item', item
                # print 'parameters', parameters
                try:
                    self.cur.execute(item, parameters)
                    rowcount = self.cur.rowcount
                except Exception as err:
                    if str(err) == 'database or disk is full':
                        logger.fatal('(while cur.execute) Alert: Your disk or data storage volume is full. sqlThread will now exit.')
                        shared.UISignalQueue.put(('alert', (tr._translate("MainWindow", "Disk full"), tr._translate("MainWindow", 'Alert: Your disk or data storage volume is full. Bitmessage will now exit.'), True)))
                        os._exit(0)
                    else:
                        logger.fatal('Major error occurred when trying to execute a SQL statement within the sqlThread. Please tell Atheros about this error message or post it in the forum! Error occurred while trying to execute statement: "%s"  Here are the parameters; you might want to censor this data with asterisks (***) as it can contain private information: %s. Here is the actual error message thrown by the sqlThread: %s', str(item), str(repr(parameters)),  str(err))
                        logger.fatal('This program shall now abruptly exit!')

                    os._exit(0)

                shared.sqlReturnQueue.put((self.cur.fetchall(), rowcount))
                # shared.sqlSubmitQueue.task_done()
