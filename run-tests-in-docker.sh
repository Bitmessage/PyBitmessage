#!/bin/bash

docker build -t pybm-test -f packages/docker/Dockerfile.bionic .
docker run --rm pybm-test
