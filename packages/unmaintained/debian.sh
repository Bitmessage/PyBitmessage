#!/bin/bash

APP=pybitmessage
PREV_VERSION=0.4.4
VERSION=0.6.0
RELEASE=1
ARCH_TYPE=all
DIR=${APP}-${VERSION}
CURDIR=`pwd`
SHORTDIR=`basename ${CURDIR}`

if [ $ARCH_TYPE == "x86_64" ]; then
    ARCH_TYPE="amd64"
fi
if [ $ARCH_TYPE == "i686" ]; then
    ARCH_TYPE="i386"
fi


# Update version numbers automatically - so you don't have to
sed -i 's/VERSION='${PREV_VERSION}'/VERSION='${VERSION}'/g' Makefile rpm.sh arch.sh puppy.sh ebuild.sh slack.sh
sed -i 's/Version: '${PREV_VERSION}'/Version: '${VERSION}'/g' rpmpackage/${APP}.spec
sed -i 's/Release: '${RELEASE}'/Release: '${RELEASE}'/g' rpmpackage/${APP}.spec
sed -i 's/pkgrel='${RELEASE}'/pkgrel='${RELEASE}'/g' archpackage/PKGBUILD
sed -i 's/pkgver='${PREV_VERSION}'/pkgver='${VERSION}'/g' archpackage/PKGBUILD
sed -i "s/-${PREV_VERSION}-/-${VERSION}-/g" puppypackage/*.specs
sed -i "s/|${PREV_VERSION}|/|${VERSION}|/g" puppypackage/*.specs
sed -i 's/VERSION='${PREV_VERSION}'/VERSION='${VERSION}'/g' puppypackage/pinstall.sh puppypackage/puninstall.sh
sed -i 's/-'${PREV_VERSION}'.so/-'${VERSION}'.so/g' debian/*.links

make clean
make

# Change the parent directory name to Debian format
mv ../${SHORTDIR} ../${DIR}

# Create a source archive
make sourcedeb

# Build the package
dpkg-buildpackage -F -us -uc

# Sign files
gpg -ba ../${APP}_${VERSION}-1_${ARCH_TYPE}.deb
gpg -ba ../${APP}_${VERSION}.orig.tar.gz

# Restore the parent directory name
mv ../${DIR} ../${SHORTDIR}
