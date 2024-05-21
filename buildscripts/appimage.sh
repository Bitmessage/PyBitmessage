#!/bin/bash

# Cleanup
rm -rf PyBitmessage
export VERSION=$(python setup.py --version)

[ -f "pkg2appimage" ] || wget -O "pkg2appimage" https://github.com/AppImage/pkg2appimage/releases/download/continuous/pkg2appimage-1807-x86_64.AppImage
chmod a+x pkg2appimage

echo "Building AppImage"

if grep docker /proc/1/cgroup; then
    export APPIMAGE_EXTRACT_AND_RUN=1
    mkdir PyBitmessage
    wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage -O PyBitmessage/appimagetool \
    && chmod +x PyBitmessage/appimagetool
fi

./pkg2appimage packages/AppImage/PyBitmessage.yml

./pkg2appimage --appimage-extract

. ./squashfs-root/usr/share/pkg2appimage/functions.sh

GLIBC=$(glibc_needed)

VERSION_EXPANDED=${VERSION}.glibc${GLIBC}-${SYSTEM_ARCH}

if [ -f "out/PyBitmessage-${VERSION_EXPANDED}.AppImage" ]; then
    echo "Build Successful";
    echo "Run out/PyBitmessage-${VERSION_EXPANDED}.AppImage";
    out/PyBitmessage-${VERSION_EXPANDED}.AppImage -t
else
    echo "Build Failed";
    exit 1
fi
