# PyBitmessage Installation Instructions
- Binary (no separate installation of dependencies required)
    - windows (32bit only): https://download.bitmessage.org/snapshots/
    - linux (64bit): https://appimage.bitmessage.org/releases/
    - mac (64bit, not up to date): https://github.com/Bitmessage/PyBitmessage/releases/tag/v0.6.3
- Source
    git clone git://github.com/Bitmessage/PyBitmessage.git

## Helper Script for building from source
Go to the directory with PyBitmessage source code and run:
```
python checkdeps.py
```
If there are missing dependencies, it will explain you what is missing and for many Unix-like systems also what you have to do to resolve it. You need to repeat calling the script until you get nothing mandatory missing. How you then run setuptools depends on whether you want to install it to user's directory or system.

### If checkdeps fails, then verify manually which dependencies are missing from below
Before running PyBitmessage, make sure you have all the necessary dependencies
installed on your system.

These dependencies may not be available on a recent OS and PyBitmessage may not build on such systems.
Here's a list of dependencies needed for PyBitmessage based on operating system

For Debian-based (Ubuntu, Raspbian, PiBang, others)
```
python2.7 openssl libssl-dev git python-msgpack python-qt4 python-six
```
For Arch Linux
```
python2 openssl git python2-pyqt4 python-six
```
For Fedora
```
python python-qt4 git openssl-compat-bitcoin-libs python-six
```
For Red Hat Enterprise Linux (RHEL)
```
python python-qt4 git openssl-compat-bitcoin-libs python-six
```
For GNU Guix
```
python2-msgpack python2-pyqt@4.11.4 python2-sip openssl python-six
```

## setuptools
This is now the recommended and in most cases the easiest procedure for installing PyBitmessage. 

There are 3 options for running setuptools: root, user, venv

### as root:
```
python setup.py install
pybitmessage
```

### as user:
```
python setup.py install --user
~/.local/bin/pybitmessage
```

### as venv:
Create virtualenv with Python 2.x version
```
virtualenv -p python2 env
```

Activate env
```
source env/bin/activate
```

Install requirements.txt
```
pip install -r requirements.txt
```

Build & run pybitmessage
```
python setup.py install
pybitmessage
```

## Alternative way to run PyBitmessage, without setuptools (this isn't recommended)
run `src/bitmessagemain.py`.
```
cd PyBitmessage/ && python src/bitmessagemain.py
```
