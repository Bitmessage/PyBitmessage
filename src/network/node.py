"""
src/network/node.py
===================
"""
import collections

Node = collections.namedtuple('Node', ['services', 'host', 'port'])
