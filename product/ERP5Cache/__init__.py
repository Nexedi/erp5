""" Cache tool initializion moved to ERP/__init__"""

import sys, Permissions, os
from Globals import package_home
this_module = sys.modules[ __name__ ]
product_path = package_home( globals() )
this_module._dtmldir = os.path.join( product_path, 'dtml' )
from Products.ERP5Type.Utils import initializeProduct, updateGlobals

#import CacheTool
  
object_classes = ()
portal_tools = () #(CacheTool.CacheTool,)
portal_tools = ()
content_classes = ()
content_constructors = ()
document_classes = updateGlobals( this_module, globals(), permissions_module = Permissions)


def initialize( context ):
  import Document
  initializeProduct(context, this_module, globals(),
                    document_module = Document,
                    document_classes = document_classes,
                    object_classes = object_classes,
                    portal_tools = portal_tools,
                    content_constructors = content_constructors,
                    content_classes = content_classes)
