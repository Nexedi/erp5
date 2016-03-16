"""
Return a list of brains according to given catalog arguments.
Only matches validated documents whose portal_type is part of "resource" group.
"""
portal = context.getPortalObject()
return portal.portal_catalog(
  validation_state='validated',
  portal_type=portal.getPortalResourceTypeList(),
  **kw
)
