#!/bin/bash

APP=pybitmessage
PREV_VERSION=0.4.1
VERSION=0.4.1
RELEASE=1
BUILDDIR=~/petbuild
CURRDIR=`pwd`
PROJECTDIR=${BUILDDIR}/${APP}-${VERSION}-${RELEASE}

# Update version numbers automatically - so you don't have to
sed -i 's/VERSION='${PREV_VERSION}'/VERSION='${VERSION}'/g' Makefile debian.sh rpm.sh arch.sh ebuild.sh slack.sh
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

# Alter the desktop file categories
sed -i "s/Categories=Office;Email;/Categories=Internet;mailnews;/g" ${PROJECTDIR}/usr/share/applications/${APP}.desktop

# Create directories specific to puppy
mkdir ${PROJECTDIR}/usr
mkdir ${PROJECTDIR}/usr/local
mkdir ${PROJECTDIR}/usr/local/bin

# Copy anything in /usr/bin into /usr/local/bin
cp ${PROJECTDIR}/usr/bin/* ${PROJECTDIR}/usr/local/bin/

# Copy the spec file into the build directory
cp ${CURRDIR}/puppypackage/${APP}-${VERSION}.pet.specs ${PROJECTDIR}

# Copy the XPM mini icon into the build directory
cp ${CURRDIR}/desktop/icon14.xpm ${PROJECTDIR}/${APP}.xpm

# Compress the build directory
cd ${BUILDDIR}
tar -c -f ${APP}-${VERSION}-${RELEASE}.tar .
sync
gzip ${APP}-${VERSION}-${RELEASE}.tar
mv ${APP}-${VERSION}-${RELEASE}.tar.gz ${CURRDIR}/puppypackage
cd ${CURRDIR}/puppypackage

# Create the PET package
MD5SUM="`md5sum ${APP}-${VERSION}-${RELEASE}.tar.gz | cut -f 1 -d ' '`"
echo -n "$MD5SUM" >> ${APP}-${VERSION}-${RELEASE}.tar.gz
sync
mv -f ${APP}-${VERSION}-${RELEASE}.tar.gz ${APP}-${VERSION}-${RELEASE}.pet
sync
cd ${CURRDIR}

# Remove the temporary build directory
rm -fr ${BUILDDIR}
