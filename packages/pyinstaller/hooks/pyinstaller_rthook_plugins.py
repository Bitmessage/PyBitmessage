"""Runtime PyInstaller hook to load plugins"""

# pylint: disable=unused-import
import os
import sys

homepath = os.path.abspath(os.path.dirname(sys.argv[0]))

os.environ['PATH'] += ';' + ';'.join([
    homepath, os.path.join(homepath, 'Tor'),
    os.path.abspath(os.curdir)
])

try:
    import pybitmessage.plugins.menu_qrcode
    import pybitmessage.plugins.proxyconfig_stem  # noqa:F401
except ImportError:
    pass
