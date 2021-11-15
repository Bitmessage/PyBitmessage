import logging

from importlib import import_module

logger = logging.getLogger('default')


def constructObject(data):
    """Constructing an object"""
    whitelist = ["message"]
    if data[""] not in whitelist:
        return None
    try:
        classBase = getattr(import_module(".{}".format(data[""]), __name__), data[""].title())
    except (NameError, AttributeError, ValueError, ImportError):
        logger.error("Don't know how to handle message type: \"%s\"", data[""], exc_info=True)
        return None
    except:  # noqa:E722
        logger.error("Don't know how to handle message type: \"%s\"", data[""], exc_info=True)
        return None

    try:
        returnObj = classBase()
        returnObj.decode(data)
    except KeyError as e:
        logger.error("Missing mandatory key %s", e)
        return None
    except:  # noqa:E722
        logger.error("classBase fail", exc_info=True)
        return None
    else:
        return returnObj


try:
    from pybitmessage import paths
except ImportError:
    paths = None

if paths and paths.frozen is not None:
    from . import message, vote  # noqa: F401 flake8: disable=unused-import
else:
    import os
    for mod in os.listdir(os.path.dirname(__file__)):
        if mod == "__init__.py":
            continue
        splitted = os.path.splitext(mod)
        if splitted[1] != ".py":
            continue
        try:
            import_module(".{}".format(splitted[0]), __name__)
        except ImportError:
            logger.error("Error importing %s", mod, exc_info=True)
        else:
            logger.debug("Imported message type module %s", mod)
