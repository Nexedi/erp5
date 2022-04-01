for ti in sorted(context.getPortalObject().portal_types.contentValues(), key=lambda x:x.getId()):
  print(ti.getId())
  print(" ", "\n  ".join([x for x in (
    "Short Title: %s" % ti.getShortTitle(),
    "Class: %s" % ti.getTypeClass(),
    "Init Script: %s" % ti.getTypeInitScriptId(),
    "Add Permission: %s" % ti.getTypeAddPermission(),
    "Acquire Local Roles: %s" % ti.getTypeAcquireLocalRole(),
    "Property Sheets: %r" % sorted(ti.getTypePropertySheetList()),
    "Base Categories: %r" % sorted(ti.getTypeBaseCategoryList()),
    "Allowed Content Types: %r" % sorted(ti.getTypeAllowedContentTypeList()),
    "Hidden Content Types: %r" % sorted(ti.getTypeHiddenContentTypeList()),
    "Searchable Property: %r" % sorted(ti.getSearchableTextPropertyIdList()),
    "Searchable Method: %r" % sorted(ti.getSearchableTextMethodIdList()),
    )]))
  print()

return printed
