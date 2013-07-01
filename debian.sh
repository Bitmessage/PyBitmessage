# To build a debian package first ensure that the code exists
# within a directory called pybitmessage-x.x.x (where the x's
# are the version number), make sure that the VERSION parameter
# within debian/rules and this script are correct, then run
# this script.

#!/bin/bash

APP=pybitmessage
PREV_VERSION=0.3.3
VERSION=0.3.4
RELEASE=1
ARCH_TYPE=all

#update version numbers automatically - so you don't have to
sed -i 's/VERSION='${PREV_VERSION}'/VERSION='${VERSION}'/g' Makefile
sed -i 's/'''${PREV_VERSION}'''/'''${VERSION}'''/g' src/shared.py 

# Create a source archive
make clean
# change the directory name to pybitmessage-version
mv ../PyBitmessage ../${APP}-${VERSION}
make source

# Build the package
dpkg-buildpackage -A

# change the directory name back
mv ../${APP}-${VERSION} ../PyBitmessage

gpg -ba ../${APP}_${VERSION}-${RELEASE}_${ARCH_TYPE}.deb
gpg -ba ../${APP}_${VERSION}.orig.tar.gz
