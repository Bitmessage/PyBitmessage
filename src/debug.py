"""
Logging and debuging facility
=============================

Levels:

   DEBUG
      Detailed information, typically of interest only when diagnosing problems.
   INFO
      Confirmation that things are working as expected.
   WARNING
      An indication that something unexpected happened, or indicative of some problem in the
      near future (e.g. 'disk space low'). The software is still working as expected.
   ERROR
      Due to a more serious problem, the software has not been able to perform some function.
   CRITICAL
      A serious error, indicating that the program itself may be unable to continue running.

There are three loggers: `console_only`, `file_only` and `both`.

Use: `from debug import logger` to import this facility into whatever module you wish to log messages from.
    Logging is thread-safe so you don't have to worry about locks, just import and log.

"""

import ConfigParser
import logging
import logging.config
import os
import sys
import helper_startup
import state

helper_startup.loadConfig()
# Now can be overriden from a config file, which uses standard python
# logging.config.fileConfig interface
# examples are here:
# https://bitmessage.org/forum/index.php/topic,4820.msg11163.html#msg11163
log_level = 'WARNING'


def log_uncaught_exceptions(ex_cls, ex, tb):
    logging.critical('Unhandled exception', exc_info=(ex_cls, ex, tb))


def configureLogging():
    fail_msg = ''
    try:
        logging_config = os.path.join(state.appdata, 'logging.dat')
        logging.config.fileConfig(logging_config)
        return (
            False,
            'Loaded logger configuration from %s' % logging_config
        )
    except (OSError, ConfigParser.NoSectionError):
        if os.path.isfile(logging_config):
            fail_msg = \
                'Failed to load logger configuration from %s, using default' \
                ' logging config\n%s' % \
                (logging_config, sys.exc_info())
        else:
            # no need to confuse the user if the logger config is missing entirely
            fail_msg = 'Using default logger configuration'

    sys.excepthook = log_uncaught_exceptions

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
                'filename': os.path.join(state.appdata, 'debug.log'),
                'maxBytes': 2097152,  # 2 MiB
                'backupCount': 1,
                'encoding': 'UTF-8',
            }
        },
        'loggers': {
            'console_only': {
                'handlers': ['console'],
                'propagate': 0
            },
            'file_only': {
                'handlers': ['file'],
                'propagate': 0
            },
            'both': {
                'handlers': ['console', 'file'],
                'propagate': 0
            },
        },
        'root': {
            'level': log_level,
            'handlers': ['console'],
        },
    })

    return True, fail_msg


def initLogging():
    preconfigured, msg = configureLogging()
    if preconfigured:
        if '-c' in sys.argv:
            logger = logging.getLogger('file_only')
        else:
            logger = logging.getLogger('both')
    else:
        logger = logging.getLogger('default')

    if msg:
        logger.log(logging.WARNING if preconfigured else logging.INFO, msg)
    return logger


def resetLogging():
    global logger
    for i in logger.handlers.iterkeys():
        logger.removeHandler(i)
        i.flush()
        i.close()
    logger = initLogging()


# !
logger = initLogging()
