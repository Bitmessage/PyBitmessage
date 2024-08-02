#!/bin/bash
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

# buildozer OOM workaround
mkdir -p ~/.gradle
echo "org.gradle.jvmargs=-Xmx2g -XX:MaxMetaspaceSize=512m -XX:+HeapDumpOnOutOfMemoryError -Dfile.encoding=UTF-8" \
    > ~/.gradle/gradle.properties

# workaround for symlink
rm -rf src/pybitmessage
mkdir -p src/pybitmessage
cp src/*.py src/pybitmessage
cp -r src/bitmessagekivy src/backend src/mockbm src/pybitmessage

pushd packages/android

BUILDMODE=debug

if [ "$BUILDBOT_JOBNAME" = "android" -a \
     "$BUILDBOT_REPOSITORY" = "https://github.com/Bitmessage/PyBitmessage" -a \
     "$BUILDBOT_BRANCH" = "v0.6" ]; then
   sed -e 's/android.release_artifact *=.*/release_artifact = aab/' -i "" buildozer.spec
   BUILDMODE=release
fi 

buildozer android $BUILDMODE || exit $?
popd

mkdir -p ../out
RELEASE_ARTIFACT=$(grep release_artifact packages/android/buildozer.spec |cut -d= -f2|tr -Cd 'a-z')
cp packages/android/bin/*.${RELEASE_ARTIFACT} ../out
