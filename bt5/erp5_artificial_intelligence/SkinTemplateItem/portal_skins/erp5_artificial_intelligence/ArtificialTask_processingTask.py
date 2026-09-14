artificial_task = context

# simulate background mode
portal = artificial_task.getPortalObject()

active_process = portal.portal_activities.newActiveProcess(
  start_date=DateTime(),
  causality_value=artificial_task,
)

active_process_relative_url = active_process.getRelativeUrl()

if artificial_task.getSimulationState() != 'processing':
  artificial_task.start()

artificial_task.activate(activity='SQLQueue').ArtificialTask_processingTaskWithBackgroundMode(
  message_list = message_list,
  tool_definition_list = tool_definition_list,
  compact_message_list = compact_message_list,
  initial_message_list = initial_message_length,
  is_subagent = is_subagent,
  active_process_relative_url = active_process_relative_url
)

return active_process_relative_url
