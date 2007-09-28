from Products.MimetypesRegistry.MimeTypeItem import MimeTypeItem
from Products.MimetypesRegistry.common import MimeTypeException


map = {
    # '.extension' : 'mimetype',
    '.svg' : 'image/svg+xml', # scaleable vector graphics
    '.pjpg' : 'image/pjpeg', # scaleable vector graphics
    
}

def initialize(registry):
    #Find things that are not in the specially registered mimetypes
    #and add them using some default policy, none of these will impl
    #iclassifier
    for ext, mt in map.items():
        if ext[0] == '.':
            ext = ext[1:]
        
        if registry.lookupExtension(ext):
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
            continue
        isBin = mt.split('/', 1)[0] != "text"
        registry.register(MimeTypeItem(mt, (mt,), (ext,), isBin))
