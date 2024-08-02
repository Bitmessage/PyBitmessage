#!/bin/bash

RELEASE_ARTIFACT=$(grep release_artifact packages/android/buildozer.spec |cut -d= -f2|tr -Cd 'a-z')

if [ $RELEASE_ARTIFACT = "aab" ]; then
	exit
fi

unzip -p packages/android/bin/*.apk assets/private.tar \
    | tar --list -z > package.list
cat package.list
cat package.list | grep '\.sql$' || exit 1
