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
