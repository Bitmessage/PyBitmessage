"""Check dependendies and give recommendations about how to satisfy them"""

from distutils.errors import CompileError
try:
    from setuptools.dist import Distribution
    from setuptools.extension import Extension
    from setuptools.command.build_ext import build_ext
    HAVE_SETUPTOOLS = True
except ImportError:
    HAVE_SETUPTOOLS = False
from importlib import import_module
import os
import sys

PACKAGE_MANAGER = {
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

PACKAGES = {
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
        "description": "python-msgpack is recommended for improved performance of message encoding/decoding"
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
        "optional": False,
    }
}

COMPILING = {
    "Debian": "build-essential libssl-dev",
    "Ubuntu": "build-essential libssl-dev",
    "Fedora": "gcc-c++ redhat-rpm-config python-devel openssl-devel",
    "openSUSE": "gcc-c++ libopenssl-devel python-devel",
    "optional": False,
}

def detectOSRelease():
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
                    version = float(line.split("=")[1].replace("\"", ""))
                except ValueError:
                    pass
        if detectOS.result == "Ubuntu" and version < 14:
            detectOS.result = "Ubuntu 12"

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
        detectOSRelease()
    elif os.path.isfile("/etc/config.scm"):
        detectOS.result = "Guix"
    return detectOS.result

def detectPrereqs(missing=True):
    available = []
    for module in PACKAGES:
        try:
            import_module(module)
            if not missing:
                available.append(module)
        except ImportError:
            if missing:
                available.append(module)
    return available

def prereqToPackages():
    if not detectPrereqs():
        return
    print "%s %s" % (
        PACKAGE_MANAGER[detectOS()], " ".join(
            PACKAGES[x][detectOS()] for x in detectPrereqs()))

def compilerToPackages():
    if not detectOS() in COMPILING:
        return
    print "%s %s" % (
        PACKAGE_MANAGER[detectOS.result], COMPILING[detectOS.result])

def testCompiler():
    if not HAVE_SETUPTOOLS:
        # silent, we can't test without setuptools
        return True

    bitmsghash = Extension(
        'bitmsghash',
        sources=['src/bitmsghash/bitmsghash.cpp'],
        libraries=['pthread', 'crypto'],
    )

    dist = Distribution()
    dist.ext_modules = [bitmsghash]
    cmd = build_ext(dist)
    cmd.initialize_options()
    cmd.finalize_options()
    cmd.force = True
    try:
        cmd.run()
    except CompileError:
        return False
    else:
        fullPath = os.path.join(cmd.build_lib, cmd.get_ext_filename("bitmsghash"))
        return os.path.isfile(fullPath)

detectOS.result = None
prereqs = detectPrereqs()

compiler = testCompiler()

if (not compiler or prereqs) and detectOS() in PACKAGE_MANAGER:
    print "It looks like you're using %s. " \
    "It is highly recommended to use the package manager\n" \
    "to install the missing dependencies." % (detectOS.result)

if not compiler:
    print "Building the bitmsghash module failed.\n" \
        "You may be missing a C++ compiler and/or the OpenSSL headers."

if prereqs:
    mandatory = list(x for x in prereqs if "optional" not in PACKAGES[x] or not PACKAGES[x]["optional"])
    optional = list(x for x in prereqs if "optional" in PACKAGES[x] and PACKAGES[x]["optional"])
    if mandatory:
        print "Missing mandatory dependencies: %s" % (" ".join(mandatory))
    if optional:
        print "Missing optional dependencies: %s" % (" ".join(optional))
        for package in optional:
            print PACKAGES[package].get('description')

if (not compiler or prereqs) and detectOS() in PACKAGE_MANAGER:
    print "You can install the missing dependencies by running, as root:"
    if not compiler:
        compilerToPackages()
    prereqToPackages()
else:
    print "All the dependencies satisfied, you can install PyBitmessage"
