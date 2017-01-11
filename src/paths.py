from os import environ, path
import sys

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

