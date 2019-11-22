from Products.PortalTransforms.Tool.TransformTool import TransformTool

PKG_NAME = 'PortalTransforms'

tools = (
    TransformTool,
    )

# XXX backward compatibility tricks to make old PortalTransform based Mimetypes
# running (required)
import sys
this_module = sys.modules[__name__]

from Products.MimetypesRegistry import mime_types
setattr(this_module, 'mime_types', mime_types)

from Products.MimetypesRegistry import MimeTypeItem
setattr(this_module, 'MimeTypeItem', MimeTypeItem)

from Products.MimetypesRegistry import MimeTypeItem
sys.modules['Products.PortalTransforms.zope.MimeTypeItem'] = MimeTypeItem

def initialize(context):
    from Products.CMFCore import utils
    utils.ToolInit("%s Tool" % PKG_NAME,
                   tools=tools,
                   icon="tool.gif",
                   ).initialize(context)
