#!/bin/bash

unzip -p packages/android/bin/*.apk assets/private.tar \
    | tar --list -z > package.list
cat package.list
cat package.list | grep '\.sql$' || exit 1
