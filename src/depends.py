#! python

import sys

#Only really old versions of Python don't have sys.hexversion. We don't support
#them. The logging module was introduced in Python 2.3
if not hasattr(sys, 'hexversion') or sys.hexversion < 0x20300F0:
    sys.stdout.write('Python version: ' + sys.version)
    sys.stdout.write('PyBitmessage requires Python 2.7.3 or greater (but not Python 3)')
    sys.exit()

#We can now use logging so set up a simple configuration
import logging
formatter = logging.Formatter(
    '%(levelname)s: %(message)s'
)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.ERROR)

#We need to check hashlib for RIPEMD-160, as it won't be available if OpenSSL is
#not linked against or the linked OpenSSL has RIPEMD disabled.
def check_hashlib():
    if sys.hexversion < 0x020500F0:
        logger.error('The hashlib module is not included in this version of Python.')
        return False
    import hashlib
    if '_hashlib' not in hashlib.__dict__:
        logger.error('The RIPEMD-160 hash algorithm is not available. The hashlib module is not linked against OpenSSL.')
        return False
    try:
        hashlib.new('ripemd160')
    except ValueError:
        logger.error('The RIPEMD-160 hash algorithm is not available. The hashlib module utilizes an OpenSSL library with RIPEMD disabled.')
        return False
    return True

def check_sqlite():
    if sys.hexversion < 0x020500F0:
        logger.error('The sqlite3 module is not included in this version of Python.')
        return False
    try:
        import sqlite3
    except ImportError:
        logger.error('The sqlite3 module is not available')
        return False

    logger.info('sqlite3 Module Version: ' + sqlite3.version)
    logger.info('SQLite Library Version: ' + sqlite3.sqlite_version)
    #sqlite_version_number formula: https://sqlite.org/c3ref/c_source_id.html
    sqlite_version_number = sqlite3.sqlite_version_info[0] * 1000000 + sqlite3.sqlite_version_info[1] * 1000 + sqlite3.sqlite_version_info[2]

    conn = None
    try:
        try:
            conn = sqlite3.connect(':memory:')
            if sqlite_version_number >= 3006018:
                sqlite_source_id = conn.execute('SELECT sqlite_source_id();').fetchone()[0]
                logger.info('SQLite Library Source ID: ' + sqlite_source_id)
            if sqlite_version_number >= 3006023:
                compile_options = ', '.join(map(lambda row: row[0], conn.execute('PRAGMA compile_options;')))
                logger.info('SQLite Library Compile Options: ' + compile_options)
            #There is no specific version requirement as yet, so we just use the
            #first version that was included with Python.
            if sqlite_version_number < 3000008:
                logger.error('This version of SQLite is too old. PyBitmessage requires SQLite 3.0.8 or later')
                return False
            return True
        except sqlite3.Error:
            logger.exception('An exception occured while checking sqlite.')
            return False
    finally:
        if conn:
            conn.close()

def check_openssl():
    try:
        import ctypes
    except ImportError:
        logger.error('Unable to check OpenSSL. The ctypes module is not available.')
        return False

    #We need to emulate the way PyElliptic searches for OpenSSL.
    if sys.platform == 'win32':
        paths = ['libeay32.dll']
        if getattr(sys, 'frozen', False):
            import os.path
            paths.insert(0, os.path.join(sys._MEIPASS, 'libeay32.dll'))
    else:
        paths = ['libcrypto.so']
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

    SSLEAY_VERSION = 0
    SSLEAY_CFLAGS = 2

    cflags_regex = re.compile(r'(?:OPENSSL_NO_)(AES|EC|ECDH|ECDSA)(?!\w)')

    for path in paths:
        logger.info('Checking OpenSSL at ' + path)
        try:
            library = ctypes.CDLL(path)
        except OSError:
            continue
        logger.info('OpenSSL Name: ' + library._name)
        try:
            library.SSLeay.restype = ctypes.c_long
            library.SSLeay_version.restype = ctypes.c_char_p
            library.SSLeay_version.argtypes = [ctypes.c_int]
        except AttributeError:
            logger.error('Cannot determine version of this OpenSSL library.')
            return False
        logger.info('OpenSSL Version: ' + library.SSLeay_version(SSLEAY_VERSION))
        compile_options = library.SSLeay_version(SSLEAY_CFLAGS)
        logger.info('OpenSSL Compile Options: ' + compile_options)
        openssl_hexversion = library.SSLeay()
        #PyElliptic uses EVP_CIPHER_CTX_new and EVP_CIPHER_CTX_free which were
        #introduced in 0.9.8b.
        if openssl_hexversion < 0x90802F:
            logger.error('This OpenSSL library is too old. PyBitmessage requires OpenSSL 0.9.8b or later with AES, Elliptic Curves (EC), ECDH, and ECDSA enabled.')
            return False
        matches = cflags_regex.findall(compile_options)
        if len(matches) > 0:
            logger.error('This OpenSSL library is missing the following required features: ' + ', '.join(matches) + '. PyBitmessage requires OpenSSL 0.9.8b or later with AES, Elliptic Curves (EC), ECDH, and ECDSA enabled.')
            return False
        return True
    return False

#TODO: The minimum versions of pythondialog and dialog need to be determined
def check_curses():
    if sys.hexversion < 0x20600F0:
        logger.error('The curses interface requires the pythondialog package and the dialog utility.')
        return False
    try:
        import curses
    except ImportError:
        logger.error('The curses interface can not be used. The curses module is not available.')
        return False
    logger.info('curses Module Version: ' + curses.version)
    try:
        import dialog
    except ImportError:
        logger.error('The curses interface can not be used. The pythondialog package is not available.')
        return False
    logger.info('pythondialog Package Version: ' + dialog.__version__)
    dialog_util_version = dialog.Dialog().cached_backend_version
    #The pythondialog author does not like Python2 str, so we have to use
    #unicode for just the version otherwise we get the repr form which includes
    #the module and class names along with the actual version.
    logger.info('dialog Utility Version' + unicode(dialog_util_version))
    return True

def check_pyqt():
    try:
        import PyQt4.QtCore
    except ImportError:
        logger.error('The PyQt4 package is not available. PyBitmessage requires PyQt 4.8 or later and Qt 4.7 or later.')
        return False
    logger.info('PyQt Version: ' + PyQt4.QtCore.PYQT_VERSION_STR)
    logger.info('Qt Version: ' + PyQt4.QtCore.QT_VERSION_STR)
    passed = True
    if PyQt4.QtCore.PYQT_VERSION < 0x40800:
        logger.error('This version of PyQt is too old. PyBitmessage requries PyQt 4.8 or later.')
        passed = False
    if PyQt4.QtCore.QT_VERSION < 0x40700:
        logger.error('This version of Qt is too old. PyBitmessage requries Qt 4.7 or later.')
        passed = False
    return passed

def check_dependencies(verbose = False, optional = False):
    if verbose:
        logger.setLevel(logging.INFO)

    has_all_dependencies = True

    #Python 2.7.3 is the required minimum. Python 3+ is not supported, but it is
    #still useful to provide information about our other requirements.
    logger.info('Python version: %s', sys.version)
    if sys.hexversion < 0x20703F0:
        logger.error('PyBitmessage requires Python 2.7.3 or greater (but not Python 3+)')
        has_all_dependencies = False
    if sys.hexversion >= 0x3000000:
        logger.error('PyBitmessage does not support Python 3+. Python 2.7.3 or greater is required.')
        has_all_dependencies = False

    check_functions = [check_hashlib, check_sqlite, check_openssl]
    if optional:
        check_functions.extend([check_pyqt, check_curses])

    #Unexpected exceptions are handled here
    for check in check_functions:
        try:
            has_all_dependencies &= check()
        except:
            logger.exception(check.__name__ + ' failed unexpectedly.')
            has_all_dependencies = False
        
    if not has_all_dependencies:
        logger.critical('PyBitmessage cannot start. One or more dependencies are unavailable.')
        sys.exit()

if __name__ == '__main__':
    check_dependencies(True, True)

