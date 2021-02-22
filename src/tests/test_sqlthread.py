"""
Test for ECC blind signatures
"""
import os
import unittest
import shutil  # used for moving the messages.dat file
import sqlite3
import sys
import threading
import time
# print sys.path
# import state
from ..state import appdata
from ..helper_sql import sqlStoredProcedure

# import threading
# from hashlib import sha256
# from ..helper_sql import sqlQuery
# from ..version import softwareVersion
# from common import cleanup
from ..class_sqlThread import (sqlThread, UpgradeDB)

class TestSqlThread(unittest.TestCase):
    """
        Test case for SQLThread
    """

    # def __init__(self):
    # initialise Db connection
    conn = sqlite3.connect(appdata + 'messages.dat')
    conn.text_factory = str
    cur = conn.cursor()

    @classmethod
    def setUpClass(cls):
        # Start SQL thread
        sqlLookup = sqlThread()
        sqlLookup.daemon = False
        sqlLookup.start()

    @classmethod
    def tearDownClass(cls):
        # Stop sql thread
        sqlStoredProcedure('exit')
        print "...TearDown"

    def db_connection(self):
        conn = sqlite3.connect(appdata + 'messages.dat')
        conn.text_factory = str
        return conn.cursor()

    def normalize_version(self):
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
            # self.cur.execute(
            #     '''CREATE TABLE inventory (hash blob, objecttype int, streamnumber int, payload blob,'''
            #     ''' expirestime integer, tag blob, UNIQUE(hash) ON CONFLICT REPLACE)''')
            self.cur.execute(
                '''CREATE TABLE inventory (hash blob, objecttype int, streamnumber int, payload blob,'''
                ''' expirestime integer, UNIQUE(hash) ON CONFLICT REPLACE)''')
            # self.cur.execute(
            #     '''INSERT INTO subscriptions VALUES'''
            #     '''('Bitmessage new releases/announcements','BM-GtovgYdgs7qXPkoYaRgrLFuFKz1SFpsw',1)''')
            self.cur.execute('''CREATE TABLE settings (key blob, value blob, UNIQUE(key) ON CONFLICT REPLACE)''')
            # self.cur.execute('''INSERT INTO settings VALUES('version','11')''')
            # self.cur.execute('''INSERT INTO settings VALUES('lastvacuumtime',?)''', (
            #     int(time.time()),))
            self.cur.execute(
                '''CREATE TABLE objectprocessorqueue'''
                ''' (objecttype int, data blob, UNIQUE(objecttype, data) ON CONFLICT REPLACE)''')
            self.conn.commit()
        except Exception as err:
            print err.message
            if str(err) == 'table inbox already exists':
                print "table inbox already exists"
            else:
                sys.stderr.write(
                    'ERROR trying to create database file (message.dat). Error message: %s\n' % str(err))
                os._exit(0)

    def clean_db(self):
        tables = list(self.cur.execute("select name from sqlite_master where type is 'table'"))
        return self.cur.executescript(';'.join(["drop table if exists %s" % i for i in tables]))

    def test_sql_thread_version_one(self):
        """
            Test with version 1
        """

        self.clean_db()
        self.normalize_version()
        self.cur.execute('''INSERT INTO settings VALUES('version','1')''')
        upgrade_db = UpgradeDB()
        upgrade_db.cur = self.cur
        upgrade_db.upgrade_schema_data_1()

