
import logging
import os
import time

from bmconfigparser import BMConfigParser


#logger = logging.getLogger(__name__)
logger = logging.getLogger('file_only')


DEFAULT_ENCODING = 'ISO8859-1'
DEFAULT_LANGUAGE = 'en_US'
DEFAULT_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

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

try:
    import locale
    encoding = locale.getpreferredencoding(True) or DEFAULT_ENCODING
    language = locale.getlocale()[0] or locale.getdefaultlocale()[0] or DEFAULT_LANGUAGE
except:
    logger.exception('Could not determine language or encoding')


if BMConfigParser().has_option('bitmessagesettings', 'timeformat'):
    time_format = BMConfigParser().get('bitmessagesettings', 'timeformat')
    #Test the format string
    try:
        time.strftime(time_format)
    except:
        logger.exception('Could not format timestamp')
        time_format = DEFAULT_TIME_FORMAT
else:
    time_format = DEFAULT_TIME_FORMAT

#It seems some systems lie about the encoding they use so we perform
#comprehensive decoding tests
if time_format != DEFAULT_TIME_FORMAT:
    try:
        #Check day names
        new_time_format = time_format 
        import sys
        if sys.version_info >= (3, 0, 0) and time_format == '%%c':
            time_format = '%c'
        for i in range(7):
            #this work for python2.7
            # unicode(time.strftime(time_format, (0, 0, 0, 0, 0, 0, i, 0, 0)), encoding)
            #this code for the python3
            (time.strftime(time_format, (0, 0, 0, 0, 0, 0, i, 0, 0))).encode()
        #Check month names
        for i in range(1, 13):
            # unicode(time.strftime(time_format, (0, i, 0, 0, 0, 0, 0, 0, 0)), encoding)
            (time.strftime(time_format, (0, i, 0, 0, 0, 0, 0, 0, 0))).encode()

        #Check AM/PM
        (time.strftime(time_format, (0, 0, 0, 11, 0, 0, 0, 0, 0))).encode()
        (time.strftime(time_format, (0, 0, 0, 13, 0, 0, 0, 0, 0))).encode()
        #Check DST
        (time.strftime(time_format, (0, 0, 0, 0, 0, 0, 0, 0, 1))).encode()
    except:
        logger.exception('Could not decode locale formatted timestamp')
        time_format = DEFAULT_TIME_FORMAT
        encoding = DEFAULT_ENCODING
    time_format = new_time_format

def setlocale(category, newlocale):
    locale.setlocale(category, newlocale)
    # it looks like some stuff isn't initialised yet when this is called the
    # first time and its init gets the locale settings from the environment
    os.environ["LC_ALL"] = newlocale

def formatTimestamp(timestamp = None, as_unicode = True):
    #For some reason some timestamps are strings so we need to sanitize.
    if timestamp is not None and not isinstance(timestamp, int):
        try:
            timestamp = int(timestamp)
        except:
            timestamp = None

    #timestamp can't be less than 0.
    if timestamp is not None and timestamp < 0:
        timestamp = None

    if timestamp is None:
        timestring = time.strftime(time_format)
    else:
        #In case timestamp is too far in the future
        try:
            timestring = time.strftime(time_format, time.localtime(timestamp))
        except ValueError:
            timestring = time.strftime(time_format)

    if as_unicode:
        return unicode(timestring, encoding)
    return timestring

def getTranslationLanguage():
    userlocale = None
    if BMConfigParser().has_option('bitmessagesettings', 'userlocale'):
        userlocale = BMConfigParser().get('bitmessagesettings', 'userlocale')

    if userlocale in [None, '', 'system']:
        return language

    return userlocale
    
def getWindowsLocale(posixLocale):
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
