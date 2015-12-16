from HTMLParser import HTMLParser
import inspect
from urllib import quote, quote_plus

class SafeHTMLParser(HTMLParser):
    # from html5lib.sanitiser
    acceptable_elements = ['a', 'abbr', 'acronym', 'address', 'area',
                           'article', 'aside', 'audio', 'b', 'big', 'blockquote', 'br', 'button',
                           'canvas', 'caption', 'center', 'cite', 'code', 'col', 'colgroup',
                           'command', 'datagrid', 'datalist', 'dd', 'del', 'details', 'dfn',
                           'dialog', 'dir', 'div', 'dl', 'dt', 'em', 'event-source', 'fieldset',
                           'figcaption', 'figure', 'footer', 'font', 'header', 'h1',
                           'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'ins',
                           'keygen', 'kbd', 'label', 'legend', 'li', 'm', 'map', 'menu', 'meter',
                           'multicol', 'nav', 'nextid', 'ol', 'output', 'optgroup', 'option',
                           'p', 'pre', 'progress', 'q', 's', 'samp', 'section', 'select',
                           'small', 'sound', 'source', 'spacer', 'span', 'strike', 'strong',
                           'sub', 'sup', 'table', 'tbody', 'td', 'textarea', 'time', 'tfoot',
                           'th', 'thead', 'tr', 'tt', 'u', 'ul', 'var', 'video']
    replaces = [["&", "&amp;"], ["\"", "&quot;"], ["<", "&lt;"], [">", "&gt;"], ["\n", "<br/>"]]

    @staticmethod
    def multi_replace(text):
        for a in SafeHTMLParser.replaces:
            text = text.replace(a[0], a[1])
        return text

    def __init__(self, *args, **kwargs):
        HTMLParser.__init__(self, *args, **kwargs)
        self.elements = set()
        self.sanitised = u""
        self.raw = u""
        self.has_html = False
        
    def reset_safe(self):
        self.elements = set()
        self.raw = u""
        self.sanitised = u""
        self.has_html = False

    def add_if_acceptable(self, tag, attrs = None):
        if not tag in self.acceptable_elements:
            return
        self.sanitised += "<"
        if inspect.stack()[1][3] == "handle_endtag":
            self.sanitised += "/"
        self.sanitised += tag
        if not attrs is None:
            for attr in attrs:
                if tag == "img" and attr[0] == "src" and not self.allow_picture:
                    attr[1] = ""
                self.sanitised += " " + quote_plus(attr[0])
                if not (attr[1] is None):
                    self.sanitised += "=\"" + attr[1] + "\""
        if inspect.stack()[1][3] == "handle_startendtag":
            self.sanitised += "/"
        self.sanitised += ">"
    
    def handle_starttag(self, tag, attrs):
        if tag in self.acceptable_elements:
            self.has_html = True
        self.add_if_acceptable(tag, attrs)

    def handle_endtag(self, tag):
        self.add_if_acceptable(tag)
        
    def handle_startendtag(self, tag, attrs):
        if tag in self.acceptable_elements:
            self.has_html = True
        self.add_if_acceptable(tag, attrs)
    
    def handle_data(self, data):
        self.sanitised += unicode(data, 'utf-8', 'replace')
        
    def handle_charref(self, name):
        self.sanitised += "&#" + name + ";"
    
    def handle_entityref(self, name):
        self.sanitised += "&" + name + ";"

    def feed(self, data):
        HTMLParser.feed(self, data)
        tmp = SafeHTMLParser.multi_replace(data)
        self.raw += unicode(tmp, 'utf-8', 'replace')

    def is_html(self, text = None, allow_picture = False):
        if text:
            self.reset()
            self.reset_safe()
            self.feed(text)
            self.close()
            self.allow_picture = allow_picture
        return self.has_html