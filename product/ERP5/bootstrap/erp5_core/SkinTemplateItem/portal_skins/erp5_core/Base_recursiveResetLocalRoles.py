for local_role in context.get_local_roles():
  context.manage_delLocalRoles((local_role[0],))

for subobj in context.objectValues():
  subobj.Base_recursiveResetLocalRoles()
