#!/bin/bash

xvfb-run --server-args="-screen 0, 720x1280x24" python3 tests-kivy.py
