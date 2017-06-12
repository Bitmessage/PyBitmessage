#!/usr/bin/env python2.7

import os
import sys
try:
    from setuptools import setup, Extension
    from setuptools.command.install import install
    haveSetuptools = True
except ImportError:
    install = object
    haveSetuptools = False

from importlib import import_module

from src.version import softwareVersion

packageManager = {
    "OpenBSD": "pkg_add",
    "FreeBSD": "pkg install",
    "Debian": "apt-get install",
    "Ubuntu": "apt-get install",
    "Ubuntu 12": "apt-get install",
    "openSUSE": "zypper install",
    "Fedora": "dnf install",
    "Guix": "guix package -i",
    "Gentoo": "emerge"
}

packageName = {
    "PyQt4": {
        "OpenBSD": "py-qt4",
        "FreeBSD": "py27-qt4",
        "Debian": "python-qt4",
        "Ubuntu": "python-qt4",
        "Ubuntu 12": "python-qt4",
        "openSUSE": "python-qt",
        "Fedora": "PyQt4",
        "Guix": "python2-pyqt@4.11.4",
        "Gentoo": "dev-python/PyQt4",
        'optional': True,
        'description': "You only need PyQt if you want to use the GUI. " \
            "When only running as a daemon, this can be skipped.\n" \
            "However, you would have to install it manually " \
            "because setuptools does not support PyQt."
    },
    "msgpack": {
        "OpenBSD": "py-msgpack",
        "FreeBSD": "py27-msgpack-python",
        "Debian": "python-msgpack",
        "Ubuntu": "python-msgpack",
        "Ubuntu 12": "msgpack-python",
        "openSUSE": "python-msgpack-python",
        "Fedora": "python2-msgpack",
        "Guix": "python2-msgpack",
        "Gentoo": "dev-python/msgpack",
        "optional": True,
        "description": "python-msgpack is recommended for messages coding"
    },
    "umsgpack": {
        "FreeBSD": "",
        "OpenBSD": "",
        "Fedora": "",
        "openSUSE": "",
        "Guix": "",
        "Ubuntu 12": "",
        "Debian": "python-u-msgpack",
        "Ubuntu": "python-u-msgpack",
        "Gentoo": "dev-python/u-msgpack",
        "optional": True,
        "description": "umsgpack can be used instead of msgpack"
    },
    "pyopencl": {
        "FreeBSD": "py27-pyopencl",
        "Debian": "python-pyopencl",
        "Ubuntu": "python-pyopencl",
        "Ubuntu 12": "python-pyopencl",
        "Fedora": "python2-pyopencl",
        "openSUSE": "",
        "OpenBSD": "",
        "Guix": "",
        "Gentoo": "dev-python/pyopencl",
        "optional": True,
        'description': "If you install pyopencl, you will be able to use " \
            "GPU acceleration for proof of work. \n" \
            "You also need a compatible GPU and drivers."
    },
    "setuptools": {
        "OpenBSD": "py-setuptools",
        "FreeBSD": "py27-setuptools",
        "Debian": "python-setuptools",
        "Ubuntu": "python-setuptools",
        "Ubuntu 12": "python-setuptools",
        "Fedora": "python2-setuptools",
        "openSUSE": "python-setuptools",
        "Guix": "python2-setuptools",
        "Gentoo": "",
    }
}

compiling = {
        "Debian": "build-essential libssl-dev",
        "Ubuntu": "build-essential libssl-dev",
        "Fedora": "gcc-c++ redhat-rpm-config python-devel openssl-devel",
        "openSUSE": "gcc-c++ libopenssl-devel python-devel",
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
        with open("/etc/os-release", 'r') as osRelease:
            version = None
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
                if line.startswith("VERSION_ID="):
                    try:
                        version = float(line.split("\"")[1])
                    except ValueError:
                        pass
            if detectOS.result == "Ubuntu" and version < 14:
                detectOS.result = "Ubuntu 12"
    elif os.path.isfile("/etc/config.scm"):
        detectOS.result = "Guix"
    return detectOS.result


def detectPrereqs(missing=True):
    available = []
    for module in packageName.keys():
        try:
            import_module(module)
            if not missing:
                available.append(module)
        except ImportError:
            if missing:
                available.append(module)
    return available


def prereqToPackages():
    print "You can install the requirements by running, as root:"
    print "%s %s" % (
        packageManager[detectOS()], " ".join(
            packageName[x][detectOS()] for x in detectPrereqs()))
    for package in detectPrereqs():
        if packageName[package].get('optional'):
            print packageName[package].get('description')


def compilerToPackages():
    if not detectOS() in compiling:
        return
    print "You can install the requirements by running, as root:"
    print "%s %s" % (
        packageManager[detectOS.result], compiling[detectOS.result])


class InstallCmd(install):
    def run(self):
        detectOS.result = None
        prereqs = detectPrereqs()
        if prereqs and detectOS() in packageManager:
            print "It looks like you're using %s. " \
                "It is highly recommended to use the package manager " \
                "instead of setuptools." % (detectOS.result)
            prereqToPackages()
            try:
                for module in prereqs:
                    if not packageName[module]['optional']:
                        sys.exit()
            except KeyError:
                sys.exit()

            if not haveSetuptools:
                print "It looks like you're missing setuptools."
                sys.exit()

        if prereqs and sys.stdin.isatty():
            print "Press Return to continue"
            try:
                raw_input()
            except (EOFError, NameError):
                pass

        return install.run(self)


if __name__ == "__main__":
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'README.md')) as f:
        README = f.read()

    bitmsghash = Extension(
        'pybitmessage.bitmsghash.bitmsghash',
        sources=['src/bitmsghash/bitmsghash.cpp'],
        libraries=['pthread', 'crypto'],
    )

    installRequires = []
    packages = [
        'pybitmessage',
        'pybitmessage.bitmessageqt',
        'pybitmessage.bitmessagecurses',
        'pybitmessage.messagetypes',
        'pybitmessage.network',
        'pybitmessage.pyelliptic',
        'pybitmessage.socks',
        'pybitmessage.storage',
        'pybitmessage.plugins'
    ]
    # this will silently accept alternative providers of msgpack
    # if they are already installed
    if "msgpack" in detectPrereqs():
        installRequires.append("msgpack-python")
    elif "umsgpack" in detectPrereqs():
        installRequires.append("umsgpack")
    else:
        packages += ['pybitmessage.fallback', 'pybitmessage.fallback.umsgpack']

    try:
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
            install_requires=installRequires,
            extras_require={
                'qrcode': ['qrcode'],
                'pyopencl': ['pyopencl']
            },
            classifiers=[
                "License :: OSI Approved :: MIT License"
                "Operating System :: OS Independent",
                "Programming Language :: Python :: 2.7 :: Only",
                "Topic :: Internet",
                "Topic :: Security :: Cryptography",
                "Topic :: Software Development :: Libraries :: Python Modules",
            ],
            package_dir={'pybitmessage': 'src'},
            packages=packages,
            package_data={'': [
                'bitmessageqt/*.ui', 'bitmsghash/*.cl', 'sslkeys/*.pem',
                'translations/*.ts', 'translations/*.qm',
                'images/*.png', 'images/*.ico', 'images/*.icns'
            ]},
            ext_modules=[bitmsghash],
            zip_safe=False,
            entry_points={
                'gui.menu': [
                    'popMenuYourIdentities.qrcode = '
                    'pybitmessage.plugins.qrcodeui [qrcode]'
                ],
            #    'console_scripts': [
            #        'pybitmessage = pybitmessage.bitmessagemain:main'
            #    ]
            },
            scripts=['src/pybitmessage'],
            cmdclass={'install': InstallCmd}
        )
    except SystemExit as err:
        print err.message
    except:
        print "It looks like building the package failed.\n" \
            "You may be missing a C++ compiler and the OpenSSL headers."
        compilerToPackages()
