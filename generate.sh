#!/bin/bash

# Generates packaging

rm -f Makefile rpmpackage/*.spec

packagemonkey -n "PyBitmessage" --version "0.3.4" --dir "." -l "mit" -e "Bob Mottram (4096 bits) <bob@robotics.uk.to>" --brief "Send encrypted messages" --desc "Bitmessage is a P2P communications protocol used to send encrypted messages to another person or to many subscribers. It is decentralized and trustless, meaning that you need-not inherently trust any entities like root certificate authorities. It uses strong authentication which means that the sender of a message cannot be spoofed, and it aims to hide \"non-content\" data, like the sender and receiver of messages, from passive eavesdroppers like those running warrantless wiretapping programs." --homepage "https://github.com/Bitmessage/PyBitmessage" --section "mail" --categories "Office/Email" --dependsdeb "python (>= 2.7.0), openssl, python-qt4, libqt4-dev (>= 4.8.0), python-qt4-dev, sqlite3, libsqlite3-dev" --dependsrpm "python, PyQt4, openssl-compat-bitcoin-libs" --mainscript "bitmessagemain.py" --librarypath "/opt/openssl-compat-bitcoin/lib/" --suggestsdeb "libmessaging-menu-dev" --dependspuppy "openssl, python-qt4, sqlite3, sqlite3-dev, python-openssl, python-sip" --dependsarch "python2, qt4, python2-pyqt4, sqlite, openssl" --suggestsarch "python2-gevent" --pythonversion 2
