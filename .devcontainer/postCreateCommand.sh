#!/bin/sh

pip3 install -r requirements.txt
pip3 install -r kivy-requirements.txt

# Linter tools needed by the VS Code extensions (ms-python.flake8,
# ms-python.pylint, nwgh.bandit).  The apt-installed system packages
# are not visible to the VS Code Python interpreter.
pip3 install flake8 pylint bandit