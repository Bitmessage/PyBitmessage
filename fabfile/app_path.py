"""
app_path.py
===========

Since fabfile directories are not part of the project they can't see modules such as `version` to update the
documentation versioning for example.

"""

import os
import sys

app_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
sys.path.insert(0, app_dir)
