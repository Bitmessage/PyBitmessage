#!/bin/sh

xvfb-run -a buildscripts/winbuild.sh || exit 1

mkdir -p ../out
mv packages/pyinstaller/dist/Bitmessage*.exe ../out
cd ../out
sha256sum Bitmessage*.exe > SHA256SUMS
