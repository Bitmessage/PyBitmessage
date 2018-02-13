from importlib import import_module
from os import path, listdir
from string import lower

from debug import logger
import paths

class MsgBase(object):
    def encode(self):
        self.data = {"": lower(type(self).__name__)}


def constructObject(data):
    try:
        m = import_module("messagetypes." + data[""])
        classBase = getattr(m, data[""].title())
    except (NameError, ImportError):
        logger.error("Don't know how to handle message type: \"%s\"", data[""], exc_info=True)
        return None
    try:
        returnObj = classBase()
        returnObj.decode(data)
    except KeyError as e:
        logger.error("Missing mandatory key %s", e)
        return None
    except:
        logger.error("classBase fail", exc_info=True)
        return None
    else:
        return returnObj

if paths.frozen is not None:
    import messagetypes.message
    import messagetypes.vote
else:
    for mod in listdir(path.dirname(__file__)):
        if mod == "__init__.py":
            continue
        splitted = path.splitext(mod)
        if splitted[1] != ".py":
            continue
        try:
            import_module("." + splitted[0], "messagetypes")
        except ImportError:
            logger.error("Error importing %s", mod, exc_info=True)
        else:
            logger.debug("Imported message type module %s", mod)
