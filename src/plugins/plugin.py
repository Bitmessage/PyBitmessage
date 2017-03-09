# -*- coding: utf-8 -*-

import pkg_resources


def get_plugins(group, point='', name=None):
    for plugin in pkg_resources.iter_entry_points(group):
        if plugin.name == name or plugin.name.startswith(point):
            try:
                yield plugin.load().connect_plugin
            except (AttributeError,
                    pkg_resources.DistributionNotFound,
                    pkg_resources.UnknownExtra):
                continue
