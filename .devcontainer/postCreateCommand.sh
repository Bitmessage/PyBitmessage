#!/bin/sh

pip3 install -r requirements.txt
pip3 install -r kivy-requirements.txt

# PyQt4 stubs, for better linter/autocomplete
git clone https://github.com/TheKewlStore/PyQt4-Stubs.git /tmp/pyqt4-stubs
P2DIR=$(python2 -c "import site; print(site.getusersitepackages())")/
P3DIR=$(python3 -c "import site; print(site.getusersitepackages())")/
cp -r /tmp/pyqt4-stubs/* "${P2DIR}"
cp -r /tmp/pyqt4-stubs/* "${P3DIR}"

# Linter tools needed by the VS Code extensions (ms-python.flake8,
# ms-python.pylint, nwgh.bandit).  The apt-installed system packages
# are not visible to the VS Code Python interpreter.
pip3 install flake8 pylint bandit
