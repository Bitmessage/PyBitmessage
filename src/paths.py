from os import environ, path
import sys
import re
import os
from datetime import datetime
from kivy.utils import platform
# When using py2exe or py2app, the variable frozen is added to the sys
# namespace.  This can be used to setup a different code path for
# binary distributions vs source distributions.
frozen = getattr(sys,'frozen', None)

def lookupExeFolder():
    if frozen:
        if frozen == "macosx_app":
            # targetdir/Bitmessage.app/Contents/MacOS/Bitmessage
            exeFolder = path.dirname(path.dirname(path.dirname(path.dirname(sys.executable)))) + path.sep
        else:
            exeFolder = path.dirname(sys.executable) + path.sep
    elif __file__:
        exeFolder = path.dirname(__file__) + path.sep
    else:
        exeFolder = ''
    return exeFolder

def lookupAppdataFolder():

    import traceback
    print(traceback.print_tb)
    APPNAME = "PyBitmessage"
    if "BITMESSAGE_HOME" in environ:
        dataFolder = environ["BITMESSAGE_HOME"]
        if dataFolder[-1] not in [path.sep, path.altsep]:
            dataFolder += path.sep
    elif sys.platform == 'darwin':
        if "HOME" in environ:
            dataFolder = path.join(environ["HOME"], "Library/Application Support/", APPNAME) + '/'
        else:
            stringToLog = 'Could not find home folder, please report this message and your OS X version to the BitMessage Github.'
            if 'logger' in globals():
                logger.critical(stringToLog)
            else:
                print stringToLog
            sys.exit()
    elif platform == 'android':
        # dataFolder = path.join(os.path.dirname(os.path.abspath("__file__")), "PyBitmessage") + '/'
        dataFolder = path.join('/sdcard/', 'DCIM/', APPNAME) + '/'

    elif 'win32' in sys.platform or 'win64' in sys.platform:
        dataFolder = path.join(environ['APPDATA'].decode(sys.getfilesystemencoding(), 'ignore'), APPNAME) + path.sep
    else:
        from shutil import move
        try:
            dataFolder = path.join(environ["XDG_CONFIG_HOME"], APPNAME)
        except KeyError:
            dataFolder = path.join(environ["HOME"], ".config", APPNAME)

        # Migrate existing data to the proper location if this is an existing install
        try:
            move(path.join(environ["HOME"], ".%s" % APPNAME), dataFolder)
            stringToLog = "Moving data folder to %s" % (dataFolder)
            if 'logger' in globals():
                logger.info(stringToLog)
            else:
                print stringToLog
        except IOError:
            # Old directory may not exist.
            pass
        dataFolder = dataFolder + '/'
    return dataFolder

def codePath():
    if frozen == "macosx_app":
        codePath = environ.get("RESOURCEPATH")
    elif frozen: # windows
        codePath = sys._MEIPASS
    else:
        codePath = path.dirname(__file__)
    return codePath

def tail(f, lines=20):
    total_lines_wanted = lines

    BLOCK_SIZE = 1024
    f.seek(0, 2)
    block_end_byte = f.tell()
    lines_to_go = total_lines_wanted
    block_number = -1
    blocks = [] # blocks of size BLOCK_SIZE, in reverse order starting
                # from the end of the file
    while lines_to_go > 0 and block_end_byte > 0:
        if (block_end_byte - BLOCK_SIZE > 0):
            # read the last block we haven't yet read
            f.seek(block_number*BLOCK_SIZE, 2)
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
    githeadfile = path.join(codePath(), '..', '.git', 'logs', 'HEAD')
    result = {}
    if path.isfile(githeadfile):
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