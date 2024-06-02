#!/bin/sh

DOCKERFILE=.buildbot/tox-bionic/Dockerfile

docker build -t pybm/tox -f $DOCKERFILE .

if [ $? -gt 0 ]; then
    docker build --no-cache -t pybm/tox -f $DOCKERFILE .
fi

docker run --rm -it pybm/tox
