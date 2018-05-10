"""
Fabric is a Python library for performing devops tasks. If you have Fabric installed (systemwide or via pip) you can
run commands like this:

    $ fab code_quality

For a list of commands

"""

from fabfile.tasks import code_quality


__all__ = ["code_quality"]
