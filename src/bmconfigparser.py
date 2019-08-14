"""
BMConfigParser class definition and default configuration settings
"""

from configparser import (
    ConfigParser,
    InterpolationError,
    NoOptionError,
    NoSectionError,
)
from datetime import datetime
import os
from past.builtins import basestring
import shutil
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
class BMConfigParser(ConfigParser):
    """Singleton class inherited from ConfigParser with additional methods
    specific to bitmessage config."""

    def set(self, section, option, value=None):
        if self._optcre is self.OPTCRE or value:
            if not isinstance(value, basestring):
                raise TypeError("option values must be strings")
        if not self.validate(section, option, value):
            raise ValueError("Invalid value %s" % value)
        return ConfigParser.set(self, section, option, value)

    def get(self, section, option, *args, raw=False, vars=None, **kwargs):
        try:
            if section == "bitmessagesettings" and option == "timeformat":
                return ConfigParser.get(self, section, option, raw=raw, vars=vars)
            return ConfigParser.get(self, section, option, raw=True, vars=vars)
        except InterpolationError:
            return ConfigParser.get(self, section, option, raw=True, vars=vars)
        except (NoSectionError, NoOptionError) as e:
            try:
                return BMConfigDefaults[section][option]
            except (KeyError, ValueError, AttributeError):
                raise e

    def safeGetBoolean(self, section, field):
        try:
            return self.getboolean(section, field)
        except (NoSectionError, NoOptionError, ValueError, AttributeError):
            return False

    def safeGetInt(self, section, field, default=0):
        try:
            return self.getint(section, field)
        except (NoSectionError, NoOptionError,
                ValueError, AttributeError):
            return default

    def safeGet(self, section, option, default=None):
        try:
            return self.get(section, option)
        except (NoSectionError, NoOptionError,
                ValueError, AttributeError):
            return default

    def items(self, section, vars=None, **kwargs):
        return ConfigParser.items(self, section, raw=True, vars=vars)

    def addresses(self):
        return filter(
            lambda x: x.startswith('BM-'), BMConfigParser().sections())

    def read(self, filenames):
        ConfigParser.read(self, filenames)
        for section in self.sections():
            for option in self.options(section):
                try:
                    if not self.validate(
                        section, option,
                        self.get(section, option)
                    ):
                        try:
                            newVal = BMConfigDefaults[section][option]
                        except KeyError:
                            continue
                        self.set(section, option, newVal)
                except InterpolationError:
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
