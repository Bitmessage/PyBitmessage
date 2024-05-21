#!/bin/bash
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
pushd packages/android
buildozer android debug || exit $?
popd

mkdir -p ../out
cp packages/android/bin/*.apk ../out
