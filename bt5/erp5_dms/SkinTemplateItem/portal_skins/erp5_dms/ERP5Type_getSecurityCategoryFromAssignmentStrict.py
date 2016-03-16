"""
  This does the same as ERP5Type_getSecurityCategoryFromAssignmentTree, but we use it if we want
only the group the user is directly assigned to (not the whole group hierarchy path).
"""

return context.ERP5Type_getSecurityCategoryFromAssignmentTree(base_category_list, user_name, object, portal_type, strict=True)
