result = []

for r in context.contentValues(filter={'portal_type': 'Requirement'}, checked_permission='View'):
  if not r.getRequirementRelatedValueList():
    if not r.contentValues(filter={'portal_type': 'Requirement'}, checked_permission='View'):
      result.append(r.getUid())
  result.extend(r.RequirementDocument_getOrphanedRequirementUidList())

return result
