#!/bin/bash

git remote add -f upstream https://github.com/Bitmessage/PyBitmessage.git
HEAD="$(git rev-parse HEAD)"
UPSTREAM="$(git merge-base --fork-point upstream/v0.6)"
SNAP_DIFF="$(git diff upstream/v0.6 -- packages/snap .buildbot/snap)"

[ -z "${SNAP_DIFF}" ] && [ $HEAD != $UPSTREAM ] && exit 0

pushd packages && snapcraft || exit 1

popd
mkdir -p ../out
mv packages/pybitmessage*.snap ../out
cd ../out
sha256sum pybitmessage*.snap > SHA256SUMS
