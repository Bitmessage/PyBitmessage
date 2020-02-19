"""
Path related functions
"""
# pylint: disable=import-error
import logging
import os
import re
import sys
from datetime import datetime
from shutil import move
from kivy.utils import platform

logger = logging.getLogger('default')

# When using py2exe or py2app, the variable frozen is added to the sys
# namespace.  This can be used to setup a different code path for
# binary distributions vs source distributions.
frozen = getattr(sys, 'frozen', None)


def lookupExeFolder():
    """Returns executable folder path"""
    if frozen:
        exeFolder = (
            # targetdir/Bitmessage.app/Contents/MacOS/Bitmessage
            os.path.dirname(sys.executable).split(os.path.sep)[0] + os.path.sep
            if frozen == "macosx_app" else
            os.path.dirname(sys.executable) + os.path.sep)
    elif __file__:
        exeFolder = os.path.dirname(__file__) + os.path.sep
    else:
        exeFolder = ''
    return exeFolder


def lookupAppdataFolder():
    """Returns path of the folder where application data is stored"""
    APPNAME = "PyBitmessage"
    dataFolder = os.environ.get('BITMESSAGE_HOME')
    if dataFolder:
        if dataFolder[-1] not in (os.path.sep, os.path.altsep):
            dataFolder += os.path.sep
    elif sys.platform == 'darwin':
        try:
            dataFolder = os.path.join(
                os.environ['HOME'],
                'Library/Application Support/', APPNAME
            ) + '/'

        except KeyError:
            sys.exit(
                'Could not find home folder, please report this message'
                ' and your OS X version to the BitMessage Github.')
    elif platform == 'android':
        dataFolder = os.path.join(os.environ['ANDROID_PRIVATE'] + '/', APPNAME) + '/'
    elif 'win32' in sys.platform or 'win64' in sys.platform:
        dataFolder = os.path.join(
            os.environ['APPDATA'].decode(
                sys.getfilesystemencoding(), 'ignore'), APPNAME
        ) + os.path.sep
    else:
        try:
            dataFolder = os.path.join(os.environ['XDG_CONFIG_HOME'], APPNAME)
        except KeyError:
            dataFolder = os.path.join(os.environ['HOME'], '.config', APPNAME)

        # Migrate existing data to the proper location
        # if this is an existing install
        try:
            move(os.path.join(os.environ['HOME'], '.%s' % APPNAME), dataFolder)
            logger.info('Moving data folder to %s', dataFolder)
        except IOError:
            # Old directory may not exist.
            pass
        dataFolder = dataFolder + os.path.sep
    return dataFolder


def codePath():
    """Returns path to the program sources"""
    # pylint: disable=protected-access
    if not frozen:
        return os.path.dirname(__file__)
    return (
        os.environ.get('RESOURCEPATH')
        # pylint: disable=protected-access
        if frozen == "macosx_app" else sys._MEIPASS)


def tail(f, lines=20):
    """Returns last lines in the f file object"""
    total_lines_wanted = lines

    BLOCK_SIZE = 1024
    f.seek(0, 2)
    block_end_byte = f.tell()
    lines_to_go = total_lines_wanted
    block_number = -1
    blocks = []
    # blocks of size BLOCK_SIZE, in reverse order starting
    # from the end of the file
    while lines_to_go > 0 and block_end_byte > 0:
        if block_end_byte - BLOCK_SIZE > 0:
            # read the last block we haven't yet read
            f.seek(block_number * BLOCK_SIZE, 2)
            blocks.append(f.read(BLOCK_SIZE))
        else:
            # file too small, start from begining
            f.seek(0, 0)
            # only read what was not read
            blocks.append(f.read(block_end_byte))
        lines_found = blocks[-1].count('\n')
        lines_to_go -= lines_found
        block_end_byte -= BLOCK_SIZE
        block_number -= 1
    all_read_text = ''.join(reversed(blocks))
    return '\n'.join(all_read_text.splitlines()[-total_lines_wanted:])


def lastCommit():
    """
    Returns last commit information as dict with 'commit' and 'time' keys
    """
    githeadfile = os.path.join(codePath(), '..', '.git', 'logs', 'HEAD')
    result = {}
    if os.path.isfile(githeadfile):
        try:
            with open(githeadfile, 'rt') as githead:
                line = tail(githead, 1)
            result['commit'] = line.split()[1]
            result['time'] = datetime.fromtimestamp(
                float(re.search(r'>\s*(.*?)\s', line).group(1))
            )
        except (IOError, AttributeError, TypeError):
            pass
    return result
