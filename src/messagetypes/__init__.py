from importlib import import_module
from pprint import pprint
from os import path, listdir
import sys


def constructObject(data):
    try:
        classBase = eval(data[""] + "." + data[""].title())
    except NameError:
        print "Don't know how to handle message type: \"%s\"" % (data[""])
        return None
    try:
        returnObj = classBase(data)
    except KeyError as e:
        print "Missing mandatory key %s" % (e)
        return None
    except:
        print "classBase fail:"
        pprint(sys.exc_info())
        return None
    else:
        return returnObj

for mod in listdir(path.dirname(__file__)):
    if mod == "__init__.py":
        continue
    splitted = path.splitext(mod)
    if splitted[1] != ".py":
        continue
    try:
        import_module("." + splitted[0], "messagetypes")
    except ImportError:
        print "Error importing %s" % (mod)
        pprint(sys.exc_info())
    else:
        print "Imported %s" % (mod)
