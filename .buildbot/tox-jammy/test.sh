#!/bin/sh

tox -e lint || exit 1
tox -e py310
