if context.portal_catalog(portal_type='Career',
                          parent_uid=context.getParentUid(),
                          reference=context.getReference(),
                          validation_state='open'):
  return ['There already is a started career with the same employee number']
return []
