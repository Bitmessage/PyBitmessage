"""
py2app/py2exe build script for Bitmessage

Usage (Mac OS X):
     python setup.py py2app

Usage (Windows):
     python setup.py py2exe
"""

import sys, os, shutil, re
from setuptools import setup  # @UnresolvedImport


name = "Bitmessage"
mainscript = 'bitmessagemain.py'
version = "0.3.5"

if sys.platform == 'darwin':
    extra_options = dict(
        setup_requires=['py2app'],
        app=[mainscript],
        options=dict(py2app=dict(argv_emulation=True,
                                 includes = ['PyQt4.QtCore','PyQt4.QtGui', 'sip', 'sqlite3'],
                                 packages = ['bitmessageqt'],
                                 frameworks = ['/usr/local/opt/openssl/lib/libcrypto.dylib'],
                                 iconfile='images/bitmessage.icns',
                                 resources=["images"])),
    )
elif sys.platform == 'win32':
    extra_options = dict(
        setup_requires=['py2exe'],
        app=[mainscript],
    )
else:
    extra_options = dict(
        # Normally unix-like platforms will use "setup.py install"
        # and install the main script as such
        scripts=[mainscript],
    )

setup(
    name = name,
    version = version,
    **extra_options
)
from distutils import dir_util
import glob

if sys.platform == 'darwin':
    resource = "dist/" + name + ".app/Contents/Resources/"
    framework = "dist/" + name + ".app/Contents/Frameworks/"

    # The pyElliptive module only works with hardcoded libcrypto paths so rename it so it can actually find it.
    libs = glob.glob(framework + "libcrypto*.dylib")
    for lib in libs:
      os.rename(lib, framework + "libcrypto.dylib")
      break

    # Try to locate qt_menu
    # Let's try the port version first!
    if os.path.isfile("/opt/local/lib/Resources/qt_menu.nib"):
      qt_menu_location = "/opt/local/lib/Resources/qt_menu.nib"
    else:
      # No dice? Then let's try the brew version
      qt_menu_location = os.popen("find /usr/local/Cellar -name qt_menu.nib | tail -n 1").read()
      qt_menu_location = re.sub('\n','', qt_menu_location)

    if(len(qt_menu_location) == 0):
      print "Sorry couldn't find your qt_menu.nib this probably won't work"
    else:
      print "Found your qib: " + qt_menu_location

    # Need to include a copy of qt_menu.nib
    shutil.copytree(qt_menu_location, resource + "qt_menu.nib")
    # Need to touch qt.conf to avoid loading 2 sets of Qt libraries
    fname = resource + "qt.conf"
    with file(fname, 'a'):
        os.utime(fname, None)

