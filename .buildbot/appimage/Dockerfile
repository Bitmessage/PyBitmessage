FROM ubuntu:bionic

RUN apt-get update

RUN apt-get install -yq --no-install-suggests --no-install-recommends \
    ca-certificates software-properties-common \
    build-essential libcap-dev libssl-dev \
    python-all-dev python-setuptools wget \
    git gtk-update-icon-cache \
    binutils-multiarch crossbuild-essential-armhf

RUN dpkg --add-architecture armhf

RUN sed -iE "s|deb |deb [arch=amd64] |g" /etc/apt/sources.list \
    && echo "deb [arch=armhf] http://ports.ubuntu.com/ubuntu-ports/ bionic main universe" >> /etc/apt/sources.list \
    && echo "deb [arch=armhf] http://ports.ubuntu.com/ubuntu-ports/ bionic-updates main universe" >> /etc/apt/sources.list

RUN apt-get update | true

RUN apt-get install -yq libssl-dev:armhf

RUN wget -qO appimage-builder-x86_64.AppImage \
    https://github.com/AppImageCrafters/appimage-builder/releases/download/v1.1.0/appimage-builder-1.1.0-x86_64.AppImage

ADD . .
