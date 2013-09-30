#!/bin/bash

APP=pybitmessage
PREV_VERSION=0.4.1
VERSION=0.4.1
RELEASE=1
ARCH_TYPE=`uname -m`
BUILDDIR=~/slackbuild
CURRDIR=`pwd`
PROJECTDIR=${BUILDDIR}/${APP}-${VERSION}-${RELEASE}

# Update version numbers automatically - so you don't have to
sed -i 's/VERSION='${PREV_VERSION}'/VERSION='${VERSION}'/g' Makefile debian.sh rpm.sh arch.sh puppy.sh ebuild.sh
sed -i 's/Version: '${PREV_VERSION}'/Version: '${VERSION}'/g' rpmpackage/${APP}.spec
sed -i 's/Release: '${RELEASE}'/Release: '${RELEASE}'/g' rpmpackage/${APP}.spec
sed -i 's/pkgrel='${RELEASE}'/pkgrel='${RELEASE}'/g' archpackage/PKGBUILD
sed -i 's/pkgver='${PREV_VERSION}'/pkgver='${VERSION}'/g' archpackage/PKGBUILD
sed -i "s/-${PREV_VERSION}-/-${VERSION}-/g" puppypackage/*.specs
sed -i "s/|${PREV_VERSION}|/|${VERSION}|/g" puppypackage/*.specs
sed -i 's/VERSION='${PREV_VERSION}'/VERSION='${VERSION}'/g' puppypackage/pinstall.sh puppypackage/puninstall.sh
sed -i 's/-'${PREV_VERSION}'.so/-'${VERSION}'.so/g' debian/*.links


# Make directories within which the project will be built
mkdir -p ${BUILDDIR}
mkdir -p ${PROJECTDIR}

# Build the project
make clean
make
make install -B DESTDIR=${PROJECTDIR} PREFIX=/usr

# Copy the slack-desc and doinst.sh files into the build install directory
mkdir ${PROJECTDIR}/install
cp ${CURRDIR}/slackpackage/slack-desc ${PROJECTDIR}/install
cp ${CURRDIR}/slackpackage/doinst.sh ${PROJECTDIR}/install

# Compress the build directory
cd ${BUILDDIR}
tar -c -f ${APP}-${VERSION}-${RELEASE}.tar .
sync
xz ${APP}-${VERSION}-${RELEASE}.tar
sync
mv ${APP}-${VERSION}-${RELEASE}.tar.xz ${CURRDIR}/slackpackage/${APP}-${VERSION}-${ARCH_TYPE}-${RELEASE}.txz
cd ${CURRDIR}

# Remove the temporary build directory
rm -fr ${BUILDDIR}
