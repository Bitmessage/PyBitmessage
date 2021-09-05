#!/bin/bash

docker build -t pybm-travis-bionic -f packages/docker/Dockerfile.travis .
docker run pybm-travis-bionic
