from Products.MimetypesRegistry import MimeTypesRegistry, mime_types
from Products.MimetypesRegistry.MimeTypeItem import MimeTypeItem
import six

preferred_extension_dict = {
  "bin": "application/octet-stream",
  "jpg": "image/jpeg",
  "js": "application/javascript",
  "swf": "application/vnd.adobe.flash.movie",
  "tar": "application/x-tar",
}

additional_mimetype_item_list = (
  {
    "name": "OnlyOffice Text",
    "mimetypes": ("application/x-asc-text",),
    "extensions": ("docy",),
    "binary": True,
    "icon_path": "application.png",
  },
  {
    "name": "OnlyOffice Spreadsheet",
    "mimetypes": ("application/x-asc-spreadsheet",),
    "extensions": ("xlsy",),
    "binary": True,
    "icon_path": "application.png",
  },
  {
    "name": "OnlyOffice Presentation",
    "mimetypes": ("application/x-asc-presentation",),
    "extensions": ("ppty",),
    "binary": True,
    "icon_path": "application.png",
  },
)

def initialize(registry):
    mime_types.initialize(registry)
    for ext, mime in six.iteritems(preferred_extension_dict):
        mime, = registry.lookup(mime)
        assert type(mime.extensions) is tuple
        x = list(mime.extensions)
        x.remove(ext)
        x.insert(0, ext)
        mime.extensions = tuple(x)
    for item in additional_mimetype_item_list:
      registry.manage_addMimeType(
        id=item["name"],
        mimetypes=item["mimetypes"],
        extensions=item["extensions"],
        binary=item["binary"],
        icon_path=item["icon_path"],
      )

MimeTypesRegistry.initialize = initialize
