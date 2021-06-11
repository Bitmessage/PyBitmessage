"""
This module is used for running test cases ui order.
"""
import unittest

from pybitmessage import state


def make_ordered_test():
    """this method is for comparing and arranging in order"""
    order = {}

    def ordered_method(f):
        """method for ordering"""
        order[f.__name__] = len(order)
        return f

    def compare_method(a, b):
        """method for comparing order of methods"""
        return [1, -1][order[a] < order[b]]

    return ordered_method, compare_method


ordered, compare = make_ordered_test()
unittest.defaultTestLoader.sortTestMethodsUsing = compare


def skip_screen_checks(x):
    """This methos is skipping current screen checks"""
    def inner(y):
        """Inner function"""
        if not state.enableKivy:
            return unittest.skip('Kivy not enabled')
        else:
            x(y)
    return inner
