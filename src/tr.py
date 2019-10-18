"""
src/tr.py
=================================
"""
# pylint: disable=relative-import
import os

import state

"""This is used so that the translateText function can be used """
"""when we are in daemon mode and not using any QT functions."""


class translateClass:        # pylint: disable=old-style-class, too-few-public-methods
    """
    This is used so that the translateText function can be used when we are
    in daemon mode and not using any QT functions.
    """
    def __init__(self, context, text):
        self.context = context
        self.text = text

    def arg(self, argument):        # pylint: disable=unused-argument
        """Replace argument placeholders"""
        if '%' in self.text:
            return translateClass(self.context, self.text.replace('%', '', 1))
            # This doesn't actually do anything with the arguments
            # because we don't have a UI in which to display this information anyway.
        return self.text


def _translate(context, text, disambiguation=None, encoding=None, n=None):      # pylint: disable=unused-argument
    return translateText(context, text, n)

# def _translate(context, text, disambiguation = None, encoding = None, n = None):
#      return translateClass(context, text.replace('%','',1))


def translateText(context, text, n=None):
    """Translate text in context"""
    try:
        enableGUI = state.enableGUI
    except AttributeError:  # inside the plugin
        enableGUI = True
    if not state.kivy and enableGUI:
        try:
            from PyQt4 import QtCore, QtGui
        except Exception as err:
            print ('PyBitmessage requires PyQt unless you want to run it as a daemon and interact with it using the API\
            .You can download PyQt from http://www.riverbankcomputing.com/software/pyqt/download\
            or by searching Google for \'PyQt Download\'.\
            If you want to run in daemon mode, see https://bitmessage.org/wiki/Daemon')
            print ('Error message:', err)
            os._exit(0)      # pylint: disable=protected-access
        if n is None:
            return QtGui.QApplication.translate(context, text)
        return QtGui.QApplication.translate(context, text, None, QtCore.QCoreApplication.CodecForTr, n)
    else:
        if '%' in text:
            return translateClass(context, text.replace('%', '', 1))
        return text
