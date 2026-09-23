from Products.ERP5Type.Message import translateString
artificial_task = context
simulation_state = artificial_task.getSimulationState()


if simulation_state == 'processing':
  return context.Base_redirect(keep_items={'portal_status_message': translateString('AI Assistant is already processing')})

portal = artificial_task.getPortalObject()
line = artificial_task.newContent(
  portal_type='Artificial Task Line',
  text_content=description,
  destination = artificial_agent,
  source_value = portal.portal_membership.getAuthenticatedMember().getUserValue()
)
line.stop()
artificial_task.start()
return artificial_task.Base_redirect(keep_items={'portal_status_message': translateString('AI Assistant is requested')})
