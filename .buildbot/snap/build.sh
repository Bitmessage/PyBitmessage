#!/bin/sh

cd packages && snapcraft

cd ..
mkdir -p ../out
mv packages/pybitmessage*.snap ../out
