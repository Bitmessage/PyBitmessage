# A container for buildbot
FROM ubuntu:focal AS kivy

ENV DEBIAN_FRONTEND=noninteractive

ENV SKIPCACHE=2022-08-29

RUN apt-get update

RUN apt-get install -yq \
    build-essential libcap-dev libssl-dev \
    libmtdev-dev libpq-dev \
    python3-dev python3-pip python3-virtualenv \
    xvfb ffmpeg xclip xsel

RUN ln -sf /usr/bin/python3 /usr/bin/python

RUN pip3 install --upgrade setuptools pip
