#!/bin/bash

# OS X Build script wrapper around the py2app script.
# These build can only be generated on OS X.
# Requires all build dependencies for Bitmessage
# Especially important is openssl installed through brew

export ARCHFLAGS="-arch i386 -arch x86_64" 

if [[ -z "$1" ]]; then
  echo "Please supply a version number for this release as the first argument."
  exit
fi

echo "Creating OS X packages for Bitmessage."

cd src && python2.7 build_osx.py py2app

if [[ $? = "0" ]]; then
  hdiutil create -fs HFS+ -volname "Bitmessage" -srcfolder dist/Bitmessage.app dist/bitmessage-v$1.dmg
else
  echo "Problem creating Bitmessage.app, stopping."
  exit
fi
