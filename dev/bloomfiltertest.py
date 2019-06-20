"""
dev/bloomfiltertest.py
======================

"""

import sqlite3
from os import getenv, path
from time import time

from pybloom import BloomFilter as BloomFilter1  # pylint: disable=import-error
from pybloomfilter import BloomFilter as BloomFilter2  # pylint: disable=import-error

# Ubuntu: apt-get install python-pybloomfiltermmap

conn = sqlite3.connect(path.join(getenv("HOME"), '.config/PyBitmessage/messages.dat'))

conn.text_factory = str
cur = conn.cursor()
rawlen = 0
itemcount = 0

cur.execute('''SELECT COUNT(hash) FROM inventory''')
for row in cur.fetchall():
    itemcount = row[0]

filtersize = 1000 * (int(itemcount / 1000) + 1)
errorrate = 1.0 / 1000.0

bf1 = BloomFilter1(capacity=filtersize, error_rate=errorrate)
bf2 = BloomFilter2(capacity=filtersize, error_rate=errorrate)

item = '''SELECT hash FROM inventory'''
cur.execute(item, '')
bf1time = 0
bf2time = 0
for row in cur.fetchall():
    rawlen += len(row[0])
    try:
        times = [time()]
        bf1.add(row[0])
        times.append(time())
        bf2.add(row[0])
        times.append(time())
        bf1time += times[1] - times[0]
        bf2time += times[2] - times[1]
    except IndexError:
        pass

# f = open("/home/shurdeek/tmp/bloom.dat", "wb")
# sb1.tofile(f)
# f.close()


print "Item count: %i" % (itemcount)
print "Raw length: %i" % (rawlen)
print "Bloom filter 1 length: %i, reduction to: %.2f%%" % \
      (bf1.bitarray.buffer_info()[1],
       100.0 * bf1.bitarray.buffer_info()[1] / rawlen)
print "Bloom filter 1 capacity: %i and error rate: %.3f%%" % (bf1.capacity, 100.0 * bf1.error_rate)
print "Bloom filter 1 took %.2fs" % (bf1time)
print "Bloom filter 2 length: %i, reduction to: %.3f%%" % \
      (bf2.num_bits / 8,
       100.0 * bf2.num_bits / 8 / rawlen)
print "Bloom filter 2 capacity: %i and error rate: %.3f%%" % (bf2.capacity, 100.0 * bf2.error_rate)
print "Bloom filter 2 took %.2fs" % (bf2time)
