"""
Testing the logger configuration
"""

import logging
import os
import tempfile
import unittest


class TestLogger(unittest.TestCase):
    """A test case for bmconfigparser"""

    conf_template = '''
[loggers]
keys=root

[handlers]
keys=default

[formatters]
keys=default

[formatter_default]
format=%(asctime)s {1} %(message)s

[handler_default]
class=FileHandler
level=NOTSET
formatter=default
args=('{0}', 'w')

[logger_root]
level=DEBUG
handlers=default
'''

    def test_fileConfig(self):
        """Put logging.dat with special pattern and check it was used"""
        tmp = os.environ['BITMESSAGE_HOME'] = tempfile.gettempdir()
        log_config = os.path.join(tmp, 'logging.dat')
        log_file = os.path.join(tmp, 'debug.log')

        def gen_log_config(pattern):
            """A small closure to generate logging.dat with custom pattern"""
            with open(log_config, 'wb') as dst:
                dst.write(self.conf_template.format(log_file, pattern))

        pattern = r' o_0 '
        gen_log_config(pattern)

        try:
            from pybitmessage.debug import logger, resetLogging
            if not os.path.isfile(log_file):  # second pass
                pattern = r' <===> '
                gen_log_config(pattern)
                resetLogging()
        except ImportError:
            self.fail('There is no package pybitmessage. Things gone wrong.')
        finally:
            os.remove(log_config)

        logger_ = logging.getLogger('default')

        self.assertEqual(logger, logger_)

        logger_.info('Testing the logger...')

        self.assertRegexpMatches(open(log_file).read(), pattern)
