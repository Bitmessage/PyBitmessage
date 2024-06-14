"""
BMConfigParser class definition and default configuration settings
"""

import os
import shutil
import sys  # FIXME: bad style! write more generally
from datetime import datetime

from six import string_types
from six.moves import configparser

try:
    import state
    from singleton import Singleton
except ImportError:
    from pybitmessage import state
    from pybitmessage.singleton import Singleton

SafeConfigParser = configparser.SafeConfigParser


BMConfigDefaults = {
    "bitmessagesettings": {
        "maxaddrperstreamsend": 500,
        "maxbootstrapconnections": 20,
        "maxdownloadrate": 0,
        "maxoutboundconnections": 8,
        "maxtotalconnections": 200,
        "maxuploadrate": 0,
        "apiinterface": "127.0.0.1",
        "apiport": 8442,
        "udp": "True"
    },
    "threads": {
        "receive": 3,
    },
    "network": {
        "bind": "",
        "dandelion": 90,
    },
    "inventory": {
        "storage": "sqlite",
        "acceptmismatch": "False",
    },
    "knownnodes": {
        "maxnodes": 20000,
    },
    "zlib": {
        "maxsize": 1048576
    }
}


@Singleton
class BMConfigParser(SafeConfigParser):
    """
    Singleton class inherited from :class:`ConfigParser.SafeConfigParser`
    with additional methods specific to bitmessage config.
    """
    # pylint: disable=too-many-ancestors
    _temp = {}

    def set(self, section, option, value=None):
        if self._optcre is self.OPTCRE or value:
            if not isinstance(value, string_types):
                raise TypeError("option values must be strings")
        if not self.validate(section, option, value):
            raise ValueError("Invalid value %s" % value)
        return SafeConfigParser.set(self, section, option, value)

    # pylint: disable=redefined-builtinm, too-many-return-statements
    def get(self, section, option, raw=False, vars=None):
        if sys.version_info[0] == 3:
            # pylint: disable=arguments-differ
            try:
                if section == "bitmessagesettings" and option == "timeformat":
                    return SafeConfigParser.get(
                        self, section, option, raw=True, vars=vars)
                try:
                    return self._temp[section][option]
                except KeyError:
                    pass
                return SafeConfigParser.get(
                    self, section, option, raw=True, vars=vars)
            except configparser.InterpolationError:
                return SafeConfigParser.get(
                    self, section, option, raw=True, vars=vars)
            except (configparser.NoSectionError, configparser.NoOptionError) as e:
                try:
                    return BMConfigDefaults[section][option]
                except (KeyError, ValueError, AttributeError):
                    raise e
        else:
            # pylint: disable=arguments-differ
            try:
                if section == "bitmessagesettings" and option == "timeformat":
                    return SafeConfigParser.get(
                        self, section, option, raw, vars)
                try:
                    return self._temp[section][option]
                except KeyError:
                    pass
                return SafeConfigParser.get(
                    self, section, option, True, vars)
            except configparser.InterpolationError:
                return SafeConfigParser.get(
                    self, section, option, True, vars)
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

    def safeGetFloat(self, section, field, default=0.0):
        """Return value as float, default on exceptions,
        0.0 if default missing"""
        try:
            return self.getfloat(section, field)
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
        return SafeConfigParser.items(self, section, True, variables)

    def _reset(self):
        """Reset current config. There doesn't appear to be a built in
            method for this"""
        sections = self.sections()
        for x in sections:
            self.remove_section(x)

    if sys.version_info[0] == 3:
        @staticmethod
        def addresses(hidden=False):
            """Return a list of local bitmessage addresses (from section labels)"""
            return [x for x in BMConfigParser().sections() if x.startswith('BM-') and (
                    hidden or not BMConfigParser().safeGetBoolean(x, 'hidden'))]

        def read(self, filenames):
            self._reset()
            SafeConfigParser.read(self, filenames)
            for section in self.sections():
                for option in self.options(section):
                    try:
                        # pylint: disable=unsubscriptable-object
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
                            SafeConfigParser.set(
                                self, section, option, newVal)
                    except configparser.InterpolationError:
                        continue

        def readfp(self, fp, filename=None):
            # pylint: disable=no-member
            SafeConfigParser.read_file(self, fp)
    else:
        @staticmethod
        def addresses():
            """Return a list of local bitmessage addresses (from section labels)"""
            return [
                x for x in BMConfigParser().sections() if x.startswith('BM-')]

        def read(self, filenames):
            """Read config and populate defaults"""
            self._reset()
            SafeConfigParser.read(self, filenames)
            for section in self.sections():
                for option in self.options(section):
                    try:
                        if not self.validate(
                                section, option,
                                SafeConfigParser.get(self, section, option)
                        ):
                            try:
                                newVal = BMConfigDefaults[section][option]
                            except KeyError:
                                continue
                            SafeConfigParser.set(
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

        with open(fileName, 'w') as configfile:
            self.write(configfile)
        # delete the backup
        if fileNameExisted:
            os.remove(fileNameBak)

    def validate(self, section, option, value):
        """Input validator interface (using factory pattern)"""
        try:
            return getattr(self, 'validate_%s_%s' % (section, option))(value)
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
