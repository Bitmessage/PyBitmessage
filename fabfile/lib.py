"""A library of functions and constrants for tasks to make use of."""

import os
<<<<<<< HEAD
=======
import sys
>>>>>>> 81c272dbc332d842b7f8ab548ebeef2dd9a73995

from fabric.api import run, hide
from fabric.context_managers import settings
from fabvenv import virtualenv


FABRIC_ROOT = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(FABRIC_ROOT)
<<<<<<< HEAD
VENV_ROOT = os.path.expanduser(os.path.join('~', '.virtualenvs', 'pybitmessage'))
=======
VENV_ROOT = os.path.expanduser(os.path.join('~', '.virtualenvs', 'pybitmessage-devops'))


def coerce_bool(value):
    """Coerce a value into a boolean"""
    if isinstance(value, bool):
        return value
    elif any(
            [
                value in [0, '0'],
                value.lower().startswith('n'),
            ]
    ):
        return False
    elif any(
            [
                value in [1, '1'],
                value.lower().startswith('y'),
            ]
    ):
        return True
    else:
        print "Bad boolean value {}".format(value)
        sys.exit(1)


def flatten(data):
    """Recursively flatten lists"""
    result = []
    for item in data:
        if isinstance(item, list):
            result.append(flatten(item))
        else:
            result.append(item)
    return result
>>>>>>> 81c272dbc332d842b7f8ab548ebeef2dd9a73995


def pycodestyle(path_to_file):
    """Run pycodestyle on a file"""
    with virtualenv(VENV_ROOT):
<<<<<<< HEAD
        with hide('warnings', 'running'):
=======
        with hide('warnings', 'running', 'stdout', 'stderr'):  # pylint: disable=not-context-manager
>>>>>>> 81c272dbc332d842b7f8ab548ebeef2dd9a73995
            with settings(warn_only=True):
                return run(
                    'pycodestyle --config={0} {1}'.format(
                        os.path.join(
                            PROJECT_ROOT,
                            'setup.cfg',
                        ),
                        path_to_file,
                    ),
                )


def flake8(path_to_file):
    """Run flake8 on a file"""
    with virtualenv(VENV_ROOT):
<<<<<<< HEAD
        with hide('warnings', 'running'):
=======
        with hide('warnings', 'running', 'stdout'):  # pylint: disable=not-context-manager
>>>>>>> 81c272dbc332d842b7f8ab548ebeef2dd9a73995
            with settings(warn_only=True):
                return run(
                    'flake8 --config={0} {1}'.format(
                        os.path.join(
                            PROJECT_ROOT,
                            'setup.cfg',
                        ),
                        path_to_file,
                    ),
                )


def pylint(path_to_file):
    """Run pylint on a file"""
    with virtualenv(VENV_ROOT):
<<<<<<< HEAD
        with hide('warnings', 'running', 'stdout', 'stderr'):
=======
        with hide('warnings', 'running', 'stdout', 'stderr'):  # pylint: disable=not-context-manager
>>>>>>> 81c272dbc332d842b7f8ab548ebeef2dd9a73995
            with settings(warn_only=True):
                return run(
                    'pylint --rcfile={0} {1}'.format(
                        os.path.join(
                            PROJECT_ROOT,
                            'setup.cfg',
                        ),
                        path_to_file,
                    ),
                )


def autopep8(path_to_file):
    """Run autopep8 on a file"""
    with virtualenv(VENV_ROOT):
<<<<<<< HEAD
        with hide('running'):
            with settings(warn_only=True):
                return run(
                    "autopep8 -ai --max-line-length=119 --hang-closing {}".format(
=======
        with hide('running'):  # pylint: disable=not-context-manager
            with settings(warn_only=True):
                return run(
                    "autopep8 --experimental --aggressive --aggressive -i --max-line-length=119 {}".format(
>>>>>>> 81c272dbc332d842b7f8ab548ebeef2dd9a73995
                        path_to_file
                    ),
                )
