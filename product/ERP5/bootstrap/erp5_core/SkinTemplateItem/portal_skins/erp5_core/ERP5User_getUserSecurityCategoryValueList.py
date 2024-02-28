"""
Override this script to customise user security group generation.

It is called on the context of the ERP5 document which represents the user.

This is called when a user object is being prepared by PAS, typically at the
end of traversal but also when calling getUser and getUserById API, in order
to list the security groups the user is member of.
When called by PAS, this script is called in a super-user security context.
"""
return context.ERP5User_getSecurityCategoryValueFromAssignment(
  rule_dict={
    tuple(context.getPortalObject().getPortalAssignmentBaseCategoryList()): ((), )
  },
)
