"""
sqlThread is defined here
"""

import os
import shutil  # used for moving the messages.dat file
import sqlite3
import sys
import threading
import time

try:
    import helper_sql
    import helper_startup
    import paths
    import queues
    import state
    import tr
    from bmconfigparser import BMConfigParser
    from debug import logger
    from addresses import encodeAddress
except ImportError:
    from . import helper_sql
    from . import helper_startup
    from . import paths
    from . import queues
    from . import state
    from . import tr
    from .bmconfigparser import BMConfigParser
    from .debug import logger
    from .addresses import encodeAddress

# pylint: disable=attribute-defined-outside-init,protected-access
root_path = os.path.dirname(os.path.dirname(__file__))


def connection_build():
    """
        Stablish SQL connection
    """
    conn = sqlite3.connect(state.appdata + 'messages.dat')
    conn.text_factory = str
    cur = conn.cursor()
    return conn, cur


class UpgradeDB(object):
    """
        Upgrade Db with respect to versions
    """

    conn, cur = connection_build()

    def __init__(self):
        self._current_level = None
        self.max_level = 11

    def __get_current_settings_version(self):
        """
            Upgrade Db with respect to their versions
        """
        item = '''SELECT value FROM settings WHERE key='version';'''
        parameters = ()
        self.cur.execute(item, parameters)
        return int(self.cur.fetchall()[0][0])

    def _upgrade_one_level_sql_statement(self, file_name):
        """
            Execute SQL files and queries
        """
        try:
            print("=======================")
            print(file_name)
            if int(file_name) == 8:
                res = self.cur.execute('''PRAGMA table_info('inbox');''')
                print("""""""""""""""-----------res""""""""""""""")
                print(res)
            print("=======================")
            with open(os.path.join(root_path, "src/sql/init_version_{}.sql".format(file_name))) as sql_file:
                sql_as_string = sql_file.read()
            self.cur.executescript(sql_as_string)
        except Exception as err:
            if str(err) == 'table inbox already exists':
                return "ERROR trying to upgrade database. Error message: table inbox already exists"
            else:
                sys.stderr.write(
                    'ERROR trying to upgrade database. Error message: %s\n' % str(err))
                os._exit(0)

    @property
    def sql_schema_version(self):
        self._current_level = self.__get_current_settings_version()

    @sql_schema_version.setter
    def sql_schema_version(self, cur, conn, current_level):
        """
            Update version with one level
        """
        item = '''update settings set value=? WHERE key='version';'''
        parameters = (current_level + 1,)
        self.cur.execute(item, parameters)
        self._current_level = self.__get_current_settings_version()

    # @sql_schema_version.setter
    def upgrade_to_latest(self, cur, conn, current_level=None):
        """
            Initialise upgrade level
        """

        # Declare variables
        self.conn = conn
        self.cur = cur
        if current_level:
            self._current_level = current_level
        else:
            self._current_level = self.__get_current_settings_version()
        self.max_level = 11

        # call upgrading level in loop
        for l in range(self._current_level, self.max_level):
            if int(l) == 1:
                continue
            self._upgrade_one_level_sql_statement(l)
            # self.increment_settings_version(l)
            self._current_level = l

    def increment_settings_version(self, level):
        """
            Update version with one level
        """
        item = '''update settings set value=? WHERE key='version';'''
        parameters = (level + 1,)
        self.cur.execute(item, parameters)


class sqlThread(threading.Thread, UpgradeDB):
    """A thread for all SQL operations"""

    def __init__(self):
        super(sqlThread, self).__init__()
        threading.Thread.__init__(self, name="SQL")

    def run(self):  # pylint: disable=too-many-locals, too-many-branches, too-many-statements,
        # Redefinition-of-parameters-type-from-tuple-to-str, R0204, line-too-long, E501
        """Process SQL queries from `.helper_sql.sqlSubmitQueue`"""
        helper_sql.sql_available = True
        self.conn, self.cur = connection_build()

        self.cur.execute('PRAGMA secure_delete = true')

        # call create_function for encode address
        self.create_function()

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
                    'ERROR trying to create database file (message.dat). in1111 Error message: %s\n' % str(err))
                os._exit(0)

        # If the settings version is equal to 2 or 3 then the
        # sqlThread will modify the pubkeys table and change
        # the settings version to 4.
        settingsversion = BMConfigParser().getint(
            'bitmessagesettings', 'settingsversion')

        settingsversion = self.earlier_setting_version(settingsversion)

        BMConfigParser().set(
            'bitmessagesettings', 'settingsversion', str(settingsversion))
        BMConfigParser().save()

        helper_startup.updateConfig()

        # From now on, let us keep a 'version' embedded in the messages.dat
        # file so that when we make changes to the database, the database
        # version we are on can stay embedded in the messages.dat file. Let us
        # check to see if the settings table exists yet.

        self.embaded_version()

        # apply version migration

        self.upgrade_to_latest(self.cur, self.conn)

        # Are you hoping to add a new option to the keys.dat file of existing
        # Bitmessage users or modify the SQLite database? Add it right
        # above this line!

        self.add_new_option()

        # Let us check to see the last time we vaccumed the messages.dat file.
        # If it has been more than a month let's do it now.

        self.check_vaccumed()

    def embaded_version(self):
        """
            From now on, let us keep a 'version' embedded in the messages.dat
            file so that when we make changes to the database, the database
            version we are on can stay embedded in the messages.dat file. Let us
            check to see if the settings table exists yet.
        """

        item = '''SELECT name FROM sqlite_master WHERE type='table' AND name='settings';'''
        parameters = ()
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

    def add_new_option(self):  # pylint: disable=too-many-locals, too-many-branches, too-many-statements
        """
            Add new option
            RUN SQL query
        """
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

    def check_vaccumed(self):  # pylint: disable=too-many-locals, too-many-branches, too-many-statements,
        # Redefinition-of-parameters-type-from-tuple-to-str, R0204, line-too-long, E501
        """
            Check vaccume and apply sql queries for different different conditions
        """

        item = '''SELECT value FROM settings WHERE key='lastvacuumtime';'''
        parameters = ()
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

    def earlier_setting_version(self, settingsversion):
        """
            Upgrade schema with respect setting version
        """

        # People running earlier versions of PyBitmessage do not have the
        # usedpersonally field in their pubkeys table. Let's add it.
        if settingsversion == 2:
            item = '''ALTER TABLE pubkeys ADD usedpersonally text DEFAULT 'no' '''
            parameters = ()
            self.cur.execute(item, parameters)
            self.conn.commit()

            settingsversion = 3

        # People running earlier versions of PyBitmessage do not have the
        # encodingtype field in their inbox and sent tables or the read field
        # in the inbox table. Let's add them.
        if settingsversion == 3:
            item = '''ALTER TABLE inbox ADD encodingtype int DEFAULT '2' '''
            parameters = ()
            self.cur.execute(item, parameters)

            item = '''ALTER TABLE inbox ADD read bool DEFAULT '1' '''
            parameters = ()
            self.cur.execute(item, parameters)

            item = '''ALTER TABLE sent ADD encodingtype int DEFAULT '2' '''
            parameters = ()
            self.cur.execute(item, parameters)
            self.conn.commit()

            return 4
        return settingsversion

    def create_function(self):
        """
            Apply create_function to DB
        """
        try:
            self.conn.create_function("enaddr", 3, func=encodeAddress, deterministic=True)
        except (TypeError, sqlite3.NotSupportedError) as err:
            logger.debug(
                "Got error while pass deterministic in sqlite create function {}, Passing 3 params".format(err))
            self.conn.create_function("enaddr", 3, encodeAddress)
