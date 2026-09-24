from Products.ERP5Type.Message import translateString

artificial_task = context.newContent(portal_type='Artificial Task')
artificial_task.ArtificialTask_createCommentLine(data=data, file=file, batch=1)
default_artificial_agent = context.getPortalObject().ERP5Site_getDefaultArtificialAgent()

if default_artificial_agent:
  artificial_task.setDestinationValue(default_artificial_agent, portal_type='Artificial Agent')
  artificial_task.setContributorValue(default_artificial_agent, portal_type='Artificial Agent')

artificial_task.confirm()
artificial_task.start()

return artificial_task.Base_redirect(
  'view',
  keep_items={
    'portal_status_message': translateString('New Artificial Task is created')
  })
