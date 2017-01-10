import ConfigParser

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

    def items(self, section, raw=False, vars=None):
        return ConfigParser.ConfigParser.items(self, section, True, vars)

