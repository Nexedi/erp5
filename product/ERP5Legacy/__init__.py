import sys
from Products.ERP5Type.Utils import initializeProduct, updateGlobals

this_module = sys.modules[__name__]
document_classes = updateGlobals(this_module, globals())

def initialize(context):
  initializeProduct(context, this_module, globals(),
                    document_classes=document_classes)
