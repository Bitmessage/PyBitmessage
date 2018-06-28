"""
pathmagic.py
===========

Makes the app portable by adding the parent directory to the path and changing to that directory. Putting this in a
seperate module make it re-usable and does not confuse isort and friends due to code interspersed among the imports.
"""

import os
import sys

app_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(app_dir)
sys.path.insert(0, app_dir)
