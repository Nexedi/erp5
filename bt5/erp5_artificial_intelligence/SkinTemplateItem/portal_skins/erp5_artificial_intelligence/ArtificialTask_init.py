artificial_task = context


tool_list = artificial_task.ArtificialTask_getDefaultToolList()
skill_list = artificial_task.ArtificialTask_getDefaultSkillList()
model = artificial_task.ArtificialTask_getDefaultModel()
connector = artificial_task.ArtificialTask_getDefaultConnector()

artificial_task.edit(
  model = model,
  tool_list = tool_list,
  skill_list = skill_list,
  connector_value = connector
)
