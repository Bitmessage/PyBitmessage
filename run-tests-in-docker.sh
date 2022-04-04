#!/bin/sh

DOCKERFILE=packages/docker/Dockerfile.bionic

# explicitly mark appimage stage because it builds in any case
docker build --target appimage -t pybm/appimage -f $DOCKERFILE .

if [ $? -gt 0 ]; then
    docker build --no-cache --target appimage -t pybm/appimage -f $DOCKERFILE .
fi

docker build --target tox -t pybm/tox -f $DOCKERFILE .
docker run --rm -t pybm/tox
