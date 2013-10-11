#!/bin/bash

APP=pybitmessage
PREV_VERSION=0.4.1
VERSION=0.4.1
RELEASE=1
ARCH_TYPE=any
CURRDIR=`pwd`
SOURCE=archpackage/${APP}-${VERSION}.tar.gz

# Update version numbers automatically - so you don't have to
sed -i 's/VERSION='${PREV_VERSION}'/VERSION='${VERSION}'/g' Makefile debian.sh rpm.sh puppy.sh ebuild.sh slack.sh
sed -i 's/Version: '${PREV_VERSION}'/Version: '${VERSION}'/g' rpmpackage/${APP}.spec
sed -i 's/Release: '${RELEASE}'/Release: '${RELEASE}'/g' rpmpackage/${APP}.spec
sed -i 's/pkgrel='${RELEASE}'/pkgrel='${RELEASE}'/g' archpackage/PKGBUILD
sed -i 's/pkgver='${PREV_VERSION}'/pkgver='${VERSION}'/g' archpackage/PKGBUILD
sed -i "s/-${PREV_VERSION}-/-${VERSION}-/g" puppypackage/*.specs
sed -i "s/|${PREV_VERSION}|/|${VERSION}|/g" puppypackage/*.specs
sed -i 's/VERSION='${PREV_VERSION}'/VERSION='${VERSION}'/g' puppypackage/pinstall.sh puppypackage/puninstall.sh
sed -i 's/-'${PREV_VERSION}'.so/-'${VERSION}'.so/g' debian/*.links


# Create the source code
make clean
rm -f archpackage/*.gz

# having the root directory called name-version seems essential
mv ../${APP} ../${APP}-${VERSION}
tar -cvzf ${SOURCE} ../${APP}-${VERSION} --exclude-vcs

# rename the root directory without the version number
mv ../${APP}-${VERSION} ../${APP}

# calculate the MD5 checksum
CHECKSM=$(md5sum ${SOURCE})
sed -i "s/md5sums[^)]*)/md5sums=(${CHECKSM%% *})/g" archpackage/PKGBUILD

cd archpackage

# Create the package
tar -c -f ${APP}-${VERSION}.pkg.tar .
sync
xz ${APP}-${VERSION}.pkg.tar
sync

# Move back to the original directory
cd ${CURRDIR}

