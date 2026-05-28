"""Tests for SQL thread"""
# flake8: noqa:E402
import os
import tempfile
import unittest

os.environ['BITMESSAGE_HOME'] = tempfile.gettempdir()

from pybitmessage.class_sqlThread import TestDB  # noqa:E402
from pybitmessage.addresses import encodeAddress  # noqa:E402


class TestSqlBase(object):  # pylint: disable=E1101, too-few-public-methods, E1004, W0232
    """ Base for test case """

    __name__ = None
    root_path = os.path.dirname(os.path.dirname(__file__))
    test_db = None

    def _setup_db(self):  # pylint: disable=W0622, redefined-builtin
        """
            Drop all tables before each test case start
        """
        self.test_db = TestDB()
        self.test_db.create_sql_function()
        self.test_db.initialize_schema()

    def get_table_schema(self, table_name):
        """Get table list of column names and value types by table name"""
        self.test_db.cur.execute("""PRAGMA table_info({})""".format(table_name))
        res = self.test_db.cur.fetchall()
        res = [[x[1], x[2].lower()] for x in res]
        return res

    def execute_test_script(self, test_db_cur, file_name):  # pylint: disable=W0622, redefined-builtin
        """
            Executing sql script from file
        """

        with open(os.path.join(self.root_path, "tests/sql/{}.sql".format(file_name)), 'r') as sql_as_string:
            sql_as_string = sql_as_string.read()

        test_db_cur.cur.executescript(sql_as_string)


class TestFnBitmessageDB(TestSqlBase, unittest.TestCase):  # pylint: disable=protected-access
    """ Test case for Sql function"""

    def setUp(self):
        """setup for test case"""
        self._setup_db()

    def test_create_function(self):
        """Check the result of enaddr function"""
        st = "21122112211221122112".encode()
        encoded_str = encodeAddress(4, 1, st)

        item = '''SELECT enaddr(4, 1, ?);'''
        parameters = (st, )
        self.test_db.cur.execute(item, parameters)
        query = self.test_db.cur.fetchall()
        self.assertEqual(query[0][-1], encoded_str, "test case fail for create_function")


class TestInitializerBitmessageDB(TestSqlBase, unittest.TestCase):
    """Test case for SQL initializer"""

    def setUp(self):
        """
            Setup DB schema before start.
            And applying default schema for initializer test.
        """
        self._setup_db()

    def test_initializer(self):
        """
            Test db initialization
        """
        # check inbox table
        res = self.get_table_schema("inbox")
        check = [['msgid', 'blob'],
                 ['toaddress', 'text'],
                 ['fromaddress', 'text'],
                 ['subject', 'text'],
                 ['received', 'text'],
                 ['message', 'text'],
                 ['folder', 'text'],
                 ['encodingtype', 'int'],
                 ['read', 'bool'],
                 ['sighash', 'blob']]
        self.assertEqual(res, check, "inbox table not valid")

        # check sent table
        res = self.get_table_schema("sent")
        check = [['msgid', 'blob'],
                 ['toaddress', 'text'],
                 ['toripe', 'blob'],
                 ['fromaddress', 'text'],
                 ['subject', 'text'],
                 ['message', 'text'],
                 ['ackdata', 'blob'],
                 ['senttime', 'integer'],
                 ['lastactiontime', 'integer'],
                 ['sleeptill', 'integer'],
                 ['status', 'text'],
                 ['retrynumber', 'integer'],
                 ['folder', 'text'],
                 ['encodingtype', 'int'],
                 ['ttl', 'int']]
        self.assertEqual(res, check, "sent table not valid")

        # check subscriptions table
        res = self.get_table_schema("subscriptions")
        check = [['label', 'text'],
                 ['address', 'text'],
                 ['enabled', 'bool']]
        self.assertEqual(res, check, "subscriptions table not valid")

        # check addressbook table
        res = self.get_table_schema("addressbook")
        check = [['label', 'text'],
                 ['address', 'text']]
        self.assertEqual(res, check, "addressbook table not valid")

        # check blacklist table
        res = self.get_table_schema("blacklist")
        check = [['label', 'text'],
                 ['address', 'text'],
                 ['enabled', 'bool']]
        self.assertEqual(res, check, "blacklist table not valid")

        # check whitelist table
        res = self.get_table_schema("whitelist")
        check = [['label', 'text'],
                 ['address', 'text'],
                 ['enabled', 'bool']]
        self.assertEqual(res, check, "whitelist table not valid")

        # check pubkeys table
        res = self.get_table_schema("pubkeys")
        check = [['address', 'text'],
                 ['addressversion', 'int'],
                 ['transmitdata', 'blob'],
                 ['time', 'int'],
                 ['usedpersonally', 'text']]
        self.assertEqual(res, check, "pubkeys table not valid")

        # check inventory table
        res = self.get_table_schema("inventory")
        check = [['hash', 'blob'],
                 ['objecttype', 'int'],
                 ['streamnumber', 'int'],
                 ['payload', 'blob'],
                 ['expirestime', 'integer'],
                 ['tag', 'blob']]
        self.assertEqual(res, check, "inventory table not valid")

        # check settings table
        res = self.get_table_schema("settings")
        check = [['key', 'blob'],
                 ['value', 'blob']]
        self.assertEqual(res, check, "settings table not valid")

        # check objectprocessorqueue table
        res = self.get_table_schema("objectprocessorqueue")
        check = [['objecttype', 'int'],
                 ['data', 'blob']]
        self.assertEqual(res, check, "objectprocessorqueue table not valid")


class TestUpgradeBitmessageDB(TestSqlBase, unittest.TestCase):  # pylint: disable=protected-access
    """Test case for SQL versions"""

    def setUp(self):
        """
            Setup DB schema before start.
            And applying default schema for version test.
        """
        self.test_db = TestDB()
        self.test_db.create_sql_function()
        self.test_db.initialize_sql("initialize_schema_v1")
        self.test_db.conn.commit()

    def version(self):
        """
            Run SQL Scripts, Initialize DB with respect to versioning
            and Upgrade DB schema for all versions
        """
        def wrapper(*args):
            """
                Run SQL and mocking DB for versions
            """
            self = args[0]
            func_name = func.__name__
            version = func_name.rsplit('_', 1)[-1]
            for i in range(1, int(version) + 1):
                if i == 7 or i == 9 or i == 10:
                    self.execute_test_script(self.test_db, 'insert_test_values_version_{}'.format(i))
                    self.test_db.conn.commit()
                self.test_db._upgrade_one_level_sql_statement(i)   # pylint: disable= W0212, protected-access
            return func(*args)  # <-- use (self, ...)
        func = self
        return wrapper

    @version
    def test_bm_db_version_1(self):
        """
            Test update from version 1 to 2
        """
        # check version update in settings table
        version = self.test_db.sql_schema_version
        self.assertEqual(version, 2, "Settings version value not updated")

        # check adding first20bytesofencryptedmessage column to inventory table
        res = self.get_table_schema('inventory')
        check = ['first20bytesofencryptedmessage', 'blob']
        answ = (check in res)
        self.assertEqual(answ, True, "No first20bytesofencryptedmessage in inventory table in second version")

    @version
    def test_bm_db_version_2(self):
        """
            Test update from version 2 to 3
        """
        # check version update in settings table
        version = self.test_db.sql_schema_version
        self.assertEqual(version, 3, "Settings version value not updated")
        inventory_schema = self.get_table_schema('inventory')
        check_column = ['first20bytesofencryptedmessage', 'blob']
        answer = (check_column in inventory_schema)

        # check deleting first20bytesofencryptedmessage column to inventory table
        self.assertNotEqual(answer, True,
                            "Column first20bytesofencryptedmessage in table inventory not deleted in version 3")

        # check deleting inventory_backup table
        self.test_db.cur.execute(''' SELECT count(name) FROM sqlite_master
            WHERE type='table' AND name='inventory_backup' ''')
        res = self.test_db.cur.fetchall()[0][0]
        self.assertNotEqual(res, 1, "Table inventory_backup not deleted in versioning 3")

    @version
    def test_bm_db_version_3(self):
        """
            Test update from version 3 to 4
        """
        # check version update in settings table
        version = self.test_db.sql_schema_version
        self.assertEqual(version, 4, "Settings version value not updated")

        # check adding tag column to inventory table
        inventory_schema = self.get_table_schema('inventory')
        check_column = ['tag', 'blob']
        answer = (check_column in inventory_schema)
        self.assertEqual(answer, True, "No column tag in table inventory in version 4")

    @version
    def test_bm_db_version_4(self):
        """
            Test update from version 4 to 5
        """
        # check version update in settings table
        version = self.test_db.sql_schema_version
        self.assertEqual(version, 5, "Settings version value not updated")

        # check changing column addressversion type to int in table pubkeys
        pubkeys_schema = self.get_table_schema("pubkeys")
        check_column = ["addressversion", "int"]
        answer = check_column in pubkeys_schema
        self.assertEqual(answer, True, "Column addressversion not changed to int in table pubkeys")

        # check deleting pubkey objects from inventory table
        self.test_db.cur.execute(''' SELECT COUNT(hash) FROM inventory WHERE objecttype = 'pubkey' ''')
        res = self.test_db.cur.fetchall()[0][0]
        self.assertEqual(res, 0, "Pubkey objects not deleted from inventory table in versioning 5")

    @version
    def test_bm_db_version_5(self):
        """
            Test update from version 5 to 6
        """
        # check version update in settings table
        version = self.test_db.sql_schema_version
        self.assertEqual(version, 6, "Settings version value not updated")

        # check deleting knownnodes table
        self.test_db.cur.execute(''' SELECT count(name) FROM sqlite_master
        WHERE type='table' AND name='knownnodes' ''')
        res = self.test_db.cur.fetchall()[0][0]
        self.assertNotEqual(res, 1, "Table knownnodes not deleted in versioning 6")

        # check creating objectprocessorqueue table
        self.test_db.cur.execute(''' SELECT count(name) FROM sqlite_master
            WHERE type='table' AND name='objectprocessorqueue' ''')
        res = self.test_db.cur.fetchall()[0][0]
        self.assertNotEqual(res, 0, "Table objectprocessorqueue not created in versioning 6")

        # check objectprocessorqueue table schema
        objectprocessorqueue_schema = self.get_table_schema("objectprocessorqueue")
        check = [['objecttype', 'text'],
                 ['data', 'blob']]
        self.assertEqual(objectprocessorqueue_schema, check, "objectprocessorqueue table is not valid")

    @version
    def test_bm_db_version_6(self):
        """
            Test update from version 6 to 7
        """
        inventory_schema = self.get_table_schema("inventory")
        objectprocessorqueue_schema = self.get_table_schema("objectprocessorqueue")

        # check version update in settings table
        version = self.test_db.sql_schema_version
        self.assertEqual(version, 7, "Settings version value not updated")

        # check changing objecttype column type to int in table objectprocessorqueue
        check = ["objecttype", "int"]
        answ = check in objectprocessorqueue_schema
        self.assertEqual(answ, True, "Type of objecttype column in table objectprocessorqueue not changed to int")

        # check changing objecttype column type to int in table inventory
        check = ["objecttype", "int"]
        answ = check in inventory_schema
        self.assertEqual(answ, True, "Type of objecttype column in table inventory not changed to int")

        # check adding expirestime column in table inventory
        check = ["expirestime", "integer"]
        answ = check in inventory_schema
        self.assertEqual(answ, True, "expirestime column not added to table inventory")

        # check deleting receivedtime column from table inventory
        check = ["receivedtime", "integer"]
        answ = check in inventory_schema
        self.assertNotEqual(answ, True, "receivedtime column not deleted from table inventory")

    @version
    def test_bm_db_version_7(self):
        """
            Test update from version 7 to 8
        """
        # check version update in settings table
        version = self.test_db.sql_schema_version
        self.assertEqual(version, 8, "Settings version value not updated")

        # check clearing pubkeys table
        self.test_db.cur.execute('''SELECT * FROM pubkeys ''')
        pubkeys = self.test_db.cur.fetchall()
        self.assertEqual(pubkeys, [], "pubkeys table is not clear")

        # check deleting pubkeys from table inventory
        self.test_db.cur.execute('''SELECT * FROM inventory WHERE objecttype = 1''')
        inventory = self.test_db.cur.fetchall()
        self.assertEqual(inventory, [], "pubkeys not deleted from inventory table")

        # check updating statuses in sent table
        self.test_db.cur.execute('''SELECT status FROM sent ''')
        sent = self.test_db.cur.fetchall()
        self.assertEqual(sent, [('msgqueued',), ('msgqueued',)], "Statuses in sent table not updated")

    @version
    def test_bm_db_version_8(self):
        """
            Test update from version 8 to 9
        """
        # check version update in settings table
        version = self.test_db.sql_schema_version
        self.assertEqual(version, 9, "Settings version value not updated")

        # check adding sighash column to inbox table
        inbox_schema = self.get_table_schema("inbox")
        check = ['sighash', 'blob']
        answ = check in inbox_schema
        self.assertEqual(answ, True, "sighash column not added to inbox table")

    @version
    def test_bm_db_version_9(self):
        """
            Test update from version 9 to 10
        """
        # check version update in settings table
        version = self.test_db.sql_schema_version
        self.assertEqual(version, 10, "Settings version value not updated")

        sent_schema = self.get_table_schema('sent')
        pubkeys_schema = self.get_table_schema('pubkeys')

        # check pubkeys table schema updating
        check = ['hash', 'blob']
        answ = check in pubkeys_schema
        self.assertNotEqual(answ, True, "Column hash not deleted from pubkeys table")

        check = ['address', 'text']
        answ = check in pubkeys_schema
        self.assertEqual(answ, True, "Column address not added to pubkeys table")

        # check sent table schema updating
        check = ['pubkeyretrynumber', 'integer']
        answ = check in sent_schema
        self.assertNotEqual(answ, True, "Column pubkeyretrynumber not deleted from sent table")

        check = ['msgretrynumber', 'integer']
        answ = check in sent_schema
        self.assertNotEqual(answ, True, "Column msgretrynumber not deleted from sent table")

        check = ['senttime', 'integer']
        answ = check in sent_schema
        self.assertEqual(answ, True, "Column senttime not added to sent table")

        check = ['sleeptill', 'integer']
        answ = check in sent_schema
        self.assertEqual(answ, True, "Column sleeptill not added to sent table")

        check = ['retrynumber', 'integer']
        answ = check in sent_schema
        self.assertEqual(answ, True, "Column retrynumber not added to sent table")

        check = ['ttl', 'int']
        answ = check in sent_schema
        self.assertEqual(answ, True, "Column ttl not added to sent table")

        # check pubkeys_backup table deleting
        self.test_db.cur.execute("SELECT count(name) FROM  sqlite_master WHERE type='table' AND name='pubkeys_backup'")  # noqa
        res = self.test_db.cur.fetchall()
        self.assertNotEqual(res[0][0], 1, "Table pubkeys_backup not deleted")

        # check data migration
        check_pubkey = [('BM-2D77qGjcBfFmqn3EGs85ojKJtCh7b3tutK', 3, '', 1, '')]
        self.test_db.cur.execute('''SELECT * FROM pubkeys''')
        res = self.test_db.cur.fetchall()
        self.assertEqual(res, check_pubkey, "Migration pubkeys table data failed")

        self.test_db.cur.execute('''SELECT * FROM sent''')
        res = self.test_db.cur.fetchall()
        check_sent = [('', '', '', '', '', '', '', 1, 1, 0, 'msgqueued', 0, '', 1, 216000),
                      ('', '', '', '', '', '', '', 1, 1, 0, 'msgqueued', 0, '', 1, 216000)]
        self.assertEqual(res, check_sent, "Migration sent table data failed")

    @version
    def test_bm_db_version_10(self):
        """
            Test update from version 10 to 11
        """
        # check version update in settings table
        version = self.test_db.sql_schema_version
        self.assertEqual(version, 11, "Settings version value not updated")

        # check data migration in addressbook table
        self.test_db.cur.execute('''SELECT * FROM addressbook''')
        res = self.test_db.cur.fetchall()
        self.assertEqual(res, [('', '')], "Migration addressbook table data failed")

    def test_upgrade_to_latest(self):
        """
            Test upgrade_to_latest func
        """
        self.test_db.upgrade_to_latest()
        # check inbox table
        res = self.get_table_schema("inbox")
        check = [['msgid', 'blob'],
                 ['toaddress', 'text'],
                 ['fromaddress', 'text'],
                 ['subject', 'text'],
                 ['received', 'text'],
                 ['message', 'text'],
                 ['folder', 'text'],
                 ['encodingtype', 'int'],
                 ['read', 'bool'],
                 ['sighash', 'blob']]
        self.assertEqual(res, check, "inbox table not valid")

        # check sent table
        res = self.get_table_schema("sent")
        check = [['msgid', 'blob'],
                 ['toaddress', 'text'],
                 ['toripe', 'blob'],
                 ['fromaddress', 'text'],
                 ['subject', 'text'],
                 ['message', 'text'],
                 ['ackdata', 'blob'],
                 ['senttime', 'integer'],
                 ['lastactiontime', 'integer'],
                 ['sleeptill', 'integer'],
                 ['status', 'text'],
                 ['retrynumber', 'integer'],
                 ['folder', 'text'],
                 ['encodingtype', 'int'],
                 ['ttl', 'int']]
        self.assertEqual(res, check, "sent table not valid")

        # check subscriptions table
        res = self.get_table_schema("subscriptions")
        check = [['label', 'text'],
                 ['address', 'text'],
                 ['enabled', 'bool']]
        self.assertEqual(res, check, "subscriptions table not valid")

        # check addressbook table
        res = self.get_table_schema("addressbook")
        check = [['label', 'text'],
                 ['address', 'text']]
        self.assertEqual(res, check, "addressbook table not valid")

        # check blacklist table
        res = self.get_table_schema("blacklist")
        check = [['label', 'text'],
                 ['address', 'text'],
                 ['enabled', 'bool']]
        self.assertEqual(res, check, "blacklist table not valid")

        # check whitelist table
        res = self.get_table_schema("whitelist")
        check = [['label', 'text'],
                 ['address', 'text'],
                 ['enabled', 'bool']]
        self.assertEqual(res, check, "whitelist table not valid")

        # check pubkeys table
        res = self.get_table_schema("pubkeys")
        check = [['address', 'text'],
                 ['addressversion', 'int'],
                 ['transmitdata', 'blob'],
                 ['time', 'int'],
                 ['usedpersonally', 'text']]
        self.assertEqual(res, check, "pubkeys table not valid")

        # check inventory table
        res = self.get_table_schema("inventory")
        check = [['hash', 'blob'],
                 ['objecttype', 'int'],
                 ['streamnumber', 'int'],
                 ['payload', 'blob'],
                 ['expirestime', 'integer'],
                 ['tag', 'blob']]
        self.assertEqual(res, check, "inventory table not valid")

        # check settings table
        res = self.get_table_schema("settings")
        check = [['key', 'blob'],
                 ['value', 'blob']]
        self.assertEqual(res, check, "settings table not valid")

        # check objectprocessorqueue table
        res = self.get_table_schema("objectprocessorqueue")
        check = [['objecttype', 'int'],
                 ['data', 'blob']]
        self.assertEqual(res, check, "objectprocessorqueue table not valid")
