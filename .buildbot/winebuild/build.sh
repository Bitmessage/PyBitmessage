#!/bin/sh

xvfb-run -a buildscripts/winbuild.sh

mkdir -p ../out
mv packages/pyinstaller/dist/*.exe ../out
