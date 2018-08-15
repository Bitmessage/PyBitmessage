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

from fabfile.tasks import build_docs, clean, code_quality, configure, deploy, push_docs, test, start, stop


# Without this, `fab -l` would display the whole docstring as preamble
__doc__ = ""

# This list defines which tasks are made available to the user
__all__ = [
    "build_docs",
    "clean",
    "code_quality",
    "configure",
    "deploy",
    "push_docs",
    "start",
    "stop",
    "test",
]

# Honour the user's ssh client configuration
env.use_ssh_config = True
