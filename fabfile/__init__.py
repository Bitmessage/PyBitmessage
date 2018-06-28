"""
Fabric is a Python library for performing devops tasks. If you have Fabric installed (systemwide or via pip) you can
run commands like this:

    $ fab code_quality

For a list of commands:

    $ fab -l

For help on fabric itself:

    $ fab -h

For more help on a particular command
"""

from fabric.api import env

from fabfile.tasks import code_quality, build_docs, push_docs, clean, test


# Without this, `fab -l` would display the whole docstring as preamble
__doc__ = ""

# This list defines which tasks are made available to the user
__all__ = [
    "code_quality",
    "test",
    "build_docs",
    "push_docs",
    "clean",
]

# Honour the user's ssh client configuration
env.use_ssh_config = True
