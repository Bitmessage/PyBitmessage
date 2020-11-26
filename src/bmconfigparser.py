"""
BMConfigParser class definition and default configuration settings
"""
# pylint: disable=no-self-use, arguments-differ
import configparser
import os
import shutil
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
    # pylint: disable=too-many-ancestors
    _temp = {}

    def set(self, section, option, value=None):
        if self._optcre is self.OPTCRE or value:
            if not isinstance(value, str):
                raise TypeError("option values must be strings")
        if not self.validate(section, option, value):
            raise ValueError("Invalid value %s" % value)
        return configparser.ConfigParser.set(self, section, option, value)

    def get(self, section, option, raw=False, vars=None):
        # pylint: disable=unused-argument
        try:
            if section == "bitmessagesettings" and option == "timeformat":
                return configparser.ConfigParser.get(
                    self, section, option, raw=True, vars=vars)
            try:
                return self._temp[section][option]
            except KeyError:
                pass
            return configparser.ConfigParser.get(
                self, section, option, raw=True, vars=vars)
        except configparser.InterpolationError:
            return configparser.ConfigParser.get(
                self, section, option, raw=True, vars=vars)
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
        """Return value as boolean, False on exceptions"""
        try:
            # Used in the python2.7
            # return self.getboolean(section, field)
            # Used in the python3.5.2
            # print(config, section, field)
            return self.getboolean(section, field)
            # return config.getboolean(section, field)
        except (configparser.NoSectionError, configparser.NoOptionError,
                ValueError, AttributeError):
            return False

    def safeGetInt(self, section, field, default=0):
        """Return value as integer, default on exceptions,
        0 if default missing"""
        try:
            # Used in the python2.7
            # return self.getint(section, field)
            # Used in the python3.7.0
            return int(self.get(section, field))
        except (configparser.NoSectionError, configparser.NoOptionError,
                ValueError, AttributeError):
            return default

    def safeGet(self, section, option, default=None):
        """Return value as is, default on exceptions, None if default missing"""
        try:
            return self.get(section, option)
        except (configparser.NoSectionError, configparser.NoOptionError,
                ValueError, AttributeError):
            return default

    def items(self, section, raw=False, variables=None):
        # pylint: disable=signature-differs
        """Return section variables as parent,
        but override the "raw" argument to always True"""
        return configparser.ConfigParser.items(self, section, True, variables)

    def addresses(self, hidden=False):

        """Return a list of local bitmessage addresses (from section labels)"""
        return [x for x in BMConfigParser().sections() if x.startswith('BM-') and (
            hidden or not BMConfigParser().safeGetBoolean(x, 'hidden'))]

    def paymentaddress(self):
        """Return a list of local payment addresses (from section labels)"""
        return ''.join([x for x in BMConfigParser().sections() if x.startswith(
            'BM-') and BMConfigParser().safeGetBoolean(x, 'payment')])

    def read(self, filenames):
        configparser.ConfigParser.read(self, filenames)
        for section in self.sections():
            for option in self.options(section):
                try:
                    if not self.validate(
                        section, option,
                        self[section][option]
                    ):
                        try:
                            newVal = BMConfigDefaults[section][option]
                        except configparser.NoSectionError:
                            continue
                        except KeyError:
                            continue
                        configparser.ConfigParser.set(
                            self, section, option, newVal)
                except configparser.InterpolationError:
                    continue

    def save(self):
        """Save the runtime config onto the filesystem"""
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
        """Input validator interface (using factory pattern)"""
        try:
            return getattr(self, 'validate_{}_{}'.format(
                section, option))(value)
        except AttributeError:
            return True

    @staticmethod
    def validate_bitmessagesettings_maxoutboundconnections(value):
        """Reject maxoutboundconnections that are too high or too low"""
        try:
            value = int(value)
        except ValueError:
            return False
        if value < 0 or value > 8:
            return False
        return True
