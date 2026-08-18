from Products.ERP5Type.Message import translateString

artificial_task = context.newContent(portal_type='Artificial Task')
artificial_task.ArtificialTask_createCommentLine(data=data, file=file)

return artificial_task.Base_redirect(
  'view',
  keep_items={
    'portal_status_message': translateString('New Artificial Task is created')
  })
