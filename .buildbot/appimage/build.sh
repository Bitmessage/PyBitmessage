#!/bin/bash

export APPIMAGE_EXTRACT_AND_RUN=1
BUILDER=appimage-builder-x86_64.AppImage
RECIPE=packages/AppImage/AppImageBuilder.yml

export APP_VERSION=$(git describe --tags | cut -d- -f1,3 | tr -d v)

function set_sourceline {
    if [ ${ARCH} == amd64 ]; then
	export SOURCELINE="deb http://archive.ubuntu.com/ubuntu/ bionic main universe"
    else
	export SOURCELINE="deb [arch=${ARCH}] http://ports.ubuntu.com/ubuntu-ports/ bionic main universe"
    fi
}

[ -f ${BUILDER} ] || wget -qO ${BUILDER} \
    https://github.com/AppImageCrafters/appimage-builder/releases/download/v1.1.0/appimage-builder-1.1.0-x86_64.AppImage \
    && chmod +x ${BUILDER}


export ARCH=amd64
export APPIMAGE_ARCH=x86_64
export RUNTIME=${APPIMAGE_ARCH}
set_sourceline

./${BUILDER} --recipe ${RECIPE} || exit 1

export ARCH=armhf
export APPIMAGE_ARCH=${ARCH}
export RUNTIME=gnueabihf
export CC=arm-linux-gnueabihf-gcc
export CXX=${CC}
set_sourceline

./${BUILDER} --recipe ${RECIPE} || exit 1

export ARCH=arm64
export APPIMAGE_ARCH=aarch64
export RUNTIME=${APPIMAGE_ARCH}
export CC=aarch64-linux-gnu-gcc
export CXX=${CC}
set_sourceline

./${BUILDER} --recipe ${RECIPE}

mkdir -p ../out
sha256sum PyBitmessage*.AppImage > ../out/SHA256SUMS
cp PyBitmessage*.AppImage ../out
