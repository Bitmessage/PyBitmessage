from sys import platform as _sys_platform
from os import environ

"""
We need to check platform and set environ for KIVY_CAMERA, if requires, before importing kivy.

We cannot use sys.platform directly because it returns 'linux' on android devices as well.
We cannot use kivy.util.platform beacuse it imports kivy beforehand and thus setting environ
after that doesn't make any sense.

So we needed to copy the `_get_platform` function from kivy.utils
"""


def _get_platform():
    # On Android sys.platform returns 'linux2', so prefer to check the
    # existence of environ variables set during Python initialization
    kivy_build = environ.get("KIVY_BUILD", "")
    if kivy_build in {"android", "ios"}:
        return kivy_build
    elif "P4A_BOOTSTRAP" in environ:
        return "android"
    elif "ANDROID_ARGUMENT" in environ:
        # We used to use this method to detect android platform,
        # leaving it here to be backwards compatible with `pydroid3`
        # and similar tools outside kivy's ecosystem
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
    """
    After tweaking a little bit with opencv camera, it's possible to make camera
    go on and off as required while the app is still running.

    Other camera provider such as `gi` has some issue upon closing the camera.
    by setting KIVY_CAMERA environment variable before importing kivy, we are forcing it to use opencv camera provider.
    """
    environ["KIVY_CAMERA"] = "opencv"
