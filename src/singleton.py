"""
src/singleton.py
================
"""


def Singleton(cls):
    """Decorator to ensure decorated classes remain singletons"""
    instances = {}

    def getinstance():
        """Decorrated function"""
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance
