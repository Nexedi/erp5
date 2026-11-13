from Products.ERP5Type.Message import translateString
artificial_task = context
simulation_state = artificial_task.getSimulationState()


if simulation_state == 'started':
  return context.Base_redirect(keep_items={'portal_status_message': translateString('AI Assistant is already processing')})

portal = artificial_task.getPortalObject()
line = artificial_task.newContent(
  portal_type='Artificial Task Line',
  text_content=description,
  destination = artificial_agent,
  source_value = portal.portal_membership.getAuthenticatedMember().getUserValue()
)
line.stop()
if artificial_task.getSimulationState() == 'draft':
  artificial_task.confirm()

if artificial_task.getSimulationState() == 'confirmed':
  artificial_task.start()
else:
  artificial_task.restart()

contributor_list = artificial_task.getContributorList()
if artificial_agent not in contributor_list:
  contributor_list.append(artificial_agent)
  artificial_task.setContributorList(contributor_list)

return artificial_task.Base_redirect(keep_items={'portal_status_message': translateString('AI Assistant is requested')})
