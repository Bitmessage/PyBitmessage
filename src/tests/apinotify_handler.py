#!/usr/bin/env python
"""
Utility configured as apinotifypath in bitmessagesettings
when pybitmessage started in test mode.
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division

from future import standard_library
standard_library.install_aliases()
from builtins import *
import sys
import tempfile

from .test_process import put_signal_file


if __name__ == '__main__':
    if sys.argv[1] == 'startingUp':
        put_signal_file(tempfile.gettempdir(), '.api_started')
