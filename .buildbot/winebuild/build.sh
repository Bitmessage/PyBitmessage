#!/bin/sh

xvfb-run -a buildscripts/winbuild.sh || exit 1

mkdir -p ../out
mv packages/pyinstaller/dist/*.exe ../out
