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

def changeObjectClass(self, object_id, new_class):
  """Creates a copy of object_id inside self, changing its class to
  new_class"""
  old_obj = self._getOb(object_id)
  self._delObject(object_id)
  new_obj = new_class(object_id)
  new_obj.__dict__.update(old_obj.__dict__)
  self._setObject(object_id, new_obj)
  
