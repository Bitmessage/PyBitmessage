# pylint: disable=not-context-manager
"""
Fabric tasks for PyBitmessage devops operations.

# pylint: disable=not-context-manager
"""

import os
import sys

from fabric.api import run, task, hide, cd
from fabvenv import virtualenv

from fabfile.lib import (
    autopep8, PROJECT_ROOT, VENV_ROOT, coerce_bool, flatten,
    get_filtered_pycodestyle_output, get_filtered_flake8_output, get_filtered_pylint_output,
)


def get_tool_results(file_list):
    """Take a list of files and resuln the results of applying the tools"""

    results = []
    for path_to_file in file_list:
        result = {}
        result['pycodestyle_violations'] = get_filtered_pycodestyle_output(path_to_file)
        result['flake8_violations'] = get_filtered_flake8_output(path_to_file)
        result['pylint_violations'] = get_filtered_pylint_output(path_to_file)
        result['path_to_file'] = path_to_file
        result['total_violations'] = sum([
                len(result['pycodestyle_violations']),
                len(result['flake8_violations']),
                len(result['pylint_violations']),
        ])
        results.append(result)
    return results


def print_results(results, top, verbose, details):
    """Print an item with the appropriate verbosity / detail"""

    if verbose:
        print ''.join(
            [
                os.linesep,
                'total pycodestyle flake8 pylint path_to_file',
                os.linesep,
            ]
        )

    for item in sort_and_slice(results, top):

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


def sort_and_slice(results, top):
    """Sort dictionary items by the `total_violations` key and honour top"""

    returnables = []
    for item in sorted(
            results,
            reverse=True,
            key=lambda x: x['total_violations']
    )[:top]:
        returnables.append(item)
    return returnables


def generate_file_list(filename):
    """Return an unfiltered list of absolute paths to the files to act on"""

    with hide('warnings', 'running', 'stdout'):
        with virtualenv(VENV_ROOT):

            if filename:
                filename = os.path.abspath(filename)
                if not os.path.exists(filename):
                    print "Bad filename, specify a Python file"
                    sys.exit(1)
                else:
                    file_list = [filename]

            else:
                with cd(PROJECT_ROOT):
                    file_list = [
                        os.path.abspath(i.rstrip('\r'))
                        for i in run('find . -name "*.py"').split(os.linesep)
                    ]

    return file_list


@task
def code_quality(verbose=True, details=False, fix=False, filename=None, top=10):
    """
    Check code quality.

    By default this command will analyse each Python file in the project with a variety of tools and display the count
    or details of the violations discovered, sorted by most violations first.

    Default usage:

    $ fab -H localhost code_quality

    :param top: Display / fix only the top N violating files, a value of 0 will display / fix all files
    :type top: int, default 10
    :param verbose: Display a header and the counts, without this you just get the filenames in order
    :type verbose: bool, default True
    :param details: Display the violations one per line after the count / file summary
    :type details: bool, default False
    :param fix: Run autopep8 aggressively on the displayed file(s)
    :type fix: bool, default False
    :param filename: Rather than analysing all files and displaying / fixing the top N, just analyse / display / fix
    the specified file
    :type filename: string, valid path to a file, default all files in the project
    :return: This fabric task has an exit status equal to the total number of violations and uses stdio but it does
    not return anything if you manage to call it successfully from Python
    :rtype: None

    Intended to be temporary until we have improved code quality and have safeguards to maintain it in place.

    """

    verbose = coerce_bool(verbose)
    details = coerce_bool(details)
    fix = coerce_bool(fix)
    top = int(top) or -1

    file_list = generate_file_list(filename)
    results = get_tool_results(file_list)

    if fix:
        for item in sort_and_slice(results, top):
            autopep8(item['path_to_file'])
    # Recalculate results after autopep8 to surprise the user the least
    results = get_tool_results(file_list)

    print_results(results, top, verbose, details)
    sys.exit(sum([item['total_violations'] for item in results]))
