artificial_task = context


tool_list = artificial_task.ArtificialTask_getDefaultToolList()
skill_list = artificial_task.ArtificialTask_getDefaultSkillList()
model = artificial_task.ArtificialTask_getDefaultModel()
connector = artificial_task.ArtificialTask_getDefaultConnector()

portal = artificial_task.getPortalObject()
task_report = portal.artificial_task_report_module.newContent(portal_type='Artificial Task Report')


artificial_task.edit(
  model = model,
  tool_list = tool_list,
  skill_list = skill_list,
  connector_value = connector
)

task_report.edit(
  follow_up_value = artificial_task
)


artificial_task.plan()
