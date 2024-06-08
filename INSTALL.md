# PyBitmessage Installation Instructions
- Binary (64bit, no separate installation of dependencies required)
    - Windows: https://artifacts.bitmessage.at/winebuild/
    - Linux AppImages: https://artifacts.bitmessage.at/appimage/
    - Linux snaps: https://artifacts.bitmessage.at/snap/
    - Mac (not up to date): https://github.com/Bitmessage/PyBitmessage/releases/tag/v0.6.1
- Source
    `git clone git://github.com/Bitmessage/PyBitmessage.git`

## Notes on the AppImages

The [AppImage](https://docs.appimage.org/introduction/index.html)
is a bundle, built by the
[appimage-builder](https://github.com/AppImageCrafters/appimage-builder) from
the Ubuntu Bionic deb files, the sources and `bitmsghash.so`, precompiled for
3 architectures, using the `packages/AppImage/AppImageBuilder.yml` recipe.

When you run the appimage the bundle is loop mounted to a location like
`/tmp/.mount_PyBitm97wj4K` with `squashfs-tools`.

The appimage name has several informational filds:
```
PyBitmessage-<VERSION>-g<COMMITHASH>[-alpha]-<ARCH>.AppImage
```

E.g. `PyBitmessage-0.6.3.2-ge571ba8a-x86_64.AppImage` is an appimage, built from
the `v0.6` for x86_64 and `PyBitmessage-0.6.3.2-g9de2aaf1-alpha-aarch64.AppImage`
is one, built from some development branch for arm64.

You can also build the appimage with local code. For that you need installed
docker:

```
$ docker build -t bm-appimage -f .buildbot/appimage/Dockerfile .
$ docker run -t --rm -v "$(pwd)"/dist:/out bm-appimage .buildbot/appimage/build.sh
```

The appimages should be in the dist dir.


## Helper Script for building from source
Go to the directory with PyBitmessage source code and run:
```
python checkdeps.py
```
If there are missing dependencies, it will explain you what is missing
and for many Unix-like systems also what you have to do to resolve it. You need
to repeat calling the script until you get nothing mandatory missing. How you
then run setuptools depends on whether you want to install it to
user's directory or system.

### If checkdeps fails, then verify manually which dependencies are missing from below
Before running PyBitmessage, make sure you have all the necessary dependencies
installed on your system.

These dependencies may not be available on a recent OS and PyBitmessage may not
build on such systems. Here's a list of dependencies needed for PyBitmessage
based on operating system

For Debian-based (Ubuntu, Raspbian, PiBang, others)
```
python2.7 openssl libssl-dev python-msgpack python-qt4 python-six
```
For Arch Linux
```
python2 openssl python2-pyqt4 python-six
```
For Fedora
```
python python-qt4 openssl-compat-bitcoin-libs python-six
```
For Red Hat Enterprise Linux (RHEL)
```
python python-qt4 openssl-compat-bitcoin-libs python-six
```
For GNU Guix
```
python2-msgpack python2-pyqt@4.11.4 python2-sip openssl python-six
```

## setuptools
This is now the recommended and in most cases the easiest way for
installing PyBitmessage.

There are 2 options for installing with setuptools: root and user.

### as root:
```
python setup.py install
pybitmessage
```

### as user:
```
python setup.py install --user
~/.local/bin/pybitmessage
```

## pip venv (daemon):
Create virtualenv with Python 2.x version
```
virtualenv -p python2 env
```

Activate env
```
source env/bin/activate
```

Build & run pybitmessage
```
pip install .
pybitmessage -d
```

## Alternative way to run PyBitmessage, without setuptools (this isn't recommended)
run `./start.sh`.
