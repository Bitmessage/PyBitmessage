#!/usr/bin/env python2
"""
Check dependencies and give recommendations about how to satisfy them

Limitations:

    * Does not detect whether packages are already installed. Solving this requires writing more of a configuration
    management system. Or we could switch to an existing one.
    * Not fully PEP508 compliant. Not slightly. It makes bold assumptions about the simplicity of the contents of
    EXTRAS_REQUIRE. This is fine because most developers do, too.
"""

import os
import sys
from distutils.errors import CompileError
try:
    from setuptools.dist import Distribution
    from setuptools.extension import Extension
    from setuptools.command.build_ext import build_ext
    HAVE_SETUPTOOLS = True
    # another import from setuptools is in setup.py
    from setup import EXTRAS_REQUIRE
except ImportError:
    HAVE_SETUPTOOLS = False
    EXTRAS_REQUIRE = {}

from importlib import import_module

from src.depends import detectOS, PACKAGES, PACKAGE_MANAGER


COMPILING = {
    "Debian": "build-essential libssl-dev",
    "Ubuntu": "build-essential libssl-dev",
    "Fedora": "gcc-c++ redhat-rpm-config python-devel openssl-devel",
    "openSUSE": "gcc-c++ libopenssl-devel python-devel",
    "optional": False,
}

# OS-specific dependencies for optional components listed in EXTRAS_REQUIRE
EXTRAS_REQUIRE_DEPS = {
    # The values from setup.EXTRAS_REQUIRE
    'python_prctl': {
        # The packages needed for this requirement, by OS
        "OpenBSD": [""],
        "FreeBSD": [""],
        "Debian": ["libcap-dev python-prctl"],
        "Ubuntu": ["libcap-dev python-prctl"],
        "Ubuntu 12": ["libcap-dev python-prctl"],
        "openSUSE": [""],
        "Fedora": ["prctl"],
        "Guix": [""],
        "Gentoo": ["dev-python/python-prctl"],
    },
}


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
    print("%s %s" % (
        PACKAGE_MANAGER[detectOS()], " ".join(
            PACKAGES[x][detectOS()] for x in detectPrereqs())))


def compilerToPackages():
    if not detectOS() in COMPILING:
        return
    print("%s %s" % (
        PACKAGE_MANAGER[detectOS.result], COMPILING[detectOS.result]))


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


prereqs = detectPrereqs()
compiler = testCompiler()

if (not compiler or prereqs) and detectOS() in PACKAGE_MANAGER:
    print(
        "It looks like you're using %s. "
        "It is highly recommended to use the package manager\n"
        "to install the missing dependencies." % detectOS.result)

if not compiler:
    print(
        "Building the bitmsghash module failed.\n"
        "You may be missing a C++ compiler and/or the OpenSSL headers.")

if prereqs:
    mandatory = [x for x in prereqs if not PACKAGES[x].get("optional")]
    optional = [x for x in prereqs if PACKAGES[x].get("optional")]
    if mandatory:
        print("Missing mandatory dependencies: %s" % " ".join(mandatory))
    if optional:
        print("Missing optional dependencies: %s" % " ".join(optional))
        for package in optional:
            print(PACKAGES[package].get('description'))

# Install the system dependencies of optional extras_require components
OPSYS = detectOS()
CMD = PACKAGE_MANAGER[OPSYS] if OPSYS in PACKAGE_MANAGER else 'UNKNOWN_INSTALLER'
for lhs, rhs in EXTRAS_REQUIRE.items():
    if OPSYS is None:
        break
    if rhs and any([
        EXTRAS_REQUIRE_DEPS[x][OPSYS]
        for x in rhs
        if x in EXTRAS_REQUIRE_DEPS
    ]):
        rhs_cmd = ''.join([
            CMD,
            ' ',
            ' '.join([
                ''. join([
                    xx for xx in EXTRAS_REQUIRE_DEPS[x][OPSYS]
                ])
                for x in rhs
                if x in EXTRAS_REQUIRE_DEPS
            ]),
        ])
        print(
            "Optional dependency `pip install .[{}]` would require `{}`"
            " to be run as root".format(lhs, rhs_cmd))

if (not compiler or prereqs) and OPSYS in PACKAGE_MANAGER:
    print("You can install the missing dependencies by running, as root:")
    if not compiler:
        compilerToPackages()
    prereqToPackages()
    if prereqs and mandatory:
        sys.exit(1)
else:
    print("All the dependencies satisfied, you can install PyBitmessage")
