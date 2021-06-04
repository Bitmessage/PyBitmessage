#!/bin/sh

# Cleanup
rm -rf PyBitmessage
export VERSION=$(python setup.py --version)

[ -f "pkg2appimage" ] || wget -O "pkg2appimage" https://github.com/AppImage/pkg2appimage/releases/download/continuous/pkg2appimage-1807-x86_64.AppImage
chmod a+x pkg2appimage

echo "Building AppImage"

./pkg2appimage packages/AppImage/PyBitmessage.yml


if [ -f "out/PyBitmessage-${VERSION}.glibc2.15-x86_64.AppImage" ]; then
    echo "Build Successful";
    echo "Run out/PyBitmessage-${VERSION}.glibc2.15-x86_64.AppImage"
else
    echo "Build Failed"
fi
