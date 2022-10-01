for ti in sorted(context.getPortalObject().portal_types.contentValues(), key=lambda x:x.getId()):
  for ri in sorted(ti.contentValues(portal_type='Role Information'), key=lambda x:(x.getTitle(), x.getLocalRoleGroupId(), x.getRoleBaseCategoryScriptId(), x.getRoleBaseCategoryList())):
    print(ti.getId())
    print(" ", "\n  ".join([x for x in (
      "Title: %s" % ri.getTitle(),
      "Roles: %r" % ri.getRoleNameList(),
      "Condition: %s" % ri.getConditionText(),
      "Local Roles Group Id: %s" % ri.getLocalRoleGroupId(),
      "Base Categories: %r" % ri.getRoleBaseCategoryList(),
      "Base Category Script: %s" % ri.getRoleBaseCategoryScriptId(),
      "Categories: %r" % ri.getRoleCategoryList() )]))
    print()

return printed
