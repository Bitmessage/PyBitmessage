# -*- coding: utf-8 -*-
'''
Logging and debuging facility
=============================

Levels:
    DEBUG       Detailed information, typically of interest only when diagnosing problems.
    INFO        Confirmation that things are working as expected.
    WARNING     An indication that something unexpected happened, or indicative of some problem in the
                near future (e.g. ‘disk space low’). The software is still working as expected.
    ERROR       Due to a more serious problem, the software has not been able to perform some function.
    CRITICAL    A serious error, indicating that the program itself may be unable to continue running.

There are three loggers: `console_only`, `file_only` and `both`.

Use: `from debug import logger` to import this facility into whatever module you wish to log messages from.
     Logging is thread-safe so you don't have to worry about locks, just import and log.
'''
import logging
import logging.config
import os
import sys
import helper_startup
import state
helper_startup.loadConfig()

# Now can be overriden from a config file, which uses standard python logging.config.fileConfig interface
# examples are here: https://bitmessage.org/forum/index.php/topic,4820.msg11163.html#msg11163
log_level = 'WARNING'

def log_uncaught_exceptions(ex_cls, ex, tb):
    logging.critical('Unhandled exception', exc_info=(ex_cls, ex, tb))

def configureLogging():
    have_logging = False
    try:
        logging.config.fileConfig(os.path.join (state.appdata, 'logging.dat'))
        have_logging = True
        print "Loaded logger configuration from %s" % (os.path.join(state.appdata, 'logging.dat'))
    except:
        if os.path.isfile(os.path.join(state.appdata, 'logging.dat')):
            print "Failed to load logger configuration from %s, using default logging config" % (os.path.join(state.appdata, 'logging.dat'))
            print sys.exc_info()
        else:
            # no need to confuse the user if the logger config is missing entirely
            print "Using default logger configuration"
    
    sys.excepthook = log_uncaught_exceptions

    if have_logging:
        return False

    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': u'%(asctime)s - %(levelname)s - %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'level': log_level,
                'stream': 'ext://sys.stderr'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'default',
                'level': log_level,
                'filename': state.appdata + 'debug.log',
                'maxBytes': 2097152, # 2 MiB
                'backupCount': 1,
                'encoding': 'UTF-8',
            }
        },
        'loggers': {
            'console_only': {
                'handlers': ['console'],
                'propagate' : 0
            },
            'file_only': {
                'handlers': ['file'],
                'propagate' : 0
            },
            'both': {
                'handlers': ['console', 'file'],
                'propagate' : 0
            },
        },
        'root': {
            'level': log_level,
            'handlers': ['console'],
        },
    })
    return True

# TODO (xj9): Get from a config file.
#logger = logging.getLogger('console_only')
if configureLogging():
    if '-c' in sys.argv:
        logger = logging.getLogger('file_only')
    else:
        logger = logging.getLogger('both')
else:
    logger = logging.getLogger('default')

def restartLoggingInUpdatedAppdataLocation():
    global logger
    for i in list(logger.handlers):
        logger.removeHandler(i)
        i.flush()
        i.close()
    if configureLogging():
        if '-c' in sys.argv:
            logger = logging.getLogger('file_only')
        else:
            logger = logging.getLogger('both')
    else:
        logger = logging.getLogger('default')

