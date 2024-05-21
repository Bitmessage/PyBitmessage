FROM ubuntu:bionic

ENV DEBIAN_FRONTEND=noninteractive

RUN dpkg --add-architecture i386

RUN apt-get update

RUN apt-get install -yq --no-install-suggests --no-install-recommends \
    software-properties-common build-essential libcap-dev libffi-dev \
    libssl-dev python-all-dev python-setuptools xvfb \
    mingw-w64 wine-stable winetricks wine32 wine64

ADD . .
