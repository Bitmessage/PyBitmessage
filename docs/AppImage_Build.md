# PyBitmessage AppImage Build instructions

## Requirements
First make sure you have `dpkg` and `appimagetool` installed.
From packages/AppImage/ Dir run `install.sh` to install the appimagetool.
```
./install.sh
```

## Build and Install

This script requires PyBitmessage .deb package.
Download the latest version from https://storage.bitmessage.org/binaries/

Once you have downloaded the package and have `dpkg` and `appimagetool` installed:

You can start to build the appimage

### Clone the source code
```
git clone git://github.com/Bitmessage/PyBitmessage.git
```
This will install the base app to your local flatpak user repository, it 
takes a while to compile because QT4 and PyQt4 have to be build, among others. But this is only required once.

### Build

Run build.sh
Usage:  ./build.sh "path to deb package"
Example  ./build.sh ~/Downloads/pybitmessage_0.6.3.2-1_amd64.deb 

```
cd PyBitmessage/packages/AppImage
./build.sh ~/Downloads/pybitmessage_0.6.3.2-1_amd64.deb 
```

# Run
```
./PyBitmessage-x86_64.AppImage
```

## Cleanup
The script performs a cleanup, deletes the intermediate AppDir & tmp files.