# pylint: disable=not-context-manager
"""
Fabric tasks for PyBitmessage devops operations.

Note that where tasks declare params to be bools, they use coerce_bool() and so will accept any commandline (string)
representation of true or false that coerce_bool() understands.

"""

import os
import sys

from fabric.api import run, task, hide, cd, settings, sudo
from fabric.contrib.project import rsync_project
from fabvenv import virtualenv

from fabfile.lib import (
    autopep8, PROJECT_ROOT, VENV_ROOT, coerce_bool, flatten, filelist_from_git, default_hosts,
    get_filtered_pycodestyle_output, get_filtered_flake8_output, get_filtered_pylint_output,
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')))  # noqa:E402
from version import softwareVersion  # pylint: disable=wrong-import-position


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

    if verbose and results:
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


def create_dependency_graphs():
    """
    To better understand the relationship between methods, dependency graphs can be drawn between functions and
    methods.

    Since the resulting images are large and could be out of date on the next commit, storing them in the repo is
    pointless. Instead, it makes sense to build a dependency graph for a particular, documented version of the code.

    .. todo:: Consider saving a hash of the intermediate dotty file so unnecessary image generation can be avoided.

    """
    with virtualenv(VENV_ROOT):
        with hide('running', 'stdout'):

            # .. todo:: consider a better place to put this, use a particular commit
            with cd(PROJECT_ROOT):
                with settings(warn_only=True):
                    if run('stat pyan').return_code:
                        run('git clone https://github.com/davidfraser/pyan.git')
            with cd(os.path.join(PROJECT_ROOT, 'pyan')):
                run('git checkout pre-python3')

            # .. todo:: Use better settings. This is MVP to make a diagram
            with cd(PROJECT_ROOT):
                file_list = run("find . -type f -name '*.py' ! -path './src/.eggs/*'").split('\r\n')
                for cmd in [
                        'neato -Goverlap=false -Tpng > deps-neato.png',
                        'sfdp -Goverlap=false -Tpng > deps-sfdp.png',
                        'dot -Goverlap=false -Tpng > deps-dot.png',
                ]:
                    pyan_cmd = './pyan/pyan.py {} --dot'.format(' '.join(file_list))
                    sed_cmd = r"sed s'/http\-old/http_old/'g"  # dot doesn't like dashes
                    run('|'.join([pyan_cmd, sed_cmd, cmd]))

                run('mv *.png docs/_build/html/_static/')


@task
@default_hosts(['localhost'])
def code_quality(verbose=True, details=False, fix=False, filename=None, top=10, rev=None):
    """
    Check code quality.

    By default this command will analyse each Python file in the project with a variety of tools and display the count
    or details of the violations discovered, sorted by most violations first.

    Default usage:

    $ fab -H localhost code_quality

    :param rev: If not None, act on files changed since this commit. 'cached/staged' and 'working' have special meaning
    :type rev: str or None, default None
    :param top: Display / fix only the top N violating files, a value of 0 will display / fix all files
    :type top: int, default 10
    :param verbose: Display a header and the counts, without this you just get the filenames in order
    :type verbose: bool, default True
    :param details: Display the violations one per line after the count / file summary
    :type details: bool, default False
    :param fix: Run autopep8 aggressively on the displayed file(s)
    :type fix: bool, default False
    :param filename: Don't test/fix the top N, just the specified file
    :type filename: string, valid path to a file, default all files in the project
    :return: None, exit status equals total number of violations
    :rtype: None

    Intended to be temporary until we have improved code quality and have safeguards to maintain it in place.

    """
    # pylint: disable=too-many-arguments

    verbose = coerce_bool(verbose)
    details = coerce_bool(details)
    fix = coerce_bool(fix)
    top = int(top) or -1

    file_list = generate_file_list(filename) if not rev else filelist_from_git(rev)
    results = get_tool_results(file_list)

    if fix:
        for item in sort_and_slice(results, top):
            autopep8(item['path_to_file'])
        # Recalculate results after autopep8 to surprise the user the least
        results = get_tool_results(file_list)

    print_results(results, top, verbose, details)
    sys.exit(sum([item['total_violations'] for item in results]))


@task
@default_hosts(['localhost'])
def test():
    """Run tests on the code"""

    with cd(PROJECT_ROOT):
        with virtualenv(VENV_ROOT):

            run('pip uninstall -y pybitmessage')
            run('python setup.py install')

            run('pybitmessage -t')
            run('python setup.py test')


@task
@default_hosts(['localhost'])
def build_docs(dep_graph=False, apidoc=True):
    """
    Build the documentation locally.

    :param dep_graph: Build the dependency graphs
    :type dep_graph: Bool, default False
    :param apidoc: Build the automatically generated rst files from the source code
    :type apidoc: Bool, default True

    Default usage:

        $ fab -H localhost build_docs

    Implementation:

    First, a dependency graph is generated and converted into an image that is referenced in the development page.

    Next, the sphinx-apidoc command is (usually) run which searches the code. As part of this it loads the modules and
    if this has side-effects then they will be evident. Any documentation strings that make use of Python documentation
    conventions (like parameter specification) or the Restructured Text (RsT) syntax will be extracted.

    Next, the `make html` command is run to generate HTML output. Other formats (epub, pdf) are available.

    .. todo:: support other languages

    """

    apidoc = coerce_bool(apidoc)

    if coerce_bool(dep_graph):
        create_dependency_graphs()

    with virtualenv(VENV_ROOT):
        with hide('running'):

            apidoc_result = 0
            if apidoc:
                run('mkdir -p {}'.format(os.path.join(PROJECT_ROOT, 'docs', 'autodoc')))
                with cd(os.path.join(PROJECT_ROOT, 'docs', 'autodoc')):
                    with settings(warn_only=True):
                        run('rm *.rst')
                with cd(os.path.join(PROJECT_ROOT, 'docs')):
                    apidoc_result = run('sphinx-apidoc -o autodoc ..').return_code

            with cd(os.path.join(PROJECT_ROOT, 'docs')):
                make_result = run('make html').return_code
                return_code = apidoc_result + make_result

    sys.exit(return_code)


@task
@default_hosts(['localhost'])
def push_docs(path=None):
    """
    Upload the generated docs to a public server.

    Default usage:

        $ fab -H localhost push_docs

    .. todo:: support other languages
    .. todo:: integrate with configuration management data to get web root and webserver restart command

    """

    # Making assumptions
    WEB_ROOT = path if path is not None else os.path.join('var', 'www', 'html', 'pybitmessage', 'en', 'latest')
    VERSION_ROOT = os.path.join(os.path.dirname(WEB_ROOT), softwareVersion)

    rsync_project(
        remote_dir=VERSION_ROOT,
        local_dir=os.path.join(PROJECT_ROOT, 'docs', '_build', 'html')
    )
    result = run('ln -sf {0} {1}'.format(WEB_ROOT, VERSION_ROOT))
    if result.return_code:
        print 'Linking the new release failed'

    # More assumptions
    sudo('systemctl restart apache2')


@task
@default_hosts(['localhost'])
def clean():
    """Clean up files generated by fabric commands."""
    with hide('running', 'stdout'):
        with cd(PROJECT_ROOT):
            run(r"find . -name '*.pyc' -exec rm '{}' \;")
