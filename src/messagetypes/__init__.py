import logging
from importlib import import_module
from os import listdir, path
from string import lower

import messagetypes
import paths

logger = logging.getLogger('default')


class MsgBase(object):  # pylint: disable=too-few-public-methods
    """Base class for message types"""
    def __init__(self):
        self.data = {"": lower(type(self).__name__)}


def constructObject(data):
    """Constructing an object"""
    whitelist = ["message"]
    if data[""] not in whitelist:
        return None
    try:
        classBase = getattr(getattr(messagetypes, data[""]), data[""].title())
    except (NameError, AttributeError):
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
    import message  # noqa : F401 flake8: disable=unused-import
    import vote     # noqa : F401 flake8: disable=unused-import
else:
    for mod in listdir(path.dirname(__file__)):
        if mod == "__init__.py":
            continue
        splitted = path.splitext(mod)
        if splitted[1] != ".py":
            continue
        try:
            import_module(".{}".format(splitted[0]), "messagetypes")
        except ImportError:
            logger.error("Error importing %s", mod, exc_info=True)
        else:
            logger.debug("Imported message type module %s", mod)
