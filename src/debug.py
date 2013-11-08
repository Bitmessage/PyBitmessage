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
import sys
import logging
import logging.handlers
import shared


def startLogger(output='console',level='debug',fileToLog='all'):
    if fileToLog == 'all':
        logger = logging.getLogger()
    else:
        logger = logging.getLogger(fileToLog)
        
    fmt_string = "[%(levelname)-7s]%(asctime)s.%(msecs)-3d\
    %(module)s[%(lineno)-3d]/%(funcName)-10s  %(message)-8s "

    # file config
    backupCount = 1 #How many Backup files to hold
    maxBytes = 2097152 #2Mib
    filename = shared.appdata + 'debug.log'
    
    if output == 'console':
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt_string, "%H:%M:%S"))
        logger.addHandler(handler)
        
    elif output == 'file':
        handler = logging.handlers.RotatingFileHandler(filename,maxBytes=maxBytes,backupCount=backupCount)
        handler.setFormatter(logging.Formatter(fmt_string, "%H:%M:%S"))
        logger.addHandler(handler)
        
    elif output == 'both':
        #add console
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt_string, "%H:%M:%S"))
        logger.addHandler(handler)
        #add file
        handler = logging.handlers.RotatingFileHandler(filename,maxBytes=maxBytes,backupCount=backupCount)
        handler.setFormatter(logging.Formatter(fmt_string, "%H:%M:%S"))
        logger.addHandler(handler)
    

    logger.addHandler(handler)
    
    #configure level
    if level == 'debug':
        logger.setLevel(logging.DEBUG)
    elif level == 'info':
        logger.setLevel(logging.INFO)
    elif level == 'warning':
        logger.setLevel(logging.WARNING)
    elif level == 'error':
        logger.setLevel(logging.ERROR)
    elif level == 'critical':
        logger.setLevel(logging.CRITICAL)


#~ def restartLoggingInUpdatedAppdataLocation():
    #~ global logger
    #~ for i in list(logger.handlers):
        #~ logger.removeHandler(i)
        #~ i.flush()
        #~ i.close()
    #~ configureLogging()
    #~ logger = logging.getLogger('both')
