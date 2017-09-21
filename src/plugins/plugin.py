# -*- coding: utf-8 -*-

import pkg_resources


def get_plugins(group, point='', name=None, fallback=None):
    """
    Iterate through plugins (`connect_plugin` attribute of entry point)
    which name starts with `point` or equals to `name`.
    If `fallback` kwarg specified, plugin with that name yield last.
    """
    for ep in pkg_resources.iter_entry_points('bitmessage.' + group):
        if name and ep.name == name or ep.name.startswith(point):
            try:
                plugin = ep.load().connect_plugin
                if ep.name == fallback:
                    _fallback = plugin
                else:
                    yield plugin
            except (AttributeError,
                    ImportError,
                    ValueError,
                    pkg_resources.DistributionNotFound,
                    pkg_resources.UnknownExtra):
                continue
    try:
        yield _fallback
    except NameError:
        pass


def get_plugin(*args, **kwargs):
    """Returns first available plugin `from get_plugins()` if any."""
    for plugin in get_plugins(*args, **kwargs):
        return plugin
