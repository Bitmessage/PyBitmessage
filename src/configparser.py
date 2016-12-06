from ConfigParser import SafeConfigParser

class BMConfigParser(SafeConfigParser):
    def set(self, section, option, value=None):
        if value is not None:
            value = value.replace('%', '%%')
        return SafeConfigParser.set(self, section, option, value)
