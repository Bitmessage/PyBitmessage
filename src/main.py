"""
src/main.py
===========

This module is for thread start.
"""

from __future__ import print_function

import state
from bitmessagemain import main

if __name__ == '__main__':
    state.kivy = True
    print("Kivy Loading......")
    main()
