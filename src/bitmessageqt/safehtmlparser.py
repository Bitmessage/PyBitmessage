"""Subclass of HTMLParser.HTMLParser for MessageView widget"""

import inspect
import re
from HTMLParser import HTMLParser

from urllib import quote_plus
from urlparse import urlparse


class SafeHTMLParser(HTMLParser):
    """HTML parser with sanitisation"""
    # from html5lib.sanitiser
    acceptable_elements = (
        'a', 'abbr', 'acronym', 'address', 'area',
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
        'th', 'thead', 'tr', 'tt', 'u', 'ul', 'var', 'video'
    )
    replaces_pre = (
        ("&", "&amp;"), ("\"", "&quot;"), ("<", "&lt;"), (">", "&gt;"))
    replaces_post = (
        ("\n", "<br/>"), ("\t", "&nbsp;&nbsp;&nbsp;&nbsp;"),
        ("  ", "&nbsp; "), ("  ", "&nbsp; "), ("<br/> ", "<br/>&nbsp;"))
    src_schemes = ["data"]
    # uriregex1 = re.compile(
    #     r'(?i)\b((?:(https?|ftp|bitcoin):(?:/{1,3}|[a-z0-9%])'
    #     r'|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)'
    #     r'(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))'
    #     r'+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?]))')
    uriregex1 = re.compile(
        r'((https?|ftp|bitcoin):(?:/{1,3}|[a-z0-9%])'
        r'(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)'
    )
    uriregex2 = re.compile(r'<a href="([^"]+)&amp;')
    emailregex = re.compile(
        r'\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})\b')

    @staticmethod
    def replace_pre(text):
        """Perform substring replacement before regex replacements"""
        for a in SafeHTMLParser.replaces_pre:
            text = text.replace(*a)
        return text

    @staticmethod
    def replace_post(text):
        """Perform substring replacement after regex replacements"""
        for a in SafeHTMLParser.replaces_post:
            text = text.replace(*a)
        if len(text) > 1 and text[0] == " ":
            text = "&nbsp;" + text[1:]
        return text

    def __init__(self, *args, **kwargs):
        HTMLParser.__init__(self, *args, **kwargs)
        self.reset()
        self.reset_safe()
        self.has_html = None
        self.allow_picture = None

    def reset_safe(self):
        """Reset runtime variables specific to this class"""
        self.elements = set()
        self.raw = u""
        self.sanitised = u""
        self.has_html = False
        self.allow_picture = False
        self.allow_external_src = False

    def add_if_acceptable(self, tag, attrs=None):
        """Add tag if it passes sanitisation"""
        if tag not in self.acceptable_elements:
            return
        self.sanitised += "<"
        if inspect.stack()[1][3] == "handle_endtag":
            self.sanitised += "/"
        self.sanitised += tag
        if attrs is not None:
            for attr, val in attrs:
                if tag == "img" and attr == "src" and not self.allow_picture:
                    val = ""
                elif attr == "src" and not self.allow_external_src:
                    url = urlparse(val)
                    if url.scheme not in self.src_schemes:
                        val = ""
                self.sanitised += " " + quote_plus(attr)
                if val is not None:
                    self.sanitised += "=\"" + val + "\""
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
        self.sanitised += data

    def handle_charref(self, name):
        self.sanitised += "&#" + name + ";"

    def handle_entityref(self, name):
        self.sanitised += "&" + name + ";"

    def feed(self, data):
        try:
            data = unicode(data, 'utf-8')
        except UnicodeDecodeError:
            data = unicode(data, 'utf-8', errors='replace')
        HTMLParser.feed(self, data)
        tmp = SafeHTMLParser.replace_pre(data)
        tmp = self.uriregex1.sub(r'<a href="\1">\1</a>', tmp)
        tmp = self.uriregex2.sub(r'<a href="\1&', tmp)
        tmp = self.emailregex.sub(r'<a href="mailto:\1">\1</a>', tmp)
        tmp = SafeHTMLParser.replace_post(tmp)
        self.raw += tmp

    def is_html(self, text=None, allow_picture=False):
        """Detect if string contains HTML tags"""
        if text:
            self.reset()
            self.reset_safe()
            self.allow_picture = allow_picture
            self.feed(text)
            self.close()
        return self.has_html
