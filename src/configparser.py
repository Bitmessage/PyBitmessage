from ConfigParser import SafeConfigParser, ConfigParser

class BMConfigParser(SafeConfigParser):
    def set(self, section, option, value=None):
        if self._optcre is self.OPTCRE or value:
            if not isinstance(value, basestring):
                raise TypeError("option values must be strings")
        return ConfigParser.set(self, section, option, value)

    def get(self, section, option, raw=False, vars=None):
        return ConfigParser.get(self, section, option, True, vars)

    def items(self, section, raw=False, vars=None):
        return ConfigParser.items(self, section, True, vars)

