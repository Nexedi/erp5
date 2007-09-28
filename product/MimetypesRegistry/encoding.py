import re
import encodings
from Products.MimetypesRegistry.common import log

EMACS_ENCODING_RGX = re.compile('[^#]*[#\s]*-\*-\s*coding: ([^\s]*)\s*-\*-\s*')
VIM_ENCODING_RGX = re.compile('[^#]*[#\s]*vim:fileencoding=\s*([^\s]*)\s*')
XML_ENCODING_RGX = re.compile('<\?xml version=[^\s]*\s*encoding=([^\s]*)\s*\?>')
CHARSET_RGX = re.compile('charset=([^\s"]*)')

def guess_encoding(buffer):
    """Better guess encoding method
    
    It checks if python supports the encoding
    """
    encoding = _guess_encoding(buffer)
    # step 1: if the encoding was detected, use the lower() because python
    # is using lower case names for encodings
    if encoding and isinstance(encoding, basestring):
        #encoding = encoding.lower()
        pass
    else:
        return None
    # try to find an encoding function for the encoding
    # if None is returned or an exception is raised the encoding is invalid
    try:
        result = encodings.search_function(encoding.lower())
    except:
        # XXX log
        result = None
    
    if result:
        # got a valid encoding
        return encoding
    else:
        return None
    

def _guess_encoding(buffer):
    """try to guess encoding from a buffer

    FIXME: it could be mime type driven but it seems less painful like that
    """
    assert type(buffer) is type(''), type(buffer)
    # default to ascii on empty buffer
    if not buffer:
        return 'ascii'

    # check for UTF-8 byte-order mark
    if buffer.startswith('\xef\xbb\xbf'):
        return 'UTF-8'

    first_lines = buffer.split('\n')[:2]
    for line in first_lines:
        # check for emacs encoding declaration
        m = EMACS_ENCODING_RGX.match(line)
        if m is not None:
            return m.group(1)
        # check for vim encoding declaration
        m = VIM_ENCODING_RGX.match(line)
        if m is not None:
            return m.group(1)

    # check for xml encoding declaration
    if first_lines[0].startswith('<?xml'):
        m = XML_ENCODING_RGX.match(first_lines[0])
        if m is not None:
            return m.group(1)[1:-1]
        # xml files with no encoding declaration default to UTF-8
        return 'UTF-8'

    # try to get charset declaration
    # FIXME: should we check it's html before ?
    m = CHARSET_RGX.search(buffer)
    if m is not None:
        return m.group(1)
    return None
