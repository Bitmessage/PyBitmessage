from HTMLParser import HTMLParser
import inspect
import multiprocessing
import re
import Queue
from urllib import quote, quote_plus
from urlparse import urlparse
from debug import logger
from shared import parserInputQueue, parserOutputQueue, parserProcess, parserLock

def regexpSubprocess(parserInputQueue, parserOutputQueue):
    for data in iter(parserInputQueue.get, None):
        if data is None:
            break;
        try:
            result = SafeHTMLParser.uriregex1.sub(
                r'<a href="\1">\1</a>',
                data)
            result = SafeHTMLParser.uriregex2.sub(r'<a href="\1&', result)
            result = SafeHTMLParser.emailregex.sub(r'<a href="mailto:\1">\1</a>', result)
            parserOutputQueue.put(result)
        except SystemExit:
            break;
        except:
            break;

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
    replaces = [["&", "&amp;"], ["\"", "&quot;"], ["<", "&lt;"], [">", "&gt;"], ["\n", "<br/>"], ["\t", "&nbsp;&nbsp;&nbsp;&nbsp;"], ["  ", "&nbsp; "], ["  ", "&nbsp; "], ["<br/> ", "<br/>&nbsp;"]]
    src_schemes = [ "data" ]
    uriregex1 = re.compile(r'(?i)\b((?:(https?|ftp|bitcoin):(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?]))')
    uriregex2 = re.compile(r'<a href="([^"]+)&amp;')
    emailregex = re.compile(r'\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})\b')

    @staticmethod
    def multi_replace(text):
        for a in SafeHTMLParser.replaces:
            text = text.replace(a[0], a[1])
        if len(text) > 1 and text[0] == " ":
            text = "&nbsp;" + text[1:]
        return text

    def __init__(self, *args, **kwargs):
        HTMLParser.__init__(self, *args, **kwargs)
        self.reset_safe()
        
    def reset_safe(self):
        self.elements = set()
        self.raw = u""
        self.sanitised = u""
        self.has_html = False
        self.allow_picture = False
        self.allow_external_src = False

    def add_if_acceptable(self, tag, attrs = None):
        if not tag in SafeHTMLParser.acceptable_elements:
            return
        self.sanitised += "<"
        if inspect.stack()[1][3] == "handle_endtag":
            self.sanitised += "/"
        self.sanitised += tag
        if not attrs is None:
            for attr, val in attrs:
                if tag == "img" and attr == "src" and not self.allow_picture:
                    val = ""
                elif attr == "src" and not self.allow_external_src:
                    url = urlparse(val)
                    if url.scheme not in SafeHTMLParser.src_schemes:
                        val == ""
                self.sanitised += " " + quote_plus(attr)
                if not (val is None):
                    self.sanitised += "=\"" + (val if isinstance(val, unicode) else unicode(val, 'utf-8', 'replace')) + "\""
        if inspect.stack()[1][3] == "handle_startendtag":
            self.sanitised += "/"
        self.sanitised += ">"
    
    def handle_starttag(self, tag, attrs):
        if tag in SafeHTMLParser.acceptable_elements:
            self.has_html = True
        self.add_if_acceptable(tag, attrs)

    def handle_endtag(self, tag):
        self.add_if_acceptable(tag)
        
    def handle_startendtag(self, tag, attrs):
        if tag in SafeHTMLParser.acceptable_elements:
            self.has_html = True
        self.add_if_acceptable(tag, attrs)
    
    def handle_data(self, data):
        self.sanitised += unicode(data, 'utf-8', 'replace')
        
    def handle_charref(self, name):
        self.sanitised += "&#" + name + ";"
    
    def handle_entityref(self, name):
        self.sanitised += "&" + name + ";"

    def feed(self, data):
        global parserLock, parserProcess, parserInputQueue, parserOutputQueue
        HTMLParser.feed(self, data)
        tmp = SafeHTMLParser.multi_replace(data)
        tmp = unicode(tmp, 'utf-8', 'replace')
        
        parserLock.acquire()
        if parserProcess is None:
            parserProcess = multiprocessing.Process(target=regexpSubprocess, name="RegExParser", args=(parserInputQueue, parserOutputQueue))
            parserProcess.start()
        parserLock.release()
        # flush queue
        try:
            while True:
                tmp = parserOutputQueue.get(False)
        except Queue.Empty:
            logger.debug("Parser queue flushed")
            pass
        parserInputQueue.put(tmp)
        try:
            tmp = parserOutputQueue.get(True, 1)
        except Queue.Empty:
            logger.error("Regular expression parsing timed out, not displaying links")
            parserLock.acquire()
            parserProcess.terminate()
            parserProcess = multiprocessing.Process(target=regexpSubprocess, name="RegExParser", args=(parserInputQueue, parserOutputQueue))
            parserProcess.start()
            parserLock.release()

        self.raw += tmp

    def is_html(self, text = None, allow_picture = False):
        if text:
            self.reset()
            self.reset_safe()
            self.allow_picture = allow_picture
            self.feed(text)
            self.close()
        return self.has_html
