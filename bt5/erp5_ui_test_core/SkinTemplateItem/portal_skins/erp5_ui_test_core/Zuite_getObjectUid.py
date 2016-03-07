"""
  Get object's uid.
"""
return context.portal_catalog.getResultValue(**kw).getUid()
