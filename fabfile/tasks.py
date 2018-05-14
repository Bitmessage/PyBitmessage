"""
Fabric tasks for PyBitmessage devops operations.
"""

import os
import sys

from fabric.api import run, task, hide, cd
from fabvenv import virtualenv

from fabfile.lib import pycodestyle, flake8, pylint, autopep8, PROJECT_ROOT, VENV_ROOT, coerce_bool, flatten


def get_tool_results(file_list):
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
    or details of the violations discovered, sorted by most violations first.

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

    with hide('warnings', 'running', 'stdout'):  # pylint: disable=not-context-manager
        with virtualenv(VENV_ROOT):
            if filename:
                filename = os.path.abspath(filename)
                if not os.path.exists(filename):
                    print "Bad filename, specify a Python file"
                    sys.exit(1)
                else:
                    file_list = [filename]
            else:
                with cd(PROJECT_ROOT):  # pylint: disable=not-context-manager
                    file_list = [
                        os.path.abspath(i.rstrip('\r'))
                        for i in run('find . -name "*.py"').split("\n")
                    ]

    if fix:
        for path_to_file in file_list:
            autopep8(path_to_file)

    results = get_tool_results(file_list)

    if verbose:
        print "\ntotal pycodestyle flake8 pylint path_to_file\n"

    # Sort and slice
    for item in sorted(
            results,
            reverse=True,
            key=lambda x: x['total_violations']
    )[:end]:

        print_item(item, verbose, details)
