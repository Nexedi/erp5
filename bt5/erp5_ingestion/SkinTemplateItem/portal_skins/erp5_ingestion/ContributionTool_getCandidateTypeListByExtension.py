"""
  Find by give filename extension which portal_type is the right one.
  Use content_type_registry for that.
"""
from Products.CMFCore.utils import getToolByName

registry = getToolByName(context, 'content_type_registry', None)
if registry is None:
  return (None, )
else:
  pt = registry.findTypeName('a.%s' %ext, None, None)
  return (pt,)
