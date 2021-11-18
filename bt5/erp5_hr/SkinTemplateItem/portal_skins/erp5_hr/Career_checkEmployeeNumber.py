if context.portal_catalog(portal_type='Career',
                          parent_uid=context.getParentUid(),
                          reference=context.getReference(),
                          validation_state='open'):
  return ['There has already started career with same employee number']
return []
