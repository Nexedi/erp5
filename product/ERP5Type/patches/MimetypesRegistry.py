from Products.MimetypesRegistry import MimeTypesRegistry, mime_types

preferred_extension_dict = {
  "bin": "application/octet-stream",
  "jpg": "image/jpeg",
}

def initialize(registry):
    mime_types.initialize(registry)
    for ext, mime in preferred_extension_dict.items():
        mime, = registry.lookup(mime)
        assert type(mime.extensions) is tuple
        x = list(mime.extensions)
        x.remove(ext)
        x.insert(0, ext)
        mime.extensions = tuple(x)

MimeTypesRegistry.initialize = initialize
