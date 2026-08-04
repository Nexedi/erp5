portal = context.getPortalObject()
return portal.portal_catalog(
  portal_type='Artificial Agent',
  validation_state='validated',
  parent_uid=portal.artificial_agent_module.getUid(),
  sort_on=(('modificiation_date', 'DESC',))
)
