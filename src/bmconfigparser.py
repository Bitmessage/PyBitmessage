"""
BMConfigParser class definition and default configuration settings
"""

import configparser
import shutil
import os
from datetime import datetime

import state
from singleton import Singleton

BMConfigDefaults = {
    "bitmessagesettings": {
        "maxaddrperstreamsend": 500,
        "maxbootstrapconnections": 20,
        "maxdownloadrate": 0,
        "maxoutboundconnections": 8,
        "maxtotalconnections": 200,
        "maxuploadrate": 0,
        "apiinterface": "127.0.0.1",
        "apiport": 8442
    },
    "threads": {
        "receive": 3,
    },
    "network": {
        "bind": '',
        "dandelion": 90,
    },
    "inventory": {
        "storage": "sqlite",
        "acceptmismatch": False,
    },
    "knownnodes": {
        "maxnodes": 20000,
    },
    "zlib": {
        'maxsize': 1048576
    }
}


@Singleton
class BMConfigParser(configparser.ConfigParser):
    """Singleton class inherited from ConfigParsedadfeConfigParser
    with additional methods specific to bitmessage config."""

    _temp = {}

    def set(self, section, option, value=None):
        if self._optcre is self.OPTCRE or value:
            if not isinstance(value, str):
                raise TypeError("option values must be strings")
        if not self.validate(section, option, value):
            raise ValueError("Invalid value %s" % value)
        return configparser.ConfigParser.set(self, section, option, value)

    def get(self, section, option, raw=False, variables=None):
        try:
            if section == "bitmessagesettings" and option == "timeformat":
                return configparser.ConfigParser.get(
                    self, section, option, raw=True, vars=variables)
            try:
                return self._temp[section][option]
            except KeyError:
                pass
            return configparser.ConfigParser.get(
                self, section, option, raw=True, vars=variables)
        except configparser.InterpolationError:
            return configparser.ConfigParser.get(
                self, section, option, raw=True, vars=variables)
        except (configparser.NoSectionError, configparser.NoOptionError) as e:
            try:
                return BMConfigDefaults[section][option]
            except (KeyError, ValueError, AttributeError):
                raise e

    def setTemp(self, section, option, value=None):
        """Temporary set option to value, not saving."""
        try:
            self._temp[section][option] = value
        except KeyError:
            self._temp[section] = {option: value}

    def safeGetBoolean(self, section, field):
        config = configparser.ConfigParser()
        try:
            #Used in the python2.7
            # return self.getboolean(section, field)
            #Used in the python3.5.2
            return config.getboolean(section, field)
        except (configparser.NoSectionError, configparser.NoOptionError,
                ValueError, AttributeError):
            return False

    def safeGetInt(self, section, field, default=0):
        config = configparser.ConfigParser()
        try:
            #Used in the python2.7
            # return self.getint(section, field)
            #Used in the python3.5.2
            return config.getint(section, field)
        except (configparser.NoSectionError, configparser.NoOptionError,
                ValueError, AttributeError):
            return default

    def safeGet(self, section, option, default=None):
        try:
            return self.get(section, option)
        except (configparser.NoSectionError, configparser.NoOptionError,
                ValueError, AttributeError):
            return default

    def items(self, section, raw=False, variables=None):
        return configparser.ConfigParser.items(self, section, True, variables)

    def addresses(self):
        return [x for x in BMConfigParser().sections() if x.startswith('BM-')]

    def read(self, filenames):
        configparser.ConfigParser.read(self, filenames)
        for section in self.sections():
            for option in self.options(section):
                try:
                    if not self.validate(
                        section, option,
                        configparser.ConfigParser.get(self, section, option)
                    ):
                        try:
                            newVal = BMConfigDefaults[section][option]
                        except KeyError:
                            continue
                        configparser.ConfigParser.set(
                            self, section, option, newVal)
                except configparser.InterpolationError:
                    continue

    def save(self):
        fileName = os.path.join(state.appdata, 'keys.dat')
        fileNameBak = '.'.join([
            fileName, datetime.now().strftime("%Y%j%H%M%S%f"), 'bak'])
        # create a backup copy to prevent the accidental loss due to
        # the disk write failure
        try:
            shutil.copyfile(fileName, fileNameBak)
            # The backup succeeded.
            fileNameExisted = True
        except (IOError, Exception):
            # The backup failed. This can happen if the file
            # didn't exist before.
            fileNameExisted = False
        # write the file
        with open(fileName, 'w') as configfile:
            self.write(configfile)
        # delete the backup
        if fileNameExisted:
            os.remove(fileNameBak)

    def validate(self, section, option, value):
        try:
            return getattr(self, 'validate_%s_%s' % (section, option))(value)
        except AttributeError:
            return True

    def validate_bitmessagesettings_maxoutboundconnections(self, value):
        try:
            value = int(value)
        except ValueError:
            return False
        if value < 0 or value > 8:
            return False
        return True
