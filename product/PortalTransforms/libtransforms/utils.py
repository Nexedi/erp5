import re
import os
import sys

try:
    # Need to be imported before win32api to avoid dll loading
    # problems.
    import pywintypes
    import pythoncom

    import win32api
    WIN32 = True
except ImportError:
    WIN32 = False

class MissingBinary(Exception): pass

envPath = os.getenv('PATH', '')
bin_search_path = [path for path in envPath.split(os.pathsep)
                   if os.path.isdir(path)]

cygwin = 'c:/cygwin'

# cygwin support
if sys.platform == 'win32' and os.path.isdir(cygwin):
    for p in ['/bin', '/usr/bin', '/usr/local/bin' ]:
        p = os.path.join(cygwin, p)
        if os.path.isdir(p):
            bin_search_path.append(p)

if sys.platform == 'win32':
    extensions = ('.exe', '.com', '.bat', )
else:
    extensions = ()

def bin_search(binary):
    """search the bin_search_path for a given binary returning its fullname or
       raises MissingBinary"""
    mode   = os.R_OK | os.X_OK
    for path in bin_search_path:
        for ext in ('', ) + extensions:
            pathbin = os.path.join(path, binary) + ext
            if os.access(pathbin, mode) == 1:
                return pathbin

    raise MissingBinary('Unable to find binary "%s" in %s' %
                        (binary, os.pathsep.join(bin_search_path)))

def getShortPathName(binary):
    if WIN32:
        try:
            binary = win32api.GetShortPathName(binary)
        except win32api.error:
            log("Failed to GetShortPathName for '%s'" % binary)
    return binary

def sansext(path):
    return os.path.splitext(os.path.basename(path))[0]


##########################################################################
# The code below is taken from CMFDefault.utils to remove
# dependencies for Python-only installations
##########################################################################

def bodyfinder(text):
    """ Return body or unchanged text if no body tags found.

    Always use html_headcheck() first.
    """
    lowertext = text.lower()
    bodystart = lowertext.find('<body')
    if bodystart == -1:
        return text
    bodystart = lowertext.find('>', bodystart) + 1
    if bodystart == 0:
        return text
    bodyend = lowertext.rfind('</body>', bodystart)
    if bodyend == -1:
        return text
    return text[bodystart:bodyend]


#
#   HTML cleaning code
#

# These are the HTML tags that we will leave intact
VALID_TAGS = { 'a'          : 1
             , 'b'          : 1
             , 'base'       : 0
             , 'blockquote' : 1
             , 'body'       : 1
             , 'br'         : 0
             , 'caption'    : 1
             , 'cite'       : 1
             , 'code'       : 1
             , 'div'        : 1
             , 'dl'         : 1
             , 'dt'         : 1
             , 'dd'         : 1
             , 'em'         : 1
             , 'h1'         : 1
             , 'h2'         : 1
             , 'h3'         : 1
             , 'h4'         : 1
             , 'h5'         : 1
             , 'h6'         : 1
             , 'head'       : 1
             , 'hr'         : 0
             , 'html'       : 1
             , 'i'          : 1
             , 'img'        : 0
             , 'kbd'        : 1
             , 'li'         : 1
             , 'meta'       : 0
             , 'ol'         : 1
             , 'p'          : 1
             , 'pre'        : 1
             , 'span'       : 1
             , 'strong'     : 1
             , 'strike'     : 1
             , 'table'      : 1
             , 'tbody'      : 1
             , 'thead'      : 1
             , 'td'         : 1
             , 'th'         : 1
             , 'title'      : 1
             , 'tr'         : 1
             , 'tt'         : 1
             , 'u'          : 1
             , 'ul'         : 1
             }

NASTY_TAGS = { 'script'     : 1
             , 'object'     : 1
             , 'embed'      : 1
             , 'applet'     : 1
             }

class IllegalHTML( ValueError ):
    pass

from Products.PortalTransforms.transforms.safe_html import scrubHTML
