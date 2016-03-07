"""
  XXX: Return list of Persons who belong to a position.
"""
kw['portal_type'] = 'Career'
kw['agent_uid'] = context.getUid()
return context.portal_catalog(**kw)
