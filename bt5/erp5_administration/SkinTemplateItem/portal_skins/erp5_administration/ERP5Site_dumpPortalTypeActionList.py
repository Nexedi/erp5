for ti in sorted(context.getPortalObject().portal_types.contentValues(), key=lambda x:x.getId()):
  for ai in sorted(ti.contentValues(portal_type='Action Information'), key=lambda x:x.getReference()):
    print(ti.getId())
    print(" ", "\n  ".join([x for x in (
      "Reference: %s" % ai.getReference(),
      "Title: %s" % ai.getTitle(),
      "Action: %s" % ai.getActionText(),
      "Icon: %s" % ai.getIconText(),
      "Permission: %s" % ai.getActionPermission(),
      "Action Type: %s" % ai.getActionType(),
      "Visible: %s" % ai.getVisible(),
      "Index: %s" % ai.getFloatIndex())]))
    print()

return printed
