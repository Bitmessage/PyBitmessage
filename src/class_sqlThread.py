"""
sqlThread is defined here
"""

import os
import shutil  # used for moving the messages.dat file
import sqlite3
import sys
import threading
import time

import helper_sql
import helper_startup
import paths
import queues
import state
import tr
from bmconfigparser import BMConfigParser
from debug import logger
pylint: disable=attribute-defined-outside-init,protected-access


class UpgradeDB():
    """Upgrade Db with respect to versions"""
    cur = None
    parameters = None
    current_level = None
    max_level = 11

    def get_current_level(self):
        # Upgrade Db with respect to their versions
        item = '''SELECT value FROM settings WHERE key='version';'''
        parameters = ''
        self.cur.execute(item, parameters)
        return int(self.cur.fetchall()[0][0])

    def upgrade_one_level(self, level):
        """ Apply switcher to call methods accordingly """

        if level != self.get_current_level():
            return None

        # Migrate Db with level
        method_name = 'upgrade_schema_data_' + str(level)
        method = getattr(self, method_name, lambda: "Invalid version")
        return method()

    def upgrade_to_latest(self, cur):
        """
            Initialise upgrade level
        """

        # Declare variables
        self.cur = cur
        self.current_level = self.get_current_level()
        self.max_level = 11

        # call upgrading level in loop
        for l in range(self.current_level, self.max_level):
            self.upgrade_one_level(l)
            self.upgrade_schema_data_level(l)

    def upgrade_schema_data_level(self, level):
        item = '''update settings set value=? WHERE key='version';'''
        parameters = (level + 1,)
        self.cur.execute(item, parameters)

    def upgrade_schema_data_1(self):
        """inventory
            For version 1 and 3
            Add a new column to the inventory table to store tags.
        """

        logger.debug(
            'In messages.dat database, adding tag field to'
            ' the inventory table.')
        item = '''ALTER TABLE inventory ADD tag blob DEFAULT '' '''
        parameters = ''
        self.cur.execute(item, parameters)

    def upgrade_schema_data_2(self):
        """
            For version 2
            Let's get rid of the first20bytesofencryptedmessage field in the inventory table.
        """

        logger.debug(
            'In messages.dat database, removing an obsolete field from'
            ' the inventory table.')
        self.cur.execute(
            '''CREATE TEMPORARY TABLE inventory_backup'''
            '''(hash blob, objecttype text, streamnumber int, payload blob,'''
            ''' receivedtime integer, UNIQUE(hash) ON CONFLICT REPLACE);''')
        self.cur.execute(
            '''INSERT INTO inventory_backup SELECT hash, objecttype, streamnumber, payload, receivedtime'''
            ''' FROM inventory;''')
        self.cur.execute('''DROP TABLE inventory''')
        self.cur.execute(
            '''CREATE TABLE inventory'''
            ''' (hash blob, objecttype text, streamnumber int, payload blob, receivedtime integer,'''
            ''' UNIQUE(hash) ON CONFLICT REPLACE)''')
        self.cur.execute(
            '''INSERT INTO inventory SELECT hash, objecttype, streamnumber, payload, receivedtime'''
            ''' FROM inventory_backup;''')
        self.cur.execute('''DROP TABLE inventory_backup;''')

    def upgrade_schema_data_3(self):
        """
            For version 3
            Call method for version 1
        """

        self.upgrade_schema_data_1()

    def upgrade_schema_data_4(self):
        """
            For version 4
            Add a new column to the pubkeys table to store the address version.
            We're going to trash all of our pubkeys and let them be redownloaded.
        """

        self.cur.execute('''DROP TABLE pubkeys''')
        self.cur.execute(
            '''CREATE TABLE pubkeys (hash blob, addressversion int, transmitdata blob, time int,'''
            '''usedpersonally text, UNIQUE(hash, addressversion) ON CONFLICT REPLACE)''')
        self.cur.execute(
            '''delete from inventory where objecttype = 'pubkey';''')

    def upgrade_schema_data_5(self):
        """
            For version 5
            Add a new table: objectprocessorqueue with which to hold objects
            That have yet to be processed if the user shuts down Bitmessage.
        """

        self.cur.execute('''DROP TABLE knownnodes''')
        self.cur.execute(
            '''CREATE TABLE objectprocessorqueue'''
            ''' (objecttype text, data blob, UNIQUE(objecttype, data) ON CONFLICT REPLACE)''')

    def upgrade_schema_data_6(self):
        """
            For version 6
            Changes related to protocol v3
            In table inventory and objectprocessorqueue, objecttype is now
            an integer (it was a human-friendly string previously)
        """

        logger.debug(
            'In messages.dat database, dropping and recreating'
            ' the inventory table.')
        self.cur.execute('''DROP TABLE inventory''')
        self.cur.execute(
            '''CREATE TABLE inventory'''
            ''' (hash blob, objecttype int, streamnumber int, payload blob, expirestime integer,'''
            ''' tag blob, UNIQUE(hash) ON CONFLICT REPLACE)''')
        self.cur.execute('''DROP TABLE objectprocessorqueue''')
        self.cur.execute(
            '''CREATE TABLE objectprocessorqueue'''
            ''' (objecttype int, data blob, UNIQUE(objecttype, data) ON CONFLICT REPLACE)''')
        logger.debug(
            'Finished dropping and recreating the inventory table.')

    def upgrade_schema_data_7(self):
        """
            For version 7
            The format of data stored in the pubkeys table has changed. Let's
            clear it, and the pubkeys from inventory, so that they'll
            be re-downloaded.
        """

        logger.debug(
            'In messages.dat database, clearing pubkeys table'
            ' because the data format has been updated.')
        self.cur.execute(
            '''delete from inventory where objecttype = 1;''')
        self.cur.execute(
            '''delete from pubkeys;''')
        # Any sending messages for which we *thought* that we had
        # the pubkey must be rechecked.
        self.cur.execute(
            '''UPDATE sent SET status='msgqueued' WHERE status='doingmsgpow' or status='badkey';''')
        logger.debug('Finished clearing currently held pubkeys.')

    def upgrade_schema_data_8(self):
        """
            For version 8
            Add a new column to the inbox table to store the hash of
            the message signature. We'll use this as temporary message UUID
            in order to detect duplicates.
        """

        logger.debug(
            'In messages.dat database, adding sighash field to'
            ' the inbox table.')
        item = '''ALTER TABLE inbox ADD sighash blob DEFAULT '' '''
        parameters = ''
        self.cur.execute(item, parameters)

    def upgrade_schema_data_9(self):
        """
            For version 9
            We'll also need a `sleeptill` field and a `ttl` field. Also we
            can combine the pubkeyretrynumber and msgretrynumber into one.
        """

        logger.info(
            'In messages.dat database, making TTL-related changes:'
            ' combining the pubkeyretrynumber and msgretrynumber'
            ' fields into the retrynumber field and adding the'
            ' sleeptill and ttl fields...')
        self.cur.execute(
            '''CREATE TEMPORARY TABLE sent_backup'''
            ''' (msgid blob, toaddress text, toripe blob, fromaddress text, subject text, message text,'''
            ''' ackdata blob, lastactiontime integer, status text, retrynumber integer,'''
            ''' folder text, encodingtype int)''')
        self.cur.execute(
            '''INSERT INTO sent_backup SELECT msgid, toaddress, toripe, fromaddress,'''
            ''' subject, message, ackdata, lastactiontime,'''
            ''' status, 0, folder, encodingtype FROM sent;''')
        self.cur.execute('''DROP TABLE sent''')
        self.cur.execute(
            '''CREATE TABLE sent'''
            ''' (msgid blob, toaddress text, toripe blob, fromaddress text, subject text, message text,'''
            ''' ackdata blob, senttime integer, lastactiontime integer, sleeptill int, status text,'''
            ''' retrynumber integer, folder text, encodingtype int, ttl int)''')
        self.cur.execute(
            '''INSERT INTO sent SELECT msgid, toaddress, toripe, fromaddress, subject, message, ackdata,'''
            ''' lastactiontime, lastactiontime, 0, status, 0, folder, encodingtype, 216000 FROM sent_backup;''')
        self.cur.execute('''DROP TABLE sent_backup''')
        logger.info('In messages.dat database, finished making TTL-related changes.')
        logger.debug('In messages.dat database, adding address field to the pubkeys table.')
        # We're going to have to calculate the address for each row in the pubkeys
        # table. Then we can take out the hash field.
        self.cur.execute('''ALTER TABLE pubkeys ADD address text DEFAULT '' ''')
        self.cur.execute('''SELECT hash, addressversion FROM pubkeys''')
        queryResult = self.cur.fetchall()
        from addresses import encodeAddress
        for row in queryResult:
            addressHash, addressVersion = row
            address = encodeAddress(addressVersion, 1, hash)
            item = '''UPDATE pubkeys SET address=? WHERE hash=?;'''
            parameters = (address, addressHash)
            self.cur.execute(item, parameters)
        # Now we can remove the hash field from the pubkeys table.
        self.cur.execute(
            '''CREATE TEMPORARY TABLE pubkeys_backup'''
            ''' (address text, addressversion int, transmitdata blob, time int,'''
            ''' usedpersonally text, UNIQUE(address) ON CONFLICT REPLACE)''')
        self.cur.execute(
            '''INSERT INTO pubkeys_backup'''
            ''' SELECT address, addressversion, transmitdata, time, usedpersonally FROM pubkeys;''')
        self.cur.execute('''DROP TABLE pubkeys''')
        self.cur.execute(
            '''CREATE TABLE pubkeys'''
            ''' (address text, addressversion int, transmitdata blob, time int, usedpersonally text,'''
            ''' UNIQUE(address) ON CONFLICT REPLACE)''')
        self.cur.execute(
            '''INSERT INTO pubkeys SELECT'''
            ''' address, addressversion, transmitdata, time, usedpersonally FROM pubkeys_backup;''')
        self.cur.execute('''DROP TABLE pubkeys_backup''')
        logger.debug(
            'In messages.dat database, done adding address field to the pubkeys table'
            ' and removing the hash field.')

    def upgrade_schema_data_10(self):
        """
            For version 10
            Update the address colunm to unique in addressbook table
        """

        logger.debug(
            'In messages.dat database, updating address column to UNIQUE'
            ' in the addressbook table.')
        self.cur.execute(
            '''ALTER TABLE addressbook RENAME TO old_addressbook''')
        self.cur.execute(
            '''CREATE TABLE addressbook'''
            ''' (label text, address text, UNIQUE(address) ON CONFLICT IGNORE)''')
        self.cur.execute(
            '''INSERT INTO addressbook SELECT label, address FROM old_addressbook;''')
        self.cur.execute('''DROP TABLE old_addressbook''')

class sqlThread(threading.Thread, UpgradeDB):
    """A thread for all SQL operations"""

    def __init__(self):
        threading.Thread.__init__(self, name="SQL")

    def run(self):  # pylint: disable=too-many-locals, too-many-branches, too-many-statements
        """Process SQL queries from `.helper_sql.sqlSubmitQueue`"""
        helper_sql.sql_available = True
        self.conn = sqlite3.connect(state.appdata + 'messages.dat')
        self.conn.text_factory = str
        self.cur = self.conn.cursor()

        self.cur.execute('PRAGMA secure_delete = true')

        try:
            self.cur.execute(
                '''CREATE TABLE inbox (msgid blob, toaddress text, fromaddress text, subject text,'''
                ''' received text, message text, folder text, encodingtype int, read bool, sighash blob,'''
                ''' UNIQUE(msgid) ON CONFLICT REPLACE)''')
            self.cur.execute(
                '''CREATE TABLE sent (msgid blob, toaddress text, toripe blob, fromaddress text, subject text,'''
                ''' message text, ackdata blob, senttime integer, lastactiontime integer,'''
                ''' sleeptill integer, status text, retrynumber integer, folder text, encodingtype int, ttl int)''')
            self.cur.execute(
                '''CREATE TABLE subscriptions (label text, address text, enabled bool)''')
            self.cur.execute(
                '''CREATE TABLE addressbook (label text, address text, UNIQUE(address) ON CONFLICT IGNORE)''')
            self.cur.execute(
                '''CREATE TABLE blacklist (label text, address text, enabled bool)''')
            self.cur.execute(
                '''CREATE TABLE whitelist (label text, address text, enabled bool)''')
            self.cur.execute(
                '''CREATE TABLE pubkeys (address text, addressversion int, transmitdata blob, time int,'''
                ''' usedpersonally text, UNIQUE(address) ON CONFLICT REPLACE)''')
            self.cur.execute(
                '''CREATE TABLE inventory (hash blob, objecttype int, streamnumber int, payload blob,'''
                ''' expirestime integer, tag blob, UNIQUE(hash) ON CONFLICT REPLACE)''')
            self.cur.execute(
                '''INSERT INTO subscriptions VALUES'''
                '''('Bitmessage new releases/announcements','BM-GtovgYdgs7qXPkoYaRgrLFuFKz1SFpsw',1)''')
            self.cur.execute(
                '''CREATE TABLE settings (key blob, value blob, UNIQUE(key) ON CONFLICT REPLACE)''')
            self.cur.execute('''INSERT INTO settings VALUES('version','11')''')
            self.cur.execute('''INSERT INTO settings VALUES('lastvacuumtime',?)''', (
                int(time.time()),))
            self.cur.execute(
                '''CREATE TABLE objectprocessorqueue'''
                ''' (objecttype int, data blob, UNIQUE(objecttype, data) ON CONFLICT REPLACE)''')
            self.conn.commit()
            logger.info('Created messages database file')
        except Exception as err:
            if str(err) == 'table inbox already exists':
                logger.debug('Database file already exists.')

            else:
                sys.stderr.write(
                    'ERROR trying to create database file (message.dat). Error message: %s\n' % str(err))
                os._exit(0)

        # If the settings version is equal to 2 or 3 then the
        # sqlThread will modify the pubkeys table and change
        # the settings version to 4.
        settingsversion = BMConfigParser().getint(
            'bitmessagesettings', 'settingsversion')

        # People running earlier versions of PyBitmessage do not have the
        # usedpersonally field in their pubkeys table. Let's add it.
        if settingsversion == 2:
            item = '''ALTER TABLE pubkeys ADD usedpersonally text DEFAULT 'no' '''
            parameters = ''
            self.cur.execute(item, parameters)
            self.conn.commit()

            settingsversion = 3

        # People running earlier versions of PyBitmessage do not have the
        # encodingtype field in their inbox and sent tables or the read field
        # in the inbox table. Let's add them.
        if settingsversion == 3:
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

            settingsversion = 4

        BMConfigParser().set(
            'bitmessagesettings', 'settingsversion', str(settingsversion))
        BMConfigParser().save()

        helper_startup.updateConfig()

        # From now on, let us keep a 'version' embedded in the messages.dat
        # file so that when we make changes to the database, the database
        # version we are on can stay embedded in the messages.dat file. Let us
        # check to see if the settings table exists yet.
        item = '''SELECT name FROM sqlite_master WHERE type='table' AND name='settings';'''
        parameters = ''
        self.cur.execute(item, parameters)
        if self.cur.fetchall() == []:
            # The settings table doesn't exist. We need to make it.
            logger.debug(
                "In messages.dat database, creating new 'settings' table.")
            self.cur.execute(
                '''CREATE TABLE settings (key text, value blob, UNIQUE(key) ON CONFLICT REPLACE)''')
            self.cur.execute('''INSERT INTO settings VALUES('version','1')''')
            self.cur.execute('''INSERT INTO settings VALUES('lastvacuumtime',?)''', (
                int(time.time()),))
            logger.debug('In messages.dat database, removing an obsolete field from the pubkeys table.')
            self.cur.execute(
                '''CREATE TEMPORARY TABLE pubkeys_backup(hash blob, transmitdata blob, time int,'''
                ''' usedpersonally text, UNIQUE(hash) ON CONFLICT REPLACE);''')
            self.cur.execute(
                '''INSERT INTO pubkeys_backup SELECT hash, transmitdata, time, usedpersonally FROM pubkeys;''')
            self.cur.execute('''DROP TABLE pubkeys''')
            self.cur.execute(
                '''CREATE TABLE pubkeys'''
                ''' (hash blob, transmitdata blob, time int, usedpersonally text, UNIQUE(hash) ON CONFLICT REPLACE)''')
            self.cur.execute(
                '''INSERT INTO pubkeys SELECT hash, transmitdata, time, usedpersonally FROM pubkeys_backup;''')
            self.cur.execute('''DROP TABLE pubkeys_backup;''')
            logger.debug(
                'Deleting all pubkeys from inventory.'
                ' They will be redownloaded and then saved with the correct times.')
            self.cur.execute(
                '''delete from inventory where objecttype = 'pubkey';''')
            logger.debug('replacing Bitmessage announcements mailing list with a new one.')
            self.cur.execute(
                '''delete from subscriptions where address='BM-BbkPSZbzPwpVcYZpU4yHwf9ZPEapN5Zx' ''')
            self.cur.execute(
                '''INSERT INTO subscriptions VALUES'''
                '''('Bitmessage new releases/announcements','BM-GtovgYdgs7qXPkoYaRgrLFuFKz1SFpsw',1)''')
            logger.debug('Commiting.')
            self.conn.commit()
            logger.debug('Vacuuming message.dat. You might notice that the file size gets much smaller.')
            self.cur.execute(''' VACUUM ''')

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

        self.upgrade_to_latest(self.cur)

        # Are you hoping to add a new option to the keys.dat file of existing
        # Bitmessage users or modify the SQLite database? Add it right
        # above this line!

        try:
            testpayload = '\x00\x00'
            t = ('1234', 1, testpayload, '12345678', 'no')
            self.cur.execute('''INSERT INTO pubkeys VALUES(?,?,?,?,?)''', t)
            self.conn.commit()
            self.cur.execute(
                '''SELECT transmitdata FROM pubkeys WHERE address='1234' ''')
            queryreturn = self.cur.fetchall()
            for row in queryreturn:
                transmitdata, = row
            self.cur.execute('''DELETE FROM pubkeys WHERE address='1234' ''')
            self.conn.commit()
            if transmitdata == '':
                logger.fatal(
                    'Problem: The version of SQLite you have cannot store Null values.'
                    ' Please download and install the latest revision of your version of Python'
                    ' (for example, the latest Python 2.7 revision) and try again.\n')
                logger.fatal(
                    'PyBitmessage will now exit very abruptly.'
                    ' You may now see threading errors related to this abrupt exit'
                    ' but the problem you need to solve is related to SQLite.\n\n')
                os._exit(0)
        except Exception as err:
            if str(err) == 'database or disk is full':
                logger.fatal(
                    '(While null value test) Alert: Your disk or data storage volume is full.'
                    ' sqlThread will now exit.')
                queues.UISignalQueue.put((
                    'alert', (
                        tr._translate(
                            "MainWindow",
                            "Disk full"),
                        tr._translate(
                            "MainWindow",
                            'Alert: Your disk or data storage volume is full. Bitmessage will now exit.'),
                        True)))
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
                    self.cur.execute(''' VACUUM ''')
                except Exception as err:
                    if str(err) == 'database or disk is full':
                        logger.fatal(
                            '(While VACUUM) Alert: Your disk or data storage volume is full.'
                            ' sqlThread will now exit.')
                        queues.UISignalQueue.put((
                            'alert', (
                                tr._translate(
                                    "MainWindow",
                                    "Disk full"),
                                tr._translate(
                                    "MainWindow",
                                    'Alert: Your disk or data storage volume is full. Bitmessage will now exit.'),
                                True)))
                        os._exit(0)
                item = '''update settings set value=? WHERE key='lastvacuumtime';'''
                parameters = (int(time.time()),)
                self.cur.execute(item, parameters)

        helper_sql.sql_ready.set()

        while True:
            item = helper_sql.sqlSubmitQueue.get()
            if item == 'commit':
                try:
                    self.conn.commit()
                except Exception as err:
                    if str(err) == 'database or disk is full':
                        logger.fatal(
                            '(While committing) Alert: Your disk or data storage volume is full.'
                            ' sqlThread will now exit.')
                        queues.UISignalQueue.put((
                            'alert', (
                                tr._translate(
                                    "MainWindow",
                                    "Disk full"),
                                tr._translate(
                                    "MainWindow",
                                    'Alert: Your disk or data storage volume is full. Bitmessage will now exit.'),
                                True)))
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
                        logger.fatal(
                            '(while movemessagstoprog) Alert: Your disk or data storage volume is full.'
                            ' sqlThread will now exit.')
                        queues.UISignalQueue.put((
                            'alert', (
                                tr._translate(
                                    "MainWindow",
                                    "Disk full"),
                                tr._translate(
                                    "MainWindow",
                                    'Alert: Your disk or data storage volume is full. Bitmessage will now exit.'),
                                True)))
                        os._exit(0)
                self.conn.close()
                shutil.move(
                    paths.lookupAppdataFolder() + 'messages.dat', paths.lookupExeFolder() + 'messages.dat')
                self.conn = sqlite3.connect(paths.lookupExeFolder() + 'messages.dat')
                self.conn.text_factory = str
                self.cur = self.conn.cursor()
            elif item == 'movemessagstoappdata':
                logger.debug('the sqlThread is moving the messages.dat file to the Appdata folder.')

                try:
                    self.conn.commit()
                except Exception as err:
                    if str(err) == 'database or disk is full':
                        logger.fatal(
                            '(while movemessagstoappdata) Alert: Your disk or data storage volume is full.'
                            ' sqlThread will now exit.')
                        queues.UISignalQueue.put((
                            'alert', (
                                tr._translate(
                                    "MainWindow",
                                    "Disk full"),
                                tr._translate(
                                    "MainWindow",
                                    'Alert: Your disk or data storage volume is full. Bitmessage will now exit.'),
                                True)))
                        os._exit(0)
                self.conn.close()
                shutil.move(
                    paths.lookupExeFolder() + 'messages.dat', paths.lookupAppdataFolder() + 'messages.dat')
                self.conn = sqlite3.connect(paths.lookupAppdataFolder() + 'messages.dat')
                self.conn.text_factory = str
                self.cur = self.conn.cursor()
            elif item == 'deleteandvacuume':
                self.cur.execute('''delete from inbox where folder='trash' ''')
                self.cur.execute('''delete from sent where folder='trash' ''')
                self.conn.commit()
                try:
                    self.cur.execute(''' VACUUM ''')
                except Exception as err:
                    if str(err) == 'database or disk is full':
                        logger.fatal(
                            '(while deleteandvacuume) Alert: Your disk or data storage volume is full.'
                            ' sqlThread will now exit.')
                        queues.UISignalQueue.put((
                            'alert', (
                                tr._translate(
                                    "MainWindow",
                                    "Disk full"),
                                tr._translate(
                                    "MainWindow",
                                    'Alert: Your disk or data storage volume is full. Bitmessage will now exit.'),
                                True)))
                        os._exit(0)
            else:
                parameters = helper_sql.sqlSubmitQueue.get()
                rowcount = 0
                try:
                    self.cur.execute(item, parameters)
                    rowcount = self.cur.rowcount
                except Exception as err:
                    if str(err) == 'database or disk is full':
                        logger.fatal(
                            '(while cur.execute) Alert: Your disk or data storage volume is full.'
                            ' sqlThread will now exit.')
                        queues.UISignalQueue.put((
                            'alert', (
                                tr._translate(
                                    "MainWindow",
                                    "Disk full"),
                                tr._translate(
                                    "MainWindow",
                                    'Alert: Your disk or data storage volume is full. Bitmessage will now exit.'),
                                True)))
                        os._exit(0)
                    else:
                        logger.fatal(
                            'Major error occurred when trying to execute a SQL statement within the sqlThread.'
                            ' Please tell Atheros about this error message or post it in the forum!'
                            ' Error occurred while trying to execute statement: "%s"  Here are the parameters;'
                            ' you might want to censor this data with asterisks (***)'
                            ' as it can contain private information: %s.'
                            ' Here is the actual error message thrown by the sqlThread: %s',
                            str(item),
                            str(repr(parameters)),
                            str(err))
                        logger.fatal('This program shall now abruptly exit!')

                    os._exit(0)

                helper_sql.sqlReturnQueue.put((self.cur.fetchall(), rowcount))
                # helper_sql.sqlSubmitQueue.task_done()
