#!/bin/sh

pip3 install -r kivy-requirements.txt

export INSTALL_TESTS=True

pip3 install .
