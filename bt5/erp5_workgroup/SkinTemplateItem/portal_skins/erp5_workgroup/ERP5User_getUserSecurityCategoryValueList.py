"""
Override this script to customise user security group generation.

It is called on the context of the ERP5 document which represents the user.

This is called when a user object is being prepared by PAS, typically at the
end of traversal but also when calling getUser and getUserById API, in order
to list the security groups the user is member of.
When called by PAS, this script is called in a super-user security context.
"""
from Products.ERP5Security.Utils import getCachedValidAssignmentList
rule_dict = {
  tuple(context.getPortalObject().getPortalAssignmentBaseCategoryList()): ((), )
}

category_list = context.ERP5User_getSecurityCategoryValueFromAssignment(rule_dict=rule_dict)

for assignment in getCachedValidAssignmentList(context):
  workgroup = assignment.getDestinationValue(portal_type="Workgroup")
  if workgroup is not None:
    category_list.extend(
      workgroup.ERP5User_getSecurityCategoryValueFromAssignment(rule_dict=rule_dict))

return category_list
