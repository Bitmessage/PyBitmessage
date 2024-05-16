#!/bin/sh
flake8 --max-line-length=119 --config=setup.cfg src/*.py src/network/*.py src/storage/*.py src/bitmessageqt/*.py
