#!/bin/bash

docker build -t pybm-kivy-travis-bionic -f packages/docker/Dockerfile.kivy-travis .
docker run pybm-kivy-travis-bionic
