import os.path
from Products.MimetypesRegistry.MimeTypeItem import MimeTypeItem
from Products.MimetypesRegistry.MimeTypeItem import guess_icon_path
from Products.MimetypesRegistry.common import MimeTypeException

try:
    from zope.contenttype import add_files
except ImportError: # BBB: Zope < 2.10
    try:
        from zope.app.content_types import add_files
    except ImportError: # BBB: Zope < 2.9
        from OFS.content_types import add_files

import mimetypes as pymimetypes

mimes_initialized = False

def mimes_initialize():
    global mimes_initialized
    if mimes_initialized:
        return
    mimes_initialized = True
    # Augment known mime-types.
    here = os.path.dirname(os.path.abspath(__file__))
    add_files([os.path.join(here, 'mime.types')])

# don't register the mimetype from python mimetypes if matching on of
# this extensions.
skip_extensions = (
    )

def initialize(registry):
    # Find things that are not in the specially registered mimetypes
    # and add them using some default policy, none of these will impl
    # iclassifier

    # Read our included mime.types file, in addition to whatever the
    # mimetypes python module might have found.
    mimes_initialize()

    # Initialize from registry known mimetypes if we are on Windows
    # and pywin32 is available.
    try:
        from windows_mimetypes import initialize
        initialize()
    except ImportError:
        pass
    
    for ext, mt in pymimetypes.types_map.items():
        if ext[0] == '.':
            ext = ext[1:]

        if registry.lookupExtension(ext):
            continue
        if ext in skip_extensions:
            continue

        try:
            mto =  registry.lookup(mt)
        except MimeTypeException:
            # malformed MIME type
            continue
        if mto:
            mto = mto[0]
            if not ext in mto.extensions:
                registry.register_extension(ext, mto)
                mto.extensions += (ext, )
                # here we guess icon path again, to find icon match the new ext
                mto.icon_path = guess_icon_path(mto)
            continue
        isBin = mt.split('/', 1)[0] != "text"
        registry.register(MimeTypeItem(mt, (mt,), (ext,), isBin))
