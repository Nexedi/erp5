artificial_task = context

# simulate background mode
portal = artificial_task.getPortalObject()

dummy_response = portal.artificial_dummy_response_module.newContent(
  portal_type='Artificial Dummy Response',
)

dummy_response_relative_url = dummy_response.getRelativeUrl()

if artificial_task.getSimulationState() != 'processing':
  artificial_task.start()

artificial_task.activate(activity='SQLQueue').ArtificialTask_processingTaskWithBackgroundMode(
  message_list = message_list,
  tool_definition_list = tool_definition_list,
  compact_message_list = compact_message_list,
  initial_message_list = initial_message_length,
  is_subagent = is_subagent,
  dummy_response_relative_url = dummy_response_relative_url
)

return dummy_response_relative_url
