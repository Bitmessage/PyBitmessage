"""
Utility functions to check the availability of dependencies
and suggest how it may be installed
"""

import sys

# Only really old versions of Python don't have sys.hexversion. We don't
# support them. The logging module was introduced in Python 2.3
if not hasattr(sys, 'hexversion') or sys.hexversion < 0x20300F0:
    sys.exit(
        'Python version: %s\n'
        'PyBitmessage requires Python 2.7.4 or greater (but not Python 3)'
        % sys.version
    )

import logging
import os
from importlib import import_module
import state
# We can now use logging so set up a simple configuration
formatter = logging.Formatter('%(levelname)s: %(message)s')
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger = logging.getLogger('both')
logger.addHandler(handler)
logger.setLevel(logging.ERROR)


OS_RELEASE = {
    "Debian GNU/Linux".lower(): "Debian",
    "fedora": "Fedora",
    "opensuse": "openSUSE",
    "ubuntu": "Ubuntu",
    "gentoo": "Gentoo",
    "calculate": "Gentoo"
}

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
        "optional": True,
        "description":
        "You only need PyQt if you want to use the GUI."
        " When only running as a daemon, this can be skipped.\n"
        "However, you would have to install it manually"
        " because setuptools does not support PyQt."
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
        "description":
        "python-msgpack is recommended for improved performance of"
        " message encoding/decoding"
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
        "description":
        "If you install pyopencl, you will be able to use"
        " GPU acceleration for proof of work.\n"
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
        "Gentoo": "dev-python/setuptools",
        "optional": False,
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
        detectOSRelease()
    elif os.path.isfile("/etc/config.scm"):
        detectOS.result = "Guix"
    return detectOS.result


detectOS.result = None


def detectOSRelease():
    with open("/etc/os-release", 'r') as osRelease:
        version = None
        for line in osRelease:
            if line.startswith("NAME="):
                detectOS.result = OS_RELEASE.get(
                    line.replace('"', '').split("=")[-1].strip().lower())
            elif line.startswith("VERSION_ID="):
                try:
                    version = float(line.split("=")[1].replace("\"", ""))
                except ValueError:
                    pass
        if detectOS.result == "Ubuntu" and version < 14:
            detectOS.result = "Ubuntu 12"


def try_import(module, log_extra=False):
    try:
        return import_module(module)
    except ImportError:
        module = module.split('.')[0]
        logger.error('The %s module is not available.', module)
        if log_extra:
            logger.error(log_extra)
            dist = detectOS()
            logger.error(
                'On %s, try running "%s %s" as root.',
                dist, PACKAGE_MANAGER[dist], PACKAGES[module][dist])
        return False


def check_ripemd160():
    """Check availability of the RIPEMD160 hash function"""
    try:
        from fallback import RIPEMD160Hash  # pylint: disable=relative-import
    except ImportError:
        return False
    return RIPEMD160Hash is not None


def check_sqlite():
    """Do sqlite check.

    Simply check sqlite3 module if exist or not with hexversion
    support in python version for specifieed platform.
    """
    if sys.hexversion < 0x020500F0:
        logger.error(
            'The sqlite3 module is not included in this version of Python.')
        if sys.platform.startswith('freebsd'):
            logger.error(
                'On FreeBSD, try running "pkg install py27-sqlite3" as root.')
        return False

    sqlite3 = try_import('sqlite3')
    if not sqlite3:
        return False

    logger.info('sqlite3 Module Version: %s', sqlite3.version)
    logger.info('SQLite Library Version: %s', sqlite3.sqlite_version)
    # sqlite_version_number formula: https://sqlite.org/c3ref/c_source_id.html
    sqlite_version_number = (
        sqlite3.sqlite_version_info[0] * 1000000 +
        sqlite3.sqlite_version_info[1] * 1000 +
        sqlite3.sqlite_version_info[2]
    )

    conn = None
    try:
        try:
            conn = sqlite3.connect(':memory:')
            if sqlite_version_number >= 3006018:
                sqlite_source_id = conn.execute(
                    'SELECT sqlite_source_id();'
                ).fetchone()[0]
                logger.info('SQLite Library Source ID: %s', sqlite_source_id)
            if sqlite_version_number >= 3006023:
                compile_options = ', '.join(map(
                    lambda row: row[0],
                    conn.execute('PRAGMA compile_options;')
                ))
                logger.info(
                    'SQLite Library Compile Options: %s', compile_options)
            # There is no specific version requirement as yet, so we just
            # use the first version that was included with Python.
            if sqlite_version_number < 3000008:
                logger.error(
                    'This version of SQLite is too old.'
                    ' PyBitmessage requires SQLite 3.0.8 or later')
                return False
            return True
        except sqlite3.Error:
            logger.exception('An exception occured while checking sqlite.')
            return False
    finally:
        if conn:
            conn.close()


def check_openssl():
    """Do openssl dependency check.

    Here we are checking for openssl with its all dependent libraries
    and version checking.
    """

    ctypes = try_import('ctypes')
    if not ctypes:
        logger.error('Unable to check OpenSSL.')
        return False

    # We need to emulate the way PyElliptic searches for OpenSSL.
    if sys.platform == 'win32':
        paths = ['libeay32.dll']
        if getattr(sys, 'frozen', False):
            import os.path
            paths.insert(0, os.path.join(sys._MEIPASS, 'libeay32.dll'))
    elif state.kivy:
        return True
    else:
        paths = ['libcrypto.so', 'libcrypto.so.1.0.0']

    if sys.platform == 'darwin':
        paths.extend([
            'libcrypto.dylib',
            '/usr/local/opt/openssl/lib/libcrypto.dylib',
            './../Frameworks/libcrypto.dylib'
        ])
    import re
    if re.match(r'linux|darwin|freebsd', sys.platform):
        try:
            import ctypes.util
            path = ctypes.util.find_library('ssl')
            if path not in paths:
                paths.append(path)
        except:
            pass

    openssl_version = None
    openssl_hexversion = None
    openssl_cflags = None

    cflags_regex = re.compile(r'(?:OPENSSL_NO_)(AES|EC|ECDH|ECDSA)(?!\w)')

    import pyelliptic.openssl

    for path in paths:
        logger.info('Checking OpenSSL at %s', path)
        try:
            library = ctypes.CDLL(path)
        except OSError:
            continue
        logger.info('OpenSSL Name: %s', library._name)
        try:
            openssl_version, openssl_hexversion, openssl_cflags = \
                pyelliptic.openssl.get_version(library)
        except AttributeError:  # sphinx chokes
            return True
        if not openssl_version:
            logger.error('Cannot determine version of this OpenSSL library.')
            return False
        logger.info('OpenSSL Version: %s', openssl_version)
        logger.info('OpenSSL Compile Options: %s', openssl_cflags)
        # PyElliptic uses EVP_CIPHER_CTX_new and EVP_CIPHER_CTX_free which were
        # introduced in 0.9.8b.
        if openssl_hexversion < 0x90802F:
            logger.error(
                'This OpenSSL library is too old. PyBitmessage requires'
                ' OpenSSL 0.9.8b or later with AES, Elliptic Curves (EC),'
                ' ECDH, and ECDSA enabled.')
            return False
        matches = cflags_regex.findall(openssl_cflags)
        if len(matches) > 0:
            logger.error(
                'This OpenSSL library is missing the following required'
                ' features: %s. PyBitmessage requires OpenSSL 0.9.8b'
                ' or later with AES, Elliptic Curves (EC), ECDH,'
                ' and ECDSA enabled.', ', '.join(matches))
            return False
        return True
    return False


# TODO: The minimum versions of pythondialog and dialog need to be determined
def check_curses():
    """Do curses dependency check.

    Here we are checking for curses if available or not with check
    as interface requires the pythondialog\ package and the dialog
    utility.
    """
    if sys.hexversion < 0x20600F0:
        logger.error(
            'The curses interface requires the pythondialog package and'
            ' the dialog utility.')
        return False
    curses = try_import('curses')
    if not curses:
        logger.error('The curses interface can not be used.')
        return False

    logger.info('curses Module Version: %s', curses.version)

    dialog = try_import('dialog')
    if not dialog:
        logger.error('The curses interface can not be used.')
        return False

    import subprocess

    try:
        subprocess.check_call(['which', 'dialog'])
    except subprocess.CalledProcessError:
        logger.error(
            'Curses requires the `dialog` command to be installed as well as'
            ' the python library.')
        return False

    logger.info('pythondialog Package Version: %s', dialog.__version__)
    dialog_util_version = dialog.Dialog().cached_backend_version
    # The pythondialog author does not like Python2 str, so we have to use
    # unicode for just the version otherwise we get the repr form which
    # includes the module and class names along with the actual version.
    logger.info('dialog Utility Version %s', unicode(dialog_util_version))
    return True


def check_pyqt():
    """Do pyqt dependency check.

    Here we are checking for PyQt4 with its version, as for it require
    PyQt 4.8 or later.
    """
    QtCore = try_import(
        'PyQt4.QtCore', 'PyBitmessage requires PyQt 4.8 or later and Qt 4.7 or later.')

    if not QtCore:
        return False

    logger.info('PyQt Version: %s', QtCore.PYQT_VERSION_STR)
    logger.info('Qt Version: %s', QtCore.QT_VERSION_STR)
    passed = True
    if QtCore.PYQT_VERSION < 0x40800:
        logger.error(
            'This version of PyQt is too old. PyBitmessage requries'
            ' PyQt 4.8 or later.')
        passed = False
    if QtCore.QT_VERSION < 0x40700:
        logger.error(
            'This version of Qt is too old. PyBitmessage requries'
            ' Qt 4.7 or later.')
        passed = False
    return passed


def check_msgpack():
    """Do sgpack module check.

    simply checking if msgpack package with all its dependency
    is available or not as recommended for messages coding.
    """
    return try_import(
        'msgpack', 'It is highly recommended for messages coding.') is not False


def check_dependencies(verbose=False, optional=False):
    """Do dependency check.

    It identifies project dependencies and checks if there are
    any known, publicly disclosed, vulnerabilities.basically
    scan applications (and their dependent libraries) so that
    easily identify any known vulnerable components.
    """
    if verbose:
        logger.setLevel(logging.INFO)

    has_all_dependencies = True

    # Python 2.7.4 is the required minimum.
    # (https://bitmessage.org/forum/index.php?topic=4081.0)
    # Python 3+ is not supported, but it is still useful to provide
    # information about our other requirements.
    logger.info('Python version: %s', sys.version)
    if sys.hexversion < 0x20704F0:
        logger.error(
            'PyBitmessage requires Python 2.7.4 or greater'
            ' (but not Python 3+)')
        has_all_dependencies = False
    if sys.hexversion >= 0x3000000:
        logger.error(
            'PyBitmessage does not support Python 3+. Python 2.7.4'
            ' or greater is required.')
        has_all_dependencies = False

    check_functions = [check_ripemd160, check_sqlite, check_openssl]
    if optional:
        check_functions.extend([check_msgpack, check_pyqt, check_curses])
    # Unexpected exceptions are handled here
    for check in check_functions:
        try:
            has_all_dependencies &= check()
        except:
            logger.exception('%s failed unexpectedly.', check.__name__)
            has_all_dependencies = False

    if not has_all_dependencies:
        sys.exit(
            'PyBitmessage cannot start. One or more dependencies are'
            ' unavailable.'
        )


logger.setLevel(0)
