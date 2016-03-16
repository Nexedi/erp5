"""
  External validator for login_form
  that checks that reference is unique into the system.
"""
kw={'reference': editor,
    'portal_type': ['Person', 'Credential Request']}
email = context.portal_catalog.getResultValue(**kw)
if email is not None:
  return 0
return 1
