import os
try:
    from setuptools import setup, find_packages, Extension
    haveSetuptools = True
except ImportError:
    haveSetuptools = False
import sys

from src.version import softwareVersion

packageManager = {
    "OpenBSD": "pkg_add",
    "FreeBSD": "pkg_install",
    "Debian": "apt-get install",
    "Ubuntu": "apt-get install",
    "openSUSE": "zypper install",
    "Fedora": "dnf install",
    "Guix": "guix package -i",
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
    },
    "msgpack": {
        "OpenBSD": "py-msgpack",
        "FreeBSD": "py27-msgpack-python",
        "Debian": "python-msgpack",
        "Ubuntu": "python-msgpack",
        "openSUSE": "python-msgpack-python",
        "Fedora": "python2-msgpack",
        "Guix": "python2-msgpack",
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
                    if "fedora" in line.lower():
                        detectOS.result = "Fedora"
                    elif "opensuse" in line.lower():
                        detectOS.result = "openSUSE"
                    elif "ubuntu" in line.lower():
                        detectOS.result = "Ubuntu"
                    elif "debian" in line.lower():
                        detectOS.result = "Debian"
                    else:
                        detectOS.result = None
    return detectOS.result

def detectPrereqs(missing=False):
    available = []
    try:
        import PyQt4.QtCore
        if not missing:
            available.append("PyQt")
    except ImportError:
        if missing:
            available.append("PyQt")
    try:
        import msgpack
        if not missing:
            available.append("msgpack")
    except ImportError:
        if missing:
            available.append("msgpack")
    return available

def prereqToPackages():
    print "You can install the requirements by running, as root:"
    print "%s %s" % (packageManager[detectOS()], " ".join(packageName[x][detectOS()] for x in detectPrereqs(True)))

if __name__ == "__main__":
    detectOS.result = None
    detectPrereqs.result = None
    if "PyQt" in detectPrereqs(True):
        print "You only need PyQt if you want to use the GUI. When only running as a daemon, this can be skipped."
        print "However, you would have to install it manually because setuptools does not support pyqt."
    if detectPrereqs(True) != [] and detectOS() in packageManager:
        if detectOS() is not None:
            print "It looks like you're using %s. It is highly recommended to use the package manager instead of setuptools." % (detectOS())
            prereqToPackages()
            sys.exit()
    if not haveSetuptools:
        print "It looks like you're missing setuptools."
        sys.exit()

    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'README.md')) as f:
        README = f.read()
    with open(os.path.join(here, 'CHANGES.txt')) as f:
        CHANGES = f.read()

    bitmsghash = Extension('bitmsghash.bitmsghash',
        sources = ['src/bitmsghash/bitmsghash.cpp'],
        libraries = ['pthread', 'crypto'],
    )

    dist = setup(
        name='pybitmessage',
        version=softwareVersion,
        description='',
        long_description=README,
        license='MIT',
        # TODO: add author info
        #author='',
        #author_email='',
        url='https://github.com/Bitmessage/PyBitmessage/',
        # TODO: add keywords
        #keywords='',
        install_requires = ['msgpack-python'],
        classifiers = [
            "License :: OSI Approved :: MIT License"
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX :: Linux",
            "Programming Language :: Python :: 2.7.3",
            "Programming Language :: Python :: 2.7.4",
            "Programming Language :: Python :: 2.7.5",
            "Programming Language :: Python :: 2.7.6",
            "Programming Language :: Python :: 2.7.7",
            "Programming Language :: Python :: 2.7.8",
            "Programming Language :: Python :: 2.7.9",
            "Programming Language :: Python :: 2.7.10",
            "Programming Language :: Python :: 2.7.11",
            "Programming Language :: Python :: 2.7.12",
            "Programming Language :: Python :: 2.7.13",
        ],
        package_dir={'':'src'},
        packages=['','bitmessageqt', 'bitmessagecurses', 'messagetypes', 'network', 'pyelliptic', 'socks'],
        package_data={'': ['bitmessageqt/*.ui', 'bitmsghash/*.cl', 'keys/*.pem', 'translations/*.ts', 'translations/*.qm', 'images/*.png', 'images/*.ico', 'images/*.icns']},
        ext_modules = [bitmsghash],
        zip_safe=False,
        entry_points="""\
        [console_scripts]
        bitmessage = bitmessagemain:Main.start
        """,
    )
    with open(os.path.join(dist.command_obj['install_scripts'].install_dir, 'bitmessage'), 'wt') as f:
        f.write("#!/bin/sh\n")
        f.write(dist.command_obj['build'].executable + " " + \
            os.path.join(dist.command_obj['install'].install_lib, 
            os.path.basename(dist.command_obj['bdist_egg'].egg_output),
            'bitmessagemain.py') + "\n")
    os.chmod(os.path.join(dist.command_obj['install_scripts'].install_dir, 'bitmessage'), 0555)
