#!/bin/sh

tox -e lint-basic # || exit 1
tox -e py310
