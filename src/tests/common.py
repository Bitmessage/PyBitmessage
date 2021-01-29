import os
import sys
import time
import unittest


_files = (
    'keys.dat', 'debug.log', 'messages.dat', 'knownnodes.dat',
    '.api_started', 'unittest.lock'
)


def cleanup(home=None, files=_files):
    """Cleanup application files"""
    if not home:
        import state
        home = state.appdata
    for pfile in files:
        try:
            os.remove(os.path.join(home, pfile))
        except OSError:
            pass


def skip_python3():
    """Raise unittest.SkipTest() if detected python3"""
    if sys.hexversion >= 0x3000000:
        raise unittest.SkipTest('Module is not ported to python3')


def put_signal_file(path, filename):
    """Creates file, presence of which is a signal about some event."""
    with open(os.path.join(path, filename), 'wb') as outfile:
        outfile.write(b'%i' % time.time())
