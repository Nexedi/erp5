"""Returns a list of temp base objects"""
from builtins import str
from builtins import range
from Products.ERP5Type.Document import newTempBase
portal_object = context.getPortalObject()
return [newTempBase(portal_object, str(x), a=x, b=x) for x in range(10)]
