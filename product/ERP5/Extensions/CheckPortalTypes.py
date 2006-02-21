from Globals import get_request
from Products.CMFCore.utils import getToolByName

def fixProductNames(self, REQUEST=None):
  msg = ''
  portal_types = getToolByName(self, 'portal_types')
  for contentType in portal_types.listTypeInfo():
    if hasattr(contentType, 'product'):
      if contentType.product in ('ERP5', 'Coramy', 'Nexedi'):
        msg += 'Change the Product Name of %s from %s to ERP5Type\n' % (contentType.getId(), contentType.product)
        contentType.product = 'ERP5Type'
  return msg

def changeObjectClass(self, container, object_id, new_class):
  """Creates a copy of object_id inside container, changing its class to
  new_class"""
  old_obj = container._getObj(object_id)
  new_obj = new_class(object_id)
  new_obj.__dict__.update(old_obj.__dict__)
  container._setObject(object_id, new_obj)
  
  
