"""
Named tuples representing the network peers
"""
from six.moves import collections_abc as collections

Peer = collections.namedtuple('Peer', ['host', 'port'])
Node = collections.namedtuple('Node', ['services', 'host', 'port'])
