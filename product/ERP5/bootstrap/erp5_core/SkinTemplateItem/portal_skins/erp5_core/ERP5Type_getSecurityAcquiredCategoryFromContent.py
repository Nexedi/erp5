"""This script is similar to ERP5Type_getSecurityCategoryFromContent, but it
uses acquisition to get categories.

Note that if you design a security with acquired categories you may have problems
to regenerate security dynamically when thoses acquired values are modified on other
documents from which we acquire those values, just because this "other document" doesn't
know which documents are acquiring values.

If unsure, you should use ERP5Type_getSecurityCategoryFromContent.
"""
category_list = []

if ob is None:
  return []

for base_category in base_category_list:
  category_list.append({base_category: ob.getAcquiredCategoryMembershipList(base_category)})

return category_list
