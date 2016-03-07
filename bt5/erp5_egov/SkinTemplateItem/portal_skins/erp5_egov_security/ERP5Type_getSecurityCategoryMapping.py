"""
Understand this and make it suit your needs
"""
return (
# This one combines function, type of procedure and destination to generate a security group
  ('ERP5Type_getSecurityCategoryFromAssignmentStrict', ['destination', 'function', 'publication_section', ] ),
# This one is the usual group and function security
  ('ERP5Type_getSecurityCategoryFromAssignmentStrict', ['function', 'group',] ),
  ('ERP5Type_getSecurityCategoryFromAssignmentParentGroup', ['function', 'group',  ]),
# This one is the usual group, function and site security, needed if access rights depend on site
  ('ERP5Type_getSecurityCategoryFromAssignmentStrict', ['function', 'group', 'site'] ),
# This one is the usual group security
  ('ERP5Type_getSecurityCategoryFromAssignmentStrict', ['group',] ),
  ('ERP5Type_getSecurityCategoryFromAssignmentParent', ['group',] ),

# This one is the usual function security
  ('ERP5Type_getSecurityCategoryFromAssignment', ['function'] ),
# This one is the usual role security
  ('ERP5Type_getSecurityCategoryFromEntity', ['role'] ),
  ('ERP5Type_getSecurityCategoryFromAssignmentStrict', ['role', ]),
# This one combines role and publication_section
  ('ERP5Type_getSecurityCategoryFromAssignmentStrict', ['publication_section', 'role', ] ),

)
