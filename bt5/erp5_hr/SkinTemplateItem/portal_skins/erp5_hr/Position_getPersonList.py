"""
  Return list of Persons that have this position in their Career.
"""
kw['portal_type'] = 'Career'
kw['agent_uid'] = context.getUid()
return [x.getParentValue() for x in context.portal_catalog(**kw)]
