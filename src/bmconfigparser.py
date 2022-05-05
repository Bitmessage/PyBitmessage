"""
BMConfigParser class definition and default configuration settings
"""

import os
import shutil
from threading import Event
from datetime import datetime

from six import string_types
from six.moves import configparser

try:
    import state
except ImportError:
    from pybitmessage import state

SafeConfigParser = configparser.SafeConfigParser
config_ready = Event()


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

    def get(self, section, option, **kwargs):
        """Try returning temporary value before using parent get()"""
        try:
            return self._temp[section][option]
        except KeyError:
            pass
        return SafeConfigParser.get(
            self, section, option, **kwargs)

    def setTemp(self, section, option, value=None):
        """Temporary set option to value, not saving."""
        try:
            self._temp[section][option] = value
        except KeyError:
            self._temp[section] = {option: value}

    def safeGetBoolean(self, section, option):
        """Return value as boolean, False on exceptions"""
        try:
            return self.getboolean(section, option)
        except (configparser.NoSectionError, configparser.NoOptionError,
                ValueError, AttributeError):
            return False

    def safeGetInt(self, section, option, default=0):
        """Return value as integer, default on exceptions,
        0 if default missing"""
        try:
            return int(self.get(section, option))
        except (configparser.NoSectionError, configparser.NoOptionError,
                ValueError, AttributeError):
            return default

    def safeGetFloat(self, section, option, default=0.0):
        """Return value as float, default on exceptions,
        0.0 if default missing"""
        try:
            return self.getfloat(section, option)
        except (configparser.NoSectionError, configparser.NoOptionError,
                ValueError, AttributeError):
            return default

    def safeGet(self, section, option, default=None):
        """
        Return value as is, default on exceptions, None if default missing
        """
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
        """
        Reset current config.
        There doesn't appear to be a built in method for this.
        """
        self._temp = {}
        sections = self.sections()
        for x in sections:
            self.remove_section(x)

    def read(self, filenames=None):
        self._reset()
        SafeConfigParser.read(
            self, os.path.join(os.path.dirname(__file__), 'default.ini'))
        if filenames:
            SafeConfigParser.read(self, filenames)

    def addresses(self):
        """Return a list of local bitmessage addresses (from section labels)"""
        return [x for x in self.sections() if x.startswith('BM-')]

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
        except(IOError, Exception):
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

    def search_addresses(self, address, searched_text):
        """Return the searched label of MyAddress"""
        return [x for x in [self.get(address, 'label').lower(),
                address.lower()] if searched_text in x]

    def disable_address(self, address):
        """"Disabling the specific Address"""
        self.set(str(address), 'enabled', 'false')
        self.save()

    def enable_address(self, address):
        """"Enabling the specific Address"""
        self.set(address, 'enabled', 'true')
        self.save()


if not getattr(BMConfigParser, 'read_file', False):
    BMConfigParser.read_file = BMConfigParser.readfp

config = BMConfigParser()  # TODO: remove this crutch
