# pylint: disable=no-else-return, too-many-return-statements

"""To check the platform"""

from sys import platform as _sys_platform
from os import environ


def _get_platform():
    kivy_build = environ.get("KIVY_BUILD", "")
    if kivy_build in {"android", "ios"}:
        return kivy_build
    elif "P4A_BOOTSTRAP" in environ:
        return "android"
    elif "ANDROID_ARGUMENT" in environ:
        return "android"
    elif _sys_platform in ("win32", "cygwin"):
        return "win"
    elif _sys_platform == "darwin":
        return "macosx"
    elif _sys_platform.startswith("linux"):
        return "linux"
    elif _sys_platform.startswith("freebsd"):
        return "linux"
    return "unknown"


platform = _get_platform()

if platform not in ("android", "unknown"):
    environ["KIVY_CAMERA"] = "opencv"
