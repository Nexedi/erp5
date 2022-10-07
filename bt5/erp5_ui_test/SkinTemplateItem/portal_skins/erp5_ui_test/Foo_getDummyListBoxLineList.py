"""Returns a list of temp base objects"""
from Products.ERP5Type.Document import newTempBase
from six.moves import range
portal_object = context.getPortalObject()
return [newTempBase(portal_object, str(x), a=x, b=x) for x in range(10)]
