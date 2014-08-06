
import logging
import time

import shared


#logger = logging.getLogger(__name__)
logger = logging.getLogger('file_only')

try:
    import locale
    encoding = locale.getpreferredencoding(False)
    language = locale.getlocale()[0] or locale.getdefaultlocale()[0]
except:
    logger.exception('Could not determine language or encoding')
    if not encoding:
        encoding = 'ISO8859-1'
    language = 'en_US'


time_format = shared.config.get('bitmessagesettings', 'timeformat')

def formatTimestamp(timestamp = None, as_unicode = True):
    if timestamp and isinstance(timestamp, (float, int)):
        timestring = time.strftime(time_format, time.localtime(timestamp))
    else:
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
    
