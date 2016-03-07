portal = context.getPortalObject()
return context.objectValues(), portal.portal_catalog(
  portal_type=portal.getPortalResourceTypeList(),
  strict_use_uid=context.getUid(),
  validation_state='validated',
)
