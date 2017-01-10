#! /usr/bin/env python

import atexit
import errno
from multiprocessing import Process
import os
import sys
import shared

try:
    import fcntl  # @UnresolvedImport
except:
    pass

class singleinstance:
    """
    Implements a single instance application by creating a lock file at appdata.

    This is based upon the singleton class from tendo https://github.com/pycontribs/tendo
    which is under the Python Software Foundation License version 2    
    """
    def __init__(self, flavor_id="", daemon=False):
        self.initialized = False
        self.counter = 0
        self.daemon = daemon
        self.lockPid = None
        self.lockfile = os.path.normpath(os.path.join(shared.appdata, 'singleton%s.lock' % flavor_id))

        if not self.daemon and not shared.curses:
            # Tells the already running (if any) application to get focus.
            import bitmessageqt
            bitmessageqt.init()

        self.lock()

        self.initialized = True
        atexit.register(self.cleanup)

    def lock(self):
        if self.lockPid is None:
            self.lockPid = os.getpid()
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
            self.fp = open(self.lockfile, 'w')
            try:
                if self.daemon and self.lockPid != os.getpid():
                    fcntl.lockf(self.fp, fcntl.LOCK_EX) # wait for parent to finish
                else:
                    fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
                self.lockPid = os.getpid()
            except IOError:
                print 'Another instance of this application is already running'
                sys.exit(-1)

    def cleanup(self):
        if not self.initialized:
            return
        if self.daemon and self.lockPid == os.getpid():
            # these are the two initial forks while daemonizing
            return
        print "Cleaning up lockfile"
        try:
            if sys.platform == 'win32':
                if hasattr(self, 'fd'):
                    os.close(self.fd)
                    os.unlink(self.lockfile)
            else:
                fcntl.lockf(self.fp, fcntl.LOCK_UN)
                if os.path.isfile(self.lockfile):
                    os.unlink(self.lockfile)
        except Exception, e:
            pass
