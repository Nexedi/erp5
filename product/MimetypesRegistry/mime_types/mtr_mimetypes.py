from Products.MimetypesRegistry.interfaces import IClassifier
from Products.MimetypesRegistry.MimeTypeItem import MimeTypeItem
from Products.MimetypesRegistry.common import MimeTypeException

from types import InstanceType
import re

class text_plain(MimeTypeItem):

    __implements__ = MimeTypeItem.__implements__
    __name__   = "Plain Text"
    mimetypes  = ('text/plain',)
    extensions = ('txt',)
    binary     = 0

class text_pre_plain(MimeTypeItem):

    __implements__ = MimeTypeItem.__implements__
    __name__   = "Pre-formatted Text (<pre>)"
    mimetypes  = ('text/plain-pre',)
    extensions = ()
    binary     = 0

class text_structured(MimeTypeItem):

    __implements__ = MimeTypeItem.__implements__
    __name__   = "Structured Text"
    mimetypes  = ('text/structured',)
    extensions = ('stx',)
    binary     = 0

class text_rest(MimeTypeItem):

    __implements__ = MimeTypeItem.__implements__
    __name__   = "reStructured Text"
    mimetypes  = ("text/x-rst", "text/restructured",)
    extensions = ("rst", "rest", "restx") #txt?
    binary     = 0

class text_python(MimeTypeItem):

    __implements__ = MimeTypeItem.__implements__
    __name__   = "Python Source"
    mimetypes  = ("text/python-source", "text/x-python",)
    extensions = ("py",)
    binary     = 0

class text_wiki(MimeTypeItem):

    __implements__ = MimeTypeItem.__implements__
    __name__   = "Wiki text"
    mimetypes  = ("text/wiki",)
    extensions = ()
    binary     = 0

class application_rtf(MimeTypeItem):

    __implements__ = MimeTypeItem.__implements__
    __name__   = 'Rich Text Format (RTF)'
    mimetypes  = ('application/rtf',)
    extensions = ('rtf',)
    binary     = 1

class application_msword(MimeTypeItem):

    __implements__ = MimeTypeItem.__implements__
    __name__   = "Microsoft Word Document"
    mimetypes  = ('application/msword',)
    extensions = ('doc',)
    binary     = 1

class text_xml(MimeTypeItem):

    __implements__ = MimeTypeItem.__implements__ + (IClassifier,)

    __name__   = "Extensible Markup Language (XML)"
    mimetypes  = ('text/xml',)
    extensions = ('xml',)
    binary     = 0

    def classify(self, data):
        m = re.search('^\s*<\\?xml.*\\?>', data)
        if m:
            return 1 # True
        return None  # False

class application_octet_stream(MimeTypeItem):
    """we need to be sure this one exists"""
    __name__   = "Octet Stream"
    mimetypes = ('application/octet-stream',)
    binary     = 1
    extensions = ()

class text_html(MimeTypeItem):

    __implements__ = MimeTypeItem.__implements__
    __name__   = "HTML"
    mimetypes  = ('text/html',)
    extensions = ('html', 'htm')
    binary     = 0

class text_html_safe(MimeTypeItem):

    __implements__ = MimeTypeItem.__implements__
    __name__   = "Safe HTML"
    mimetypes  = ('text/x-html-safe',)
    extensions = ()
    binary     = 0

reg_types = [
    text_plain,
    text_pre_plain,
    application_msword,
    text_xml,
    text_structured,
    text_rest,
    text_python,
    text_wiki,
    application_octet_stream,
    application_rtf,
    text_html,
    text_html_safe,
    ]

def initialize(registry):
    for mt in reg_types:
        if type(mt) != InstanceType:
            mt = mt()
        registry.register(mt)

__all__ = tuple([cls.__name__ for cls in reg_types])
