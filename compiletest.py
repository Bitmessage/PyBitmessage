#!/usr/bin/python2.7

import ctypes
import fnmatch
import os
import sys
import traceback

matches = []
for root, dirnames, filenames in os.walk('src'):
    for filename in fnmatch.filter(filenames, '*.py'):
        matches.append(os.path.join(root, filename))

for filename in matches:
    source = open(filename, 'r').read() + '\n'
    try:
        compile(source, filename, 'exec')
    except Exception as e:
        ctypes.windll.user32.MessageBoxA(0, traceback.format_exc(), "Exception in " + filename, 1)
        sys.exit(1)