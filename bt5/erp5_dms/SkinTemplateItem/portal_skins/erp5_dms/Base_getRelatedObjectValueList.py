"""
get related object value list in a security-aware way (without throwing exception
if I don't have permissions to access the object)
"""

category_list = context.getPropertyList(base_category)
if category_list is None:
  return []

def getValueIfAvailable(category):
  ob = context.restrictedTraverse(category, None)
  return ob

object_list = [getValueIfAvailable(category) for category in category_list]
object_list = [o for o in object_list if o is not None]

if portal_type_list is not None:
  object_list = [o for o in object_list if o.portal_type in portal_type_list]

return object_list
