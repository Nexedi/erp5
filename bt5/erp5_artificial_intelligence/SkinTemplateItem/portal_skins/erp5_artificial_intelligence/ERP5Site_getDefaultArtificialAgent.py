portal = context.getPortalObject()
return portal.portal_catalog.getResultValue(
  portal_type='Artificial Agent',
  validation_state='validated',
  reference = 'default',
  parent_uid=portal.artificial_agent_module.getUid()
)
