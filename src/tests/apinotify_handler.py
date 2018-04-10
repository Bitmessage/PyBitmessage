#!/usr/bin/env python

import os
import sys
import tempfile
from datetime import datetime


if __name__ == '__main__':
    if sys.argv()[1] == 'startingUp':
        with open(
            os.path.join(tempfile.gettempdir(), '.api_started'), 'wb'
        ) as start_file:
            start_file.write(datetime.now())
