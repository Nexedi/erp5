artifical_task = context
comment_list = []
for line in artifical_task.objectValues(
  portal_type='Artificial Task Line',
  sort_on=[('creation_date', 'ascending')],
  simulation_state = ('stopped', 'delivered')
 ):
  comment_list.append((dict(
      date=line.getCreationDate().ISO8601(),
      text=line.getTextContent(),
      response = True if line.getSimulationState() == 'delivered' else False
  )))

return comment_list
