#!/bin/bash

docker build -t pybm-travis-bionic -f Dockerfile.travis .
docker run pybm-travis-bionic
