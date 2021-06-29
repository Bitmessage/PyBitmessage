"""
This module is used for running test cases ui order.
"""
import unittest

from pybitmessage import state


def make_ordered_test():
    """this method is for compairing and arranging in order"""
    order = {}

    def ordered_method(f):
        """method for ordering"""
        order[f.__name__] = len(order)
        return f

    def compare_method(a, b):
        """method for compairing order of methods"""
        return [1, -1][order[a] < order[b]]

    return ordered_method, compare_method


ordered, compare = make_ordered_test()
unittest.defaultTestLoader.sortTestMethodsUsing = compare


def skip_screen_checks(x):
    """This methos is skipping current screen checks"""
    def inner(y):
        """Inner function"""
        if not state.isKivyworking:
            return unittest.skip('Kivy is not working')
        else:
            x(y)
    return inner
