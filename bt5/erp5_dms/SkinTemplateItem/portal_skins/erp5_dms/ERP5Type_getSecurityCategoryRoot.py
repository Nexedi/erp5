"""
This is the same as ERP5Type_getSecurityCategoryFromAssignmentTree
only it returns only the first part of category
It is used e.g. to figure out if the user is working anywhere
in the certain organisation - for this, all we need is the first part
of the group category.
"""

return context.ERP5Type_getSecurityCategoryFromAssignmentTree(base_category_list, user_name, obj, portal_type, strict=True, root=True)
