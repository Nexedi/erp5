from Products.MimetypesRegistry import MimeTypesRegistry, mime_types
import six

preferred_extension_dict = {
  "bin": "application/octet-stream",
  "jpg": "image/jpeg",
}

def initialize(registry):
    mime_types.initialize(registry)
    for ext, mime in six.iteritems(preferred_extension_dict):
        mime, = registry.lookup(mime)
        assert type(mime.extensions) is tuple
        x = list(mime.extensions)
        x.remove(ext)
        x.insert(0, ext)
        mime.extensions = tuple(x)

MimeTypesRegistry.initialize = initialize

# patched from https://github.com/plone/Products.MimetypesRegistry/blob/2.1.8/Products/MimetypesRegistry/MimeTypesRegistry.py#L305-L359
# to change type of `data`. Originally, Products.MimetypesRegistry only "native str" for data, but this data is passed
# to magic.guessMime(data), which expects bytes and later before passing it to guess_content_type
# it is .encode()'ed, which so this expectes str - which is inconsistent.
# This relaxes the data type to tolerate bytes or str on python3
from Products.MimetypesRegistry.mime_types import magic
from zope.contenttype import guess_content_type
from Acquisition import aq_base

def classify(self, data, mimetype=None, filename=None):
    """Classify works as follows:
    1) you tell me the rfc-2046 name and I give you an IMimetype
        object
    2) the filename includes an extension from which we can guess
        the mimetype
    3) we can optionally introspect the data
    4) default to self.defaultMimetype if no data was provided
        else to application/octet-stream of no filename was provided,
        else to text/plain

    Return an IMimetype object or None
    """
    mt = None
    if mimetype:
        mt = self.lookup(mimetype)
        if mt:
            mt = mt[0]
    elif filename:
        mt = self.lookupExtension(filename)
        if mt is None:
            mt = self.globFilename(filename)
    if data and not mt:
        for c in self._classifiers():
            if c.classify(data):
                mt = c
                break
        if not mt:
            if six.PY3 and isinstance(data, str):  # <<<< patch allow bytes or str
                data = data.encode()
            mstr = magic.guessMime(data)
            if mstr:
                _mt = self.lookup(mstr)
                if len(_mt) > 0:
                    mt = _mt[0]
    if not mt:
        if not data:
            mtlist = self.lookup(self.defaultMimetype)
        elif filename:
            mtlist = self.lookup('application/octet-stream')
        else:
            failed = 'text/x-unknown-content-type'
            filename = filename or ''
            data = data or ''
            if six.PY3 and isinstance(data, str):  # <<<< patch allow bytes or str
                data = data.encode()
            ct, enc = guess_content_type(filename, data, None)
            if ct == failed:
                ct = 'text/plain'
            mtlist = self.lookup(ct)
        if len(mtlist) > 0:
            mt = mtlist[0]
        else:
            return None

    # Remove acquisition wrappers
    return aq_base(mt)

MimeTypesRegistry.MimeTypesRegistry.classify = classify
