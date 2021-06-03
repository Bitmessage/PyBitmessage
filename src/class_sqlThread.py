"""
sqlThread is defined here
"""

import logging
import os
import shutil  # used for moving the messages.dat file
import sqlite3
import threading
import time

try:
    import helper_sql
    import helper_startup
    import paths
    import queues
    import state
    from addresses import encodeAddress
    from bmconfigparser import config, config_ready
    from tr import _translate
except ImportError:
    from . import helper_sql, helper_startup, paths, queues, state
    from .addresses import encodeAddress
    from .bmconfigparser import config, config_ready
    from .tr import _translate

logger = logging.getLogger('default')


class BitmessageDB(object):
    """ Upgrade Db with respect to versions """

    def __init__(self):
        self._current_level = None
        self.max_level = 11
        self.conn = None
        self.cur = None
        self._connection_build()
        self.root_path = os.path.dirname(os.path.dirname(__file__))

    def _connection_build(self):
        self._connection_build_internal('messages.dat', False)

    def _connection_build_internal(self, file_name="messages.dat", memory=False):
        """
            Stablish SQL connection
        """
        if memory:
            self.conn = sqlite3.connect(':memory:')
        else:
            self.conn = sqlite3.connect(os.path.join(state.appdata + file_name))
        self.conn.text_factory = str
        self.cur = self.conn.cursor()
        self.cur.execute('PRAGMA secure_delete = true')

    def __get_current_settings_version(self):
        """
            Get current setting Version
        """
        query = "SELECT value FROM settings WHERE key='version'"
        parameters = ()
        self.cur.execute(query, parameters)
        return int(self.cur.fetchall()[0][0])

    def _upgrade_one_level_sql_statement(self, file_name):
        """
            Upgrade database versions with applying sql scripts
        """
        self.initialise_sql("init_version_{}".format(file_name))

    def initialise_sql(self, file_name):
        try:
            with open(os.path.join(self.root_path, "pybitmessage/sql/{}.sql".format(file_name))) as sql_file:
                sql_as_string = sql_file.read()
            self.cur.executescript(sql_as_string)
        except IOError as err:
            logger.debug(
                'ERROR trying to initialize database. Error message: %s\n', str(err))
        except Exception as err:
            logger.debug(
                'ERROR trying to initialize database. Error message: %s\n', str(err))

    @property
    def sql_schema_version(self):
        """
            Getter for get current schema version
        """
        return self.__get_current_settings_version()

    @sql_schema_version.setter
    def sql_schema_version(self, setter):
        """
            Update version with one level
        """
        if setter:
            query = "UPDATE settings SET value=CAST(value AS INT) + 1 WHERE key = 'version'"
            self.cur.execute(query)

    def upgrade_to_latest(self):
        """
            Initialise upgrade level
        """

        while self.sql_schema_version < self.max_level:
            self._upgrade_one_level_sql_statement(self.sql_schema_version)
            self.sql_schema_version = True

    def upgrade_schema_if_old_version(self):
        """ check settings table exists """

        query = "SELECT name FROM sqlite_master WHERE type='table' AND name='settings'"
        parameters = ()
        self.cur.execute(query, parameters)
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

            # initiate sql file
            self.initialise_sql("upg_sc_if_old_ver_1")
        # After code refactoring, the possible status values for sent messages
        # have changed.
        self.initialise_sql("upg_sc_if_old_ver_2")

    def check_columns_can_store_binary_null(self):  # pylint: disable=too-many-locals,
        # too-many-branches, too-many-statements
        """
            Check if sqlite can store binary zeros.
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
                        _translate(
                            "MainWindow",
                            "Disk full"),
                        _translate(
                            "MainWindow",
                            'Alert: Your disk or data storage volume is full. Bitmessage will now exit.'),
                        True)))
                os._exit(0)
            else:
                logger.error(err)

    def check_vacuum(self):  # pylint: disable=too-many-locals, too-many-branches, too-many-statements,
        # Redefinition-of-parameters-type-from-tuple-to-str, R0204, line-too-long, E501
        """
            Check vacuum and apply sql queries for different different conditions.
            Let us check to see the last time we vaccumed the messages.dat file.
            If it has been more than a month let's do it now.
        """

        query = "SELECT value FROM settings WHERE key='lastvacuumtime'"
        parameters = ()
        self.cur.execute(query, parameters)
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
                                _translate(
                                    "MainWindow",
                                    "Disk full"),
                                _translate(
                                    "MainWindow",
                                    'Alert: Your disk or data storage volume is full. Bitmessage will now exit.'),
                                True)))
                        os._exit(0)
                query = "update settings set value=? WHERE key='lastvacuumtime'"
                parameters = (int(time.time()),)
                self.cur.execute(query, parameters)

    def upgrade_config_parser_setting_version(self, settingsversion):
        """
            Upgrade schema with respect setting version
        """

        self.initialise_sql("config_setting_ver_{}".format(settingsversion))

    def initialize_schema(self):
        """
            Initialise Db schema
        """
        try:
            inbox_exists = list(self.cur.execute('PRAGMA table_info(inbox)'))
            if not inbox_exists:
                self.initialise_sql("initialize_schema")
                self.conn.commit()
                logger.info('Created messages database file')
        except Exception as err:
            if str(err) == 'table inbox already exists':
                logger.debug('Database file already exists.')
            else:
                os._exit(
                    'ERROR trying to create database file (message.dat). Error message: %s\n' % str(err))

    def create_sql_function(self):
        """
            Apply create_function to DB
        """
        try:
            self.conn.create_function("enaddr", 3, func=encodeAddress, deterministic=True)
        except (TypeError, sqlite3.NotSupportedError) as err:
            logger.debug(
                "Got error while pass deterministic in sqlite create function {}, Passing 3 params".format(err))
            self.conn.create_function("enaddr", 3, encodeAddress)


class sqlThread(threading.Thread):
    """A thread for all SQL operations"""

    def __init__(self):
        threading.Thread.__init__(self, name="SQL")
        self.db = None
        self.max_setting_level = 4
        logger.debug('Init thread in sqlthread')

    @property
    def sql_config_settings_version(self):
        """ Getter for BMConfigParser (obj) """

        return config.getint(
            'bitmessagesettings', 'settingsversion')

    @sql_config_settings_version.setter
    def sql_config_settings_version(self, settingsversion):  # pylint: disable=R0201, no-self-use
        # Setter for BmConfigparser

        config.set(
            'bitmessagesettings', 'settingsversion', str(int(settingsversion) + 1))
        return config.save()

    def upgrade_config_setting_version(self):
        """
            upgrade config parser setting version.
            If the settings version is equal to 2 or 3 then the
            sqlThread will modify the pubkeys table and change
            the settings version to 4.
        """
        while self.sql_config_settings_version < self.max_setting_level:
            self.db.upgrade_config_parser_setting_version(self.sql_config_settings_version)
            self.sql_config_settings_version = self.sql_config_settings_version

    def loop_queue(self):  # pylint: disable=too-many-locals, too-many-branches, too-many-statements
        """
            Looping queue and process them
        """
        query = helper_sql.sqlSubmitQueue.get()
        if query == 'commit':
            try:
                self.db.conn.commit()
            except Exception as err:
                if str(err) == 'database or disk is full':
                    logger.fatal(
                        '(While committing) Alert: Your disk or data storage volume is full.'
                        ' sqlThread will now exit.')
                    queues.UISignalQueue.put((
                        'alert', (
                            _translate(
                                "MainWindow",
                                "Disk full"),
                            _translate(
                                "MainWindow",
                                'Alert: Your disk or data storage volume is full. Bitmessage will now exit.'),
                            True)))
                    os._exit(0)
        elif query == 'exit':
            self.db.conn.close()
            logger.info('sqlThread exiting gracefully.')
            return False
        elif query == 'movemessagstoprog':
            logger.debug('the sqlThread is moving the messages.dat file to the local program directory.')

            try:
                self.db.conn.commit()
            except Exception as err:
                if str(err) == 'database or disk is full':
                    logger.fatal(
                        '(while movemessagstoprog) Alert: Your disk or data storage volume is full.'
                        ' sqlThread will now exit.')
                    queues.UISignalQueue.put((
                        'alert', (
                            _translate(
                                "MainWindow",
                                "Disk full"),
                            _translate(
                                "MainWindow",
                                'Alert: Your disk or data storage volume is full. Bitmessage will now exit.'),
                            True)))
                    os._exit(0)
            self.db.conn.close()
            shutil.move(
                paths.lookupAppdataFolder() + 'messages.dat', paths.lookupExeFolder() + 'messages.dat')
            self.db.conn = sqlite3.connect(paths.lookupExeFolder() + 'messages.dat')
            self.db.conn.text_factory = str
            self.db.cur = self.db.conn.cursor()
        elif query == 'movemessagstoappdata':
            logger.debug('the sqlThread is moving the messages.dat file to the Appdata folder.')

            try:
                self.db.conn.commit()
            except Exception as err:
                if str(err) == 'database or disk is full':
                    logger.fatal(
                        '(while movemessagstoappdata) Alert: Your disk or data storage volume is full.'
                        ' sqlThread will now exit.')
                    queues.UISignalQueue.put((
                        'alert', (
                            _translate(
                                "MainWindow",
                                "Disk full"),
                            _translate(
                                "MainWindow",
                                'Alert: Your disk or data storage volume is full. Bitmessage will now exit.'),
                            True)))
                    os._exit(0)
            self.db.conn.close()
            shutil.move(
                paths.lookupExeFolder() + 'messages.dat', paths.lookupAppdataFolder() + 'messages.dat')
            self.db.conn = sqlite3.connect(paths.lookupAppdataFolder() + 'messages.dat')
            self.db.conn.text_factory = str
            self.db.cur = self.db.conn.cursor()
        elif query == 'deleteandvacuume':
            self.db.cur.execute('''delete from inbox where folder='trash' ''')
            self.db.cur.execute('''delete from sent where folder='trash' ''')
            self.db.conn.commit()
            try:
                self.db.cur.execute(''' VACUUM ''')
            except Exception as err:
                if str(err) == 'database or disk is full':
                    logger.fatal(
                        '(while deleteandvacuume) Alert: Your disk or data storage volume is full.'
                        ' sqlThread will now exit.')
                    queues.UISignalQueue.put((
                        'alert', (
                            _translate(
                                "MainWindow",
                                "Disk full"),
                            _translate(
                                "MainWindow",
                                'Alert: Your disk or data storage volume is full. Bitmessage will now exit.'),
                            True)))
                    os._exit(0)
        else:
            parameters = helper_sql.sqlSubmitQueue.get()
            rowcount = 0
            try:
                self.db.cur.execute(query, parameters)
                rowcount = self.db.cur.rowcount
            except Exception as err:
                if str(err) == 'database or disk is full':
                    logger.fatal(
                        '(while cur.execute) Alert: Your disk or data storage volume is full.'
                        ' sqlThread will now exit.')
                    queues.UISignalQueue.put((
                        'alert', (
                            _translate(
                                "MainWindow",
                                "Disk full"),
                            _translate(
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
                        str(query),
                        str(repr(parameters)),
                        str(err))
                    logger.fatal('This program shall now abruptly exit!')
                os._exit(0)

            helper_sql.sqlReturnQueue.put((self.db.cur.fetchall(), rowcount))
            # helper_sql.sqlSubmitQueue.task_done()
        return True

    def run(self):  # pylint: disable=too-many-locals, too-many-branches, too-many-statements,
        # Redefinition-of-parameters-type-from-tuple-to-str, R0204, line-too-long, E501
        """Process SQL queries from `.helper_sql.sqlSubmitQueue`"""

        logger.info('Init thread in sqlthread')

        self.db = BitmessageDB()

        helper_sql.sql_available = True

        config_ready.wait()

        self.db.create_sql_function()

        self.db.initialize_schema()

        self.upgrade_config_setting_version()

        helper_startup.updateConfig()

        self.db.upgrade_schema_if_old_version()

        self.db.upgrade_to_latest()

        self.db.check_columns_can_store_binary_null()

        self.db.check_vacuum()

        helper_sql.sql_ready.set()

        while self.loop_queue():
            pass


class TestDB(BitmessageDB):
    """
        Database connection build for test case
    """
    def _connection_build(self):
        self._connection_build_internal("memory", True)
        return self.conn, self.cur
