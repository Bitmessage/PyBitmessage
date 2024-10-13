"""
SQLThread is defined here
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

    def _connection_build(self):
        self._connection_build_internal('messages.dat', False)

    def _connection_build_internal(
            self, file_name="messages.dat", memory=False
    ):
        """Establish SQL connection"""
        self.conn = sqlite3.connect(
            ':memory:' if memory else os.path.join(state.appdata, file_name))
        self.conn.text_factory = str
        self.cur = self.conn.cursor()
        self.cur.execute("PRAGMA secure_delete = true")

    def __get_current_settings_version(self):
        """Get current setting Version"""
        self.cur.execute(
            "SELECT value FROM settings WHERE key='version'")
        try:
            return int(self.cur.fetchall()[0][0])
        except (ValueError, IndexError):
            return 0

    def _upgrade_one_level_sql_statement(self, file_name):
        """Upgrade database versions with applying sql scripts"""
        self.initialize_sql("init_version_{}".format(file_name))

    def initialize_sql(self, file_name):
        """Initializing sql"""
        try:
            with open(os.path.join(
                    paths.codePath(), 'sql', '{}.sql'.format(file_name))
            ) as sql_file:
                sql_as_string = sql_file.read()
            self.cur.executescript(sql_as_string)
            return True
        except OSError as err:
            logger.debug('The file is missing. Error message: %s\n',
                         str(err))
        except IOError as err:
            logger.debug(
                'ERROR trying to initialize database. Error message: %s\n',
                str(err))
        except sqlite3.Error as err:
            logger.error(err)
        except Exception as err:
            logger.debug(
                'ERROR trying to initialize database. Error message: %s\n',
                str(err))
        return False

    @property
    def sql_schema_version(self):
        """Getter for get current schema version"""
        return self.__get_current_settings_version()

    def upgrade_to_latest(self):
        """Initialize upgrade level"""
        self.cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")
        if not self.cur.fetchall():
            # The settings table doesn't exist. We need to make it.
            logger.debug(
                "In messages.dat database, creating new 'settings' table.")
            self.cur.execute(
                "CREATE TABLE settings (key text, value blob, UNIQUE(key)"
                " ON CONFLICT REPLACE)")
            self.cur.execute("INSERT INTO settings VALUES('version','1')")
            self.cur.execute(
                "INSERT INTO settings VALUES('lastvacuumtime',?)",
                (int(time.time()),))
            logger.debug(
                'In messages.dat database, removing an obsolete field'
                'from the pubkeys table.')

            # initiate sql file
            self.initialize_sql("upg_sc_if_old_ver_1")
            self.conn.commit()
        # After code refactoring, the possible status values for sent messages
        # have changed.
        self.initialize_sql("upg_sc_if_old_ver_2")
        self.conn.commit()

        while self.sql_schema_version < self.max_level:
            self._upgrade_one_level_sql_statement(self.sql_schema_version)
            self.conn.commit()

    def check_columns_can_store_binary_null(self):
        """Check if sqlite can store binary zeros."""
        try:
            testpayload = '\x00\x00'
            t = ('1234', 1, testpayload, '12345678', 'no')
            self.cur.execute("INSERT INTO pubkeys VALUES(?,?,?,?,?)", t)
            self.conn.commit()
            self.cur.execute(
                "SELECT transmitdata FROM pubkeys WHERE address='1234' ")
            transmitdata = self.cur.fetchall()[-1][0]
            self.cur.execute("DELETE FROM pubkeys WHERE address='1234' ")
            self.conn.commit()
            if transmitdata != testpayload:
                logger.fatal(
                    'Problem: The version of SQLite you have cannot store Null'
                    'values. Please download and install the latest revision'
                    'of your version of Python (for example, the latest '
                    'Python 2.7 revision) and try again.\n')
                logger.fatal(
                    'PyBitmessage will now exit very abruptly.'
                    ' You may now see threading errors related to this abrupt'
                    'exit but the problem you need to solve is related to'
                    'SQLite.\n\n')
                os._exit(1)
        except Exception as err:
            sqlThread.error_handler(err, 'null value test')

    def check_vacuum(self):
        """
        Check vacuum and apply sql queries for different conditions.
        Let us check to see the last time we vaccumed the messages.dat file.
        If it has been more than a month let's do it now.
        """
        self.cur.execute(
            "SELECT value FROM settings WHERE key='lastvacuumtime'")
        try:
            date = self.cur.fetchall()[-1][0]
        except IndexError:
            return
        if int(date) < int(time.time()) - 86400:
            logger.info(
                'It has been a long time since the messages.dat file'
                ' has been vacuumed. Vacuuming now...')
            try:
                self.cur.execute(''' VACUUM ''')
            except Exception as err:
                sqlThread.error_handler(err, 'VACUUM')
            self.cur.execute(
                "UPDATE settings SET value=? WHERE key='lastvacuumtime'",
                (int(time.time()),))

    def upgrade_config_parser_setting_version(self, settingsversion):
        """Upgrade schema with respect setting version"""

        self.initialize_sql("config_setting_ver_{}".format(settingsversion))

    def initialize_schema(self):
        """Initialize DB schema"""
        try:
            inbox_exists = list(self.cur.execute("PRAGMA table_info(inbox)"))
            if not inbox_exists:
                self.initialize_sql("initialize_schema")
                self.conn.commit()
                logger.info('Created messages database file')
        except Exception as err:
            if str(err) == 'table inbox already exists':
                logger.debug('Database file already exists.')
            else:
                logger.fatal(
                    'Error trying to create database file (message.dat).'
                    ' Error message: %s\n', str(err))
                os._exit(1)

    def create_sql_function(self):
        """Apply create_function to DB"""
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
        self.rowcount = 0
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

    @staticmethod
    def error_handler(err, command, query=None, parameters=None):
        """Common error handler"""
        if str(err) == 'database or disk is full':
            logger.fatal(
                "(While %s) Alert: Your disk or data storage volume is full. sqlThread will now exit.", command
            )
            queues.UISignalQueue.put((
                'alert', (
                    _translate(
                        "MainWindow",
                        "Disk full"),
                    _translate(
                        "MainWindow",
                        'Alert: Your disk or data storage volume is full. Bitmessage will now exit.'),
                    True)))
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

    def is_query_commit(self):
        """When query == 'commit'"""
        try:
            self.db.conn.commit()
        except Exception as err:
            self.error_handler(err, 'committing')

    def is_query_movemessagstoprog(self):
        """When query == 'movemessagstoprogs'"""
        logger.debug('the sqlThread is moving the messages.dat file to the local program directory.')
        try:
            self.db.conn.commit()
        except Exception as err:
            self.error_handler(err, 'movemessagstoprog')
        self.db.conn.close()
        shutil.move(
            paths.lookupAppdataFolder() + 'messages.dat', paths.lookupExeFolder() + 'messages.dat')
        self.db.conn = sqlite3.connect(paths.lookupExeFolder() + 'messages.dat')
        self.db.conn.text_factory = str
        self.db.cur = self.db.conn.cursor()

    def is_query_deleteandvacuume(self):
        """When query == 'deleteandvacuume'"""
        try:
            self.db.cur.execute(''' VACUUM ''')
        except Exception as err:
            self.error_handler(err, 'deleteandvacuume')
        self.db.cur.execute('''delete from inbox where folder='trash' ''')
        self.db.cur.execute('''delete from sent where folder='trash' ''')
        self.db.conn.commit()

    def is_query_other(self, query):
        """When the query can be default or other '"""
        parameters = helper_sql.sqlSubmitQueue.get()
        try:
            self.db.cur.execute(query, parameters)
            self.rowcount = self.db.cur.rowcount
            return self.rowcount
        except Exception as err:
            self.error_handler(err, 'cur.execute', query, parameters)

    def is_query_movemessagestoappdata(self):
        """When query == 'movemessagestoappdata'"""
        logger.debug('the sqlThread is moving the messages.dat file to the Appdata folder.')
        try:
            self.db.conn.commit()
        except Exception as err:
            self.error_handler(err, 'movemessagstoappdata')
        self.db.conn.close()
        shutil.move(
            paths.lookupExeFolder() + 'messages.dat', paths.lookupAppdataFolder() + 'messages.dat')
        self.db.conn = sqlite3.connect(paths.lookupAppdataFolder() + 'messages.dat')
        self.db.conn.text_factory = str
        self.db.cur = self.db.conn.cursor()

    def is_query_exit(self):
        """When query == 'exit'"""
        self.db.conn.close()
        logger.info('sqlThread exiting gracefully.')

    def loop_queue(self):
        """Looping queue and process them"""
        query = helper_sql.sqlSubmitQueue.get()
        if query == 'commit':
            self.is_query_commit()
        elif query == 'exit':
            self.is_query_exit()
            return False
        elif query == 'movemessagstoprog':
            self.is_query_movemessagstoprog()
        elif query == 'movemessagstoappdata':
            self.is_query_movemessagestoappdata()
        elif query == 'deleteandvacuume':
            self.is_query_deleteandvacuume()
        else:
            self.rowcount = self.is_query_other(query)
            helper_sql.sqlReturnQueue.put((self.db.cur.fetchall(), self.rowcount))
        return True

    def run(self):  # pylint: disable=R0204, E501
        """Process SQL queries from `.helper_sql.sqlSubmitQueue`"""

        logger.info('Init thread in sqlthread')
        # pylint: disable=redefined-variable-type
        if state.testmode:
            self.db = TestDB()
        else:
            self.db = BitmessageDB()
        helper_sql.sql_available = True

        config_ready.wait()

        self.db.create_sql_function()

        self.db.initialize_schema()

        self.upgrade_config_setting_version()

        helper_startup.updateConfig()

        self.db.upgrade_to_latest()

        self.db.check_columns_can_store_binary_null()

        self.db.check_vacuum()

        helper_sql.sql_ready.set()

        while self.loop_queue():
            pass


class TestDB(BitmessageDB):
    """Database connection build for test e"""

    def _connection_build(self):
        self._connection_build_internal("memory", True)
        return self.conn, self.cur
