"""
Core security script - defines the way to get security groups of the current user.

WARNING: providing such script in erp5_dms could be dangerous
if this conflicts with an existing production site which uses
deprecated ERP5Type_asSecurityGroupIdList
"""

return (
  # Person security
  ('ERP5Type_getSecurityCategoryFromAssignment', ['function']),
  ('ERP5Type_getSecurityCategoryFromAssignmentParent', ['function']),
  # Wendelin Telecom security
  ('ERP5Type_getSecurityCategoryFromAssignment', ['destination_project', 'function']),
)
