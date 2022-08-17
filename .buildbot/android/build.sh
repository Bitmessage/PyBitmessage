#!/bin/sh
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
cd packages/android
buildozer android debug || exit $?
cd ../..
mkdir -p ../out
mv packages/android/bin/*.apk ../out