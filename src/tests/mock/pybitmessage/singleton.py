"""
Singleton decorator definition
"""

from functools import wraps


def Singleton(cls):
    """
    Decorator implementing the singleton pattern:
    it restricts the instantiation of a class to one "single" instance.
    """
    instances = {}

    # https://github.com/sphinx-doc/sphinx/issues/3783
    @wraps(cls)
    def getinstance():
        """Find an instance or save newly created one"""
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance
