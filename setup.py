#!/usr/bin/env python2.7

import os
import sys
try:
    from setuptools import setup, Extension
    haveSetuptools = True
except ImportError:
    haveSetuptools = False

from importlib import import_module

from src.version import softwareVersion

packageManager = {
    "OpenBSD": "pkg_add",
    "FreeBSD": "pkg install",
    "Debian": "apt-get install",
    "Ubuntu": "apt-get install",
    "openSUSE": "zypper install",
    "Fedora": "dnf install",
    "Guix": "guix package -i",
    "Gentoo": "emerge"
}

packageName = {
    "PyQt": {
        "OpenBSD": "py-qt4",
        "FreeBSD": "py27-qt4",
        "Debian": "python-qt4",
        "Ubuntu": "python-qt4",
        "openSUSE": "python-qt",
        "Fedora": "PyQt4",
        "Guix": "python2-pyqt@4.11.4",
        "Gentoo": "dev-python/PyQt4"
    },
    "msgpack": {
        "OpenBSD": "py-msgpack",
        "FreeBSD": "py27-msgpack-python",
        "Debian": "python-msgpack",
        "Ubuntu": "python-msgpack",
        "openSUSE": "python-msgpack-python",
        "Fedora": "python2-msgpack",
        "Guix": "python2-msgpack",
        "Gentoo": "dev-python/msgpack"
    },
    "pyopencl": {
        "FreeBSD": "py27-pyopencl",
        "Debian": "python-pyopencl",
        "Ubuntu": "python-pyopencl",
        "Fedora": "python2-pyopencl",
        "Gentoo": "dev-python/pyopencl"
    }
}


def detectOS():
    if detectOS.result is not None:
        return detectOS.result
    if sys.platform.startswith('openbsd'):
        detectOS.result = "OpenBSD"
    elif sys.platform.startswith('freebsd'):
        detectOS.result = "FreeBSD"
    elif sys.platform.startswith('win'):
        detectOS.result = "Windows"
    elif os.path.isfile("/etc/os-release"):
        with open("/etc/os-release", 'rt') as osRelease:
            for line in osRelease:
                if line.startswith("NAME="):
                    line = line.lower()
                    if "fedora" in line:
                        detectOS.result = "Fedora"
                    elif "opensuse" in line:
                        detectOS.result = "openSUSE"
                    elif "ubuntu" in line:
                        detectOS.result = "Ubuntu"
                    elif "debian" in line:
                        detectOS.result = "Debian"
                    elif "gentoo" in line or "calculate" in line:
                        detectOS.result = "Gentoo"
                    else:
                        detectOS.result = None
    elif os.path.isfile("/etc/config.scm"):
        detectOS.result = "Guix"
    return detectOS.result


def detectPrereqs(missing=False):
    available = []
    try:
        import_module("PyQt4.QtCore")
        if not missing:
            available.append("PyQt")
    except ImportError:
        if missing:
            available.append("PyQt")
    try:
        import_module("msgpack")
        if not missing:
            available.append("msgpack")
    except ImportError:
        if missing:
            available.append("msgpack")
    try:
        import_module("pyopencl")
        if not missing:
            available.append("pyopencl")
    except ImportError:
        if missing:
            available.append("pyopencl")
    return available


def prereqToPackages():
    print "You can install the requirements by running, as root:"
    print "%s %s" % (
        packageManager[detectOS()], " ".join(
            packageName[x][detectOS()] for x in detectPrereqs(True)))


if __name__ == "__main__":
    detectOS.result = None
    detectPrereqs.result = None
    if "PyQt" in detectPrereqs(True):
        print "You only need PyQt if you want to use the GUI. " \
            "When only running as a daemon, this can be skipped.\n" \
            "However, you would have to install it manually " \
            "because setuptools does not support pyqt."
    if detectPrereqs(True) != [] and detectOS() in packageManager:
        if detectOS() is not None:
            print "It looks like you're using %s. " \
                "It is highly recommended to use the package manager " \
                "instead of setuptools." % (detectOS())
            prereqToPackages()
            sys.exit()
    if not haveSetuptools:
        print "It looks like you're missing setuptools."
        sys.exit()

    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'README.md')) as f:
        README = f.read()

    bitmsghash = Extension(
        'pybitmessage.bitmsghash.bitmsghash',
        sources=['src/bitmsghash/bitmsghash.cpp'],
        libraries=['pthread', 'crypto'],
    )

    dist = setup(
        name='pybitmessage',
        version=softwareVersion,
        description="Reference client for Bitmessage: "
        "a P2P communications protocol",
        long_description=README,
        license='MIT',
        # TODO: add author info
        #author='',
        #author_email='',
        url='https://bitmessage.org',
        # TODO: add keywords
        #keywords='',
        install_requires=['msgpack-python'],
        classifiers=[
            "License :: OSI Approved :: MIT License"
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 2.7 :: Only",
            "Topic :: Internet",
            "Topic :: Security :: Cryptography",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ],
        package_dir={'pybitmessage': 'src'},
        packages=[
            'pybitmessage',
            'pybitmessage.bitmessageqt',
            'pybitmessage.bitmessagecurses',
            'pybitmessage.messagetypes',
            'pybitmessage.network',
            'pybitmessage.pyelliptic',
            'pybitmessage.socks',
        ],
        package_data={'': [
            'bitmessageqt/*.ui', 'bitmsghash/*.cl', 'sslkeys/*.pem',
            'translations/*.ts', 'translations/*.qm',
            'images/*.png', 'images/*.ico', 'images/*.icns'
        ]},
        ext_modules=[bitmsghash],
        zip_safe=False,
        #entry_points={
        #    'console_scripts': [
        #        'pybitmessage = pybitmessage.bitmessagemain:main'
        #    ]
        #},
        scripts=['src/pybitmessage']
    )
