#!/usr/bin/python2.7
# This function mimicks ctypes.util.find_library()
# but allows you to specify a desired library version.
# (c) 2017 Wolfgang Frisch
# based on https://github.com/python/cpython/blob/2.7/Lib/ctypes/util.py

import ctypes.util
import os
import re
import subprocess
import sys


def find_library_version(name, version=None):
    """
    Try to find the desired version of a library, and return a pathname.
    Fall back to ctypes.util.find_library() on platforms other than POSIX.
    :param name: The library name without any prefix like lib,
                 suffix like .so, .dylib or version number.
    :param version: The library version.
    :return: Returns the filename or, if no library can be found, None.
    """
    def _num_version(libname):
        # "libxyz.so.MAJOR.MINOR" => [ MAJOR, MINOR ]
        parts = libname.split(b".")
        nums = []
        try:
            while parts:
                nums.insert(0, int(parts.pop()))
        except ValueError:
            pass
        return nums or [sys.maxint]

    if "linux" in sys.platform:
        ename = re.escape(name)
        expr = r'lib%s\.so[.0-9]*.*? => \S*/(lib%s\.so[.0-9]*)' % (ename, ename)

        null = open(os.devnull, 'wb')
        try:
            with null:
                proc = subprocess.Popen(('/sbin/ldconfig', '-p'),
                                        stdout=subprocess.PIPE,
                                        stderr=null)
        except OSError:  # E.g. command not found
            data = b''
        else:
            [data, _] = proc.communicate()

        res = re.findall(expr, data)
        if not res:
            return None

        res.sort(key=_num_version)
        if version:
            lst = filter(lambda x: x.split("so.")[-1].startswith(version), res)
            if len(lst):
                return lst[-1]
        return res[-1]
    else:
        # fallback (unversioned)
        return ctypes.util.find_library(name)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("example: %s crypto 1.0" % sys.argv[0])
    else:
        name = sys.argv[1]
        version = sys.argv[2] if len(sys.argv) == 3 else None
        print(find_library_version(name, version))


# vim:set expandtab tabstop=4 shiftwidth=4 softtabstop=4 nowrap:
