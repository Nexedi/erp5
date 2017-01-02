portal_catalog = context.portal_catalog

for i in portal_catalog(portal_type='Text Post', simulation_state = 'Draft'):
  if i.getFollowUpUid() is None:
    EVR_list = portal_catalog(portal_type='Expense Validation Request', source_reference=i.getDestinationReference())
    if len(EVR_list) > 0:
      i.setFollowUpValue(EVR_list[0])
      i.post()
