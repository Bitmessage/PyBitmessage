import os
import textwrap

import shared

_codec = None


# This is used so that the translateText function can be used
# when we are in daemon mode and not using any Qt functions.
class translateClass:
    def __init__(self, context, text):
        self.text = text

    def __str__(self):
        return unicode(self.text)

    def arg(self, *args):
        # if args and '%' in self.text:
        #     try:
        #         ''.join(args)
        #     except TypeError:
        #         args = None
        #     self.text = self.text.replace('%', '', len(args) if args else 1)
        # This doesn't actually do anything with the arguments because
        # we don't have a UI in which to display this information anyway.
        return self


def _translate(context, text, disambiguation=None, encoding=None, n=None):
    return translateText(context, text, disambiguation, n)


def translateText(context, text, disambiguation=None, n=None):
    try:
        is_daemon = shared.thisapp.daemon
    except AttributeError:  # inside the plugin
        is_daemon = False
    if is_daemon:
        return translateClass(context, text)

    try:
        from PyQt4 import QtCore, QtGui
    except Exception as err:
        print textwrap.dedent("""
        PyBitmessage requires PyQt unless you want to run it as a daemon
        and interact with it using the API. You can download PyQt from
        http://www.riverbankcomputing.com/software/pyqt/download
        or by searching Google for 'PyQt Download'.
        If you want to run in daemon mode, see
        https://bitmessage.org/wiki/Daemon
        """)
        print 'Error message:', err
        os._exit(0)

    return QtGui.QApplication.translate(
        context, text, disambiguation,
        QtCore.QCoreApplication.CodecForTr, n
        ) if n is not None \
        else QtGui.QApplication.translate(context, text, disambiguation)
