#!/bin/bash

pushd packages && snapcraft || exit 1

popd
mkdir -p ../out
mv packages/pybitmessage*.snap ../out
cd ../out
sha256sum pybitmessage*.snap > SHA256SUMS
