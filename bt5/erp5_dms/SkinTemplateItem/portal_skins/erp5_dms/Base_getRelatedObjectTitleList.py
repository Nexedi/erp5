"""
get related object title list in a security-aware way (without throwing exception
if I don't have permissions to access the object)
"""

object_list = context.Base_getRelatedObjectValueList(base_category, portal_type_list)

title_list = [o.getTitle() for o in object_list]
return [t for t in title_list if t != '']
