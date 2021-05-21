"""
This module is used for running test cases ui order.
"""
import unittest


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
