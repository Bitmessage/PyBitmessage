"""
Testing the logger configuration
"""

import logging
import os
import tempfile
import unittest

from pybitmessage.paths import set_appdata_folder


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

    def test_fileConfig(self):  # pylint: disable=invalid-name
        """Put logging.dat with special pattern and check it was used"""
        # FIXME: this doesn't always work, probably due to module
        # load order. Workaround through .travis.yml
        tmp = set_appdata_folder(tempfile.gettempdir())
        log_config = os.path.join(tmp, 'logging.dat')
        log_file = os.path.join(tmp, 'debug.log')
        pass_ = 1

        def gen_log_config(pattern):
            """A small closure to generate logging.dat with custom pattern"""
            with open(log_config, 'wb') as dst:
                dst.write(self.conf_template.format(log_file, pattern))

        pattern = r' o_0 '
        gen_log_config(pattern)
        pass_ = 1

        try:
            # pylint: disable=import-outside-toplevel
            from pybitmessage.debug import logger, resetLogging, flush_logs
            if not os.path.isfile(log_file):  # second pass
                pattern = r' <===> '
                pass_ = 2
                gen_log_config(pattern)
                resetLogging()
        except ImportError:
            self.fail('There is no package pybitmessage. Things gone wrong.')
        finally:
            os.remove(log_config)

        # pylint: disable=invalid-name
        self.longMessage = True

        logger_ = logging.getLogger('default')

        self.assertEqual(logger, logger_, ", pass {}".
                         format(pass_))

        logger_.info('Testing the logger...')
        flush_logs()

        # pylint: disable=deprecated-method
        self.assertRegexpMatches(open(log_file).read(), pattern,
                                 ", pass {}".format(pass_))
