"""
get related object title in a security-aware way (without throwing exception
if I don't have permissions to access the object)
"""

title_list = context.Base_getRelatedObjectTitleList(category, portal_type_list)

if title_list:
  return title_list[0]
else:
  return ''

# XXX-JPS What would be the problem in using getMyCategoryTitle() ?
