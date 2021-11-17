#!/bin/bash

docker build -t pybm-test -f packages/docker/Dockerfile.bionic .
docker run pybm-test
