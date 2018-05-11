"""
<<<<<<< HEAD
Fabric is a Python library for performing devops tasks. If you have Fabric installed (systemwide or via pip) you can
run commands from within the project directory like this:

    $ fab code_quality

For a list of commands:

    $ fab -l

Known bugs:

=======
Fabric tasks for PyBitmessage devops operations.
>>>>>>> 81c272dbc332d842b7f8ab548ebeef2dd9a73995
"""

import os
import sys

<<<<<<< HEAD
import fabric
from fabric.api import run, task, hide, cd
from fabfile.lib import pycodestyle, flake8, pylint, autopep8, PROJECT_ROOT, VENV_ROOT
from fabvenv import virtualenv


fabric.state.output['running'] = False


@task
def code_quality(top=10, verbose=True, details=False, fix=True, filename=None):
    """Intended to be temporary until we have improved code quality and have safeguards to maintain it in place."""

    end = int(top) if int(top) else -1

    if verbose == "0":
        verbose = False
    if not isinstance(verbose, bool):
        print "Bad verbosity value, try 0"
        sys.exit(1)

    if details == "1":
        details = True
    if not isinstance(details, bool):
        print "Bad details value, try 1"
        sys.exit(1)

    if fix == "0":
        fix = False
    if not isinstance(fix, bool):
        print "Bad fix value, try 0"
        sys.exit(1)

    with hide('warnings'):
=======
from fabric.api import run, task, hide, cd
from fabvenv import virtualenv

from fabfile.lib import pycodestyle, flake8, pylint, autopep8, PROJECT_ROOT, VENV_ROOT, coerce_bool, flatten


def get_results_for_tools_applied_to_file_list(file_list):
    """Take a list of files and resuln the results of applying the tools"""
    results = []
    for path_to_file in file_list:
        result = {}

        result['pycodestyle_violations'] = [
            i
            for i in pycodestyle(path_to_file).split("\n")
            if i
        ]
        result['flake8_violations'] = [
            i
            for i in flake8(path_to_file).split("\n")
            if i
        ]
        result['pylint_violations'] = [
            i
            for i in pylint(path_to_file).split("\n")
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
        result['path_to_file'] = path_to_file
        result['total_violations'] = sum(
            [
                len(result['pycodestyle_violations']),
                len(result['flake8_violations']),
                len(result['pylint_violations']),
            ]
        )
        results.append(result)
        return results


def print_item(item, verbose, details):
    """Print an item with the appropriate verbosity / detail"""
    if verbose:
        line = "{0} {1} {2} {3} {4}".format(
            item['total_violations'],
            len(item['pycodestyle_violations']),
            len(item['flake8_violations']),
            len(item['pylint_violations']),
            item['path_to_file'],
        )
    else:
        line = item['path_to_file']
    print line

    if details:
        print "pycodestyle:"
        for detail in flatten(item['pycodestyle_violations']):
            print detail
        print

        print "flake8:"
        for detail in flatten(item['flake8_violations']):
            print detail
        print

        print "pylint:"
        for detail in flatten(item['pylint_violations']):
            print detail
        print


@task
def code_quality(top=10, verbose=True, details=False, fix=False, filename=None):
    """
    Check code quality.

    By default this command will analyse each Python file in the project with a variety of tools and display the count
    or details of the violations discovered, sorted by most iolations first.

    Default usage:

    $ fab -H localhost code_quality

    Options:
        top: Display / fix only the top violating files, a value of 0 will display / fix all files
        verbose: Display a header and the counts. Without this you just get the filenames in order
        details: Display the violations one per line after the count/file summary
        fix: Run autopep8 on the displayed file(s)
        filename: Rather than analysing all files and displaying / fixing the top N, just analyse / diaply / fix the
        specified file

    Intended to be temporary until we have improved code quality and have safeguards to maintain it in place.

    """

    verbose = coerce_bool(verbose)
    details = coerce_bool(details)
    fix = coerce_bool(fix)
    end = int(top) if int(top) else -1

    with hide('warnings', 'running'):  # pylint: disable=not-context-manager
>>>>>>> 81c272dbc332d842b7f8ab548ebeef2dd9a73995
        with virtualenv(VENV_ROOT):
            if filename:
                filename = os.path.abspath(filename)
                if not os.path.exists(filename):
                    print "Bad filename, specify a Python file"
                    sys.exit(1)
                else:
                    file_list = [filename]
            else:
<<<<<<< HEAD
                with cd(PROJECT_ROOT):
                    file_list = run('find . -name "*.py"', capture=True).split("\n")

    results = []
    for path_to_file in file_list:

        results.append(
            {
                'pycodestyle_violations': [
                    i
                    for i in pycodestyle(path_to_file).split("\n")
                    if i
                ],
                'flake8_violations': [
                    i
                    for i in flake8(path_to_file).split("\n")
                    if i
                ],
                'pylint_violations': [
                    i
                    for i in pylint(path_to_file).split("\n")
                    if all([
                        i,
                        not i.startswith(' '),
                        not i.startswith('-'),
                        not i.startswith('Y'),
                        not i.startswith('*'),
                    ])
                ],
                'path_to_file': path_to_file,
            }
        )
=======
                with cd(PROJECT_ROOT):  # pylint: disable=not-context-manager
                    file_list = run('find . -name "*.py"').split("\n")

    if fix:
        for path_to_file in file_list:
            autopep8(path_to_file)

    results = get_results_for_tools_applied_to_file_list(file_list)
>>>>>>> 81c272dbc332d842b7f8ab548ebeef2dd9a73995

    if verbose:
        print "\ntotal pycodestyle flake8 pylint path_to_file\n"

<<<<<<< HEAD
    for item in sorted(
            results,
            reverse=True,
            key=lambda x: len(x['pycodestyle_violations']) + len(x['flake8_violations']) + len(x['pylint_violations']),
    )[:end]:

        violation_detail = item['pycodestyle_violations'] + item['flake8_violations'] + item['pylint_violations'],

        if verbose:
            line = "{0} {1} {2} {3} {4}".format(
                len(violation_detail[0]),
                len(item['pycodestyle_violations']),
                len(item['flake8_violations']),
                len(item['pylint_violations']),
                item['path_to_file'],
            )
        else:
            line = item['path_to_file']

        print line
        if details:
            for detail_line in violation_detail:
                if isinstance(detail_line, list):
                    for subline in detail_line:
                        if isinstance(subline, list):
                            for subsubline in subline:
                                print subsubline
                        else:
                            print subline
                else:
                    print detail_line
            print

        if fix:
            autopep8_output = [i for i in autopep8(item['path_to_file']) if i]
            print autopep8_output
=======
    # Sort and slice
    for item in sorted(
            results,
            reverse=True,
            key=lambda x: x['total_violations']
    )[:end]:

        print_item(item, verbose, details)
>>>>>>> 81c272dbc332d842b7f8ab548ebeef2dd9a73995
