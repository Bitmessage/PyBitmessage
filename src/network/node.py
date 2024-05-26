"""
Named tuples representing the network peers
"""
import collections

Peer = collections.namedtuple('Peer', ['host', 'port'])
Node = collections.namedtuple('Node', ['services', 'host', 'port'])
