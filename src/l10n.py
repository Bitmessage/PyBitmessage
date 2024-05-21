"""Localization helpers"""

import logging
import os
import re
import sys
import time

from six.moves import range

from bmconfigparser import config

logger = logging.getLogger('default')

DEFAULT_ENCODING = 'ISO8859-1'
DEFAULT_LANGUAGE = 'en_US'
DEFAULT_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

try:
    import locale
    encoding = locale.getpreferredencoding(True) or DEFAULT_ENCODING
    language = (
        locale.getlocale()[0] or locale.getdefaultlocale()[0]
        or DEFAULT_LANGUAGE)
except (ImportError, AttributeError):  # FIXME: it never happens
    logger.exception('Could not determine language or encoding')
    locale = None
    encoding = DEFAULT_ENCODING
    language = DEFAULT_LANGUAGE


windowsLanguageMap = {
    "ar": "arabic",
    "cs": "czech",
    "da": "danish",
    "de": "german",
    "en": "english",
    "eo": "esperanto",
    "fr": "french",
    "it": "italian",
    "ja": "japanese",
    "nl": "dutch",
    "no": "norwegian",
    "pl": "polish",
    "pt": "portuguese",
    "ru": "russian",
    "sk": "slovak",
    "zh": "chinese",
    "zh_CN": "chinese-simplified",
    "zh_HK": "chinese-traditional",
    "zh_SG": "chinese-simplified",
    "zh_TW": "chinese-traditional"
}


time_format = config.safeGet(
    'bitmessagesettings', 'timeformat', DEFAULT_TIME_FORMAT)

if not re.search(r'\d', time.strftime(time_format)):
    time_format = DEFAULT_TIME_FORMAT

# It seems some systems lie about the encoding they use
# so we perform comprehensive decoding tests
elif sys.version_info[0] == 2:
    try:
        # Check day names
        for i in range(7):
            time.strftime(
                time_format, (0, 0, 0, 0, 0, 0, i, 0, 0)).decode(encoding)
        # Check month names
        for i in range(1, 13):
            time.strftime(
                time_format, (0, i, 0, 0, 0, 0, 0, 0, 0)).decode(encoding)
        # Check AM/PM
        time.strftime(
            time_format, (0, 0, 0, 11, 0, 0, 0, 0, 0)).decode(encoding)
        time.strftime(
            time_format, (0, 0, 0, 13, 0, 0, 0, 0, 0)).decode(encoding)
        # Check DST
        time.strftime(
            time_format, (0, 0, 0, 0, 0, 0, 0, 0, 1)).decode(encoding)
    except Exception:  # TODO: write tests and determine exception types
        logger.exception('Could not decode locale formatted timestamp')
        # time_format = DEFAULT_TIME_FORMAT
        encoding = DEFAULT_ENCODING


def setlocale(newlocale):
    """Set the locale"""
    try:
        locale.setlocale(locale.LC_ALL, newlocale)
    except AttributeError:  # locale is None
        pass
    # it looks like some stuff isn't initialised yet when this is called the
    # first time and its init gets the locale settings from the environment
    os.environ["LC_ALL"] = newlocale


def formatTimestamp(timestamp=None):
    """Return a formatted timestamp"""
    # For some reason some timestamps are strings so we need to sanitize.
    if timestamp is not None and not isinstance(timestamp, int):
        try:
            timestamp = int(timestamp)
        except (ValueError, TypeError):
            timestamp = None

    # timestamp can't be less than 0.
    if timestamp is not None and timestamp < 0:
        timestamp = None

    if timestamp is None:
        timestring = time.strftime(time_format)
    else:
        # In case timestamp is too far in the future
        try:
            timestring = time.strftime(time_format, time.localtime(timestamp))
        except ValueError:
            timestring = time.strftime(time_format)

    if sys.version_info[0] == 2:
        return timestring.decode(encoding)
    return timestring


def getTranslationLanguage():
    """Return the user's language choice"""
    userlocale = config.safeGet(
        'bitmessagesettings', 'userlocale', 'system')
    return userlocale if userlocale and userlocale != 'system' else language


def getWindowsLocale(posixLocale):
    """
    Get the Windows locale
    Technically this converts the locale string from UNIX to Windows format,
    because they use different ones in their
    libraries. E.g. "en_EN.UTF-8" to "english".
    """
    if posixLocale in windowsLanguageMap:
        return windowsLanguageMap[posixLocale]
    if "." in posixLocale:
        loc = posixLocale.split(".", 1)
        if loc[0] in windowsLanguageMap:
            return windowsLanguageMap[loc[0]]
    if "_" in posixLocale:
        loc = posixLocale.split("_", 1)
        if loc[0] in windowsLanguageMap:
            return windowsLanguageMap[loc[0]]
    if posixLocale != DEFAULT_LANGUAGE:
        return getWindowsLocale(DEFAULT_LANGUAGE)
    return None
