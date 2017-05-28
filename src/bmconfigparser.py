import ConfigParser
import datetime
import shutil
import os

from singleton import Singleton
import state

BMConfigDefaults = {
    "bitmessagesettings": {
        "maxaddrperstreamsend": 500,
        "maxbootstrapconnections": 20,
        "maxdownloadrate": 0,
        "maxoutboundconnections": 8,
        "maxtotalconnections": 200,
        "maxuploadrate": 0,
    },
    "network": {
        "asyncore": True,
        "bind": None,
    },
    "inventory": {
        "storage": "sqlite",
    },
    "zlib": {
        'maxsize': 1048576
    }
}

@Singleton
class BMConfigParser(ConfigParser.SafeConfigParser):
    def set(self, section, option, value=None):
        if self._optcre is self.OPTCRE or value:
            if not isinstance(value, basestring):
                raise TypeError("option values must be strings")
        return ConfigParser.ConfigParser.set(self, section, option, value)

    def get(self, section, option, raw=False, vars=None):
        try:
            if section == "bitmessagesettings" and option == "timeformat":
                return ConfigParser.ConfigParser.get(self, section, option, raw, vars)
            else:
                return ConfigParser.ConfigParser.get(self, section, option, True, vars)
        except ConfigParser.InterpolationError:
                return ConfigParser.ConfigParser.get(self, section, option, True, vars)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError) as e:
            try:
                return BMConfigDefaults[section][option]
            except (KeyError, ValueError, AttributeError):
                raise e

    def safeGetBoolean(self, section, field):
        try:
            return self.getboolean(section, field)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError, ValueError, AttributeError):
            return False

    def safeGetInt(self, section, field, default=0):
        try:
            return self.getint(section, field)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError, ValueError, AttributeError):
            return default

    def safeGet(self, section, option, default = None):
        try:
            return self.get(section, option)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError, ValueError, AttributeError):
            return default

    def items(self, section, raw=False, vars=None):
        return ConfigParser.ConfigParser.items(self, section, True, vars)

    def addresses(self):
        return filter(lambda x: x.startswith('BM-'), BMConfigParser().sections())

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
