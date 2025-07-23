data_analysis = state_change['object']

tag = script.id + '_' + data_analysis.getRelativeUrl()
activate_kw = dict(tag=tag)

data_analysis.reindexObject(activate_kw=activate_kw)

data_analysis_line_list = data_analysis.contentValues(portal_type='Data Analysis Line')
if len(data_analysis_line_list) == 0:
  return

for data_analysis_line in data_analysis_line_list:
  for value in data_analysis_line.getAggregateValueList():
    value.activate(after_tag=tag).updateLocalRolesOnSecurityGroups()
