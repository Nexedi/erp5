request = container.REQUEST
movement = brain.getObject()

explanation = movement.getExplanationValue()

if movement.hasTitle():
  title = movement.getTitle()
else:
  title = explanation.getTitle()

analytic_property_list = [explanation.getReference()]
if analytic_column_list is None:
  analytic_column_list = request.get('analytic_column_list', ())

for property_name, property_title in analytic_column_list: #pylint: disable=unused-variable
  # XXX it would be a little better to reuse editable field
  if property_name == 'project':
    analytic_property_list.append(brain.Movement_getProjectTitle())
  elif property_name == 'function':
    analytic_property_list.append(brain.Movement_getFunctionTitle())
  elif property_name == 'funding':
    analytic_property_list.append(brain.Movement_getFundingTitle())
  else:
    analytic_property_list.append(movement.getProperty(property_name))

return "%s\n%s" % (title, ', '.join([x for x in analytic_property_list if x]))
