#! /usr/bin/env python

import atexit
import os
import sys
import state

try:
    import fcntl  # @UnresolvedImport
except ImportError:
    pass



class singleinstance:
    """
    Implements a single instance application by creating a lock file
    at appdata.

    This is based upon the singleton class from tendo
    https://github.com/pycontribs/tendo
    which is under the Python Software Foundation License version 2
    """
    def __init__(self, flavor_id="", daemon=False):
        self.initialized = False
        self.counter = 0
        self.daemon = daemon
        self.lockPid = None
        self.lockfile = os.path.normpath(
            os.path.join(state.appdata, 'singleton%s.lock' % flavor_id))

        if state.enableGUI and not state.kivy and not self.daemon and not state.curses:
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
                # file already exists, we try to remove
                # (in case previous execution was interrupted)
                if os.path.exists(self.lockfile):
                    os.unlink(self.lockfile)
                self.fd = os.open(
                    self.lockfile,
                    os.O_CREAT | os.O_EXCL | os.O_RDWR | os.O_TRUNC
                )
            except OSError:
                type, e, tb = sys.exc_info()
                if e.errno == 13:
                    print(
                        'Another instance of this application'
                        ' is already running'
                    )
                    sys.exit(-1)
                print(e.errno)
                raise
            else:
                pidLine = "%i\n" % self.lockPid
                os.write(self.fd, pidLine)
        else:  # non Windows
            self.fp = open(self.lockfile, 'a+')
            try:
                if self.daemon and self.lockPid != os.getpid():
                    # wait for parent to finish
                    fcntl.lockf(self.fp, fcntl.LOCK_EX)
                else:
                    fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
                self.lockPid = os.getpid()
            except IOError:
                print 'Another instance of this application is already running'
                sys.exit(-1)
            else:
                pidLine = "%i\n" % self.lockPid
                self.fp.truncate(0)
                self.fp.write(pidLine)
                self.fp.flush()

    def cleanup(self):
        if not self.initialized:
            return
        if self.daemon and self.lockPid == os.getpid():
            # these are the two initial forks while daemonizing
            try:
                if sys.platform == 'win32':
                    if hasattr(self, 'fd'):
                        os.close(self.fd)
                else:
                    fcntl.lockf(self.fp, fcntl.LOCK_UN)
            except Exception, e:
                pass

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
        except Exception:
            pass
