#!/bin/bash

docker build --target travis -t pybm -f packages/docker/Dockerfile.bionic .
docker run pybm

