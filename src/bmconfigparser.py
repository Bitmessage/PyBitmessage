import ConfigParser
import datetime
import shutil
import os

from singleton import Singleton
import state


@Singleton
class BMConfigParser(ConfigParser.SafeConfigParser):
    def set(self, section, option, value=None):
        if self._optcre is self.OPTCRE or value:
            if not isinstance(value, basestring):
                raise TypeError("option values must be strings")
        return ConfigParser.ConfigParser.set(self, section, option, value)

    def get(self, section, option, raw=False, vars=None):
        if section == "bitmessagesettings" and option == "timeformat":
            try: 
                return ConfigParser.ConfigParser.get(self, section, option, raw, vars)
            except ConfigParser.InterpolationError:
                return ConfigParser.ConfigParser.get(self, section, option, True, vars)
        return ConfigParser.ConfigParser.get(self, section, option, True, vars)

    def safeGetBoolean(self, section, field):
        if self.has_option(section, field):
            try:
                return self.getboolean(section, field)
            except ValueError:
                return False
        return False

    def safeGetInt(self, section, field, default=0):
        if self.has_option(section, field):
            try:
                return self.getint(section, field)
            except ValueError:
                return default
        return default

    def safeGet(self, section, option, default = None):
        if self.has_option(section, option):
            return self.get(section, option)
        else:
            return default

    def items(self, section, raw=False, vars=None):
        return ConfigParser.ConfigParser.items(self, section, True, vars)

    def save(self):
        fileName = os.path.join(state.appdata, 'keys.dat')
        fileNameBak = fileName + "." + datetime.datetime.now().strftime("%Y%j%H%M%S%f") + '.bak'
        # create a backup copy to prevent the accidental loss due to the disk write failure
        try:
            shutil.copyfile(fileName, fileNameBak)
            # The backup succeeded.
            fileNameExisted = True
        except (IOError, Exception):
            # The backup failed. This can happen if the file didn't exist before.
            fileNameExisted = False
        # write the file
        with open(fileName, 'wb') as configfile:
            self.write(configfile)
        # delete the backup
        if fileNameExisted:
            os.remove(fileNameBak)
