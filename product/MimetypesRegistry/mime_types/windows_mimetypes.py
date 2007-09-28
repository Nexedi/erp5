# Utilities for mime-types and the Windows registry.
import _winreg
import win32api
import win32con
import mimetypes

import logging
logger = logging.getLogger('mimetypes.win32')

# "safely" query a value, returning a default when it doesn't exist.
def _RegQueryValue(key, value, default=None):
    try:
        data, typ = win32api.RegQueryValueEx(key, value)
    except win32api.error:
        return default
    if typ == win32con.REG_EXPAND_SZ:
        data = win32api.ExpandEnvironmentStrings(data)
    if type in (win32con.REG_EXPAND_SZ, win32con.REG_SZ):
        # Occasionally see trailing \0 chars.
        data = data.rstrip('\0')
    return data

def get_desc_for_mimetype(mime_type):
    try:
        hk = win32api.RegOpenKey(win32con.HKEY_CLASSES_ROOT,
                                 r"MIME\Database\Content Type\\" + mime_type)
        desc = _RegQueryValue(hk, "")
    except win32api.error, details:
        logger.info("win32api error fetching description for mime-type %r: %s",
                     mime_type, details)
        desc = None
    logger.debug("mime-type %s has description %s", mime_type, desc)
    return desc

def get_ext_for_mimetype(mime_type):
    try:
        hk = win32api.RegOpenKey(win32con.HKEY_CLASSES_ROOT,
                                 r"MIME\Database\Content Type\\" + mime_type)
        ext = _RegQueryValue(hk, "Extension")
    except win32api.error, details:
        logger.info("win32api error fetching extension for mime-type %r: %s",
                     mime_type, details)
        ext = None
    logger.debug("mime-type %s has extension %s", mime_type, ext)
    return ext

def get_mime_types():
    try:
        hk = win32api.RegOpenKey(win32con.HKEY_CLASSES_ROOT,
                                 r"MIME\Database\Content Type")
        items = win32api.RegEnumKeyEx(hk)
    except win32api.error, details:
        logger.info("win32api error fetching mimetypes: %s",
                    details)
        items = []
    return [i[0] for i in items if i[0]]

def normalize(mt):
    # Some mimetypes might have extra ';q=value' params.
    return mt.lower().split(';')[0]

def initialize():
    if not mimetypes.inited:
        mimetypes.init()

    for mt in get_mime_types():
        ext = get_ext_for_mimetype(mt)
        if ext is None:
            continue
        if not mimetypes.types_map.has_key(ext):
            mimetypes.add_type(normalize(mt), ext)

if __name__=='__main__':
    for mt in get_mime_types():
        ext = get_ext_for_mimetype(mt)
        desc = get_desc_for_mimetype(mt)
        print "%s (%s) - %s" % (mt.lower(), desc, ext)
    import code; code.interact(local=locals())
