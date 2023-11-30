mirror_node_formatted_title = ''
if context.mirror_node_uid:
  brain_list = context.getPortalObject().portal_catalog(
    uid=context.mirror_node_uid,
    portal_type='Account',
    limit=2,
  )
  if brain_list:
    brain, = brain_list
    mirror_node_formatted_title = brain.getObject().Account_getFormattedTitle()

return mirror_node_formatted_title
