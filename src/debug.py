#!/usr/bin/env python2.7

import logging
import logging.config

log_level = 'DEBUG' # Get from a config file at some point?

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
            'filename': 'bm.log',
            'maxBytes': 1024,
            'backupCount': 0,
        }
    },
    'loggers': {
        'console_only': {
            'handlers': ['console']
        },
        'both': {
            'handlers': ['console', 'file']
        },
    },
    'root': {
        'level': log_level,
        'handlers': ['console']
    },
})

logger = logging.getLogger('console_only')
