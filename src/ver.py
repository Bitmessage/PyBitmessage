import sys

if not hasattr(sys, "hexversion"):
    sys.exit("Python version: {0}\n"
             "PyBitmessage requires Python 2.7.4 or greater"
             .format(sys.version))

if sys.hexversion < 0x3000000:
    VER = 2
else:
    VER = 3

def ustr(v):
    if VER == 3:
        if isinstance(v, str):
            return v
        else:
            return str(v)
    # assume VER == 2
    if isinstance(v, unicode):
        return v.encode("utf-8", "replace")
    return str(v)

def unic(v):
    if VER == 3:
        return v
    # assume VER == 2
    if isinstance(v, unicode):
        return v
    return unicode(v, "utf-8", "replace")
