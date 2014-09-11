
import logging
import time

import shared


#logger = logging.getLogger(__name__)
logger = logging.getLogger('file_only')


DEFAULT_ENCODING = 'ISO8859-1'
DEFAULT_LANGUAGE = 'en_US'
DEFAULT_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

encoding = DEFAULT_ENCODING
language = DEFAULT_LANGUAGE

try:
    import locale
    encoding = locale.getpreferredencoding(True) or DEFAULT_ENCODING
    language = locale.getlocale()[0] or locale.getdefaultlocale()[0] or DEFAULT_LANGUAGE
except:
    logger.exception('Could not determine language or encoding')


if shared.config.has_option('bitmessagesettings', 'timeformat'):
    time_format = shared.config.get('bitmessagesettings', 'timeformat')
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
        for i in xrange(7):
            unicode(time.strftime(time_format, (0, 0, 0, 0, 0, 0, i, 0, 0)), encoding)
        #Check month names
        for i in xrange(1, 13):
            unicode(time.strftime(time_format, (0, i, 0, 0, 0, 0, 0, 0, 0)), encoding)
        #Check AM/PM
        unicode(time.strftime(time_format, (0, 0, 0, 11, 0, 0, 0, 0, 0)), encoding)
        unicode(time.strftime(time_format, (0, 0, 0, 13, 0, 0, 0, 0, 0)), encoding)
        #Check DST
        unicode(time.strftime(time_format, (0, 0, 0, 0, 0, 0, 0, 0, 1)), encoding)
    except:
        logger.exception('Could not decode locale formatted timestamp')
        time_format = DEFAULT_TIME_FORMAT
        encoding = DEFAULT_ENCODING


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
    if shared.config.has_option('bitmessagesettings', 'userlocale'):
        userlocale = shared.config.get('bitmessagesettings', 'userlocale')

    if userlocale in [None, '', 'system']:
        return language

    return userlocale
    
