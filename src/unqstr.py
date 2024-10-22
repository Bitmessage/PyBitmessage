import sys
import six

def ustr(v):
    if six.PY3:
        if isinstance(v, str):
            return v
        elif isinstance(v, bytes):
            return v.decode("utf-8", "replace")
        else:
            return str(v)
    # assume six.PY2
    if isinstance(v, unicode):
        return v.encode("utf-8", "replace")
    return str(v)

def unic(v):
    if six.PY3:
        return v
    # assume six.PY2
    if isinstance(v, unicode):
        return v
    return unicode(v, "utf-8", "replace")
