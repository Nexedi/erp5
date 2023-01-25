"""
  Returns the list of documents which belong to
  the current user or to the user provided as
  a parameter.

  WARNING: implementation depends on the fact
  that owner is being indexed.
"""
if user is None:
  user = context.portal_membership.getAuthenticatedMember().getId()

kw['portal_type'] = context.getPortalMyDocumentTypeList()
kw['owner'] = user

if 'validation_state' not in kw:
  kw['validation_state'] = "!=embedded"

return context.portal_catalog(**kw)
