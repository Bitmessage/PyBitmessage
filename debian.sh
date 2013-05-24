# To build a debian package first ensure that the code exists
# within a directory called pybitmessage-x.x.x (where the x's
# are the version number), make sure that the VERSION parameter
# within debian/rules and this script are correct, then run
# this script.

#!/bin/bash

APP=pybitmessage
VERSION=0.3.1
ARCH_TYPE=all

# Create a source archive
make clean
make source

# Build the package
fakeroot dpkg-buildpackage -A

gpg -ba ../${APP}_${VERSION}-1_${ARCH_TYPE}.deb
gpg -ba ../${APP}_${VERSION}.orig.tar.gz
