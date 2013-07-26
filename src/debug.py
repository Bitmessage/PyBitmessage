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
import shared

# TODO(xj9): Get from a config file.
log_level = 'DEBUG'

def configureLogging():
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '%(asctime)s - %(levelname)s - %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'level': log_level,
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'default',
                'level': log_level,
                'filename': shared.appdata + 'debug.log',
                'maxBytes': 2097152, # 2 MiB
                'backupCount': 1,
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
# TODO (xj9): Get from a config file.
#logger = logging.getLogger('console_only')
configureLogging()
logger = logging.getLogger('both')

def restartLoggingInUpdatedAppdataLocation():
    global logger
    for i in list(logger.handlers):
        logger.removeHandler(i)
        i.flush()
        i.close()
    configureLogging()
    logger = logging.getLogger('both')