import time
import uuid

import helper_inbox
import helper_sql

# from .tests.samples import sample_inbox_msg_ids, sample_deterministic_addr4
sample_deterministic_addr4 = 'BM-2cWzSnwjJ7yRP3nLEWUV5LisTZyREWSzUK'
sample_inbox_msg_ids = ['27e644765a3e4b2e973ee7ccf958ea20', '51fc5531-3989-4d69-bbb5-68d64b756f5b',
                        '2c975c515f8b414db5eea60ba57ba455', 'bc1f2d8a-681c-4cc0-9a12-6067c7e1ac24']


def populate_api_test_data():
    '''Adding test records in inbox table'''
    helper_sql.sql_ready.wait()

    test1 = (
        sample_inbox_msg_ids[0], sample_deterministic_addr4,
        sample_deterministic_addr4, 'Test1 subject', int(time.time()),
        'Test1 body', 'inbox', 2, 0, uuid.uuid4().bytes
    )
    test2 = (
        sample_inbox_msg_ids[1], sample_deterministic_addr4,
        sample_deterministic_addr4, 'Test2 subject', int(time.time()),
        'Test2 body', 'inbox', 2, 0, uuid.uuid4().bytes
    )
    test3 = (
        sample_inbox_msg_ids[2], sample_deterministic_addr4,
        sample_deterministic_addr4, 'Test3 subject', int(time.time()),
        'Test3 body', 'inbox', 2, 0, uuid.uuid4().bytes
    )
    test4 = (
        sample_inbox_msg_ids[3], sample_deterministic_addr4,
        sample_deterministic_addr4, 'Test4 subject', int(time.time()),
        'Test4 body', 'inbox', 2, 0, uuid.uuid4().bytes
    )
    helper_inbox.insert(test1)
    helper_inbox.insert(test2)
    helper_inbox.insert(test3)
    helper_inbox.insert(test4)
