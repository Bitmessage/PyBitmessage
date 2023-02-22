#!/bin/sh

wget -O appimage-builder-x86_64.AppImage \
    https://github.com/AppImageCrafters/appimage-builder/releases/download/v1.1.0/appimage-builder-1.1.0-x86_64.AppImage \
    && chmod +x appimage-builder-x86_64.AppImage

APPIMAGE_EXTRACT_AND_RUN=1 ./appimage-builder-x86_64.AppImage \
			--recipe packages/AppImage/AppImageBuilder.yml

mkdir -p ../out
mv PyBitmessage*.AppImage ../out
