#! /usr/bin/env python

import sys
import os
import errno
import shared
from multiprocessing import Process

class singleinstance:
    """
    Implements a single instance application by creating a lock file at appdata.

    This is based upon the singleton class from tendo https://github.com/pycontribs/tendo
    which is under the Python Software Foundation License version 2    
    """
    def __init__(self, flavor_id="", daemon=False):
        import sys
        self.initialized = False
        self.daemon = daemon;
        self.lockfile = os.path.normpath(os.path.join(shared.appdata, 'singleton%s.lock' % flavor_id))

        if not self.daemon:
            # Tells the already running (if any) application to get focus.
            import bitmessageqt
            bitmessageqt.init()

        if sys.platform == 'win32':
            try:
                # file already exists, we try to remove (in case previous execution was interrupted)
                if os.path.exists(self.lockfile):
                    os.unlink(self.lockfile)
                self.fd = os.open(self.lockfile, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            except OSError:
                type, e, tb = sys.exc_info()
                if e.errno == 13:
                    print 'Another instance of this application is already running'
                    sys.exit(-1)
                print(e.errno)
                raise
        else:  # non Windows
            import fcntl  # @UnresolvedImport
            self.fp = open(self.lockfile, 'w')
            try:
                fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except IOError:
                print 'Another instance of this application is already running'
                sys.exit(-1)
        self.initialized = True

    def __del__(self):
        import sys
        if not self.initialized:
            return
        try:
            if sys.platform == 'win32':
                if hasattr(self, 'fd'):
                    os.close(self.fd)
                    os.unlink(self.lockfile)
            else:
                import fcntl  # @UnresolvedImport
                fcntl.lockf(self.fp, fcntl.LOCK_UN)
                if os.path.isfile(self.lockfile):
                    os.unlink(self.lockfile)
        except Exception, e:
            sys.exit(-1)
