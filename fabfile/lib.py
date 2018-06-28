# pylint: disable=not-context-manager
"""
A library of functions and constants for tasks to make use of.

"""

import os
import sys
import re
from functools import wraps

from fabric.api import run, hide, cd, env
from fabric.context_managers import settings, shell_env
from fabvenv import virtualenv


FABRIC_ROOT = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(FABRIC_ROOT)
VENV_ROOT = os.path.expanduser(os.path.join('~', '.virtualenvs', 'pybitmessage-devops'))
PYTHONPATH = os.path.join(PROJECT_ROOT, 'src',)


def coerce_list(value):
    """Coerce a value into a list"""
    if isinstance(value, str):
        return value.split(',')
    else:
        sys.exit("Bad string value {}".format(value))


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
        sys.exit("Bad boolean value {}".format(value))


def flatten(data):
    """Recursively flatten lists"""
    result = []
    for item in data:
        if isinstance(item, list):
            result.append(flatten(item))
        else:
            result.append(item)
    return result


def filelist_from_git(rev=None):
    """Return a list of files based on git output"""
    cmd = 'git diff --name-only'
    if rev:
        if rev in ['cached', 'staged']:
            cmd += ' --{}'.format(rev)
        elif rev == 'working':
            pass
        else:
            cmd += ' -r {}'.format(rev)

    with cd(PROJECT_ROOT):
        with hide('running', 'stdout'):
            results = []
            ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
            clean = ansi_escape.sub('', run(cmd))
            clean = re.sub('\n', '', clean)
            for line in clean.split('\r'):
                if line.endswith(".py"):
                    results.append(os.path.abspath(line))
            return results


def pycodestyle(path_to_file):
    """Run pycodestyle on a file"""
    with virtualenv(VENV_ROOT):
        with hide('warnings', 'running', 'stdout', 'stderr'):
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
        with hide('warnings', 'running', 'stdout'):
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
        with hide('warnings', 'running', 'stdout', 'stderr'):
            with settings(warn_only=True):
                with shell_env(PYTHONPATH=PYTHONPATH):
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
        with hide('running'):
            with settings(warn_only=True):
                return run(
                    "autopep8 --experimental --aggressive --aggressive -i --max-line-length=119 {}".format(
                        path_to_file
                    ),
                )


def get_filtered_pycodestyle_output(path_to_file):
    """Clean up the raw results for pycodestyle"""

    return [
        i
        for i in pycodestyle(path_to_file).split(os.linesep)
        if i
    ]


def get_filtered_flake8_output(path_to_file):
    """Clean up the raw results for flake8"""

    return [
        i
        for i in flake8(path_to_file).split(os.linesep)
        if i
    ]


def get_filtered_pylint_output(path_to_file):
    """Clean up the raw results for pylint"""

    return [
        i
        for i in pylint(path_to_file).split(os.linesep)
        if all([
            i,
            not i.startswith(' '),
            not i.startswith('\r'),
            not i.startswith('-'),
            not i.startswith('Y'),
            not i.startswith('*'),
            not i.startswith('Using config file'),
        ])
    ]


def default_hosts(hosts):
    """Decorator to apply default hosts to a task"""

    def real_decorator(func):
        """Manipulate env"""
        env.hosts = env.hosts or hosts

        @wraps(func)
        def wrapper(*args, **kwargs):
            """Original function called from here"""
            return func(*args, **kwargs)

        return wrapper

    return real_decorator
