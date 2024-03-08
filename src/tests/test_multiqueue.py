"""Test cases for multiqueue"""

import unittest
from pybitmessage.multiqueue import MultiQueue


class TestMultiQueue(unittest.TestCase):
    """Test cases for multiqueue"""

    def test_queue_creation(self):
        """Check if the queueCount matches the specified value"""
        mqsize = 3
        multiqueue = MultiQueue(count=mqsize)
        self.assertEqual(multiqueue.queueCount, mqsize)

    def test_empty_queue(self):
        """Check for empty queue"""
        multiqueue = MultiQueue(count=5)
        self.assertEqual(multiqueue.totalSize(), 0)

    def test_put_get_count(self):
        """check if put & get count is equal"""
        multiqueue = MultiQueue(count=5)
        put_count = 6
        for i in range(put_count):
            multiqueue.put(i)

        get_count = 0
        while multiqueue.totalSize() != 0:
            if multiqueue.qsize() > 0:
                multiqueue.get()
                get_count += 1
            multiqueue.iterate()

        self.assertEqual(get_count, put_count)

    def test_put_and_get(self):
        """Testing Put and Get"""
        item = 400
        multiqueue = MultiQueue(count=3)
        multiqueue.put(item)
        result = None
        for _ in multiqueue.queues:
            if multiqueue.qsize() > 0:
                result = multiqueue.get()
                break
            multiqueue.iterate()
        self.assertEqual(result, item)

    def test_iteration(self):
        """Check if the iteration wraps around correctly"""
        mqsize = 3
        iteroffset = 1
        multiqueue = MultiQueue(count=mqsize)
        for _ in range(mqsize + iteroffset):
            multiqueue.iterate()
        self.assertEqual(multiqueue.iter, iteroffset)

    def test_total_size(self):
        """Check if the total size matches the expected value"""
        multiqueue = MultiQueue(count=3)
        put_count = 5
        for i in range(put_count):
            multiqueue.put(i)
        self.assertEqual(multiqueue.totalSize(), put_count)
